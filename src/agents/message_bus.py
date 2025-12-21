"""
Agent Message Bus
Inter-agent communication using Redis Streams or NATS.
"""
import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine
from uuid import uuid4

from pydantic import BaseModel, Field

from src.core.logging import get_logger
from src.core.tracing import traced, add_span_attributes

logger = get_logger(__name__)


class MessagePriority(int, Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


class MessageType(str, Enum):
    """Types of inter-agent messages."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    BROADCAST = "broadcast"
    HEARTBEAT = "heartbeat"


class AgentMessage(BaseModel):
    """Message format for inter-agent communication."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: MessageType
    source: str  # Agent ID
    target: str | None = None  # None for broadcasts
    subject: str
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = None  # For request/response tracking
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ttl_seconds: int = 300  # Time-to-live

    def to_json(self) -> str:
        """Serialize message to JSON."""
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> "AgentMessage":
        """Deserialize message from JSON."""
        return cls.model_validate_json(data)


class MessageHandler:
    """Handler for processing messages."""

    def __init__(
        self,
        subject_pattern: str,
        handler: Callable[[AgentMessage], Coroutine[Any, Any, AgentMessage | None]],
        message_types: list[MessageType] | None = None,
    ):
        self.subject_pattern = subject_pattern
        self.handler = handler
        self.message_types = message_types or list(MessageType)

    def matches(self, message: AgentMessage) -> bool:
        """Check if this handler matches the message."""
        if message.type not in self.message_types:
            return False

        # Simple wildcard matching
        if self.subject_pattern == "*":
            return True
        if self.subject_pattern.endswith(".*"):
            prefix = self.subject_pattern[:-2]
            return message.subject.startswith(prefix)

        return message.subject == self.subject_pattern


class BaseMessageBus(ABC):
    """Abstract base class for message bus implementations."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._handlers: list[MessageHandler] = []
        self._running = False

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the message bus."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the message bus."""
        pass

    @abstractmethod
    async def publish(self, message: AgentMessage) -> None:
        """Publish a message to the bus."""
        pass

    @abstractmethod
    async def subscribe(self, subject: str) -> None:
        """Subscribe to a subject pattern."""
        pass

    def register_handler(
        self,
        subject_pattern: str,
        handler: Callable[[AgentMessage], Coroutine[Any, Any, AgentMessage | None]],
        message_types: list[MessageType] | None = None,
    ) -> None:
        """Register a message handler."""
        self._handlers.append(
            MessageHandler(subject_pattern, handler, message_types)
        )
        logger.info(f"Registered handler for {subject_pattern}")

    async def _dispatch_message(self, message: AgentMessage) -> None:
        """Dispatch message to matching handlers."""
        for handler in self._handlers:
            if handler.matches(message):
                try:
                    response = await handler.handler(message)
                    if response and message.type == MessageType.REQUEST:
                        response.correlation_id = message.id
                        response.target = message.source
                        await self.publish(response)
                except Exception as e:
                    logger.error(f"Handler error: {e}")


class RedisMessageBus(BaseMessageBus):
    """Redis Streams based message bus implementation."""

    def __init__(
        self,
        agent_id: str,
        redis_url: str = "redis://localhost:6379",
        stream_prefix: str = "kosmos:agents:",
    ):
        super().__init__(agent_id)
        self.redis_url = redis_url
        self.stream_prefix = stream_prefix
        self._redis = None
        self._consumer_group = f"kosmos-agents"
        self._consumer_name = agent_id

    async def connect(self) -> None:
        """Connect to Redis."""
        import redis.asyncio as aioredis

        self._redis = await aioredis.from_url(self.redis_url)
        self._running = True

        # Create consumer group if it doesn't exist
        stream_name = f"{self.stream_prefix}messages"
        try:
            await self._redis.xgroup_create(
                stream_name,
                self._consumer_group,
                id="0",
                mkstream=True,
            )
        except Exception:
            pass  # Group already exists

        # Start message consumer
        asyncio.create_task(self._consume_messages())
        logger.info(f"Redis message bus connected for agent {self.agent_id}")

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        self._running = False
        if self._redis:
            await self._redis.close()
        logger.info(
            f"Redis message bus disconnected for agent {self.agent_id}")

    @traced(name="redis_bus_publish")
    async def publish(self, message: AgentMessage) -> None:
        """Publish message to Redis Stream."""
        if not self._redis:
            raise RuntimeError("Not connected to Redis")

        stream_name = f"{self.stream_prefix}messages"

        await self._redis.xadd(
            stream_name,
            {
                "message": message.to_json(),
                "source": message.source,
                "target": message.target or "*",
                "subject": message.subject,
                "priority": str(message.priority.value),
            },
            maxlen=10000,  # Limit stream size
        )

        add_span_attributes({
            "message.id": message.id,
            "message.type": message.type.value,
            "message.subject": message.subject,
        })

        logger.debug(f"Published message {message.id} to {message.subject}")

    async def subscribe(self, subject: str) -> None:
        """Subscribe to a subject pattern (handled by handlers)."""
        # Redis Streams don't have native subject filtering
        # Filtering is done in _consume_messages
        logger.info(f"Subscribed to {subject}")

    async def _consume_messages(self) -> None:
        """Consume messages from Redis Stream."""
        stream_name = f"{self.stream_prefix}messages"

        while self._running:
            try:
                messages = await self._redis.xreadgroup(
                    self._consumer_group,
                    self._consumer_name,
                    {stream_name: ">"},
                    count=10,
                    block=1000,
                )

                for stream, entries in messages:
                    for entry_id, data in entries:
                        try:
                            message = AgentMessage.from_json(data[b"message"])

                            # Check if message is for us
                            if message.target and message.target != self.agent_id:
                                continue

                            await self._dispatch_message(message)

                            # Acknowledge message
                            await self._redis.xack(
                                stream_name,
                                self._consumer_group,
                                entry_id,
                            )
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Consumer error: {e}")
                await asyncio.sleep(1)


class NATSMessageBus(BaseMessageBus):
    """NATS based message bus implementation."""

    def __init__(
        self,
        agent_id: str,
        nats_url: str = "nats://localhost:4222",
        subject_prefix: str = "kosmos.agents.",
    ):
        super().__init__(agent_id)
        self.nats_url = nats_url
        self.subject_prefix = subject_prefix
        self._nc = None
        self._js = None  # JetStream context
        self._subscriptions = []

    async def connect(self) -> None:
        """Connect to NATS."""
        import nats

        self._nc = await nats.connect(self.nats_url)
        self._js = self._nc.jetstream()
        self._running = True

        # Create stream if it doesn't exist
        try:
            await self._js.add_stream(
                name="KOSMOS_AGENTS",
                subjects=[f"{self.subject_prefix}*"],
                max_msgs=100000,
                max_age=3600,  # 1 hour retention
            )
        except Exception:
            pass  # Stream already exists

        logger.info(f"NATS message bus connected for agent {self.agent_id}")

    async def disconnect(self) -> None:
        """Disconnect from NATS."""
        self._running = False

        for sub in self._subscriptions:
            await sub.unsubscribe()

        if self._nc:
            await self._nc.close()

        logger.info(f"NATS message bus disconnected for agent {self.agent_id}")

    @traced(name="nats_bus_publish")
    async def publish(self, message: AgentMessage) -> None:
        """Publish message to NATS."""
        if not self._nc:
            raise RuntimeError("Not connected to NATS")

        subject = f"{self.subject_prefix}{message.subject}"

        await self._js.publish(
            subject,
            message.to_json().encode(),
            headers={
                "source": message.source,
                "target": message.target or "*",
                "priority": str(message.priority.value),
            },
        )

        add_span_attributes({
            "message.id": message.id,
            "message.type": message.type.value,
            "message.subject": message.subject,
        })

        logger.debug(f"Published message {message.id} to {subject}")

    async def subscribe(self, subject: str) -> None:
        """Subscribe to a NATS subject."""
        full_subject = f"{self.subject_prefix}{subject}"

        async def message_handler(msg):
            try:
                message = AgentMessage.from_json(msg.data.decode())

                # Check if message is for us
                target = msg.headers.get("target", "*") if msg.headers else "*"
                if target != "*" and target != self.agent_id:
                    return

                await self._dispatch_message(message)
                await msg.ack()
            except Exception as e:
                logger.error(f"Error processing NATS message: {e}")

        sub = await self._js.subscribe(
            full_subject,
            durable=f"{self.agent_id}-{subject.replace('.', '-')}",
            cb=message_handler,
        )
        self._subscriptions.append(sub)
        logger.info(f"Subscribed to {full_subject}")


class InMemoryMessageBus(BaseMessageBus):
    """In-memory message bus for testing."""

    _instance = None
    _messages: list[AgentMessage] = []
    _agents: dict[str, "InMemoryMessageBus"] = {}

    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        InMemoryMessageBus._agents[agent_id] = self

    async def connect(self) -> None:
        """No-op for in-memory bus."""
        self._running = True
        logger.info(
            f"In-memory message bus connected for agent {self.agent_id}")

    async def disconnect(self) -> None:
        """No-op for in-memory bus."""
        self._running = False
        if self.agent_id in InMemoryMessageBus._agents:
            del InMemoryMessageBus._agents[self.agent_id]

    async def publish(self, message: AgentMessage) -> None:
        """Publish to all in-memory agents."""
        InMemoryMessageBus._messages.append(message)

        for agent_id, bus in InMemoryMessageBus._agents.items():
            if message.target and message.target != agent_id:
                continue
            if agent_id != message.source:  # Don't send to self
                await bus._dispatch_message(message)

    async def subscribe(self, subject: str) -> None:
        """No-op for in-memory bus - all messages are delivered."""
        pass


# Factory function
async def create_message_bus(
    agent_id: str,
    bus_type: str = "redis",
    **kwargs,
) -> BaseMessageBus:
    """Create a message bus instance."""
    if bus_type == "redis":
        bus = RedisMessageBus(agent_id, **kwargs)
    elif bus_type == "nats":
        bus = NATSMessageBus(agent_id, **kwargs)
    elif bus_type == "memory":
        bus = InMemoryMessageBus(agent_id)
    else:
        raise ValueError(f"Unknown bus type: {bus_type}")

    await bus.connect()
    return bus

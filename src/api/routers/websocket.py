"""
WebSocket endpoint for real-time chat streaming.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from pydantic import BaseModel

from src.api.metrics import (
    websocket_connections_total,
    websocket_messages_total,
    track_time,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.user_connections: Dict[str, set] = {}

    async def connect(
        self,
        websocket: WebSocket,
        conversation_id: str,
        user_id: Optional[str] = None
    ) -> str:
        """Accept and track a new WebSocket connection."""
        await websocket.accept()

        connection_id = str(uuid4())

        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = {}
        self.active_connections[conversation_id][connection_id] = websocket

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)

        websocket_connections_total.labels(
            conversation_id=conversation_id
        ).inc()

        logger.info(
            f"WebSocket connected: {connection_id}",
            extra={
                "connection_id": connection_id,
                "conversation_id": conversation_id,
                "user_id": user_id,
            }
        )

        return connection_id

    def disconnect(self, connection_id: str, conversation_id: str):
        """Remove a WebSocket connection."""
        if conversation_id in self.active_connections:
            if connection_id in self.active_connections[conversation_id]:
                del self.active_connections[conversation_id][connection_id]
                if not self.active_connections[conversation_id]:
                    del self.active_connections[conversation_id]

        for user_id, connections in self.user_connections.items():
            connections.discard(connection_id)

        websocket_connections_total.labels(
            conversation_id=conversation_id
        ).dec()

        logger.info(
            f"WebSocket disconnected: {connection_id}",
            extra={"connection_id": connection_id}
        )

    async def send_personal_message(
        self,
        message: dict,
        websocket: WebSocket
    ):
        """Send a message to a specific WebSocket."""
        await websocket.send_json(message)
        websocket_messages_total.labels(direction="outbound").inc()

    async def broadcast_to_conversation(
        self,
        message: dict,
        conversation_id: str,
        exclude_connection: Optional[str] = None
    ):
        """Broadcast a message to all connections in a conversation."""
        if conversation_id not in self.active_connections:
            return

        for conn_id, websocket in self.active_connections[conversation_id].items():
            if conn_id != exclude_connection:
                try:
                    await websocket.send_json(message)
                    websocket_messages_total.labels(direction="outbound").inc()
                except Exception as e:
                    logger.error(f"Failed to send to {conn_id}: {e}")

    async def stream_response(
        self,
        websocket: WebSocket,
        message_id: str,
        content_generator,
        agent: Optional[str] = None
    ):
        """Stream a response chunk by chunk."""
        full_content = ""

        async for chunk in content_generator:
            full_content += chunk
            await self.send_personal_message({
                "type": "stream",
                "id": message_id,
                "chunk": chunk,
                "agent": agent,
            }, websocket)
            await asyncio.sleep(0.01)  # Small delay for smooth streaming

        # Send completion message
        await self.send_personal_message({
            "type": "stream_end",
            "id": message_id,
            "full_content": full_content,
            "agent": agent,
            "timestamp": datetime.utcnow().isoformat(),
        }, websocket)

        return full_content


manager = ConnectionManager()


async def mock_agent_response(query: str):
    """Mock streaming response generator for demo purposes."""
    response = f"I received your message: '{query}'. Let me think about this..."

    words = response.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.05)  # Simulate thinking


@router.websocket("/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint for real-time chat.

    Message Types (Client -> Server):
    - {"type": "message", "content": "...", "agent": "optional_agent_id"}
    - {"type": "typing", "is_typing": true/false}
    - {"type": "ping"}

    Message Types (Server -> Client):
    - {"type": "message", "id": "...", "role": "...", "content": "...", "agent": "..."}
    - {"type": "stream", "id": "...", "chunk": "...", "agent": "..."}
    - {"type": "stream_end", "id": "...", "full_content": "...", "timestamp": "..."}
    - {"type": "typing", "user_id": "...", "is_typing": true/false}
    - {"type": "error", "message": "..."}
    - {"type": "pong"}
    """
    connection_id = await manager.connect(websocket, conversation_id)

    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connected",
            "connection_id": connection_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
        }, websocket)

        while True:
            try:
                data = await websocket.receive_json()
                websocket_messages_total.labels(direction="inbound").inc()

                msg_type = data.get("type", "message")

                if msg_type == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)

                elif msg_type == "typing":
                    # Broadcast typing indicator to other users
                    await manager.broadcast_to_conversation({
                        "type": "typing",
                        "is_typing": data.get("is_typing", True),
                        "timestamp": datetime.utcnow().isoformat(),
                    }, conversation_id, exclude_connection=connection_id)

                elif msg_type == "message":
                    content = data.get("content", "")
                    agent = data.get("agent")

                    if not content.strip():
                        await manager.send_personal_message({
                            "type": "error",
                            "message": "Empty message content",
                        }, websocket)
                        continue

                    # Echo user message to other participants
                    message_id = str(uuid4())
                    await manager.broadcast_to_conversation({
                        "type": "message",
                        "id": message_id,
                        "role": "user",
                        "content": content,
                        "timestamp": datetime.utcnow().isoformat(),
                    }, conversation_id)

                    # Generate and stream response
                    response_id = str(uuid4())
                    await manager.stream_response(
                        websocket,
                        response_id,
                        mock_agent_response(content),
                        agent=agent or "kosmos"
                    )

                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown message type: {msg_type}",
                    }, websocket)

            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format",
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(connection_id, conversation_id)
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
        manager.disconnect(connection_id, conversation_id)


@router.get("/connections")
async def get_connection_stats():
    """Get WebSocket connection statistics."""
    return {
        "active_conversations": len(manager.active_connections),
        "total_connections": sum(
            len(conns) for conns in manager.active_connections.values()
        ),
        "conversations": {
            conv_id: len(conns)
            for conv_id, conns in manager.active_connections.items()
        },
    }

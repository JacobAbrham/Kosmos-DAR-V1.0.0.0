# ADR-014: Agent Communication Protocol

**Status:** Accepted  
**Date:** 2025-12-13  
**Decision Makers:** Architecture Team, AI Engineering Team  

---

## Context

KOSMOS's 11 specialized agents need to communicate efficiently for coordinated task execution. The communication protocol affects system performance, debuggability, and the ability to add new agents.

### Requirements

1. **Low Latency:** Agent-to-agent communication &lt;10ms
2. **Reliable Delivery:** Messages must not be lost
3. **Observability:** All communications traceable
4. **Extensibility:** Easy to add new agents
5. **State Consistency:** Shared state across agent interactions

### Options Considered

#### Option A: Direct HTTP/gRPC Calls

Agents call each other directly via synchronous APIs.

**Pros:**
- Simple implementation
- Strong typing with gRPC
- Familiar patterns

**Cons:**
- Tight coupling between agents
- Complex service mesh for routing
- Cascade failures on agent unavailability
- Difficult to add new agents without code changes

#### Option B: Message Queue (Kafka/RabbitMQ)

Full async messaging with dedicated queues per agent.

**Pros:**
- Decoupled architecture
- Message persistence
- Replay capability

**Cons:**
- Eventual consistency challenges
- Complex for request-response patterns
- Operational overhead
- Latency for real-time interactions

#### Option C: LangGraph State + NATS Messaging (Selected)

Combine LangGraph shared state for synchronous workflows with NATS for async events.

**Pros:**
- LangGraph handles workflow state naturally
- NATS provides lightweight pub/sub
- Clean separation of sync vs async
- Built-in checkpointing

**Cons:**
- Two systems to maintain
- Learning curve for LangGraph
- State size limits

---

## Decision

We implement **LangGraph State + NATS Messaging** with clear patterns for each communication type.

### 1. Synchronous Communication via LangGraph State

For request-response patterns within a single workflow:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from operator import add

class KOSMOSState(TypedDict):
    # User input
    user_message: str
    tenant_id: str
    user_id: str
    
    # Routing
    target_agent: str
    
    # Agent outputs (accumulated)
    agent_responses: Annotated[list[dict], add]
    
    # Context from agents
    retrieved_context: list[dict]
    tool_results: list[dict]
    
    # Final response
    final_response: str
    
    # Metadata
    trace_id: str
    timestamps: dict

def create_workflow() -> StateGraph:
    workflow = StateGraph(KOSMOSState)
    
    # Add agent nodes
    workflow.add_node("zeus", zeus_agent)
    workflow.add_node("athena", athena_agent)
    workflow.add_node("hermes", hermes_agent)
    workflow.add_node("chronos", chronos_agent)
    workflow.add_node("hephaestus", hephaestus_agent)
    
    # Zeus routes to appropriate agent
    workflow.add_conditional_edges(
        "zeus",
        route_to_agent,
        {
            "athena": "athena",
            "hermes": "hermes",
            "chronos": "chronos",
            "hephaestus": "hephaestus",
            "respond": END,
        }
    )
    
    # Agents can request other agents
    workflow.add_conditional_edges(
        "athena",
        needs_collaboration,
        {"zeus": "zeus", "respond": END}
    )
    
    workflow.set_entry_point("zeus")
    return workflow.compile(checkpointer=PostgresCheckpointer())
```

### 2. Asynchronous Events via NATS

For fire-and-forget notifications and background tasks:

```python
import nats
from nats.js import JetStream

class AgentEventBus:
    """NATS-based event bus for async agent communication"""
    
    SUBJECTS = {
        "agent.started": "Agent started processing",
        "agent.completed": "Agent completed task",
        "agent.error": "Agent encountered error",
        "tool.executed": "Tool execution completed",
        "context.updated": "Knowledge context updated",
    }
    
    async def connect(self):
        self.nc = await nats.connect("nats://localhost:4222")
        self.js = self.nc.jetstream()
        
        # Create stream for durability
        await self.js.add_stream(
            name="KOSMOS_EVENTS",
            subjects=["agent.*", "tool.*", "context.*"],
            retention="limits",
            max_msgs=1_000_000,
        )
    
    async def publish(self, subject: str, data: dict):
        """Publish event to NATS"""
        await self.js.publish(
            subject,
            json.dumps({
                **data,
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": get_current_trace_id(),
            }).encode()
        )
    
    async def subscribe(self, subject: str, handler: Callable):
        """Subscribe to events with durable consumer"""
        await self.js.subscribe(
            subject,
            cb=handler,
            durable="kosmos-agent-events",
            deliver_policy="all",
        )
```

### 3. Agent Message Schema

Standardized message format for all agent communications:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class AgentMessage(BaseModel):
    """Standard message format for agent communication"""
    
    # Identification
    message_id: str
    trace_id: str
    parent_message_id: Optional[str] = None
    
    # Routing
    source_agent: str
    target_agent: str
    
    # Content
    action: str  # e.g., "search", "send_email", "schedule"
    payload: dict[str, Any]
    
    # Context
    tenant_id: str
    user_id: str
    conversation_id: str
    
    # Metadata
    timestamp: datetime
    priority: int = 5  # 1-10, higher = more urgent
    ttl_seconds: int = 300
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_abc123",
                "trace_id": "trace_xyz789",
                "source_agent": "zeus",
                "target_agent": "athena",
                "action": "search",
                "payload": {"query": "quarterly report", "top_k": 5},
                "tenant_id": "tenant_acme",
                "user_id": "user_alice",
                "conversation_id": "conv_123",
                "timestamp": "2025-12-13T10:00:00Z",
            }
        }
```

### 4. Communication Patterns

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Agent Communication Patterns                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   SYNCHRONOUS (LangGraph State)                                      │
│   ─────────────────────────────                                      │
│   User → Zeus → Athena → Zeus → Response                             │
│          ↓       ↓       ↓                                           │
│        State   State   State                                         │
│                                                                      │
│   • Request-response within workflow                                 │
│   • State shared via LangGraph                                       │
│   • Checkpointed for resume                                          │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ASYNCHRONOUS (NATS Events)                                         │
│   ───────────────────────────                                        │
│   Agent ──publish──→ NATS ──subscribe──→ Listeners                   │
│                        │                                             │
│                   JetStream                                          │
│                  (durable)                                           │
│                                                                      │
│   • Fire-and-forget notifications                                    │
│   • Background task triggers                                         │
│   • System events (metrics, logs)                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Consequences

### Positive

- Clean separation of sync/async patterns
- LangGraph provides built-in checkpointing
- NATS scales horizontally
- Easy to trace request flow
- Agents remain loosely coupled

### Negative

- Two systems to maintain
- State size limits in LangGraph
- NATS requires operational expertise
- Debugging distributed workflows

### Mitigations

1. **State size:** Compress large payloads, reference external storage
2. **Debugging:** Comprehensive tracing via OpenTelemetry
3. **Complexity:** Clear documentation and patterns

---

## Observability

All agent communications are traced:

```python
from opentelemetry import trace

tracer = trace.get_tracer("kosmos.agents")

@tracer.start_as_current_span("agent.process")
async def process_message(message: AgentMessage):
    span = trace.get_current_span()
    span.set_attribute("agent.source", message.source_agent)
    span.set_attribute("agent.target", message.target_agent)
    span.set_attribute("agent.action", message.action)
    span.set_attribute("tenant.id", message.tenant_id)
    
    # Process message...
```

---

## Related

- [Inter-Agent Communication](../agents/inter-agent-communication)
- [Tracing Documentation](../../04-operations/observability/tracing)
- [ADR-009: LangGraph Selection](ADR-009-langgraph-selection)

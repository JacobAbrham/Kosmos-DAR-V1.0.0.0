# ADR-009: LangGraph Selection for Agent Orchestration

**Status:** Accepted  
**Date:** 2025-09-15  
**Deciders:** Chief Architect, Engineering Lead  
**Technical Area:** Agent Orchestration

---

## Context

KOSMOS requires a framework for orchestrating multiple AI agents that can:

- Manage complex, multi-step workflows
- Maintain state across conversation turns
- Support human-in-the-loop interactions
- Enable agent-to-agent communication
- Provide checkpointing and recovery

We evaluated several multi-agent orchestration frameworks:

1. **LangGraph** (LangChain ecosystem)
2. **AutoGen** (Microsoft)
3. **CrewAI**
4. **Custom implementation**

---

## Decision

We will use **LangGraph** as the agent orchestration framework for KOSMOS.

---

## Rationale

### LangGraph Advantages

| Factor | LangGraph | AutoGen | CrewAI | Custom |
|--------|-----------|---------|--------|--------|
| State Management | Excellent - built-in | Manual | Limited | Manual |
| Checkpointing | Native PostgreSQL | None | None | Manual |
| Graph Visualization | Built-in | None | None | Manual |
| Human-in-the-loop | Native support | Manual | Manual | Manual |
| Production Readiness | High | Medium | Low | Varies |
| Community/Support | Strong | Growing | Small | None |
| Learning Curve | Moderate | Steep | Easy | High |

### Key Selection Factors

1. **Native Checkpointing** - LangGraph's PostgreSQL checkpointer enables state recovery without custom implementation.

2. **Graph-based Workflows** - The graph abstraction matches KOSMOS's multi-agent coordination model naturally.

3. **LangChain Ecosystem** - Integration with existing LangChain tooling (LCEL, callbacks, tracing).

4. **Production Features** - Built-in streaming, async support, and observability hooks.

### Rejected Alternatives

**AutoGen**: More complex setup, lacks native checkpointing, Microsoft ecosystem lock-in concerns.

**CrewAI**: Too focused on crew/role metaphor, limited state management, less mature.

**Custom**: High development cost, maintenance burden, delayed time-to-market.

---

## Consequences

### Positive

- Reduced development time for agent orchestration
- Native state persistence and recovery
- Strong integration with LangChain ecosystem
- Active community and documentation
- Built-in support for complex workflows

### Negative

- LangChain ecosystem dependency
- Learning curve for team members
- Framework upgrade management
- Some patterns require workarounds

### Risks

| Risk | Mitigation |
|------|------------|
| Framework breaking changes | Pin versions, maintain abstraction layer |
| Performance bottlenecks | Profile critical paths, optimize hot spots |
| Ecosystem lock-in | Abstract core interfaces, document alternatives |

---

## Implementation Notes

### State Graph Pattern

```python
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    messages: list
    context: dict
    current_agent: str

graph = StateGraph(AgentState)
graph.add_node("zeus", zeus_node)
graph.add_node("athena", athena_node)
# ... additional nodes
```

### Checkpointing Configuration

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)
compiled_graph = graph.compile(checkpointer=checkpointer)
```

---

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)

---

**Last Updated:** 2025-12-12

# ADR-018: Memory Architecture

## Status

**Accepted** — December 2025

## Context

KOSMOS requires a sophisticated memory system to support:

1. **Short-term context** — Conversation state within agent sessions
2. **Long-term memory** — Persistent knowledge across sessions
3. **Semantic search** — Vector-based retrieval of relevant information
4. **Cross-agent memory** — Shared context between agents
5. **Personal memory** — User-specific preferences and history

Traditional approaches (simple databases, file storage) fail to address:
- Semantic similarity search at scale
- Temporal decay of relevance
- Privacy-aware memory isolation
- Efficient retrieval for LLM context windows

## Decision

Implement a **hybrid memory architecture** with:

### 1. PostgreSQL + pgvector for Vector Storage

```sql
-- Memory embeddings table
CREATE TABLE memory_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    agent_id VARCHAR(50),
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI ada-002 compatible
    memory_type VARCHAR(50) NOT NULL,  -- 'episodic', 'semantic', 'procedural'
    importance_score FLOAT DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    accessed_at TIMESTAMPTZ DEFAULT NOW(),
    decay_rate FLOAT DEFAULT 0.01,
    metadata JSONB DEFAULT '{}'
);

-- HNSW index for fast similarity search
CREATE INDEX ON memory_embeddings 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

### 2. Memory Types

| Type | Purpose | Retention | Example |
|------|---------|-----------|---------|
| **Episodic** | Event memories | 90 days decay | "User scheduled meeting on Dec 14" |
| **Semantic** | Facts and knowledge | Permanent | "User prefers dark mode" |
| **Procedural** | How-to knowledge | Permanent | "User's email signature format" |
| **Working** | Active session context | Session only | Current task state |

### 3. MEMORIX Agent Ownership

The MEMORIX agent manages all memory operations:

```python
class MemoryManager:
    async def store(
        self,
        content: str,
        memory_type: MemoryType,
        importance: float = 0.5,
        metadata: dict = None
    ) -> UUID:
        embedding = await self.embed(content)
        return await self.db.insert_memory(
            content=content,
            embedding=embedding,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata
        )
    
    async def recall(
        self,
        query: str,
        limit: int = 10,
        memory_types: list[MemoryType] = None,
        min_relevance: float = 0.7
    ) -> list[Memory]:
        query_embedding = await self.embed(query)
        return await self.db.similarity_search(
            embedding=query_embedding,
            limit=limit,
            filters={
                "memory_types": memory_types,
                "min_similarity": min_relevance
            }
        )
```

### 4. Memory Decay Algorithm

Memories decay over time based on:
- Initial importance score
- Access frequency
- Time since last access

```python
def calculate_relevance(memory: Memory) -> float:
    age_days = (now() - memory.created_at).days
    access_recency = (now() - memory.accessed_at).days
    
    time_decay = exp(-memory.decay_rate * age_days)
    recency_boost = 1 / (1 + access_recency * 0.1)
    
    return memory.importance_score * time_decay * recency_boost
```

### 5. Privacy Isolation

```yaml
memory_isolation:
  user_level:
    strict: true
    cross_user_access: never
  
  agent_level:
    shared_pool: true
    agent_specific: optional
  
  privacy_zones:
    SENSITIVE: encrypted_at_rest
    PERSONAL: user_key_encrypted
    PROFESSIONAL: org_key_encrypted
```

## Consequences

### Positive

- **Semantic search** enables relevant memory retrieval without exact matching
- **pgvector** provides native PostgreSQL integration without additional infrastructure
- **Memory decay** prevents context pollution with stale information
- **Type classification** allows targeted memory queries
- **MEMORIX ownership** centralizes memory operations for consistency

### Negative

- **Embedding costs** — Each memory store requires embedding API call
- **Index maintenance** — HNSW indexes require periodic rebuilding
- **Storage growth** — Vector embeddings are space-intensive (~6KB per memory)
- **Complexity** — Multi-type memory system requires careful management

### Mitigations

| Concern | Mitigation |
|---------|------------|
| Embedding costs | Local embedding model (e5-small) for non-critical memories |
| Index maintenance | Scheduled nightly reindex during low-usage |
| Storage growth | Aggressive decay for low-importance episodic memories |
| Complexity | MEMORIX agent abstracts complexity from other agents |

## Alternatives Considered

### 1. Dedicated Vector Database (Pinecone, Weaviate)

**Rejected because:**
- Additional infrastructure to manage
- Network latency for queries
- Cost at scale
- pgvector is sufficient for KOSMOS scale (millions of memories)

### 2. Redis with Vector Search

**Rejected because:**
- In-memory storage limits scale
- Durability concerns
- Less mature vector implementation

### 3. Simple Key-Value Storage

**Rejected because:**
- No semantic search capability
- Requires exact key matching
- Poor retrieval for natural language queries

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [MEMORIX Agent Specification](../agents/memorix-memory.md)
- [Memory in LLM Applications](https://langchain.com/docs/modules/memory)

---

**Authors:** Architecture Team  
**Reviewers:** MEMORIX Agent Lead, Security Team  
**Last Updated:** December 2025

# Athena Knowledge Agent

**Domain:** Knowledge Management, RAG & Information Retrieval  
**Greek Deity:** Athena - Goddess of Wisdom and Strategic Warfare  
**Status:** Active  
**Version:** 1.2.0

---

## Overview

Athena is the **knowledge and wisdom** agent of KOSMOS, responsible for Retrieval-Augmented Generation (RAG), document search, and contextual information retrieval. Named after the goddess of wisdom, Athena excels at finding, synthesizing, and presenting relevant knowledge from the organization's document corpus.

### Key Capabilities

- **Semantic Search** - Find relevant documents using vector similarity
- **RAG Pipeline** - Augment LLM responses with retrieved context
- **Document Ingestion** - Process and embed new documents
- **Knowledge Synthesis** - Combine information from multiple sources
- **Citation Generation** - Provide source references for answers
- **Context Management** - Optimize context window usage

### When to Use This Agent

| Use Case | Example |
|----------|---------|
| Knowledge questions | "What is our security policy for remote access?" |
| Document search | "Find all documents about Q3 performance" |
| Contextual answers | "Summarize our benefits package" |
| Research assistance | "What do our docs say about deployment procedures?" |

---

## Interface Specification

### Supported Actions

| Action | Description | Required Params | Returns |
|--------|-------------|-----------------|---------|
| `retrieve` | Find relevant documents | `query`, `k` | Document chunks with scores |
| `query` | RAG-enhanced question answering | `question` | Answer with citations |
| `ingest` | Add document to knowledge base | `document`, `metadata` | Ingestion confirmation |
| `search` | Keyword + semantic hybrid search | `query`, `filters` | Search results |
| `evaluate_proposal` | Pentarchy vote (compliance) | `proposal_id`, `cost`, `description` | Vote, Score, Reasoning |

---

## Architecture

### RAG Pipeline

```mermaid
graph LR
    Q[Query] --> E[Embed Query]
    E --> V[Vector Search]
    V --> R[Rerank Results]
    R --> C[Build Context]
    C --> L[LLM Generation]
    L --> A[Answer + Citations]
```

### Data Stores

| Store | Purpose | Technology |
|-------|---------|------------|
| Vector Store | Semantic embeddings | PostgreSQL + pgvector |
| Document Store | Raw documents | MinIO |
| Metadata Store | Document metadata | PostgreSQL |
| Cache | Frequent queries | Dragonfly |

---

## Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ATHENA_EMBEDDING_MODEL` | Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| `ATHENA_CHUNK_SIZE` | Document chunk size | `512` |
| `ATHENA_CHUNK_OVERLAP` | Chunk overlap | `50` |
| `ATHENA_TOP_K` | Default retrieval count | `5` |
| `ATHENA_RERANK_MODEL` | Reranking model | `cross-encoder/ms-marco-MiniLM-L-6-v2` |

### MCP Connections

| MCP Server | Purpose |
|------------|---------|
| context7 | External documentation lookup |
| memory | Conversation memory retrieval |

---

## Performance

### SLOs

| Metric | Target | Current |
|--------|--------|---------|
| Retrieval P50 | <100ms | 85ms |
| Retrieval P99 | <300ms | 240ms |
| RAG Query P50 | <1s | 850ms |
| RAG Query P99 | <3s | 2.4s |

---

## Related Documentation

- [ADR-011 RAG Architecture](../adr/ADR-011-rag-architecture.md)
- [Data Lineage - Document Pipeline](../data-lineage.md#document-pipeline)

---

**Last Updated:** 2025-12-12  
**Document Owner:** Chief Architect


## Auto-Detected Tools

| Tool Name | Status | Source |
|-----------|--------|--------|
| `evaluate_proposal` | Active | `src/agents/athena/main.py` |
| `ingest` | Active | `src/agents/athena/main.py` |
| `query` | Active | `src/agents/athena/main.py` |
| `retrieve` | Active | `src/agents/athena/main.py` |
| `search` | Active | `src/agents/athena/main.py` |

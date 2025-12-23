# KOSMOS Architecture Overview

High-level architectural overview of the KOSMOS AI-Native Enterprise Operating System.

## Table of Contents

- [System Overview](#system-overview)
- [Core Principles](#core-principles)
- [Component Architecture](#component-architecture)
- [Agent Architecture](#agent-architecture)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Deployment Architecture](#deployment-architecture)

---

## System Overview

KOSMOS is an AI-native enterprise operating system built around a multi-agent architecture. The system features 11 specialized agents coordinated through a central orchestrator (Zeus) with distributed governance (Pentarchy).

```
┌─────────────────────────────────────────────────────────────────┐
│                        KOSMOS System                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌───────────────┐     ┌──────────────┐  │
│  │   Frontend   │─────▶│  API Gateway  │────▶│  Agent Layer │  │
│  │  (Next.js)   │      │   (FastAPI)   │     │  (11 Agents) │  │
│  └──────────────┘      └───────┬───────┘     └──────┬───────┘  │
│                                 │                     │           │
│                                 ▼                     ▼           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              MCP Server Layer (88 Tools)                 │   │
│  └─────────────────┬───────────────────────────────────────┘   │
│                    │                                             │
│                    ▼                                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Infrastructure Layer (PostgreSQL, Redis, MinIO, NATS)   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. Agent-Centric Design

- **Specialization:** Each agent has a specific domain expertise
- **Autonomy:** Agents make decisions within their domain
- **Collaboration:** Agents work together through Zeus orchestration
- **Governance:** Pentarchy provides distributed decision-making for $50-$100 actions

### 2. API-First Architecture

- All functionality exposed via REST APIs
- OpenAPI/Swagger documentation
- Versioned endpoints (`/api/v1/...`)
- GraphQL support for complex queries (future)

### 3. Cloud-Native

- Containerized deployments (Docker)
- Kubernetes orchestration
- Horizontal scalability
- Infrastructure as Code (IaC)

### 4. Security by Design

- Zero-trust architecture
- JWT-based authentication
- RBAC authorization
- Encryption at rest and in transit
- Audit logging

### 5. Observability

- Structured logging (JSON)
- Distributed tracing (OpenTelemetry)
- Metrics collection (Prometheus)
- Alerting (AlertManager)

---

## Component Architecture

### Layer 1: Presentation Layer

**Frontend (Next.js 14)**

- Server-side rendering (SSR)
- TypeScript for type safety
- Tailwind CSS for styling
- Real-time updates via WebSockets
- Responsive design

**Responsibilities:**

- User interface rendering
- User input validation
- State management
- API communication

### Layer 2: API Gateway Layer

**FastAPI Application**

- REST API endpoints
- WebSocket support for real-time
- Authentication middleware
- Rate limiting
- CORS handling

**Key Routers:**

- `/api/v1/auth` - Authentication & authorization
- `/api/v1/chat` - Chat and conversations
- `/api/v1/agents` - Agent management
- `/api/v1/votes` - Pentarchy governance
- `/api/v1/mcp` - MCP server integration

### Layer 3: Agent Layer

**11 Specialized Agents:**

| Agent | Domain | Key Responsibilities |
|-------|--------|---------------------|
| **Zeus** | Orchestration | Request routing, governance, oversight |
| **Hermes** | Communications | Task routing, message delivery |
| **AEGIS** | Security | Threat detection, compliance, access control |
| **Chronos** | Scheduling | Calendar management, temporal reasoning |
| **Athena** | Knowledge | RAG, research, document processing |
| **Hephaestus** | Operations | DevOps, infrastructure, code generation |
| **Nur PROMETHEUS** | Analytics | Data analysis, financial planning |
| **Iris** | Interface | External communications, notifications |
| **MEMORIX** | Memory | Long-term memory, context management |
| **Hestia** | Personal | User preferences, wellness, media |
| **Morpheus** | Learning | Pattern recognition, optimization |

**Pentarchy Voters:** Nur PROMETHEUS, Hephaestus, Athena

### Layer 4: MCP Server Layer

**88 MCP Servers across 9 domains:**

1. **AI & ML** (7 servers)
2. **Cloud & Infrastructure** (15 servers)
3. **Databases** (12 servers)
4. **Development & DevOps** (18 servers)
5. **Enterprise & Collaboration** (10 servers)
6. **Search & Knowledge** (8 servers)
7. **Monitoring & Observability** (6 servers)
8. **Security** (8 servers)
9. **Utilities** (4 servers)

See [MCP Strategy](03-engineering/mcp-strategy.md) for details.

### Layer 5: Infrastructure Layer

**Core Services:**

- **PostgreSQL 15** - Primary database with pgvector extension
- **Redis 7** - Caching and session storage
- **MinIO** - Object storage for documents and media
- **NATS** - Message bus for agent communication
- **Ollama** (optional) - Local LLM inference

**Observability:**

- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **Loki** - Log aggregation
- **Tempo** - Distributed tracing

---

## Agent Architecture

### Agent Structure

Each agent follows a consistent structure:

```
src/agents/<agent-name>/
├── __init__.py
├── main.py              # Agent entry point
├── config.py            # Agent configuration
├── tools/               # Agent-specific tools
│   ├── __init__.py
│   └── <tool>.py
├── prompts/             # System prompts
│   └── system.txt
└── tests/               # Agent tests
    └── test_<agent>.py
```

### Agent Communication

**Message Bus (NATS):**

```python
# Agent publishes a message
await nats_client.publish(
    subject="agent.hermes.task",
    payload={
        "task_id": "123",
        "query": "Route this message",
        "priority": "high"
    }
)

# Agent subscribes to messages
@nats_client.subscribe("agent.hermes.*")
async def handle_task(msg):
    # Process task
    pass
```

**Direct API Calls:**

```python
# One agent calling another via API
response = await http_client.post(
    "http://agent-athena:8000/api/v1/query",
    json={"query": "Search for policy documents"},
    headers={"Authorization": f"Bearer {service_token}"}
)
```

### Pentarchy Governance

**Decision Flow:**

```
1. Action proposal created (amount: $50-$100)
2. Zeus initiates Pentarchy vote
3. Three agents vote:
   - Nur PROMETHEUS: Financial viability
   - Hephaestus: Technical feasibility  
   - Athena: Compliance verification
4. 2/3 majority required to approve
5. Zeus executes or rejects based on outcome
```

**Vote Structure:**

```json
{
  "proposal_id": "prop-123",
  "action": "purchase",
  "amount": 75.00,
  "description": "Buy API credits",
  "votes": {
    "nur-prometheus": {
      "vote": "APPROVE",
      "score": 2,
      "reasoning": ["ROI positive", "Within budget"]
    },
    "hephaestus": {
      "vote": "APPROVE", 
      "score": 3,
      "reasoning": ["API stable", "No technical risks"]
    },
    "athena": {
      "vote": "REJECT",
      "score": 1,
      "reasoning": ["Needs compliance review"]
    }
  },
  "decision": "APPROVED",
  "executed_at": "2025-12-23T10:30:00Z"
}
```

---

## Data Flow

### Request Flow (Chat)

```
1. User sends message via Frontend
   ↓
2. Frontend → API Gateway: POST /api/v1/chat/message
   ↓
3. API Gateway validates JWT token
   ↓
4. API Gateway → Zeus: Route query
   ↓
5. Zeus analyzes query and selects agent (e.g., Athena)
   ↓
6. Zeus → Athena: Forward query
   ↓
7. Athena performs RAG search
   ↓
8. Athena → LLM: Generate response
   ↓
9. Athena → Zeus: Return response
   ↓
10. Zeus → API Gateway: Forward response
   ↓
11. API Gateway → Frontend: JSON response
   ↓
12. Frontend displays message to user
```

### Data Storage

**PostgreSQL Database:**

```
kosmos_db
├── users                  # User accounts
├── conversations         # Chat conversations
├── messages              # Chat messages
├── agents                # Agent metadata
├── proposals             # Pentarchy proposals
├── votes                 # Pentarchy votes
├── api_keys              # API key management
├── documents             # Document metadata
└── embeddings            # Vector embeddings (pgvector)
```

**MinIO Object Storage:**

```
kosmos-bucket/
├── documents/            # Uploaded documents
├── media/                # Images, videos
├── exports/              # User data exports
└── backups/              # Database backups
```

**Redis Cache:**

```
redis:
├── sessions:<session_id>     # User sessions
├── rate_limit:<user_id>      # Rate limiting
├── cache:<key>               # Query cache
└── locks:<resource>          # Distributed locks
```

---

## Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Primary language |
| FastAPI | 0.104+ | Web framework |
| Pydantic | 2.5+ | Data validation |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | 1.13+ | Database migrations |
| LangGraph | Latest | Agent orchestration |
| LangChain | Latest | LLM integration |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14+ | React framework |
| TypeScript | 5+ | Type safety |
| Tailwind CSS | 3+ | Styling |
| React Query | Latest | Data fetching |
| Zustand | Latest | State management |

### Infrastructure

| Technology | Version | Purpose |
|------------|---------|---------|
| Docker | 24+ | Containerization |
| Kubernetes | 1.28+ | Orchestration |
| Helm | 3.12+ | Package management |
| PostgreSQL | 15+ | Database |
| Redis | 7+ | Cache |
| MinIO | Latest | Object storage |
| NATS | Latest | Message bus |

### Observability

| Technology | Version | Purpose |
|------------|---------|---------|
| Prometheus | Latest | Metrics |
| Grafana | Latest | Visualization |
| Loki | Latest | Logs |
| Tempo | Latest | Tracing |
| OpenTelemetry | Latest | Instrumentation |

---

## Deployment Architecture

### Development Environment

```
Docker Compose
├── kosmos-api           (FastAPI)
├── kosmos-frontend      (Next.js)
├── kosmos-docs          (MkDocs)
├── postgres             (PostgreSQL 15)
├── redis                (Redis 7)
├── minio                (MinIO)
└── nats                 (NATS)
```

### Production Environment (Kubernetes)

```
Kubernetes Cluster
├── kosmos-core namespace
│   ├── api-deployment (3 replicas)
│   ├── frontend-deployment (2 replicas)
│   ├── agent-deployments (11 agents)
│   ├── postgres-statefulset (3 replicas)
│   ├── redis-deployment
│   ├── minio-deployment
│   └── nats-deployment
├── kosmos-monitoring namespace
│   ├── prometheus
│   ├── grafana
│   ├── loki
│   └── tempo
└── kosmos-ingress namespace
    ├── ingress-nginx
    └── cert-manager
```

### Scaling Strategy

**Horizontal Scaling:**

- API Gateway: 3-10 replicas (auto-scaling)
- Agents: 1-3 replicas per agent
- Database: Read replicas for query load

**Vertical Scaling:**

- Agent pods: 2-4 CPU, 4-8GB RAM
- Database: 8-16 CPU, 32-64GB RAM
- Redis: 2-4 CPU, 8-16GB RAM

**Resource Targets:**

- **Development:** 8GB RAM, 4 cores
- **Staging:** 32GB RAM, 8 cores
- **Production:** 128GB+ RAM, 32+ cores

---

## Related Documentation

- **Detailed Architecture:** [docs/02-architecture](02-architecture/)
- **ADRs:** [docs/02-architecture/adr](02-architecture/adr/)
- **Agent Specs:** [docs/02-architecture/agents](02-architecture/agents/)
- **API Design:** [docs/03-engineering/api-design.md](03-engineering/api-design.md)
- **Security Architecture:** [docs/security/architecture.md](security/architecture.md)
- **Deployment Guide:** [docs/deployment/DEPLOYMENT_SUMMARY.md](deployment/DEPLOYMENT_SUMMARY.md)

---

**Last Updated:** December 2025  
**Version:** 1.0.0

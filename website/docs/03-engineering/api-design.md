# API Design Standards

**RESTful API Design for KOSMOS Services**

:::info Design Philosophy
    All KOSMOS APIs follow REST principles with OpenAPI 3.1 documentation, consistent error handling, and versioned endpoints.

---

## API Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY                            │
│                    (Kong / Traefik)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  /api/v1/zeus/*      → Zeus Orchestrator API               │
│  /api/v1/agents/*    → Agent Management API                │
│  /api/v1/mcp/*       → MCP Server Proxy                    │
│  /api/v1/auth/*      → Zitadel Auth Proxy                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## URL Structure

### Base URL Pattern
```
https://api.kosmos.nuvanta.local/api/v1/{service}/{resource}
```

### Resource Naming

| Pattern | Example | Description |
|---------|---------|-------------|
| Collection | `/agents` | List all agents |
| Resource | `/agents/zeus` | Single agent |
| Sub-resource | `/agents/zeus/tasks` | Agent's tasks |
| Action | `/agents/zeus/invoke` | RPC-style action |

---

## HTTP Methods

| Method | Usage | Idempotent |
|--------|-------|------------|
| `GET` | Retrieve resource(s) | ✅ Yes |
| `POST` | Create resource / RPC action | ❌ No |
| `PUT` | Full resource replacement | ✅ Yes |
| `PATCH` | Partial update | ❌ No |
| `DELETE` | Remove resource | ✅ Yes |

---

## Request Format

### Headers

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer {jwt_token}
X-Request-ID: {uuid}
X-Correlation-ID: {uuid}
```

### Request Body (POST/PUT/PATCH)

```json
{
  "data": {
    "type": "task",
    "attributes": {
      "description": "Schedule meeting",
      "priority": "high"
    }
  }
}
```

---

## Response Format

### Success Response

```json
{
  "data": {
    "id": "task_abc123",
    "type": "task",
    "attributes": {
      "description": "Schedule meeting",
      "status": "pending"
    },
    "links": {
      "self": "/api/v1/tasks/task_abc123"
    }
  },
  "meta": {
    "request_id": "req_xyz789",
    "timestamp": "2025-12-14T10:30:00Z"
  }
}
```

### Error Response

```json
{
  "errors": [
    {
      "status": "400",
      "code": "VALIDATION_ERROR",
      "title": "Invalid Request",
      "detail": "Field 'priority' must be one of: low, medium, high",
      "source": {
        "pointer": "/data/attributes/priority"
      }
    }
  ],
  "meta": {
    "request_id": "req_xyz789"
  }
}
```

---

## Status Codes

### Success Codes

| Code | Usage |
|------|-------|
| `200 OK` | Successful GET, PUT, PATCH |
| `201 Created` | Successful POST (resource created) |
| `202 Accepted` | Async operation accepted |
| `204 No Content` | Successful DELETE |

### Client Error Codes

| Code | Usage |
|------|-------|
| `400 Bad Request` | Malformed request / validation error |
| `401 Unauthorized` | Missing or invalid auth token |
| `403 Forbidden` | Valid auth, insufficient permissions |
| `404 Not Found` | Resource doesn't exist |
| `409 Conflict` | Resource state conflict |
| `422 Unprocessable` | Semantic validation error |
| `429 Too Many Requests` | Rate limit exceeded |

### Server Error Codes

| Code | Usage |
|------|-------|
| `500 Internal Server Error` | Unexpected server error |
| `502 Bad Gateway` | Upstream service failure |
| `503 Service Unavailable` | Temporary overload |
| `504 Gateway Timeout` | Upstream timeout |

---

## Pagination

### Request

```http
GET /api/v1/tasks?page[number]=2&page[size]=25
```

### Response

```json
{
  "data": [...],
  "meta": {
    "pagination": {
      "current_page": 2,
      "per_page": 25,
      "total_pages": 10,
      "total_count": 243
    }
  },
  "links": {
    "self": "/api/v1/tasks?page[number]=2&page[size]=25",
    "first": "/api/v1/tasks?page[number]=1&page[size]=25",
    "prev": "/api/v1/tasks?page[number]=1&page[size]=25",
    "next": "/api/v1/tasks?page[number]=3&page[size]=25",
    "last": "/api/v1/tasks?page[number]=10&page[size]=25"
  }
}
```

---

## Filtering & Sorting

### Filtering

```http
GET /api/v1/tasks?filter[status]=pending&filter[agent]=chronos
```

### Sorting

```http
GET /api/v1/tasks?sort=-created_at,priority
```

Prefix with `-` for descending order.

---

## Versioning Strategy

| Version | Status | Sunset |
|---------|--------|--------|
| `v1` | Current | - |
| `v0` | Deprecated | 2025-06-01 |

### Version Header (Alternative)

```http
Accept: application/vnd.kosmos.v1+json
```

---

## Rate Limiting

### Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1702560000
```

### Limits

| Tier | Requests/Hour | Burst |
|------|--------------|-------|
| Agent | 10,000 | 100/s |
| User | 1,000 | 10/s |
| Anonymous | 100 | 1/s |

---

## Authentication

All API requests require JWT bearer token from Zitadel:

```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

See [Zitadel Identity](../security/zitadel-identity) for token acquisition.

---

## OpenAPI Specification

Auto-generated OpenAPI 3.1 spec available at:

```
GET /api/v1/openapi.json
GET /api/v1/docs        # Swagger UI
GET /api/v1/redoc       # ReDoc
```

---

## See Also

- [ADR-008 API Versioning Strategy](../02-architecture/adr/ADR-008-api-versioning-strategy)
- [Testing Strategy](testing-strategy)
- [MCP Strategy](mcp-strategy)

---

**Last Updated:** December 2025

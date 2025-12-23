# API Reference

**KOSMOS REST API Documentation**

---

## Overview

The KOSMOS API provides RESTful endpoints for accessing AI services. All endpoints require authentication and return JSON responses.

## Base URL

| Environment | Base URL |
|-------------|----------|
| Production | `https://api.kosmos.nuvanta.com/v1` |
| Staging | `https://api-staging.kosmos.nuvanta.com/v1` |

---

## Authentication

All requests require an API key in the `Authorization` header:

```bash
Authorization: Bearer your-api-key
```

### Obtaining API Keys

1. Log in to the [KOSMOS Developer Portal](https://portal.kosmos.nuvanta.com)
2. Navigate to **Settings > API Keys**
3. Generate a new key with appropriate scopes

### Key Scopes

| Scope | Description |
|-------|-------------|
| `models:read` | Read model information |
| `models:invoke` | Invoke model endpoints |
| `usage:read` | View usage statistics |
| `admin` | Full administrative access |

---

## Rate Limits

| Tier | Requests/min | Tokens/day |
|------|-------------|------------|
| Free | 60 | 100,000 |
| Standard | 300 | 1,000,000 |
| Enterprise | Custom | Custom |

Rate limit headers are included in every response:

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 299
X-RateLimit-Reset: 1704067200
```

---

## Endpoints

### Models

#### List Available Models

```http
GET /models
```

**Response:**

```json
{
  "models": [
    {
      "id": "MC-001",
      "name": "Document Summarizer",
      "version": "2.1.0",
      "status": "production"
    }
  ]
}
```

#### Get Model Details

```http
GET /models/{model_id}
```

#### Invoke Model

```http
POST /models/{model_id}/invoke
```

**Request Body:**

```json
{
  "input": {
    "content": "Your input text..."
  },
  "parameters": {
    "max_length": 500,
    "temperature": 0.7
  }
}
```

**Response:**

```json
{
  "output": {
    "result": "Processed output..."
  },
  "usage": {
    "input_tokens": 150,
    "output_tokens": 75,
    "total_tokens": 225
  },
  "metadata": {
    "request_id": "req_abc123",
    "latency_ms": 342,
    "model_version": "2.1.0"
  }
}
```

---

### Summarization (MC-001)

```http
POST /models/MC-001/invoke
```

**Request:**

```json
{
  "input": {
    "content": "Long document text to summarize...",
    "format": "text"
  },
  "parameters": {
    "max_length": 500,
    "style": "executive",
    "preserve_key_points": true
  }
}
```

---

### Sentiment Analysis (MC-002)

```http
POST /models/MC-002/invoke
```

**Request:**

```json
{
  "input": {
    "text": "Customer feedback text...",
    "language": "en"
  },
  "parameters": {
    "include_confidence": true,
    "include_aspects": true
  }
}
```

**Response:**

```json
{
  "output": {
    "sentiment": "positive",
    "confidence": 0.92,
    "aspects": [
      {"aspect": "service", "sentiment": "positive"},
      {"aspect": "price", "sentiment": "neutral"}
    ]
  }
}
```

---

### Code Review (MC-003)

```http
POST /models/MC-003/invoke
```

**Request:**

```json
{
  "input": {
    "code": "def example(): pass",
    "language": "python",
    "context": "Production API endpoint"
  },
  "parameters": {
    "check_security": true,
    "check_style": true,
    "check_performance": true
  }
}
```

---

### Usage Statistics

```http
GET /usage?start_date=2025-01-01&end_date=2025-01-31
```

**Response:**

```json
{
  "summary": {
    "total_requests": 15420,
    "total_tokens": 4521000,
    "estimated_cost": 125.50
  },
  "by_model": [
    {
      "model_id": "MC-001",
      "requests": 8500,
      "tokens": 2800000
    }
  ]
}
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please retry after 60 seconds.",
    "details": {
      "retry_after": 60
    }
  },
  "request_id": "req_abc123"
}
```

### Error Codes

| HTTP Status | Code | Description |
|------------|------|-------------|
| 400 | `INVALID_REQUEST` | Malformed request body |
| 401 | `UNAUTHORIZED` | Invalid or missing API key |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |
| 503 | `SERVICE_UNAVAILABLE` | Temporary outage |

---

## SDKs

- [Python SDK](../python-sdk) - Official Python client
- JavaScript SDK - Coming soon
- Go SDK - Coming soon

---

## OpenAPI Specification

The full OpenAPI 3.0 specification is available at:

```
https://api.kosmos.nuvanta.com/v1/openapi.json
```

---

**Last Updated:** 2025-12-12
**API Version:** v1
**Status:** Production

# Python SDK

**KOSMOS Python SDK - Programmatic Access to AI Services**

---

## Overview

The KOSMOS Python SDK provides a simple, type-safe interface for integrating KOSMOS AI services into your Python applications.

## Installation

```bash
pip install kosmos-sdk
```

Or with optional dependencies:

```bash
# With async support
pip install kosmos-sdk[async]

# With all extras
pip install kosmos-sdk[all]
```

### Requirements

- Python 3.9+
- Valid KOSMOS API credentials

---

## Quick Start

### Basic Usage

```python
from kosmos import KosmosClient

# Initialize client
client = KosmosClient(
    api_key="your-api-key",
    environment="production"  # or "staging"
)

# Call document summarizer
result = client.models.summarize(
    model_id="MC-001",
    content="Your document text here...",
    max_length=500
)

print(result.summary)
```

### Async Usage

```python
import asyncio
from kosmos import AsyncKosmosClient

async def main():
    client = AsyncKosmosClient(api_key="your-api-key")

    result = await client.models.summarize(
        model_id="MC-001",
        content="Your document text here..."
    )

    print(result.summary)

asyncio.run(main())
```

---

## Configuration

### Environment Variables

```bash
export KOSMOS_API_KEY="your-api-key"
export KOSMOS_ENVIRONMENT="production"
export KOSMOS_TIMEOUT="30"
export KOSMOS_MAX_RETRIES="3"
```

### Client Configuration

```python
from kosmos import KosmosClient, KosmosConfig

config = KosmosConfig(
    api_key="your-api-key",
    environment="production",
    timeout=30,
    max_retries=3,
    enable_logging=True,
    log_level="INFO"
)

client = KosmosClient(config=config)
```

---

## Available Models

### Document Summarizer (MC-001)

```python
result = client.models.summarize(
    model_id="MC-001",
    content="Long document text...",
    max_length=500,
    style="executive"  # or "technical", "bullet_points"
)
```

### Sentiment Analyzer (MC-002)

```python
result = client.models.analyze_sentiment(
    model_id="MC-002",
    text="Customer feedback text...",
    include_confidence=True
)

print(f"Sentiment: {result.sentiment}")  # positive, negative, neutral
print(f"Confidence: {result.confidence}")
```

### Code Reviewer (MC-003)

```python
result = client.models.review_code(
    model_id="MC-003",
    code="def my_function(): ...",
    language="python",
    check_security=True,
    check_style=True
)

for issue in result.issues:
    print(f"[{issue.severity}] Line {issue.line}: {issue.message}")
```

---

## Error Handling

```python
from kosmos import KosmosClient
from kosmos.exceptions import (
    KosmosAPIError,
    RateLimitError,
    AuthenticationError,
    ValidationError
)

client = KosmosClient(api_key="your-api-key")

try:
    result = client.models.summarize(model_id="MC-001", content="...")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except KosmosAPIError as e:
    print(f"API error: {e.status_code} - {e.message}")
```

---

## Streaming Responses

For long-running operations, use streaming:

```python
# Stream summarization for large documents
for chunk in client.models.summarize_stream(
    model_id="MC-001",
    content=large_document
):
    print(chunk.text, end="", flush=True)
```

---

## Batch Processing

Process multiple items efficiently:

```python
documents = ["doc1...", "doc2...", "doc3..."]

results = client.models.summarize_batch(
    model_id="MC-001",
    items=documents,
    max_concurrency=5
)

for doc, result in zip(documents, results):
    print(f"Summary: {result.summary[:100]}...")
```

---

## Monitoring & Observability

### Request Tracing

```python
from kosmos import KosmosClient

client = KosmosClient(
    api_key="your-api-key",
    enable_tracing=True
)

result = client.models.summarize(
    model_id="MC-001",
    content="...",
    trace_id="custom-trace-id"  # Optional custom trace ID
)

print(f"Request ID: {result.request_id}")
print(f"Latency: {result.latency_ms}ms")
print(f"Tokens used: {result.usage.total_tokens}")
```

### Cost Tracking

```python
# Get usage statistics
usage = client.usage.get_summary(
    start_date="2025-01-01",
    end_date="2025-01-31"
)

print(f"Total requests: {usage.total_requests}")
print(f"Total tokens: {usage.total_tokens}")
print(f"Estimated cost: ${usage.estimated_cost:.2f}")
```

---

## Best Practices

### Connection Pooling

```python
# Reuse client instances
client = KosmosClient(api_key="your-api-key")

# Use context manager for automatic cleanup
with KosmosClient(api_key="your-api-key") as client:
    result = client.models.summarize(...)
```

### Retry Configuration

```python
from kosmos import KosmosClient, RetryConfig

retry_config = RetryConfig(
    max_retries=3,
    backoff_factor=2.0,
    retry_on_status=[429, 500, 502, 503, 504]
)

client = KosmosClient(
    api_key="your-api-key",
    retry_config=retry_config
)
```

### Rate Limiting

```python
from kosmos import KosmosClient, RateLimiter

# Client-side rate limiting
limiter = RateLimiter(requests_per_second=10)

client = KosmosClient(
    api_key="your-api-key",
    rate_limiter=limiter
)
```

---

## Type Hints

The SDK is fully typed for IDE support:

```python
from kosmos import KosmosClient
from kosmos.types import SummarizeRequest, SummarizeResponse

client: KosmosClient = KosmosClient(api_key="...")

request: SummarizeRequest = SummarizeRequest(
    model_id="MC-001",
    content="...",
    max_length=500
)

response: SummarizeResponse = client.models.summarize(**request.dict())
```

---

## Related Documentation

- [API Reference](api-reference/README) - Full API documentation
- [Model Cards](../03-engineering/model-cards/README) - Detailed model specifications
- [SLA/SLO](../04-operations/sla-slo) - Service level objectives

---

**Last Updated:** 2025-12-12
**SDK Version:** 1.0.0
**Minimum Python:** 3.9+

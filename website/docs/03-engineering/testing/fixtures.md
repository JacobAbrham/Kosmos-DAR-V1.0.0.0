# Test Fixtures & Mocking

**Document Type:** Engineering Guide  
**Owner:** Engineering Lead  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

This document provides comprehensive guidance on test fixtures, mocking strategies, and test data management for KOSMOS. Proper fixture design ensures tests are isolated, reproducible, and maintainable.

---

## Fixture Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Test Fixture Layers                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Session Fixtures (Slow)                       │   │
│   │   • Database connections  • External service clients            │   │
│   │   • Browser instances     • Container orchestration             │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Module Fixtures (Medium)                      │   │
│   │   • Shared test data        • Configuration objects              │   │
│   │   • Mock service instances  • Schema setup                       │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Function Fixtures (Fast)                      │   │
│   │   • Individual mocks        • Request/response objects           │   │
│   │   • Temporary files         • Isolated state                     │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Fixtures

### Database Fixtures

```python
# tests/fixtures/database.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from kosmos.db.models import Base

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    """Create database engine for test session."""
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:test@localhost:5432/kosmos_test",
        poolclass=NullPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    """Create isolated database session for each test."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()  # Rollback after each test

@pytest.fixture
async def seeded_db(db_session):
    """Database with seed data."""
    from tests.fixtures.seeds import seed_test_data
    await seed_test_data(db_session)
    yield db_session
```

### Authentication Fixtures

```python
# tests/fixtures/auth.py
import pytest
from datetime import datetime, timedelta
from jose import jwt
from kosmos.auth.config import AuthConfig

@pytest.fixture
def auth_config():
    """Test authentication configuration."""
    return AuthConfig(
        secret_key="test-secret-key-for-testing-only",
        algorithm="HS256",
        access_token_expire_minutes=30,
    )

@pytest.fixture
def test_user():
    """Standard test user."""
    return {
        "id": "user_test123",
        "email": "test.user@nuvanta-holding.com",
        "name": "Test User",
        "tenant_id": "tenant_test",
        "roles": ["user"],
    }

@pytest.fixture
def admin_user():
    """Admin test user."""
    return {
        "id": "user_admin123",
        "email": "admin.user@nuvanta-holding.com",
        "name": "Admin User",
        "tenant_id": "tenant_test",
        "roles": ["admin", "user"],
    }

@pytest.fixture
def auth_token(auth_config, test_user):
    """Generate valid JWT token."""
    payload = {
        "sub": test_user["id"],
        "email": test_user["email"],
        "tenant_id": test_user["tenant_id"],
        "roles": test_user["roles"],
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, auth_config.secret_key, algorithm=auth_config.algorithm)

@pytest.fixture
def auth_headers(auth_token):
    """Authorization headers for API requests."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def expired_token(auth_config, test_user):
    """Generate expired JWT token."""
    payload = {
        "sub": test_user["id"],
        "exp": datetime.utcnow() - timedelta(hours=1),
        "iat": datetime.utcnow() - timedelta(hours=2),
    }
    return jwt.encode(payload, auth_config.secret_key, algorithm=auth_config.algorithm)
```

### LLM Fixtures

```python
# tests/fixtures/llm.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from dataclasses import dataclass

@dataclass
class MockLLMResponse:
    """Mock LLM response object."""
    text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    finish_reason: str = "stop"
    model: str = "mistral-7b"

@pytest.fixture
def mock_llm_response():
    """Factory for mock LLM responses."""
    def _create(
        text: str = "This is a mock response.",
        input_tokens: int = 50,
        output_tokens: int = 25,
    ):
        return MockLLMResponse(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        )
    return _create

@pytest.fixture
def mock_llm_client(mock_llm_response):
    """Mock LLM client with configurable responses."""
    client = AsyncMock()
    client.generate = AsyncMock(return_value=mock_llm_response())
    client.embed = AsyncMock(return_value=[0.1] * 384)  # Mock embedding
    return client

@pytest.fixture
def mock_llm_streaming():
    """Mock streaming LLM responses."""
    async def stream_response():
        chunks = ["Hello", ", ", "this ", "is ", "a ", "streamed ", "response."]
        for chunk in chunks:
            yield {"text": chunk, "done": False}
        yield {"text": "", "done": True, "total_tokens": 50}
    
    client = AsyncMock()
    client.stream = stream_response
    return client

@pytest.fixture
def mock_llm_rate_limited(mock_llm_response):
    """Mock LLM client that rate limits on first call."""
    from kosmos.llm.exceptions import RateLimitError
    
    client = AsyncMock()
    client.generate = AsyncMock(side_effect=[
        RateLimitError("Rate limited", retry_after=1),
        mock_llm_response(),
    ])
    return client
```

### Agent Fixtures

```python
# tests/fixtures/agents.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_zeus():
    """Mock Zeus orchestrator agent."""
    zeus = AsyncMock()
    zeus.name = "zeus"
    zeus.process = AsyncMock(return_value={
        "response": "Orchestrated response",
        "routed_to": "athena",
        "trace_id": "trace_123",
    })
    zeus.route = AsyncMock(return_value="athena")
    return zeus

@pytest.fixture
def mock_athena():
    """Mock Athena knowledge agent."""
    athena = AsyncMock()
    athena.name = "athena"
    athena.search = AsyncMock(return_value=[
        {"id": "doc1", "text": "Relevant document", "score": 0.95},
        {"id": "doc2", "text": "Another document", "score": 0.85},
    ])
    athena.process = AsyncMock(return_value={
        "response": "Knowledge-based response",
        "sources": ["doc1", "doc2"],
    })
    return athena

@pytest.fixture
def mock_hermes():
    """Mock Hermes communications agent."""
    hermes = AsyncMock()
    hermes.name = "hermes"
    hermes.send_email = AsyncMock(return_value={"status": "sent", "message_id": "msg_123"})
    hermes.send_notification = AsyncMock(return_value={"status": "delivered"})
    return hermes

@pytest.fixture
def mock_chronos():
    """Mock Chronos scheduling agent."""
    chronos = AsyncMock()
    chronos.name = "chronos"
    chronos.schedule_meeting = AsyncMock(return_value={
        "event_id": "event_123",
        "scheduled_at": "2025-12-15T14:00:00Z",
    })
    chronos.check_availability = AsyncMock(return_value=[
        {"start": "2025-12-15T14:00:00Z", "end": "2025-12-15T15:00:00Z"},
    ])
    return chronos

@pytest.fixture
def agent_registry(mock_zeus, mock_athena, mock_hermes, mock_chronos):
    """Registry of all mock agents."""
    return {
        "zeus": mock_zeus,
        "athena": mock_athena,
        "hermes": mock_hermes,
        "chronos": mock_chronos,
    }
```

---

## Mocking Strategies

### External Service Mocks

```python
# tests/mocks/external_services.py
import pytest
from unittest.mock import AsyncMock, patch
import httpx

@pytest.fixture
def mock_httpx_client():
    """Mock httpx async client."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        yield client

@pytest.fixture
def mock_huggingface_api(mock_httpx_client):
    """Mock HuggingFace Inference API."""
    mock_httpx_client.post.return_value = httpx.Response(
        200,
        json={
            "generated_text": "Mock HuggingFace response",
            "details": {
                "tokens": 75,
                "finish_reason": "stop",
            }
        }
    )
    return mock_httpx_client

@pytest.fixture
def mock_nats_client():
    """Mock NATS messaging client."""
    client = AsyncMock()
    client.publish = AsyncMock()
    client.subscribe = AsyncMock()
    client.jetstream = MagicMock()
    client.jetstream.publish = AsyncMock()
    return client

@pytest.fixture
def mock_redis_client():
    """Mock Redis/Dragonfly client."""
    client = AsyncMock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.exists = AsyncMock(return_value=0)
    client.expire = AsyncMock(return_value=True)
    return client

@pytest.fixture
def mock_minio_client():
    """Mock MinIO storage client."""
    client = AsyncMock()
    client.put_object = AsyncMock()
    client.get_object = AsyncMock(return_value=b"mock file content")
    client.remove_object = AsyncMock()
    client.list_objects = AsyncMock(return_value=[])
    return client
```

### Context Manager Mocks

```python
# tests/mocks/context_managers.py
import pytest
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

@pytest.fixture
def mock_db_transaction():
    """Mock database transaction context manager."""
    @asynccontextmanager
    async def transaction():
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        try:
            yield mock_session
            await mock_session.commit()
        except Exception:
            await mock_session.rollback()
            raise
    
    return transaction

@pytest.fixture
def mock_distributed_lock():
    """Mock distributed lock context manager."""
    @asynccontextmanager
    async def lock(name: str, timeout: int = 30):
        # Simulate acquiring lock
        yield True
        # Simulate releasing lock
    
    return lock

@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter context manager."""
    @asynccontextmanager
    async def rate_limit(key: str, limit: int = 100, window: int = 60):
        # Check rate limit
        yield {"allowed": True, "remaining": limit - 1}
    
    return rate_limit
```

### Time-Based Mocks

```python
# tests/mocks/time.py
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from freezegun import freeze_time

@pytest.fixture
def frozen_time():
    """Freeze time at specific moment."""
    with freeze_time("2025-12-13T10:00:00Z") as frozen:
        yield frozen

@pytest.fixture
def mock_datetime():
    """Mock datetime for controlled time progression."""
    current_time = datetime(2025, 12, 13, 10, 0, 0)
    
    class MockDateTime:
        @classmethod
        def now(cls):
            return current_time
        
        @classmethod
        def utcnow(cls):
            return current_time
        
        @classmethod
        def advance(cls, **kwargs):
            nonlocal current_time
            current_time += timedelta(**kwargs)
    
    with patch("datetime.datetime", MockDateTime):
        yield MockDateTime

@pytest.fixture
def mock_sleep():
    """Mock asyncio.sleep to skip delays."""
    async def instant_sleep(seconds):
        pass  # Don't actually sleep
    
    with patch("asyncio.sleep", instant_sleep):
        yield
```

---

## Test Data Factories

### Factory Pattern Implementation

```python
# tests/factories/base.py
import factory
from faker import Faker
from uuid import uuid4

fake = Faker()

class BaseFactory(factory.Factory):
    """Base factory with common utilities."""
    
    class Meta:
        abstract = True
    
    @classmethod
    def create_batch_dict(cls, size: int, **kwargs):
        """Create batch and return as dict keyed by id."""
        items = cls.create_batch(size, **kwargs)
        return {item.id: item for item in items}
```

```python
# tests/factories/models.py
import factory
from faker import Faker
from datetime import datetime, timedelta
from tests.factories.base import BaseFactory, fake
from kosmos.models import User, Tenant, Conversation, Message, Document

class TenantFactory(BaseFactory):
    class Meta:
        model = Tenant
    
    id = factory.LazyFunction(lambda: f"tenant_{fake.uuid4()[:8]}")
    name = factory.LazyAttribute(lambda _: fake.company())
    plan = factory.Iterator(["free", "pro", "enterprise"])
    created_at = factory.LazyFunction(datetime.utcnow)

class UserFactory(BaseFactory):
    class Meta:
        model = User
    
    id = factory.LazyFunction(lambda: f"user_{fake.uuid4()[:8]}")
    email = factory.LazyAttribute(lambda _: fake.unique.email())
    name = factory.LazyAttribute(lambda _: fake.name())
    tenant = factory.SubFactory(TenantFactory)
    tenant_id = factory.LazyAttribute(lambda o: o.tenant.id)
    roles = ["user"]
    created_at = factory.LazyFunction(datetime.utcnow)

class ConversationFactory(BaseFactory):
    class Meta:
        model = Conversation
    
    id = factory.LazyFunction(lambda: f"conv_{fake.uuid4()[:8]}")
    user = factory.SubFactory(UserFactory)
    user_id = factory.LazyAttribute(lambda o: o.user.id)
    tenant_id = factory.LazyAttribute(lambda o: o.user.tenant_id)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)

class MessageFactory(BaseFactory):
    class Meta:
        model = Message
    
    id = factory.LazyFunction(lambda: f"msg_{fake.uuid4()[:8]}")
    conversation = factory.SubFactory(ConversationFactory)
    conversation_id = factory.LazyAttribute(lambda o: o.conversation.id)
    role = factory.Iterator(["user", "assistant"])
    content = factory.LazyAttribute(lambda _: fake.paragraph())
    tokens = factory.LazyAttribute(lambda _: fake.random_int(min=10, max=500))
    created_at = factory.LazyFunction(datetime.utcnow)

class DocumentFactory(BaseFactory):
    class Meta:
        model = Document
    
    id = factory.LazyFunction(lambda: f"doc_{fake.uuid4()[:8]}")
    tenant_id = factory.LazyAttribute(lambda _: TenantFactory().id)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=5))
    content = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=2000))
    source = factory.Iterator(["upload", "confluence", "sharepoint", "gdrive"])
    embedding = factory.LazyFunction(lambda: [fake.pyfloat() for _ in range(384)])
    created_at = factory.LazyFunction(datetime.utcnow)
```

### Specialized Factories

```python
# tests/factories/scenarios.py
from tests.factories.models import *

class ConversationWithHistoryFactory(ConversationFactory):
    """Conversation with pre-populated message history."""
    
    @factory.post_generation
    def messages(obj, create, extracted, **kwargs):
        if not create:
            return
        
        count = extracted or 5
        for i in range(count):
            MessageFactory(
                conversation=obj,
                role="user" if i % 2 == 0 else "assistant",
            )

class LongConversationFactory(ConversationWithHistoryFactory):
    """Conversation with many messages for pagination testing."""
    
    @factory.post_generation
    def messages(obj, create, extracted, **kwargs):
        if not create:
            return
        
        for i in range(100):
            MessageFactory(
                conversation=obj,
                role="user" if i % 2 == 0 else "assistant",
            )

class MultiTenantDataFactory:
    """Factory for creating multi-tenant test scenarios."""
    
    @staticmethod
    def create(num_tenants: int = 3, users_per_tenant: int = 5):
        tenants = TenantFactory.create_batch(num_tenants)
        
        data = {}
        for tenant in tenants:
            users = UserFactory.create_batch(
                users_per_tenant,
                tenant=tenant,
                tenant_id=tenant.id,
            )
            data[tenant.id] = {
                "tenant": tenant,
                "users": users,
                "conversations": [],
            }
            
            for user in users:
                conv = ConversationWithHistoryFactory(
                    user=user,
                    user_id=user.id,
                    tenant_id=tenant.id,
                )
                data[tenant.id]["conversations"].append(conv)
        
        return data
```

---

## Seed Data Management

### Database Seeds

```python
# tests/fixtures/seeds.py
from datetime import datetime, timedelta
from tests.factories.models import *

async def seed_test_data(session):
    """Seed database with standard test data."""
    
    # Create tenants
    tenants = {
        "acme": Tenant(
            id="tenant_acme",
            name="Acme Corporation",
            plan="enterprise",
        ),
        "startup": Tenant(
            id="tenant_startup",
            name="Cool Startup",
            plan="pro",
        ),
    }
    
    for tenant in tenants.values():
        session.add(tenant)
    
    # Create users
    users = {
        "alice": User(
            id="user_alice",
            email="alice@acme.com",
            name="Alice Smith",
            tenant_id="tenant_acme",
            roles=["admin", "user"],
        ),
        "bob": User(
            id="user_bob",
            email="bob@acme.com",
            name="Bob Jones",
            tenant_id="tenant_acme",
            roles=["user"],
        ),
        "charlie": User(
            id="user_charlie",
            email="charlie@startup.com",
            name="Charlie Brown",
            tenant_id="tenant_startup",
            roles=["admin", "user"],
        ),
    }
    
    for user in users.values():
        session.add(user)
    
    # Create sample conversations
    conversations = [
        Conversation(
            id="conv_sample1",
            user_id="user_alice",
            tenant_id="tenant_acme",
            title="Vacation Policy Question",
            created_at=datetime.utcnow() - timedelta(days=1),
        ),
        Conversation(
            id="conv_sample2",
            user_id="user_bob",
            tenant_id="tenant_acme",
            title="Q3 Report Analysis",
            created_at=datetime.utcnow() - timedelta(hours=2),
        ),
    ]
    
    for conv in conversations:
        session.add(conv)
    
    # Create sample messages
    messages = [
        Message(
            id="msg_1",
            conversation_id="conv_sample1",
            role="user",
            content="What is our vacation policy?",
            tokens=10,
        ),
        Message(
            id="msg_2",
            conversation_id="conv_sample1",
            role="assistant",
            content="Our vacation policy allows for 20 days of PTO per year...",
            tokens=150,
        ),
    ]
    
    for msg in messages:
        session.add(msg)
    
    await session.commit()
    
    return {
        "tenants": tenants,
        "users": users,
        "conversations": conversations,
        "messages": messages,
    }

async def seed_documents(session, tenant_id: str = "tenant_acme"):
    """Seed knowledge base documents."""
    documents = [
        Document(
            id="doc_policy1",
            tenant_id=tenant_id,
            title="Employee Handbook - Vacation Policy",
            content="All employees are entitled to 20 days of paid time off...",
            source="upload",
            embedding=[0.1] * 384,
        ),
        Document(
            id="doc_policy2",
            tenant_id=tenant_id,
            title="Remote Work Guidelines",
            content="Employees may work remotely up to 3 days per week...",
            source="confluence",
            embedding=[0.2] * 384,
        ),
        Document(
            id="doc_q3report",
            tenant_id=tenant_id,
            title="Q3 2025 Financial Report",
            content="Revenue increased by 25% compared to Q2...",
            source="sharepoint",
            embedding=[0.3] * 384,
        ),
    ]
    
    for doc in documents:
        session.add(doc)
    
    await session.commit()
    return documents
```

---

## Fixture Best Practices

### Do's

- **Use appropriate scope**: Session for expensive setup, function for isolation
- **Keep fixtures focused**: One responsibility per fixture
- **Use factories for data**: Avoid hardcoded test data
- **Clean up resources**: Always implement teardown
- **Document fixtures**: Explain purpose and usage

### Don'ts

- **Don't share mutable state**: Use fresh fixtures per test
- **Don't over-mock**: Test real behavior when possible
- **Don't couple fixtures**: Keep fixtures independent
- **Don't skip cleanup**: Prevent test pollution

---

## Related Documentation

- [Testing Strategy](README)
- [CI/CD Pipeline](../../04-operations/infrastructure/deployment)

---

**Document Owner:** engineering@nuvanta-holding.com

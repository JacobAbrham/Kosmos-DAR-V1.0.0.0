# LLM Testing Strategies

**Document Type:** Engineering Standards  
**Owner:** MLOps Team  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

Testing LLM-powered systems presents unique challenges due to non-deterministic outputs, high latency, and cost. This document covers strategies for effectively testing KOSMOS agent behaviors.

---

## Testing Challenges

| Challenge | Impact | Mitigation |
|-----------|--------|------------|
| **Non-determinism** | Same input produces different outputs | Semantic similarity checks, ranges |
| **High latency** | Slow test execution | Mocking, caching, parallel execution |
| **Cost** | API calls cost money | Mock by default, selective live tests |
| **Prompt sensitivity** | Minor changes cause major shifts | Regression testing, golden datasets |
| **Context dependence** | Behavior varies with context | Controlled test scenarios |

---

## Testing Pyramid for LLM Systems

```
                    ┌─────────────────────┐
                    │   Live LLM Tests    │  ← 5% (Expensive, Slow)
                    │   (Real API Calls)  │
                ┌───┴─────────────────────┴───┐
                │   Evaluation Tests          │  ← 15% (Golden Datasets)
                │   (Semantic Similarity)     │
            ┌───┴─────────────────────────────┴───┐
            │      Behavioral Tests               │  ← 30% (Mock LLM)
            │    (Intent Classification)          │
        ┌───┴─────────────────────────────────────┴───┐
        │           Unit Tests (No LLM)               │  ← 50% (Fast)
        │   (Prompt Construction, Parsing, Routing)   │
        └─────────────────────────────────────────────┘
```

---

## Mock Strategies

### Deterministic Mock Responses

```python
# mocks/llm_mock.py
from typing import Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock
import re

class DeterministicLLMMock:
    """Mock LLM with deterministic responses based on patterns."""
    
    def __init__(self):
        self.response_patterns: List[Dict] = []
        self.default_response = "I don't understand the request."
        self.call_history: List[Dict] = []
    
    def add_pattern(
        self,
        pattern: str,
        response: str,
        tokens: Dict[str, int] = None
    ):
        """Add pattern-response mapping."""
        self.response_patterns.append({
            "pattern": re.compile(pattern, re.IGNORECASE),
            "response": response,
            "tokens": tokens or {"input": 50, "output": 25, "total": 75},
        })
    
    async def generate(self, prompt: str, **kwargs) -> MagicMock:
        """Generate response based on pattern matching."""
        self.call_history.append({"prompt": prompt, "kwargs": kwargs})
        
        for mapping in self.response_patterns:
            if mapping["pattern"].search(prompt):
                response = MagicMock()
                response.text = mapping["response"]
                response.input_tokens = mapping["tokens"]["input"]
                response.output_tokens = mapping["tokens"]["output"]
                response.total_tokens = mapping["tokens"]["total"]
                return response
        
        # Default response
        response = MagicMock()
        response.text = self.default_response
        response.input_tokens = 50
        response.output_tokens = 25
        response.total_tokens = 75
        return response

# Usage in tests
@pytest.fixture
def mock_llm():
    mock = DeterministicLLMMock()
    
    # Route decision patterns
    mock.add_pattern(
        r"(policy|document|knowledge|search)",
        '{"agent": "athena", "confidence": 0.9, "reasoning": "Knowledge query detected"}'
    )
    mock.add_pattern(
        r"(email|send|notify|message)",
        '{"agent": "hermes", "confidence": 0.85, "reasoning": "Communication request"}'
    )
    mock.add_pattern(
        r"(schedule|meeting|calendar|appointment)",
        '{"agent": "chronos", "confidence": 0.88, "reasoning": "Scheduling request"}'
    )
    
    return mock
```

### Recorded Response Playback

```python
# mocks/recorded_responses.py
import json
import hashlib
from pathlib import Path
from typing import Optional

class RecordedResponseMock:
    """Mock using recorded real LLM responses."""
    
    def __init__(self, recordings_dir: str = "tests/fixtures/llm_recordings"):
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.recording_mode = False
    
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model."""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _get_recording_path(self, cache_key: str) -> Path:
        return self.recordings_dir / f"{cache_key}.json"
    
    async def generate(self, prompt: str, model: str = "default", **kwargs):
        """Return recorded response or record new one."""
        cache_key = self._get_cache_key(prompt, model)
        recording_path = self._get_recording_path(cache_key)
        
        if recording_path.exists():
            # Playback mode
            with open(recording_path) as f:
                data = json.load(f)
            
            response = MagicMock()
            response.text = data["text"]
            response.input_tokens = data["input_tokens"]
            response.output_tokens = data["output_tokens"]
            response.total_tokens = data["total_tokens"]
            return response
        
        if self.recording_mode:
            # Record new response
            real_response = await self._real_llm_call(prompt, model, **kwargs)
            
            with open(recording_path, 'w') as f:
                json.dump({
                    "prompt": prompt,
                    "model": model,
                    "text": real_response.text,
                    "input_tokens": real_response.input_tokens,
                    "output_tokens": real_response.output_tokens,
                    "total_tokens": real_response.total_tokens,
                }, f, indent=2)
            
            return real_response
        
        raise ValueError(f"No recording found for prompt (key: {cache_key})")

# Record new responses (run once to populate fixtures)
# RECORD_LLM=1 pytest tests/llm -v
@pytest.fixture
def recorded_llm(request):
    mock = RecordedResponseMock()
    if os.getenv("RECORD_LLM"):
        mock.recording_mode = True
    return mock
```

---

## Behavioral Testing

### Intent Classification Tests

```python
# test_intent_classification.py
import pytest
from kosmos.agents.zeus.routing import classify_intent

class TestIntentClassification:
    """Test intent classification without calling LLM."""
    
    @pytest.mark.parametrize("query,expected_intent", [
        # Knowledge queries
        ("What is the vacation policy?", "knowledge_search"),
        ("Find documents about onboarding", "knowledge_search"),
        ("Search for Q3 report", "knowledge_search"),
        
        # Communication queries
        ("Send an email to John", "communication"),
        ("Notify the team about the meeting", "communication"),
        ("Draft a message to HR", "communication"),
        
        # Scheduling queries
        ("Schedule a meeting for tomorrow", "scheduling"),
        ("What's on my calendar today?", "scheduling"),
        ("Book a room for 2pm", "scheduling"),
        
        # Analysis queries
        ("Analyze the sales data", "analysis"),
        ("Summarize the quarterly results", "analysis"),
        ("Compare last month's metrics", "analysis"),
    ])
    def test_intent_classification(self, query, expected_intent, mock_llm):
        """Verify intent classification accuracy."""
        intent = classify_intent(query, llm=mock_llm)
        assert intent == expected_intent
    
    @pytest.mark.parametrize("query", [
        "Hello",
        "Thanks",
        "asdfghjkl",
        "",
    ])
    def test_ambiguous_intent_handling(self, query, mock_llm):
        """Ambiguous queries should return fallback intent."""
        intent = classify_intent(query, llm=mock_llm)
        assert intent in ["general", "clarification_needed"]
```

### Agent Routing Tests

```python
# test_agent_routing.py
import pytest
from kosmos.agents.zeus import ZeusOrchestrator

class TestAgentRouting:
    """Test routing decisions without live LLM."""
    
    @pytest.fixture
    def zeus(self, mock_llm):
        return ZeusOrchestrator(llm=mock_llm)
    
    @pytest.mark.parametrize("query,expected_agent,min_confidence", [
        ("What is the company policy on remote work?", "athena", 0.8),
        ("Send an email to the team", "hermes", 0.7),
        ("Schedule a meeting for tomorrow", "chronos", 0.7),
        ("Analyze the sales data", "apollo", 0.6),
    ])
    def test_routing_decisions(self, zeus, query, expected_agent, min_confidence):
        """Verify routing decisions match expected agents."""
        decision = zeus.route(query)
        
        assert decision.target_agent == expected_agent
        assert decision.confidence >= min_confidence
    
    def test_routing_fallback(self, zeus):
        """Unknown queries should fallback gracefully."""
        decision = zeus.route("xyzzy plugh")
        
        assert decision.target_agent in ["general", "clarification"]
        assert decision.requires_clarification == True
    
    def test_multi_agent_routing(self, zeus):
        """Complex queries may route to multiple agents."""
        query = "Find the Q3 report and email a summary to the team"
        decision = zeus.route(query)
        
        # Should identify multiple required agents
        assert len(decision.agent_chain) >= 2
        assert "athena" in decision.agent_chain
        assert "hermes" in decision.agent_chain
```

---

## Semantic Evaluation

### Golden Dataset Testing

```python
# test_golden_datasets.py
import pytest
import json
from pathlib import Path
from kosmos.evaluation import SemanticSimilarity

class TestGoldenDatasets:
    """Test against golden datasets of expected behaviors."""
    
    @pytest.fixture
    def golden_qa(self):
        """Load golden Q&A dataset."""
        path = Path("tests/fixtures/golden/qa_pairs.json")
        with open(path) as f:
            return json.load(f)
    
    @pytest.fixture
    def similarity_checker(self):
        return SemanticSimilarity(threshold=0.75)
    
    @pytest.mark.parametrize("dataset", ["knowledge", "scheduling", "communication"])
    @pytest.mark.evaluation
    async def test_golden_dataset(self, dataset, zeus, similarity_checker):
        """Test against golden dataset."""
        golden_path = Path(f"tests/fixtures/golden/{dataset}.json")
        with open(golden_path) as f:
            test_cases = json.load(f)
        
        results = []
        for case in test_cases:
            response = await zeus.process({"query": case["query"]})
            
            similarity = similarity_checker.compare(
                response["response"],
                case["expected_response"]
            )
            
            results.append({
                "query": case["query"],
                "similarity": similarity,
                "passed": similarity >= 0.75,
            })
        
        # Assert minimum pass rate
        pass_rate = sum(1 for r in results if r["passed"]) / len(results)
        assert pass_rate >= 0.9, f"Golden dataset pass rate: {pass_rate:.1%}"
    
    @pytest.mark.evaluation
    async def test_response_format_compliance(self, zeus, golden_qa):
        """Verify responses follow expected format."""
        for case in golden_qa[:10]:  # Sample
            response = await zeus.process({"query": case["query"]})
            
            # Check structure
            assert "response" in response
            assert "trace_id" in response
            assert len(response["response"]) > 0
            assert len(response["response"]) < 10000  # Reasonable length
```

### Semantic Similarity Evaluation

```python
# evaluation/similarity.py
from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticSimilarity:
    """Evaluate semantic similarity between responses."""
    
    def __init__(self, model: str = "all-MiniLM-L6-v2", threshold: float = 0.75):
        self.model = SentenceTransformer(model)
        self.threshold = threshold
    
    def compare(self, actual: str, expected: str) -> float:
        """Calculate cosine similarity between texts."""
        embeddings = self.model.encode([actual, expected])
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(similarity)
    
    def is_similar(self, actual: str, expected: str) -> bool:
        """Check if texts are semantically similar."""
        return self.compare(actual, expected) >= self.threshold
    
    def batch_compare(self, pairs: list) -> list:
        """Compare multiple pairs efficiently."""
        all_texts = []
        for actual, expected in pairs:
            all_texts.extend([actual, expected])
        
        embeddings = self.model.encode(all_texts)
        
        results = []
        for i in range(0, len(embeddings), 2):
            similarity = np.dot(embeddings[i], embeddings[i+1]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i+1])
            )
            results.append(float(similarity))
        
        return results

# Usage in tests
def test_response_semantic_match(similarity_checker):
    actual = "The vacation policy allows 20 days of paid time off per year."
    expected = "Employees receive 20 days of annual paid vacation."
    
    assert similarity_checker.is_similar(actual, expected)
```

---

## Prompt Regression Testing

### Prompt Change Detection

```python
# test_prompt_regression.py
import pytest
import hashlib
from pathlib import Path

class TestPromptRegression:
    """Detect unintended prompt changes."""
    
    @pytest.fixture
    def prompt_checksums(self):
        """Load expected prompt checksums."""
        path = Path("tests/fixtures/prompt_checksums.json")
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}
    
    def test_system_prompts_unchanged(self, prompt_checksums):
        """Verify system prompts haven't changed unexpectedly."""
        from kosmos.prompts import SYSTEM_PROMPTS
        
        for name, prompt in SYSTEM_PROMPTS.items():
            current_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
            
            if name in prompt_checksums:
                expected_hash = prompt_checksums[name]
                assert current_hash == expected_hash, (
                    f"Prompt '{name}' has changed. "
                    f"Expected hash: {expected_hash}, Got: {current_hash}. "
                    f"Run `pytest --update-checksums` to update if intentional."
                )
    
    @pytest.mark.parametrize("prompt_name", [
        "zeus_router",
        "athena_search",
        "hermes_compose",
        "chronos_schedule",
    ])
    @pytest.mark.evaluation
    async def test_prompt_behavior_stability(self, prompt_name, mock_llm, golden_qa):
        """Verify prompt changes don't affect expected behavior."""
        from kosmos.prompts import get_prompt
        
        prompt_template = get_prompt(prompt_name)
        
        # Test against golden dataset
        failures = []
        for case in golden_qa[:20]:
            formatted_prompt = prompt_template.format(**case["variables"])
            response = await mock_llm.generate(formatted_prompt)
            
            if not meets_expectations(response.text, case["expected"]):
                failures.append(case["id"])
        
        assert len(failures) == 0, f"Prompt regression detected in cases: {failures}"
```

---

## Live LLM Testing

### Selective Live Tests

```python
# test_live_llm.py
import pytest
import os

# Skip if no API key or not in CI
pytestmark = pytest.mark.skipif(
    not os.getenv("HUGGINGFACE_API_KEY") or not os.getenv("CI"),
    reason="Live LLM tests only run in CI with API key"
)

@pytest.mark.live
@pytest.mark.slow
class TestLiveLLM:
    """Tests that call real LLM API."""
    
    @pytest.fixture
    def live_llm(self):
        from kosmos.services.llm import HuggingFaceService
        return HuggingFaceService(
            api_key=os.getenv("HUGGINGFACE_API_KEY"),
            endpoint=os.getenv("HUGGINGFACE_ENDPOINT"),
        )
    
    @pytest.mark.asyncio
    async def test_basic_generation(self, live_llm):
        """Verify LLM can generate responses."""
        response = await live_llm.generate(
            prompt="What is 2 + 2?",
            max_tokens=50,
        )
        
        assert response.text is not None
        assert "4" in response.text or "four" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_structured_output(self, live_llm):
        """Verify LLM can produce structured JSON output."""
        prompt = """
        Extract the following information as JSON:
        Name: John Doe, Age: 30, City: New York
        
        Output format: {"name": "", "age": 0, "city": ""}
        """
        
        response = await live_llm.generate(prompt, max_tokens=100)
        
        # Should contain valid JSON
        import json
        data = json.loads(response.text)
        assert "name" in data
        assert "age" in data
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_latency_acceptable(self, live_llm):
        """Verify LLM response time is acceptable."""
        import time
        
        start = time.time()
        await live_llm.generate("Hello, world!", max_tokens=50)
        duration = time.time() - start
        
        assert duration < 10, f"LLM latency too high: {duration:.2f}s"
```

---

## Test Fixtures

### Golden Dataset Structure

```json
// tests/fixtures/golden/knowledge.json
{
  "dataset": "knowledge",
  "version": "1.0",
  "test_cases": [
    {
      "id": "knowledge_001",
      "query": "What is the vacation policy?",
      "expected_response": "Employees receive 20 days of paid time off per year, plus company holidays.",
      "expected_agent": "athena",
      "expected_intent": "knowledge_search",
      "variables": {
        "context": "HR policy documents",
        "user_role": "employee"
      },
      "tags": ["hr", "policy", "vacation"]
    },
    {
      "id": "knowledge_002",
      "query": "How do I submit an expense report?",
      "expected_response": "Submit expense reports through the Finance portal within 30 days of the expense.",
      "expected_agent": "athena",
      "expected_intent": "knowledge_search",
      "variables": {
        "context": "Finance procedures",
        "user_role": "employee"
      },
      "tags": ["finance", "expenses", "procedure"]
    }
  ]
}
```

---

## CI Integration

### Test Configuration

```yaml
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (may need services)
    e2e: End-to-end tests (full system)
    live: Tests that call real LLM APIs
    evaluation: Evaluation/benchmark tests
    slow: Slow running tests

addopts = 
    -v
    --strict-markers
    -m "not live and not slow"

filterwarnings =
    ignore::DeprecationWarning
```

### GitHub Actions for LLM Tests

```yaml
# .github/workflows/llm-tests.yml
name: LLM Tests

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM
  workflow_dispatch:

jobs:
  live-llm-tests:
    runs-on: ubuntu-latest
    environment: llm-testing
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      
      - name: Run live LLM tests
        run: pytest tests/llm -v -m live --timeout=120
        env:
          HUGGINGFACE_API_KEY: ${{ secrets.HUGGINGFACE_API_KEY }}
          HUGGINGFACE_ENDPOINT: ${{ secrets.HUGGINGFACE_ENDPOINT }}
      
      - name: Run evaluation tests
        run: pytest tests/evaluation -v -m evaluation
      
      - name: Upload test results
        uses: actions/upload-artifact@v4
        with:
          name: llm-test-results
          path: test-results/
```

---

## Related Documentation

- [Testing Strategy Overview](README.md)
- [Prompt Standards](../prompt-standards.md)
- [LLM Observability](../../04-operations/observability/llm-observability.md)

---

**Document Owner:** mlops@nuvanta-holding.com

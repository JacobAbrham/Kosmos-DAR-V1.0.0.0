# Loop Detection & Remediation

**Handling Infinite Loops and Recursive Behavior**

> "Detect early, break fast, prevent recurrence."

---

## 🚨 Incident Overview

**Severity:** P1 (High)  
**Response Time:** < 15 minutes  
**Owner:** ML Team + DevOps

### What are AI Loops?

AI loops occur when:
- Models call themselves recursively
- Output feeds back as input indefinitely
- Agents get stuck in action cycles
- Token generation doesn't terminate

---

## 🔍 Detection

### Automated Monitoring

```python
# Detect loops
def detect_loop(request_id, max_iterations=10):
    history = get_request_history(request_id)
    
    if len(history) > max_iterations:
        return True, "max_iterations_exceeded"
    
    # Check for repeated patterns
    if has_repeated_pattern(history, window=3):
        return True, "pattern_loop_detected"
    
    # Check token usage
    if total_tokens(history) > 100_000:
        return True, "token_limit_exceeded"
    
    return False, None
```

### Alert Triggers
- Request duration > 5 minutes
- Token count > 50K for single request
- Repeated API calls (same input/output)
- Memory usage spike
- Timeout errors

---

## ⚡ Immediate Response

### Step 1: Kill the Loop
```python
# Circuit breaker
def break_loop(request_id):
    # Terminate request
    cancel_request(request_id)
    
    # Block further iterations
    blacklist_request_id(request_id, duration=3600)
    
    # Log incident
    log_loop_incident(request_id)
```

### Step 2: Prevent Cascade
```bash
# Rate limit the user/session
curl -X POST https://api.nuvanta.com/v1/ratelimit \
  -d '{"user_id": "user_123", "limit": 10, "window": 3600}'

# Scale down if needed
kubectl scale deployment model-api --replicas=5
```

---

## 🛠️ Remediation

### Add Circuit Breakers

```python
from circuitbreaker import CircuitBreaker

@CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=60,
    expected_exception=LoopDetected
)
def generate_with_protection(prompt):
    # Add iteration counter
    if get_iteration_count() > MAX_ITERATIONS:
        raise LoopDetected("Too many iterations")
    
    response = model.generate(prompt)
    return response
```

### Implement Timeouts

```python
# Request timeout
@timeout(seconds=120)
def generate_response(prompt):
    return model.generate(prompt)
```

---

## 📋 Prevention

### Design Patterns
- Always set `max_tokens` limits
- Implement iteration counters
- Use timeouts on all AI calls
- Monitor token usage
- Add circuit breakers

---

**Last Updated:** 2025-12-11  
**Document Owner:** ML Team

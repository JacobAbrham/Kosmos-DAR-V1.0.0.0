# Prompt Injection Attack Response

**Detecting and Mitigating Prompt Injection Attempts**

> "Trust but verify. Sanitize all inputs, filter all outputs."

---

## 🚨 Incident Overview

**Severity:** P0 (Critical)  
**Response Time:** < 5 minutes  
**Owner:** Security Team + ML Team

### What is Prompt Injection?

Prompt injection is when malicious users craft inputs that manipulate AI models to:
- Ignore system instructions
- Leak sensitive information
- Perform unauthorized actions
- Generate harmful content

---

## 🔍 Detection

### Automated Detection

```python
# Monitor for injection patterns
injection_patterns = [
    r"ignore.*previous.*instructions",
    r"disregard.*above",
    r"you\s*are\s*now\s*(DAN|jailbroken)",
    r"print.*system.*prompt",
    r"reveal.*instructions"
]

def detect_injection(user_input):
    for pattern in injection_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return True, pattern
    return False, None
```

### Alert Triggers
- Pattern matching hits
- Unusual token sequences
- Model confidence drops
- Output format violations
- Security monitoring alerts

---

## ⚡ Immediate Response (< 5 minutes)

### Step 1: Contain
```bash
# Block the user/IP immediately
curl -X POST https://api.nuvanta.com/v1/security/block \
  -H "Authorization: Bearer $ADMIN_KEY" \
  -d '{"user_id": "suspicious_user", "reason": "prompt_injection"}'

# Rate limit if widespread
kubectl scale deployment model-api --replicas=2  # Reduce capacity
```

### Step 2: Assess Impact
- Check logs for successful attacks
- Review recent outputs for leaks
- Identify affected users
- Determine data exposure

### Step 3: Notify
```bash
# Alert security team
pagerduty-cli trigger \
  --service kosmos-security \
  --severity critical \
  --summary "Prompt injection detected"

# Update status page
status-cli update --status investigating \
  --message "Investigating security incident"
```

---

## 🛠️ Remediation

### Immediate Mitigations

```python
# Enhanced input filtering
def sanitize_input(user_input):
    # Remove dangerous patterns
    cleaned = remove_system_commands(user_input)
    cleaned = escape_special_chars(cleaned)
    cleaned = truncate_length(cleaned, max=2000)
    return cleaned

# Output filtering
def filter_output(model_output):
    # Remove system artifacts
    filtered = remove_system_prompts(model_output)
    filtered = remove_pii(filtered)
    return filtered
```

### Deploy Hotfix
```bash
# Deploy security patch
git checkout -b hotfix/prompt-injection
# Apply fixes
git commit -m "security: add prompt injection defenses"
git push origin hotfix/prompt-injection

# Emergency deployment
kubectl apply -f k8s/security-patch.yaml
```

---

## 📋 Post-Incident

### Conduct Post-Mortem
- Timeline of events
- Attack vectors used
- Impact assessment
- Lessons learned
- Action items

### Update Defenses
- Improve pattern detection
- Enhance input validation
- Strengthen output filtering
- Update monitoring alerts

---

## 🔗 Related Documentation

- **[Prompt Standards](../../03-engineering/prompt-standards.md)**
- **[Security Scorecard](../../01-governance/ethics-scorecard.md)**

---

**Last Updated:** 2025-12-11  
**Document Owner:** Security Team

# MC-003: Code Reviewer

**Model Card v3.0.1**

> "Review code like an expert, teach like a mentor."

---

## 📋 Model Details

| Attribute | Value |
|-----------|-------|
| **Model ID** | MC-003 |
| **Model Name** | Code Reviewer |
| **Version** | 3.0.1 |
| **Status** | ✅ Production |
| **Model Type** | Code Analysis & Generation |
| **Architecture** | GPT-4-Turbo |
| **Provider** | OpenAI |
| **Last Updated** | 2025-12-01 |
| **Owner** | ML Engineering Lead |

---

## 🎯 Intended Use

### Primary Use Cases

1. **Pull Request Review** - Automated code review suggestions
2. **Security Analysis** - Identify potential vulnerabilities
3. **Style Compliance** - Check adherence to coding standards
4. **Performance Tips** - Suggest optimizations

### Supported Languages

| Language | Support Level | Notes |
|----------|---------------|-------|
| Python | ⭐⭐⭐ Full | Primary focus |
| JavaScript/TypeScript | ⭐⭐⭐ Full | Including React/Node.js |
| Java | ⭐⭐ Good | Spring Boot focus |
| Go | ⭐⭐ Good | Idiomatic suggestions |
| C# | ⭐⭐ Good | .NET patterns |
| Rust | ⭐ Basic | Limited coverage |

### Out-of-Scope Applications

- ❌ Automated code fixes without human review
- ❌ Security-critical vulnerability patching
- ❌ Legacy COBOL/Fortran review
- ❌ Real-time IDE integration (latency constraints)

---

## 📊 Performance Metrics

### Accuracy & Quality

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Issue Detection Rate | 89% | >80% | ✅ |
| False Positive Rate | 8% | <15% | ✅ |
| Suggestion Acceptance | 72% | >60% | ✅ |
| Security Issue Detection | 85% | >75% | ✅ |
| Human Agreement | 87% | >80% | ✅ |

### By Category

| Category | Precision | Recall | F1 |
|----------|-----------|--------|-----|
| Security Issues | 91% | 85% | 88% |
| Performance | 84% | 78% | 81% |
| Style/Formatting | 95% | 92% | 93% |
| Logic Errors | 79% | 75% | 77% |
| Best Practices | 88% | 82% | 85% |

### Operational Metrics

| Metric | Value | SLO | Status |
|--------|-------|-----|--------|
| Availability | 99.7% | 99.5% | ✅ |
| P50 Latency | 1.5s | <2s | ✅ |
| P95 Latency | 2.4s | <3s | ✅ |
| P99 Latency | 4.5s | <5s | ✅ |
| Error Rate | 0.8% | <2% | ✅ |

### Cost Metrics

| Metric | Value |
|--------|-------|
| Cost per Request | $0.0112 |
| Monthly Volume | 9M requests |
| Monthly Cost | $100,800 |
| Cost Trend | ↓ 3% MoM |

---

## 📚 Training Data

### Dataset Composition

| Source | Size | Description |
|--------|------|-------------|
| Internal Code Reviews | 100,000 reviews | Historical PR reviews |
| Open Source Reviews | 500,000 reviews | GitHub public reviews |
| Security Advisories | 50,000 examples | CVE-linked code samples |
| Style Guides | 1,000 docs | Major style guide rules |

### Data Preprocessing

1. **Anonymization** - Removed author/org identifiers
2. **Deduplication** - Removed duplicate reviews
3. **Quality Filtering** - Only accepted/merged reviews
4. **Syntax Validation** - Ensured valid code samples

---

## ⚠️ Limitations & Risks

### Known Failure Modes

| Failure Mode | Frequency | Mitigation |
|--------------|-----------|------------|
| False security alerts | ~8% | Severity scoring, human review |
| Language version mismatch | ~5% | Version specification in config |
| Framework-specific misses | ~10% | Framework-aware prompting |
| Over-optimization suggestions | ~6% | Readability priority flag |

### Bias Considerations

- Favors popular coding patterns (may miss valid alternatives)
- Open-source style bias (may not match enterprise conventions)
- English-centric comments and documentation

### Risk Mitigations

1. **Severity Tiers** - Critical issues flagged, minor suggestions optional
2. **Confidence Scoring** - Low-confidence reviews marked
3. **Human Override** - All suggestions require human approval
4. **Audit Trail** - Full logging of all reviews

---

## ✅ Ethical Considerations

### Fairness Analysis

| Dimension | Assessment | Notes |
|-----------|------------|-------|
| Language Bias | Low | Multi-language training |
| Style Preference | Medium | May favor certain patterns |
| Authorship Bias | None | Fully anonymized |

### Privacy Considerations

- Code snippets not stored post-inference
- No training on proprietary code without consent
- API logs retained for 30 days only

### Environmental Impact

- **Carbon Footprint:** N/A (API-based)
- **Token Optimization:** Chunked reviews reduce usage

---

## 🔧 Technical Specifications

### Input/Output

```yaml
input:
  type: code
  max_length: 32,000 tokens
  formats: [diff, full_file, snippet]
  context: [file_path, language, framework]

output:
  type: structured_review
  includes:
    - issues: list of identified problems
    - suggestions: improvement recommendations
    - severity: critical/high/medium/low/info
    - line_numbers: specific code locations
    - explanations: educational context
```

### API Example

```python
from kosmos.models import CodeReviewer

reviewer = CodeReviewer(model_id="MC-003")

result = reviewer.review(
    code=pull_request_diff,
    language="python",
    framework="fastapi",
    focus=["security", "performance"],
    max_issues=10
)

for issue in result.issues:
    print(f"[{issue.severity}] Line {issue.line}: {issue.title}")
    print(f"  Suggestion: {issue.suggestion}")
    print(f"  Explanation: {issue.explanation}")
```

### Integration Example

```yaml
# GitHub Actions integration
- name: AI Code Review
  uses: kosmos/code-reviewer-action@v3
  with:
    model_id: MC-003
    focus: security,performance
    fail_on: critical
    comment_on_pr: true
```

---

## 📞 Contact & Support

| Role | Contact |
|------|---------|
| Model Owner | ml-engineering@nuvanta-holding.com |
| On-Call Support | #ml-support (Slack) |
| Escalation | VP Engineering |

---

## 📜 Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0.1 | 2025-12-01 | Improved TypeScript support |
| 3.0.0 | 2025-11-01 | Major upgrade to GPT-4-Turbo |
| 2.5.0 | 2025-09-15 | Added security focus mode |
| 2.0.0 | 2025-07-01 | Multi-language support |
| 1.0.0 | 2025-05-01 | Initial release (Python only) |

---

## 🔗 Related Documentation

- **[AIBOM](https://github.com/Nuvanta-Holding/kosmos-docs/blob/main/aibom/production/MC-003-v3.0.1.yaml)** - Machine-readable metadata
- **[SLA/SLO](../../04-operations/sla-slo.md)** - Service level objectives
- **[Prompt Standards](../prompt-standards.md)** - Prompt engineering guidelines

---

**Last Updated:** 2025-12-12  
**Document Owner:** ML Engineering Lead  
**Review Cycle:** Quarterly

[← MC-002](MC-002-sentiment-analyzer.md) | [Back to Model Cards](README.md) | [MC-004 →](MC-004-image-classifier.md)

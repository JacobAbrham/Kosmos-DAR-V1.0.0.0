# MC-002: Sentiment Analyzer

**Model Card v1.5.2**

> "Understand emotion, respond with empathy."

---

## 📋 Model Details

| Attribute | Value |
|-----------|-------|
| **Model ID** | MC-002 |
| **Model Name** | Sentiment Analyzer |
| **Version** | 1.5.2 |
| **Status** | ✅ Production |
| **Model Type** | Text Classification |
| **Architecture** | Fine-tuned BERT |
| **Provider** | Internal |
| **Last Updated** | 2025-11-15 |
| **Owner** | ML Engineering Lead |

---

## 🎯 Intended Use

### Primary Use Cases

1. **Customer Feedback Analysis** - Classify sentiment in reviews/feedback
2. **Social Media Monitoring** - Track brand sentiment across platforms
3. **Support Ticket Triage** - Prioritize tickets by customer sentiment
4. **Survey Analysis** - Aggregate sentiment from survey responses

### Out-of-Scope Applications

- ❌ Sarcasm/irony detection (limited accuracy)
- ❌ Multi-turn conversation sentiment
- ❌ Real-time streaming analysis
- ❌ Non-text content (images, audio)

### Target Users

- Customer success teams
- Marketing analysts
- Support managers
- Product managers

---

## 📊 Performance Metrics

### Accuracy & Quality

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Accuracy | 94.2% | &gt;90% | ✅ |
| Precision | 93.1% | &gt;88% | ✅ |
| Recall | 95.3% | &gt;88% | ✅ |
| F1 Score | 94.2% | &gt;88% | ✅ |
| AUC-ROC | 0.97 | &gt;0.92 | ✅ |

### Per-Class Performance

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| Positive | 95.2% | 96.1% | 95.6% | 45,000 |
| Neutral | 89.5% | 88.2% | 88.8% | 32,000 |
| Negative | 94.8% | 95.7% | 95.2% | 23,000 |

### Operational Metrics

| Metric | Value | SLO | Status |
|--------|-------|-----|--------|
| Availability | 99.8% | 99.5% | ✅ |
| P50 Latency | 45ms | &lt;100ms | ✅ |
| P95 Latency | 120ms | &lt;200ms | ✅ |
| P99 Latency | 250ms | &lt;500ms | ✅ |
| Error Rate | 0.2% | &lt;1% | ✅ |

### Cost Metrics

| Metric | Value |
|--------|-------|
| Cost per Request | $0.0045 |
| Monthly Volume | 6M requests |
| Monthly Cost | $27,000 |
| Cost Trend | → Stable |

---

## 📚 Training Data

### Dataset Composition

| Source | Size | Description |
|--------|------|-------------|
| Customer Feedback | 250,000 samples | Labeled internal feedback |
| SST-5 | 300,000 samples | Stanford Sentiment Treebank |
| IMDB Reviews | 200,000 samples | Movie review sentiment |

### Class Distribution

```yaml
training_distribution:
  positive: 42%
  neutral: 31%
  negative: 27%
  
# Balanced through:
# - Oversampling minority class
# - Class weights in loss function
```

### Data Preprocessing

1. **Text Normalization** - Lowercasing, punctuation handling
2. **Tokenization** - WordPiece tokenization (BERT)
3. **Length Truncation** - Max 512 tokens
4. **Label Balancing** - Class weight adjustment

---

## ⚠️ Limitations & Risks

### Known Failure Modes

| Failure Mode | Frequency | Mitigation |
|--------------|-----------|------------|
| Sarcasm misclassification | ~15% | Flag uncertain predictions |
| Mixed sentiment confusion | ~8% | Multi-label output option |
| Domain-specific jargon | ~5% | Domain adaptation training |
| Short text unreliability | ~7% | Minimum text length warning |

### Bias Considerations

- English-centric training (limited multilingual support)
- Formal text bias (may underperform on casual/slang text)
- Domain skew toward product reviews

### Risk Mitigations

1. **Confidence Thresholds** - Low confidence → manual review
2. **Ensemble Voting** - Multiple model agreement required
3. **Continuous Monitoring** - Drift detection on production data
4. **Regular Retraining** - Quarterly model updates

---

## ✅ Ethical Considerations

### Fairness Analysis

| Dimension | Assessment | Notes |
|-----------|------------|-------|
| Demographic Parity | Monitored | No significant disparities |
| Language Style | Medium Risk | May favor formal language |
| Cultural Bias | Low Risk | Training data is diverse |

### Privacy Considerations

- No user data stored in model
- Inference data not retained
- GDPR compliant

### Environmental Impact

- **Training Carbon:** 12 kg CO2
- **Inference:** Highly efficient (BERT-base)
- **GPU Hours:** 32 hours (A100)

---

## 🔧 Technical Specifications

### Input/Output

```yaml
input:
  type: text
  max_length: 512 tokens
  min_length: 10 tokens (recommended)
  languages: [en]  # Primary support

output:
  type: classification
  classes: [positive, neutral, negative]
  includes: [label, confidence, probabilities]
```

### API Example

```python
from kosmos.models import SentimentAnalyzer

analyzer = SentimentAnalyzer(model_id="MC-002")

result = analyzer.analyze(
    text="This product exceeded my expectations!",
    return_probabilities=True
)

print(result.label)        # "positive"
print(result.confidence)   # 0.95
print(result.probabilities)
# {"positive": 0.95, "neutral": 0.03, "negative": 0.02}
```

### Batch Processing

```python
texts = ["Great service!", "It was okay.", "Terrible experience."]
results = analyzer.analyze_batch(texts, batch_size=32)

for text, result in zip(texts, results):
    print(f"{text} → {result.label} ({result.confidence:.2f})")
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
| 1.5.2 | 2025-11-15 | Bug fixes, improved neutral detection |
| 1.5.0 | 2025-09-01 | Added confidence calibration |
| 1.4.0 | 2025-07-01 | Performance improvements |
| 1.0.0 | 2025-06-01 | Initial release |

---

## 🔗 Related Documentation

- **[AIBOM](https://github.com/Nuvanta-Holding/kosmos-docs/blob/main/aibom/production/MC-002-v1.5.2.yaml)** - Machine-readable metadata
- **[SLA/SLO](../../04-operations/sla-slo)** - Service level objectives
- **[Drift Detection](../../04-operations/drift-detection)** - Monitoring configuration

---

**Last Updated:** 2025-12-12  
**Document Owner:** ML Engineering Lead  
**Review Cycle:** Quarterly

[← MC-001](MC-001-document-summarizer) | [Back to Model Cards](README) | [MC-003 →](MC-003-code-reviewer)

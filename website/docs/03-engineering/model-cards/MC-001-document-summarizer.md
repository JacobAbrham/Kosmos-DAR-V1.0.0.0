# MC-001: Document Summarizer

**Model Card v2.1.0**

> "Distill knowledge, preserve meaning."

---

## 📋 Model Details

| Attribute | Value |
|-----------|-------|
| **Model ID** | MC-001 |
| **Model Name** | Document Summarizer |
| **Version** | 2.1.0 |
| **Status** | ✅ Production |
| **Model Type** | Text Summarization |
| **Architecture** | GPT-4-Turbo |
| **Provider** | OpenAI |
| **Last Updated** | 2025-12-11 |
| **Owner** | ML Engineering Lead |

---

## 🎯 Intended Use

### Primary Use Cases

1. **Executive Summaries** - Condense long documents into key points
2. **Report Digests** - Summarize financial/technical reports
3. **Email Summarization** - Extract key action items from email threads
4. **Meeting Notes** - Generate concise meeting summaries

### Out-of-Scope Applications

- ❌ Legal document summarization (requires legal review)
- ❌ Medical record summarization (requires HIPAA compliance)
- ❌ Real-time transcription summarization
- ❌ Summarization of content &lt;100 words

### Target Users

- Business analysts
- Executive assistants
- Knowledge workers
- Documentation teams

---

## 📊 Performance Metrics

### Accuracy & Quality

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| ROUGE-1 | 0.48 | &gt;0.40 | ✅ |
| ROUGE-2 | 0.24 | &gt;0.18 | ✅ |
| ROUGE-L | 0.42 | &gt;0.35 | ✅ |
| BERTScore | 0.89 | &gt;0.85 | ✅ |
| Human Eval | 4.2/5 | &gt;3.8 | ✅ |

### Operational Metrics

| Metric | Value | SLO | Status |
|--------|-------|-----|--------|
| Availability | 99.95% | 99.9% | ✅ |
| P50 Latency | 800ms | &lt;1000ms | ✅ |
| P95 Latency | 1200ms | &lt;2000ms | ✅ |
| P99 Latency | 3100ms | &lt;5000ms | ✅ |
| Error Rate | 0.3% | &lt;1% | ✅ |

### Cost Metrics

| Metric | Value |
|--------|-------|
| Cost per Request | $0.0084 |
| Monthly Volume | 15M requests |
| Monthly Cost | $126,000 |
| Cost Trend | ↓ 5% MoM |

---

## 📚 Training Data

### Dataset Composition

| Source | Size | Description |
|--------|------|-------------|
| Internal Documents | 50,000 docs | Corporate documents, cleaned |
| Academic Papers | 100,000 abstracts | Public research papers |
| News Articles | 75,000 articles | Licensed news content |

### Data Preprocessing

1. **Deduplication** - Removed duplicate documents
2. **PII Removal** - Scrubbed personal identifiable information
3. **Quality Filtering** - Removed low-quality/incomplete documents
4. **Format Normalization** - Standardized document formats

### Known Data Limitations

- Training data primarily English (95%)
- Limited representation of technical jargon in specialized domains
- Academic papers over-represented vs. business documents

---

## ⚠️ Limitations & Risks

### Known Failure Modes

| Failure Mode | Frequency | Mitigation |
|--------------|-----------|------------|
| Hallucination of facts | ~2% | Confidence scoring, human review |
| Loss of numerical precision | ~5% | Post-processing validation |
| Over-compression | ~3% | Minimum length constraints |
| Context window overflow | ~1% | Chunking strategy |

### Bias Considerations

- May favor formal/academic writing styles
- English-centric summarization patterns
- Potential underrepresentation of non-Western perspectives

### Risk Mitigations

1. **Confidence Scoring** - Low-confidence outputs flagged for review
2. **Length Guardrails** - Minimum/maximum summary lengths enforced
3. **Human-in-the-Loop** - Critical documents require human approval
4. **Audit Logging** - All summarizations logged for review

---

## ✅ Ethical Considerations

### Fairness Analysis

| Dimension | Assessment | Notes |
|-----------|------------|-------|
| Language Bias | Medium | Primarily English-trained |
| Domain Bias | Low | Diverse training corpus |
| Output Bias | Low | Neutral summarization style |

### Privacy Considerations

- No PII stored in model weights
- User documents not retained post-processing
- GDPR Article 17 compliant (Amnesia Protocol)

### Environmental Impact

- **Carbon Footprint:** N/A (API-based, provider responsibility)
- **Inference Efficiency:** Optimized prompt templates reduce token usage

---

## 🔧 Technical Specifications

### Input/Output

```yaml
input:
  type: text
  max_length: 128,000 tokens
  formats: [plain_text, markdown, html]
  languages: [en, ar, de, fr]  # Primary: en

output:
  type: text
  max_length: 4,096 tokens
  format: markdown
  includes: [summary, key_points, action_items]
```

### API Example

```python
from kosmos.models import DocumentSummarizer

summarizer = DocumentSummarizer(model_id="MC-001")

result = summarizer.summarize(
    document=long_document,
    max_length=500,
    style="executive",
    include_key_points=True
)

print(result.summary)
print(result.key_points)
print(result.confidence_score)
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
| 2.1.0 | 2025-12-11 | Improved Arabic language support |
| 2.0.0 | 2025-10-01 | Upgraded to GPT-4-Turbo |
| 1.5.0 | 2025-07-15 | Added key points extraction |
| 1.0.0 | 2025-05-01 | Initial release |

---

## 🔗 Related Documentation

- **[AIBOM](https://github.com/Nuvanta-Holding/kosmos-docs/blob/main/aibom/production/MC-001-v2.1.0.yaml)** - Machine-readable metadata
- **[SLA/SLO](../../04-operations/sla-slo)** - Service level objectives
- **[Drift Detection](../../04-operations/drift-detection)** - Monitoring configuration
- **[FinOps Metrics](../../04-operations/finops-metrics)** - Cost tracking

---

**Last Updated:** 2025-12-12  
**Document Owner:** ML Engineering Lead  
**Review Cycle:** Quarterly

[← Back to Model Cards](README) | [MC-002 →](MC-002-sentiment-analyzer)

# MC-005: Translation Engine

**Model Card v2.0-rc1**

> "Bridge languages, connect worlds."

:::info Release Candidate
    This model is in **release candidate** status, pending final production approval.

---

## 📋 Model Details

| Attribute | Value |
|-----------|-------|
| **Model ID** | MC-005 |
| **Model Name** | Translation Engine |
| **Version** | 2.0-rc1 |
| **Status** | 🟡 Release Candidate |
| **Model Type** | Neural Machine Translation |
| **Architecture** | mBART-50 |
| **Provider** | Internal |
| **Last Updated** | 2025-12-08 |
| **Owner** | ML Engineering Lead |

---

## 🎯 Intended Use

### Primary Use Cases

1. **Document Translation** - Translate business documents
2. **Real-time Chat Translation** - Support multilingual communication
3. **Content Localization** - Adapt content for regional markets
4. **Email Translation** - Cross-language email communication

### Supported Languages

| Language | Code | Translation Quality |
|----------|------|---------------------|
| English | en | ⭐⭐⭐ Native |
| Arabic | ar | ⭐⭐⭐ Excellent |
| German | de | ⭐⭐⭐ Excellent |
| French | fr | ⭐⭐⭐ Excellent |
| Spanish | es | ⭐⭐ Good |
| Chinese | zh | ⭐⭐ Good |
| Japanese | ja | ⭐⭐ Good |
| Korean | ko | ⭐⭐ Good |

### Out-of-Scope Applications

- ❌ Legal document translation (requires certified translator)
- ❌ Medical content translation
- ❌ Simultaneous interpretation
- ❌ Poetry/literary translation

---

## 📊 Performance Metrics (RC1)

### Translation Quality (BLEU Scores)

| Language Pair | BLEU | Target | Status |
|---------------|------|--------|--------|
| EN → AR | 42.5 | 40.0 | ✅ |
| EN → DE | 38.2 | 36.0 | ✅ |
| EN → FR | 45.1 | 42.0 | ✅ |
| AR → EN | 40.8 | 38.0 | ✅ |
| DE → EN | 41.2 | 38.0 | ✅ |
| FR → EN | 44.3 | 42.0 | ✅ |

### Operational Metrics

| Metric | Value | Target |
|--------|-------|--------|
| P50 Latency | 200ms | &lt;250ms |
| P95 Latency | 450ms | &lt;500ms |
| P99 Latency | 800ms | &lt;1000ms |
| Error Rate | 0.5% | &lt;1% |

---

## 📚 Training Data

### Dataset Composition

| Source | Size | Description |
|--------|------|-------------|
| Parallel Corpus | 10M sentence pairs | Multi-language aligned |
| Internal TM | 500,000 pairs | Domain-specific terminology |

### Data Quality

- Human-verified alignment
- Domain terminology preserved
- Regular quality audits

---

## ⚠️ Release Candidate Status

### Completed Milestones

- [x] Performance tuning complete
- [x] Security review passed
- [x] BLEU score targets achieved
- [x] Load testing completed

### Pending Approval

- [ ] Final stakeholder sign-off
- [ ] Production deployment configuration
- [ ] Monitoring dashboard setup

### Target Production Date

**2025-12-20**

---

## 📞 Contact

| Role | Contact |
|------|---------|
| Model Owner | ml-engineering@nuvanta-holding.com |
| Release Manager | #ml-releases (Slack) |

---

**Last Updated:** 2025-12-12  
**Document Owner:** ML Engineering Lead  

[← MC-004](MC-004-image-classifier) | [Back to Model Cards](README)

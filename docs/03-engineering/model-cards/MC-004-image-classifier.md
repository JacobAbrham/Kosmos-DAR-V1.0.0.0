# MC-004: Image Classifier

**Model Card v0.9-beta**

> "See clearly, classify accurately."

!!! warning "Development Model"
    This model is currently in **beta testing** and not approved for production use.

---

## 📋 Model Details

| Attribute | Value |
|-----------|-------|
| **Model ID** | MC-004 |
| **Model Name** | Image Classifier |
| **Version** | 0.9-beta |
| **Status** | 🟡 Testing |
| **Model Type** | Image Classification |
| **Architecture** | ViT-Large/14 |
| **Provider** | Internal |
| **Last Updated** | 2025-12-10 |
| **Owner** | ML Engineering Lead |

---

## 🎯 Intended Use

### Primary Use Cases (Planned)

1. **Document Classification** - Classify document types from images
2. **Quality Inspection** - Visual quality control checks
3. **Content Moderation** - Flag inappropriate image content
4. **Asset Categorization** - Organize image libraries

### Out-of-Scope Applications

- ❌ Medical image diagnosis
- ❌ Biometric identification
- ❌ Surveillance applications
- ❌ Real-time video classification

---

## 📊 Performance Metrics (Development)

### Accuracy & Quality

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Top-1 Accuracy | 87.2% | 90% | 🟡 |
| Top-5 Accuracy | 96.5% | 98% | 🟡 |
| Precision | 85.1% | 88% | 🟡 |
| Recall | 88.3% | 90% | 🟡 |
| F1 Score | 86.7% | 89% | 🟡 |

### Latency (Development Environment)

| Metric | Value | Target |
|--------|-------|--------|
| P50 Latency | 150ms | <100ms |
| P95 Latency | 300ms | <250ms |
| P99 Latency | 500ms | <400ms |

---

## 📚 Training Data

### Dataset Composition

| Source | Size | Description |
|--------|------|-------------|
| Internal Images | 500,000 images | Document/product images |
| ImageNet Subset | 1,000,000 images | General image classification |

### Known Limitations

- Limited diversity in certain categories
- Primarily Western-centric imagery
- Indoor/studio lighting bias

---

## ⚠️ Development Status

### Pending Tasks

- [ ] Performance optimization to meet latency targets
- [ ] Bias testing and mitigation
- [ ] Security review
- [ ] Load testing
- [ ] Documentation completion

### Target Production Date

**2026-01-15** (subject to testing results)

---

## 📞 Contact

| Role | Contact |
|------|---------|
| Model Owner | ml-engineering@nuvanta-holding.com |
| Development Lead | #ml-development (Slack) |

---

**Last Updated:** 2025-12-12  
**Document Owner:** ML Engineering Lead  

[← MC-003](MC-003-code-reviewer.md) | [Back to Model Cards](README.md) | [MC-005 →](MC-005-translation-engine.md)

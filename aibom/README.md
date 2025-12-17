# AI Bill of Materials (AIBOM)

**Machine-Readable Metadata for AI Models**

> "Know what's in your models like you know what's in your software."

---

## 📋 Overview

The AI Bill of Materials (AIBOM) provides structured, machine-readable metadata for all AI models deployed in KOSMOS. AIBOMs enable supply chain transparency, compliance verification, and automated governance.

---

## 📁 Directory Structure

```
aibom/
├── production/          # Active production models
│   ├── MC-001-v2.1.0.yaml
│   ├── MC-002-v1.5.2.yaml
│   └── MC-003-v3.0.1.yaml
├── development/         # Models in development/testing
│   ├── MC-004-v0.9-beta.yaml
│   └── MC-005-v2.0-rc1.yaml
└── deprecated/          # Archived models (for audit trail)
    └── MC-000-v1.2.0.yaml
```

---

## 🔗 Related Documentation

- **[Model Cards](../docs/03-engineering/model-cards/README.md)** - Human-readable model documentation
- **[AIBOM Schema](../schemas/aibom-schema.json)** - JSON Schema for validation
- **[AIBOM Documentation](../docs/03-engineering/aibom.md)** - Full AIBOM specification

---

**Last Updated:** 2025-12-12  
**Document Owner:** ML Engineering Lead

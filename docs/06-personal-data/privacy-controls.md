# Privacy Controls

**Your Data, Your Rules**

!!! abstract "Privacy by Design"
    KOSMOS implements privacy controls that give you complete control over your data, including who can access it, how it's processed, and where it's stored.

---

## Privacy Zones

KOSMOS organizes data into four privacy zones, each with different access controls and processing rules.

```
┌─────────────────────────────────────────────────────────────┐
│                     PRIVACY ZONES                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ZONE 1: PUBLIC                                            │
│  ───────────────────────────────────────────────────────── │
│  Access: Anyone                                            │
│  Processing: Full AI, cloud-allowed                        │
│  Examples: Published content, public profiles              │
│                                                             │
│  ZONE 2: PROFESSIONAL                                      │
│  ───────────────────────────────────────────────────────── │
│  Access: Work colleagues, authenticated users              │
│  Processing: Full AI, logged                               │
│  Examples: Work documents, project files                   │
│                                                             │
│  ZONE 3: PERSONAL                                          │
│  ───────────────────────────────────────────────────────── │
│  Access: User only                                         │
│  Processing: AI with consent, local preferred              │
│  Examples: Personal notes, photos, journals                │
│                                                             │
│  ZONE 4: SENSITIVE                                         │
│  ───────────────────────────────────────────────────────── │
│  Access: Explicit unlock required                          │
│  Processing: Local only, encrypted at rest                 │
│  Examples: Medical records, financial data, passwords      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Zone Configuration

### Setting Default Zone

```yaml
# privacy-config.yaml
privacy:
  default_zone: PERSONAL
  
  auto_classification:
    enabled: true
    rules:
      - pattern: "*.medical.*"
        zone: SENSITIVE
      - pattern: "/Work/*"
        zone: PROFESSIONAL
      - pattern: "*.public.*"
        zone: PUBLIC
```

### Per-File Override

```python
# Set privacy zone for specific file
await memorix.set_privacy_zone(
    file_id="doc_123",
    zone=PrivacyZone.SENSITIVE,
    reason="Contains medical information"
)
```

---

## Access Controls

### Permission Model

| Permission | Description | Zones |
|------------|-------------|-------|
| `read` | View content | All |
| `write` | Modify content | All |
| `share` | Share with others | PUBLIC, PROFESSIONAL |
| `export` | Export outside KOSMOS | All (with logging) |
| `ai_process` | Allow AI analysis | Configurable |

### Agent Permissions

```yaml
# agent-permissions.yaml
agents:
  zeus:
    zones: [PUBLIC, PROFESSIONAL, PERSONAL]
    permissions: [read, write, ai_process]
  
  athena:
    zones: [PUBLIC, PROFESSIONAL]
    permissions: [read, ai_process]
  
  hestia:
    zones: [PERSONAL, SENSITIVE]
    permissions: [read]
    sensitive_unlock: required
```

---

## AI Processing Controls

### Opt-In/Opt-Out

```yaml
# ai-processing-config.yaml
ai_processing:
  default: opt_in
  
  per_zone:
    PUBLIC: always
    PROFESSIONAL: opt_in
    PERSONAL: opt_in
    SENSITIVE: never  # Requires explicit per-item consent
  
  excluded_file_types:
    - "*.key"
    - "*.pem"
    - "*password*"
```

### Processing Transparency

All AI processing is logged and auditable:

```json
{
  "timestamp": "2025-12-14T10:30:00Z",
  "file_id": "doc_456",
  "operation": "summarize",
  "agent": "athena",
  "model": "mistral-7b",
  "tokens_processed": 1234,
  "result_stored": false
}
```

---

## Data Minimization

### Retention Policies

```yaml
# retention-config.yaml
retention:
  default: 2555  # 7 years (days)
  
  per_category:
    cache: 7
    search_history: 90
    ai_responses: 30
    documents: 2555
    media: 3650  # 10 years
  
  per_zone:
    SENSITIVE:
      auto_delete: 365  # 1 year unless explicitly retained
      require_confirmation: true
```

### Automatic Cleanup

```bash
# Scheduled cleanup job
kubectl exec -n kosmos-data memorix-xxxxx -- \
  /app/cleanup --dry-run=false --older-than=retention
```

---

## Consent Management

### Consent Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                   CONSENT MANAGEMENT                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AI Processing                                             │
│  ☑ Allow AI to analyze my documents                        │
│  ☑ Allow AI to suggest actions                             │
│  ☐ Allow AI to learn from my patterns                      │
│                                                             │
│  Data Sharing                                              │
│  ☑ Share usage analytics (anonymized)                      │
│  ☐ Participate in model improvement                        │
│                                                             │
│  Cloud Storage                                             │
│  ☑ Sync with Google Drive                                  │
│  ☑ Sync with OneDrive                                      │
│  ☐ Sync with iCloud                                        │
│                                                             │
│  [Save Preferences]                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Consent API

```python
# Check consent before processing
if await privacy.has_consent(user_id, ConsentType.AI_PROCESSING):
    result = await athena.analyze(document)
else:
    raise PrivacyError("AI processing consent not granted")

# Request consent
await privacy.request_consent(
    user_id=user_id,
    consent_type=ConsentType.AI_LEARNING,
    reason="Improve personalization",
    expires_in_days=365
)
```

---

## Audit Trail

### Access Logging

All data access is logged:

```json
{
  "timestamp": "2025-12-14T10:30:00Z",
  "user_id": "user_123",
  "agent": "athena",
  "action": "read",
  "resource": "doc_456",
  "zone": "PERSONAL",
  "ip_address": "10.0.1.50",
  "success": true
}
```

### Audit Reports

```bash
# Generate access report
kubectl exec -n kosmos-data aegis-xxxxx -- \
  /app/audit-report --user=user_123 --days=30 --format=pdf
```

---

## Encryption

### At Rest

| Zone | Encryption | Key Management |
|------|------------|----------------|
| PUBLIC | AES-256 | Shared key |
| PROFESSIONAL | AES-256 | Org key |
| PERSONAL | AES-256 | User key |
| SENSITIVE | AES-256 + additional | User key + PIN |

### In Transit

All data encrypted with TLS 1.3, mTLS between services.

---

## Regulatory Compliance

| Regulation | Requirement | Implementation |
|------------|-------------|----------------|
| **GDPR** | Right to erasure | [Data Portability](data-portability.md) |
| **GDPR** | Data portability | Export in standard formats |
| **CCPA** | Opt-out of sale | No data sale, toggle available |
| **UAE PDPL** | Data localization | Dubai region storage |

---

## See Also

- [Personal Data Ecosystem](personal-data-ecosystem.md)
- [Data Portability](data-portability.md)
- [Security Architecture](../security/architecture.md)

---

**Last Updated:** December 2025

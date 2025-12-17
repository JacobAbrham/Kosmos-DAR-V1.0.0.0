# Data Portability

**Your Data, Anywhere You Need It**

!!! abstract "No Vendor Lock-In"
    KOSMOS guarantees your right to export all your data at any time in standard, open formats. You own your data—always.

---

## Export Capabilities

### Full Account Export

Export everything in one package:

```bash
# Request full export via CLI
kosmos export --full --format=zip --destination=/exports/

# Via API
POST /api/v1/user/export
{
  "scope": "full",
  "format": "zip",
  "include_metadata": true
}
```

### Export Contents

```
kosmos-export-20251214/
├── metadata.json           # Export metadata
├── documents/              # All documents (original formats)
│   ├── work/
│   └── personal/
├── media/                  # Photos, videos, audio
│   ├── photos/
│   └── videos/
├── communications/         # Email archives
│   └── mbox/
├── calendar/              # Calendar data
│   └── events.ics
├── contacts/              # Contact information
│   └── contacts.vcf
├── notes/                 # Notes and journals
│   └── notes.json
├── preferences/           # Settings and preferences
│   └── settings.json
├── ai_interactions/       # AI conversation history
│   └── conversations.jsonl
└── audit_log/             # Access audit trail
    └── audit.jsonl
```

---

## Export Formats

### Standard Formats

| Data Type | Primary Format | Alternative |
|-----------|---------------|-------------|
| Documents | Original (docx, pdf, etc.) | Markdown |
| Spreadsheets | Original (xlsx) | CSV |
| Photos | Original (jpg, png, heic) | - |
| Videos | Original (mp4, mkv) | - |
| Calendar | iCalendar (.ics) | JSON |
| Contacts | vCard (.vcf) | JSON |
| Email | MBOX | EML |
| Notes | Markdown | JSON |
| Conversations | JSONL | Markdown |

### Metadata Format

```json
{
  "export_version": "1.0",
  "export_date": "2025-12-14T10:30:00Z",
  "user_id": "user_123",
  "total_items": 15847,
  "total_size_bytes": 52428800000,
  "checksums": {
    "algorithm": "sha256",
    "manifest": "abc123..."
  },
  "categories": {
    "documents": 2847,
    "photos": 10234,
    "videos": 156,
    "emails": 2500,
    "notes": 110
  }
}
```

---

## Selective Export

### By Category

```python
# Export only documents
await export.create(
    categories=["documents"],
    format="zip"
)

# Export only from specific date range
await export.create(
    categories=["photos", "videos"],
    date_range={
        "start": "2025-01-01",
        "end": "2025-06-30"
    }
)
```

### By Privacy Zone

```python
# Export only personal data (exclude work)
await export.create(
    zones=[PrivacyZone.PERSONAL, PrivacyZone.SENSITIVE],
    format="zip"
)
```

### By Source

```python
# Export only Google Drive content
await export.create(
    sources=["google_drive"],
    include_metadata=True
)
```

---

## Import Capabilities

### From Other Services

| Source | Import Method | Supported Data |
|--------|---------------|----------------|
| Google Takeout | ZIP upload | All data types |
| Apple iCloud | Download + upload | Photos, documents |
| Microsoft | ZIP upload | OneDrive, Outlook |
| Dropbox | API sync | Files only |

### Import Process

```bash
# Import from Google Takeout
kosmos import --source=google-takeout --file=/imports/takeout.zip

# Via API
POST /api/v1/user/import
{
  "source": "google-takeout",
  "file_id": "upload_abc123",
  "options": {
    "merge_duplicates": true,
    "preserve_timestamps": true
  }
}
```

### Duplicate Handling

```yaml
# import-config.yaml
import:
  duplicate_handling: merge  # or "skip", "replace", "rename"
  
  merge_strategy:
    documents: content_hash  # Dedupe by content
    photos: exif_hash       # Dedupe by EXIF data
    emails: message_id      # Dedupe by Message-ID
```

---

## Data Deletion

### Right to Erasure (GDPR Article 17)

```python
# Request account deletion
await user.request_deletion(
    reason="Moving to different service",
    confirm=True
)

# Deletion process:
# 1. Export provided (optional)
# 2. 30-day grace period
# 3. Permanent deletion
# 4. Confirmation email
```

### Deletion Scope

| Data | Deleted | Retained |
|------|---------|----------|
| User content | ✅ | - |
| AI interactions | ✅ | - |
| Preferences | ✅ | - |
| Audit logs | - | 90 days (legal) |
| Anonymized analytics | - | Aggregated only |

### Deletion Verification

```json
{
  "deletion_request_id": "del_123",
  "requested_at": "2025-12-14T10:30:00Z",
  "scheduled_deletion": "2026-01-13T10:30:00Z",
  "status": "pending_grace_period",
  "items_to_delete": 15847,
  "export_link": "https://export.kosmos.nuvanta.local/abc123",
  "export_expires": "2026-01-13T10:30:00Z"
}
```

---

## Transfer to Another Service

### Authorized Transfers

```python
# Direct transfer to another service (if supported)
await export.transfer(
    destination="nextcloud",
    credentials={
        "url": "https://my.nextcloud.com",
        "username": "user",
        "app_password": "xxx"
    },
    categories=["documents", "photos"]
)
```

### Manual Transfer Process

1. **Request Export** — Full or selective
2. **Download Package** — ZIP with all data
3. **Verify Integrity** — Check SHA256 checksums
4. **Import to New Service** — Use their import tools

---

## API Reference

### Export Endpoints

```
POST   /api/v1/user/export           Create export request
GET    /api/v1/user/export/{id}      Check export status
GET    /api/v1/user/export/{id}/download  Download export
DELETE /api/v1/user/export/{id}      Cancel export
```

### Import Endpoints

```
POST   /api/v1/user/import           Create import request
GET    /api/v1/user/import/{id}      Check import status
DELETE /api/v1/user/import/{id}      Cancel import
```

### Deletion Endpoints

```
POST   /api/v1/user/deletion         Request deletion
GET    /api/v1/user/deletion/{id}    Check deletion status
DELETE /api/v1/user/deletion/{id}    Cancel deletion (grace period)
```

---

## See Also

- [Privacy Controls](privacy-controls.md)
- [Personal Data Ecosystem](personal-data-ecosystem.md)
- [Compliance Mapping](../security/compliance-mapping.md)

---

**Last Updated:** December 2025

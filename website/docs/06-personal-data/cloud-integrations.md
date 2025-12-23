# Cloud Integrations

**Connecting Your Digital Life to KOSMOS**

:::info Unified Access
    KOSMOS integrates with major cloud storage providers, enabling unified search and management across all your digital assets.

---

## Supported Providers

| Provider | Status | Features | Agent |
|----------|--------|----------|-------|
| Google Drive | ✅ Phase 1 | Full sync, search, edit | MEMORIX |
| OneDrive | 🟡 Phase 2 | Full sync, search | MEMORIX |
| iCloud | 🟡 Phase 3 | Photos, documents | MEMORIX |
| Dropbox | 🔵 Phase 4 | Full sync | MEMORIX |

---

## Google Drive Integration

### MCP Server

```yaml
# mcp-google-drive configuration
mcp_server: mcp-google-drive
version: 1.0.0
capabilities:
  - list_files
  - read_file
  - write_file
  - search
  - watch_changes
```

### OAuth Setup

1. Create Google Cloud project
2. Enable Drive API
3. Configure OAuth consent screen
4. Create OAuth 2.0 credentials
5. Add to KOSMOS secrets

```bash
# Store credentials in Infisical
infisical secrets set GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"
infisical secrets set GOOGLE_CLIENT_SECRET="xxx"
infisical secrets set GOOGLE_REFRESH_TOKEN="xxx"
```

### Sync Configuration

```yaml
# google-drive-sync.yaml
sync:
  enabled: true
  mode: selective  # or "full"
  
  include:
    - /Documents
    - /Projects
    - /Shared with me
  
  exclude:
    - /Trash
    - "*.tmp"
    - ".~*"
  
  schedule:
    full_sync: "0 2 * * *"  # Daily at 2 AM
    incremental: 300  # Every 5 minutes
  
  conflict_resolution: server_wins  # or "local_wins", "manual"
```

### Usage

```python
# Query through MEMORIX
result = await memorix.search(
    query="Q3 financial report",
    sources=["google_drive"],
    file_types=["spreadsheet", "document"]
)

# Access file
content = await memorix.get_file(
    source="google_drive",
    file_id="1abc123..."
)
```

---

## OneDrive Integration

### MCP Server

```yaml
# mcp-onedrive configuration
mcp_server: mcp-onedrive
version: 1.0.0
capabilities:
  - list_files
  - read_file
  - write_file
  - search
```

### Microsoft Graph Setup

1. Register application in Azure AD
2. Configure API permissions (Files.ReadWrite.All)
3. Create client secret
4. Store credentials

```bash
infisical secrets set MICROSOFT_CLIENT_ID="xxx"
infisical secrets set MICROSOFT_CLIENT_SECRET="xxx"
infisical secrets set MICROSOFT_TENANT_ID="xxx"
```

### Sync Configuration

```yaml
# onedrive-sync.yaml
sync:
  enabled: true
  mode: selective
  
  include:
    - /Documents
    - /Desktop
  
  schedule:
    full_sync: "0 3 * * *"
    incremental: 300
```

---

## iCloud Integration

### MCP Server

```yaml
# mcp-icloud configuration
mcp_server: mcp-icloud
version: 1.0.0
capabilities:
  - list_files
  - read_file
  - photos_access  # iCloud Photos
```

### Setup Requirements

:::warning Apple Limitations
    iCloud integration requires app-specific password and has limited API access compared to Google/Microsoft.

1. Generate app-specific password at appleid.apple.com
2. Enable two-factor authentication
3. Store credentials

```bash
infisical secrets set ICLOUD_EMAIL="user@icloud.com"
infisical secrets set ICLOUD_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"
```

### Sync Configuration

```yaml
# icloud-sync.yaml
sync:
  enabled: true
  mode: read_only  # iCloud has limited write API
  
  include:
    - /iCloud Drive/Documents
    - /Photos  # iCloud Photos library
  
  schedule:
    full_sync: "0 4 * * *"
```

---

## Dropbox Integration

### MCP Server

```yaml
# mcp-dropbox configuration (Phase 4)
mcp_server: mcp-dropbox
version: 1.0.0
capabilities:
  - list_files
  - read_file
  - write_file
  - search
  - shared_links
```

### OAuth Setup

1. Create Dropbox app at developers.dropbox.com
2. Configure permissions (files.content.read, files.content.write)
3. Generate access token

```bash
infisical secrets set DROPBOX_ACCESS_TOKEN="xxx"
infisical secrets set DROPBOX_REFRESH_TOKEN="xxx"
```

---

## Unified Search

MEMORIX provides unified search across all connected providers:

```python
# Search across all sources
results = await memorix.search(
    query="project proposal",
    sources=["google_drive", "onedrive", "local"],
    date_range={
        "after": "2025-01-01",
        "before": "2025-12-31"
    },
    limit=50
)

# Results include source information
for result in results:
    print(f"{result.title} ({result.source})")
    print(f"  Path: {result.path}")
    print(f"  Modified: {result.modified_at}")
```

---

## Sync Status Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                   CLOUD SYNC STATUS                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Google Drive    ● Connected    Last sync: 5 min ago       │
│  ─────────────────────────────────────────────────────────│
│    Files indexed: 2,847                                    │
│    Storage used: 12.3 GB                                   │
│    Pending changes: 3                                      │
│                                                             │
│  OneDrive        ● Connected    Last sync: 8 min ago       │
│  ─────────────────────────────────────────────────────────│
│    Files indexed: 1,234                                    │
│    Storage used: 5.6 GB                                    │
│    Pending changes: 0                                      │
│                                                             │
│  iCloud          ○ Disconnected                            │
│  ─────────────────────────────────────────────────────────│
│    Status: Requires re-authentication                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| Sync stuck | Rate limiting | Wait 15 min, check quotas |
| Auth expired | Token expiry | Re-authenticate via UI |
| Missing files | Exclusion rules | Check sync configuration |
| Duplicate files | Conflict resolution | Review conflict_resolution setting |

---

## See Also

- [Personal Data Ecosystem](personal-data-ecosystem)
- [Privacy Controls](privacy-controls)
- [MEMORIX Agent](../02-architecture/agents/memorix-memory)

---

**Last Updated:** December 2025

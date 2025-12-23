# Content Compliance

**Appropriate Content for Every Context**

:::info Context-Aware Filtering
    KOSMOS provides intelligent content filtering to ensure media consumption is appropriate for the current context—professional, family, or personal.

---

## Compliance Modes

### Mode Overview

| Mode | Audience | Filtering Level | Use Case |
|------|----------|-----------------|----------|
| **Corporate** | Professional | Strict | Work environment |
| **Family** | All ages | Moderate | Shared spaces |
| **Personal** | Adult | Minimal | Private use |
| **Kids** | Children | Maximum | Child-safe |

---

## Corporate Mode

For professional environments where content must be work-appropriate.

### Restrictions

```yaml
# corporate-mode.yaml
corporate_mode:
  enabled: true
  trigger:
    - work_calendar_active: true
    - location: office_network
    - manual: "Enable work mode"
  
  music:
    exclude:
      - explicit_lyrics: true
      - controversial_themes: true
      - loud_genres: [metal, punk, hardcore]
    prefer:
      - instrumental: true
      - background_friendly: true
  
  video:
    blocked_categories:
      - adult
      - violence
      - gambling
      - controversial
  
  images:
    safe_search: strict
```

### Automatic Detection

```python
# Corporate mode auto-activation
async def check_corporate_context():
    calendar = await chronos.get_current_event()
    network = await system.get_network_info()
    
    if calendar and calendar.type == "work":
        return True
    if network.ssid in OFFICE_NETWORKS:
        return True
    if datetime.now().weekday() < 5 and 9 <= datetime.now().hour < 18:
        return True  # Weekday business hours
    
    return False
```

---

## Family Mode

Safe content for mixed-age environments.

### Configuration

```yaml
# family-mode.yaml
family_mode:
  enabled: false
  trigger:
    - location: home_network
    - device: shared_tv
    - manual: "Enable family mode"
  
  ratings:
    movies: [G, PG, PG-13]
    tv: [TV-Y, TV-Y7, TV-G, TV-PG]
    music: explicit_filter_on
    games: [E, E10+, T]
  
  blocked_content:
    - adult_themes
    - excessive_violence
    - strong_language
    - drug_references
```

### Age-Appropriate Recommendations

```python
# Family-safe recommendations
recommendations = await hestia.recommend_content(
    type="movie",
    audience="family",
    preferences={
        "max_rating": "PG-13",
        "genres": user.preferences.family_genres,
        "exclude_themes": ["horror", "intense_violence"]
    }
)
```

---

## Kids Mode

Maximum protection for children.

### Strict Filtering

```yaml
# kids-mode.yaml
kids_mode:
  enabled: false
  requires_pin: true  # PIN to exit
  
  content:
    whitelist_only: true
    approved_apps: [disney_plus, pbs_kids, youtube_kids]
    approved_websites: [...whitelist...]
  
  time_limits:
    daily_max_minutes: 120
    per_session_max: 30
    break_required_minutes: 10
  
  monitoring:
    activity_log: true
    notify_parent: true
    screenshot_on_flag: false  # Privacy consideration
```

### Parental Controls

```
┌─────────────────────────────────────────────────────────────┐
│                   PARENTAL CONTROLS                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Kids Profile: Alex                                        │
│  ─────────────────────────────────────────────────────────│
│                                                             │
│  Daily Limit:         2 hours                              │
│  Today's Usage:       45 minutes                           │
│  Remaining:           1h 15m                               │
│                                                             │
│  Content Settings                                          │
│  ☑ Whitelist only                                         │
│  ☑ Safe search enforced                                   │
│  ☑ Explicit music blocked                                 │
│  ☐ YouTube allowed (currently blocked)                    │
│                                                             │
│  Bedtime:             8:00 PM                              │
│  ☑ Auto-disable after bedtime                             │
│                                                             │
│  [Edit Settings]  [View Activity]  [Add Time]             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Content Classification

### Rating Systems

| Region | System | Integrated |
|--------|--------|------------|
| US | MPAA, TV Parental | ✅ |
| UK | BBFC | ✅ |
| EU | PEGI (games) | ✅ |
| UAE | NMC | ✅ |
| Global | Common Sense Media | ✅ |

### AI Content Analysis

```yaml
# content-analysis.yaml
analysis:
  enabled: true
  
  scan_for:
    - explicit_language: true
    - violence_level: true
    - adult_themes: true
    - drug_references: true
    - gambling: true
  
  confidence_threshold: 0.85
  
  on_uncertain:
    action: flag_for_review
    default_block: true  # Err on side of caution
```

---

## Regional Compliance

### UAE Content Guidelines

```yaml
# uae-compliance.yaml
uae_mode:
  enabled: true
  
  blocked_categories:
    - gambling
    - adult_content
    - blasphemous_content
    - content_against_state
    - vpn_promotion
  
  additional_filtering:
    dating_apps: blocked
    alcohol_promotion: blocked
```

### Multi-Region Support

```python
# Adjust compliance based on location
def get_compliance_rules(location: str) -> ComplianceRules:
    base_rules = load_base_rules()
    
    regional_rules = {
        "UAE": uae_rules,
        "Saudi": saudi_rules,
        "EU": eu_rules,
        "US": us_rules
    }
    
    return base_rules.merge(regional_rules.get(location, {}))
```

---

## Override and Exceptions

### Temporary Override

```python
# Temporarily disable corporate mode
await compliance.override(
    mode="corporate",
    duration_minutes=30,
    reason="Personal break",
    requires_pin=True
)
```

### Content Exceptions

```yaml
# exceptions.yaml
exceptions:
  - content_id: "documentary_xyz"
    reason: "Educational content, approved by admin"
    approved_by: "admin@nuvanta.local"
    expiry: "2026-01-01"
```

---

## Audit and Reporting

### Compliance Log

```json
{
  "timestamp": "2025-12-14T10:30:00Z",
  "user": "user_123",
  "mode": "corporate",
  "action": "content_blocked",
  "content_type": "music",
  "reason": "explicit_lyrics",
  "content_id": "track_456"
}
```

### Reports

- Daily content filter summary
- Weekly mode activation stats
- Monthly compliance audit

---

## See Also

- [Media Management](media-management)
- [Music Curation](music-curation)
- [Privacy Controls](../06-personal-data/privacy-controls)

---

**Last Updated:** December 2025

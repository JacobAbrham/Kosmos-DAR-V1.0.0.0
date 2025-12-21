# HESTIA Personal & Media Agent

**Domain:** Personal Productivity, Preferences & Media Management  
**Symbol:** 🏠 (Hearth)  
**Status:** Active  
**Version:** 1.0.0

---

## Overview

HESTIA is the **Sanctuary Personal & Media Agent**, responsible for managing user preferences, personalization, UI adaptation, habit tracking, and comprehensive entertainment & media management. Named after the goddess of the hearth and home, HESTIA creates a personalized, comfortable digital environment for each user.

## Core Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **User Preferences** | Store and apply personal settings |
| **Personalization** | Adapt system behavior to user patterns |
| **UI Adaptation** | Customize interface based on preferences |
| **Habit Tracking** | Monitor and suggest productivity patterns |
| **Media Management** | Music, video, and content organization |
| **Entertainment Curation** | Personalized recommendations |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       HESTIA AGENT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │Preferences Mod  │  │   Media Module  │  │ Wellness Module │ │
│  │                 │  │                 │  │                 │ │
│  │ • User settings │  │ • Music curation│  │ • Habit track   │ │
│  │ • UI themes     │  │ • Content anal  │  │ • Break remind  │ │
│  │ • Shortcuts     │  │ • Playlists     │  │ • Focus modes   │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │          │
│           └────────────────────┼────────────────────┘          │
│                                │                               │
│                    ┌───────────▼───────────┐                   │
│                    │  Recommendation Eng   │                   │
│                    │  (Personalization)    │                   │
│                    └───────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
    ┌──────────┐         ┌──────────┐         ┌──────────┐
    │PostgreSQL│         │  MinIO   │         │   NATS   │
    │  (Prefs) │         │ (Media)  │         │ (Events) │
    └──────────┘         └──────────┘         └──────────┘
```

## Supported Actions

| Action | Description | Required Params | Approval |
|--------|-------------|-----------------|----------|
| `get_preferences` | Retrieve user preferences | `user_id`, `category` | Auto |
| `set_preference` | Update preference | `key`, `value` | Auto |
| `adapt_ui` | Apply UI customizations | `adaptations` | Auto |
| `track_habit` | Record habit data | `habit_type`, `data` | Auto |
| `curate_playlist` | Create music playlist | `mood`, `duration`, `genre` | Auto |
| `analyze_content` | Extract content metadata | `content_id` | Auto |
| `recommend_content` | Get personalized recommendations | `context`, `type` | Auto |
| `schedule_break` | Set wellness reminder | `interval`, `type` | Auto |

## MCP Connections

| MCP Server | Purpose | Direction |
|------------|---------|-----------|
| `mcp-postgresql` | Preference storage | Bidirectional |
| `mcp-minio` | Media file storage | Bidirectional |
| `mcp-local-filesystem` | Local media access | Inbound |
| `mcp-spotify` | Music streaming (optional) | Bidirectional |

## Wellness Features

### Focus Mode

```python
async def enable_focus_mode(
    duration: int = 25,
    mode_type: str = "pomodoro"
) -> FocusSession:
    """Enable distraction-free focus mode."""
    
    session = FocusSession(
        duration=duration,
        mode_type=mode_type,
        started_at=datetime.utcnow()
    )
    
    # Suppress non-critical notifications
    await notification_manager.set_mode("focus", duration)
    
    # Minimize UI distractions
    await ui_manager.enable_focus_mode()
    
    # Optional: Start focus music
    if await get_preference("focus_music_enabled"):
        playlist = await music_curator.create_playlist(
            mood="focus",
            duration=duration
        )
        await media_player.play(playlist)
    
    return session
```

## Configuration

```yaml
# hestia-config.yaml
agent:
  name: hestia
  version: "1.0.0"
  icon: "🏠"
  
preferences:
  sync_enabled: true
  sync_interval: 300  # 5 minutes
  history_retention_days: 90
  
media:
  supported_audio: [mp3, flac, wav, m4a, ogg]
  supported_video: [mp4, mkv, avi, mov]
  library_scan_interval: 3600  # 1 hour
  
wellness:
  default_break_interval: 90  # minutes
  default_break_duration: 5   # minutes
  focus_mode_default: 25      # minutes (Pomodoro)
  fatigue_detection: true
```

## Monitoring

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `hestia_preferences_updates` | Preference change count | N/A |
| `hestia_focus_sessions` | Focus mode sessions | N/A |
| `hestia_break_compliance` | Break taken vs scheduled | < 50% |
| `hestia_playlist_satisfaction` | User rating of playlists | < 3.5/5 |

---

## See Also

- [Personal Data Ecosystem](../../06-personal-data/personal-data-ecosystem.md) — Data integration
- [Entertainment & Media](../../07-entertainment/media-management.md) — Media features
- [UI/UX Guidelines](../../05-human-factors/ui-ux-guidelines.md) — Interface design

---

**Last Updated:** December 2025


## Auto-Detected Tools

| Tool Name | Status | Source |
|-----------|--------|--------|
| `adapt_ui` | Active | `src/agents/hestia/main.py` |
| `curate_playlist` | Active | `src/agents/hestia/main.py` |
| `enable_focus_mode` | Active | `src/agents/hestia/main.py` |
| `evaluate_proposal` | Active | `src/agents/hestia/main.py` |
| `get_preferences` | Active | `src/agents/hestia/main.py` |
| `process_query` | Active | `src/agents/hestia/main.py` |
| `set_preference` | Active | `src/agents/hestia/main.py` |
| `track_habit` | Active | `src/agents/hestia/main.py` |

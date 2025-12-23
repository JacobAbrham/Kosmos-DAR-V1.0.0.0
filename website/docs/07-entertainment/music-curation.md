# Music Curation

**Intelligent Music Management for Your Digital Life**

:::info AI-Powered Playlists
    KOSMOS uses AI to understand your music preferences, automatically organize your library, and create context-aware playlists.

---

## Features Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MUSIC FEATURES                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🎵 Library Management                                     │
│     • Auto-tagging (genre, mood, energy)                   │
│     • Duplicate detection                                  │
│     • Missing metadata completion                          │
│     • Album art retrieval                                  │
│                                                             │
│  📋 Smart Playlists                                        │
│     • Mood-based generation                                │
│     • Activity-aware suggestions                           │
│     • Time-of-day optimization                             │
│     • Cross-source unification                             │
│                                                             │
│  🔊 Playback Integration                                   │
│     • Multi-room support                                   │
│     • Queue management                                     │
│     • Listening history                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Library Organization

### Supported Formats

| Format | Quality | Metadata |
|--------|---------|----------|
| FLAC | Lossless | Full |
| ALAC | Lossless | Full |
| WAV | Lossless | Limited |
| MP3 | 320kbps max | Full |
| AAC/M4A | 256kbps max | Full |
| OGG | Variable | Full |

### Auto-Tagging

```yaml
# music-tagging-config.yaml
tagging:
  enabled: true
  
  sources:
    - musicbrainz
    - acoustid
    - lastfm
  
  auto_tag:
    genre: true
    mood: true
    energy_level: true
    bpm: true
    key: true
  
  metadata_completion:
    artist: true
    album: true
    year: true
    track_number: true
    album_art: true
```

### Mood Classification

| Mood | Characteristics | Example Genres |
|------|-----------------|----------------|
| Energetic | High BPM, major key | Pop, EDM, Rock |
| Relaxed | Low BPM, soft dynamics | Jazz, Ambient, Acoustic |
| Focused | Minimal vocals, steady rhythm | Lo-fi, Classical, Electronic |
| Melancholic | Minor key, slow tempo | Indie, Blues, Singer-songwriter |
| Uplifting | Major key, building dynamics | Pop, Orchestral, House |

---

## Smart Playlists

### Context-Aware Generation

```python
# Request playlist from HESTIA
playlist = await hestia.create_playlist(
    context={
        "activity": "working",
        "time_of_day": "afternoon",
        "energy_preference": "moderate",
        "duration_minutes": 60
    },
    exclude_recent=True,  # Don't repeat recent plays
    variety_level="medium"
)
```

### Activity Presets

| Activity | Characteristics | Example Rules |
|----------|-----------------|---------------|
| Focus Work | No lyrics, steady BPM | `mood:focused AND vocals:instrumental` |
| Exercise | High energy, 120-150 BPM | `energy:high AND bpm:120-150` |
| Morning | Gentle, building energy | `mood:uplifting AND energy:low-medium` |
| Evening | Relaxing, winding down | `mood:relaxed AND energy:low` |
| Social | Crowd-pleasers, varied | `popularity:high AND energy:medium-high` |

### Dynamic Playlists

```yaml
# dynamic-playlist-config.yaml
playlists:
  - name: "Daily Mix"
    type: dynamic
    refresh: daily
    rules:
      - recently_played: exclude_24h
      - favorites_ratio: 0.3
      - discovery_ratio: 0.2
      - similar_to_recent: 0.5
  
  - name: "Work Focus"
    type: context
    trigger:
      calendar_event_type: "focus_time"
    rules:
      - mood: focused
      - vocals: instrumental
      - energy: low-medium
```

---

## Cross-Source Integration

### Unified Library

```
┌─────────────────────────────────────────────────────────────┐
│                  UNIFIED MUSIC LIBRARY                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Local Files     ────────┐                                 │
│  (MinIO)                 │                                 │
│                          ▼                                 │
│  Spotify         ───► MEMORIX ───► Unified Index          │
│  (via API)              Music                              │
│                          ▲                                 │
│  YouTube Music   ────────┘                                 │
│  (via API)                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Source Priority

```yaml
# source-priority.yaml
playback_priority:
  1: local_flac      # Highest quality
  2: local_mp3       # Local fallback
  3: spotify         # Streaming
  4: youtube_music   # Last resort
```

---

## Playback Control

### Queue Management

```python
# Add to queue
await music.add_to_queue(track_id="track_123", position="next")

# Get current queue
queue = await music.get_queue()

# Shuffle queue
await music.shuffle_queue()

# Clear queue
await music.clear_queue()
```

### Multi-Room Audio

```yaml
# multi-room-config.yaml
rooms:
  - name: "Living Room"
    device: sonos_living
    default_volume: 40
  
  - name: "Office"
    device: homepod_office
    default_volume: 30
  
  - name: "Kitchen"
    device: echo_kitchen
    default_volume: 50

groups:
  - name: "Whole House"
    rooms: [living_room, office, kitchen]
```

---

## Listening Insights

### Statistics Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                   LISTENING STATS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  This Week                                                 │
│  ─────────────────────────────────────────────────────────│
│  Total listening time:    12h 34m                          │
│  Unique tracks:           187                              │
│  Top genre:               Electronic (34%)                 │
│  Peak listening:          2-4 PM                           │
│                                                             │
│  Top Artists                                               │
│  ─────────────────────────────────────────────────────────│
│  1. Tycho                 2h 15m                           │
│  2. Bonobo                1h 48m                           │
│  3. Khruangbin            1h 22m                           │
│                                                             │
│  Mood Distribution                                         │
│  ─────────────────────────────────────────────────────────│
│  Focused   ████████████░░░░░░░░ 58%                       │
│  Relaxed   ████████░░░░░░░░░░░░ 28%                       │
│  Energetic ███░░░░░░░░░░░░░░░░░ 14%                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Voice Commands

| Command | Action |
|---------|--------|
| "Play some focus music" | Start focus playlist |
| "What's playing?" | Announce current track |
| "Skip this" | Next track |
| "Play more like this" | Generate similar playlist |
| "Add to favorites" | Save current track |
| "Play in living room" | Switch output device |

---

## See Also

- [Media Management](media-management)
- [Content Compliance](content-compliance)
- [Hestia Personal Agent](../02-architecture/agents/hestia-personal)

---

**Last Updated:** December 2025

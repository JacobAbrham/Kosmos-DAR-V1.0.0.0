# Entertainment & Media Management

!!! abstract "Digital Life Entertainment"
    KOSMOS manages entertainment and media as an integral part of the Digital Life OS, enabling intelligent curation, organization, and playback across all media types.

## Overview

The Entertainment domain covers music, video, podcasts, and other media content, with AI-powered curation and cross-platform management.

## Media Types

| Type | Supported Formats | Agent Owner |
|------|-------------------|-------------|
| Music | MP3, FLAC, WAV, M4A, OGG | HESTIA |
| Video | MP4, MKV, AVI, MOV | HESTIA |
| Podcasts | RSS feeds, downloaded audio | HESTIA |
| Audiobooks | M4B, MP3 chapters | HESTIA |
| Photos | JPG, PNG, RAW, HEIC | MEMORIX |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEDIA MANAGEMENT STACK                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    HESTIA AGENT                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │Music Curator│  │Video Manager│  │Podcast Agent│      │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │  │
│  │         │                │                │              │  │
│  │         └────────────────┼────────────────┘              │  │
│  │                          │                               │  │
│  └──────────────────────────┼───────────────────────────────┘  │
│                             │                                  │
│                    ┌────────▼────────┐                        │
│                    │  Media Library  │                        │
│                    │    (MinIO)      │                        │
│                    └────────┬────────┘                        │
│                             │                                  │
│              ┌──────────────┼──────────────┐                  │
│              │              │              │                   │
│              ▼              ▼              ▼                   │
│        ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│        │ Metadata │  │ Playlists│  │ Playback │              │
│        │PostgreSQL│  │PostgreSQL│  │  State   │              │
│        └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Music Curation

### Features

| Feature | Description |
|---------|-------------|
| **Smart Playlists** | AI-generated based on mood, activity, time |
| **Genre Detection** | Automatic genre classification |
| **Mood Tagging** | Energy, valence, tempo analysis |
| **Duplicate Detection** | Find and merge duplicate tracks |
| **Missing Metadata** | Auto-fill artist, album, artwork |

### Playlist Types

| Type | Generation Method |
|------|-------------------|
| Focus | Low-distraction, instrumental-heavy |
| Energize | High-tempo, motivational |
| Relax | Calm, ambient |
| Commute | Time-based, varied |
| Workout | BPM-matched progression |
| Custom | User-defined rules |

## Video Management

### Features

| Feature | Description |
|---------|-------------|
| **Auto-Organization** | Sort by type, date, content |
| **Scene Detection** | Chapter markers for long videos |
| **Content Tagging** | AI-detected objects, people, places |
| **Watch Progress** | Resume across devices |
| **Collections** | Automatic series grouping |

## Podcast Management

### Features

| Feature | Description |
|---------|-------------|
| **Feed Aggregation** | Centralized podcast feeds |
| **Episode Transcription** | Searchable transcripts |
| **Smart Queues** | Priority-based playback order |
| **Highlights** | Mark and export key segments |

## Storage Architecture

### MinIO Bucket Structure

```
kosmos-media/
├── music/
│   ├── library/
│   │   └── {artist}/{album}/{track}.flac
│   ├── playlists/
│   │   └── {playlist_id}.json
│   └── artwork/
│       └── {album_id}.jpg
├── video/
│   ├── library/
│   │   └── {title}/{quality}.mp4
│   └── thumbnails/
│       └── {video_id}.jpg
├── podcasts/
│   ├── episodes/
│   │   └── {show}/{episode}.mp3
│   └── transcripts/
│       └── {episode_id}.txt
└── photos/
    ├── originals/
    │   └── {year}/{month}/{filename}.jpg
    └── thumbnails/
        └── {photo_id}_thumb.jpg
```

## Configuration

```yaml
# media-config.yaml
library:
  music:
    formats: [mp3, flac, wav, m4a, ogg]
    auto_organize: true
    duplicate_detection: true
    
  video:
    formats: [mp4, mkv, avi, mov]
    thumbnail_generation: true
    scene_detection: true
    
  podcasts:
    auto_download: true
    transcription: true
    retention_days: 30

playback:
  default_quality: "high"
  crossfade: 2  # seconds for music
  
curation:
  smart_playlists: true
  mood_detection: true
  
compliance:
  content_filtering: true
  corporate_mode: false
```

---

## See Also

- [HESTIA Agent](../02-architecture/agents/hestia-personal.md) — Personal agent
- [Personal Data Ecosystem](../06-personal-data/personal-data-ecosystem.md) — Data integration

---

**Last Updated:** December 2025

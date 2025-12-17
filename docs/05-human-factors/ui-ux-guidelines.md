# UI/UX Guidelines

!!! info "16-Hour Operational Design"
    KOSMOS interfaces are designed for sustained 16-hour operational use, prioritizing ergonomics, reduced fatigue, and accessibility.

## Design Principles

### Core Principles

1. **Clarity over complexity** — Information hierarchy over feature density
2. **Progressive disclosure** — Show only what's needed, when needed
3. **Consistent patterns** — Predictable interactions reduce cognitive load
4. **Keyboard-first** — Power users shouldn't need a mouse
5. **Accessibility-native** — A11y is not an afterthought

## Ergonomic Design

### Color Temperature

| Time of Day | Temperature | Rationale |
|-------------|-------------|-----------|
| 6:00 - 12:00 | Neutral (5500K) | Morning alertness |
| 12:00 - 18:00 | Neutral (5500K) | Productivity hours |
| 18:00 - 22:00 | Warm (4500K) | Reduced eye strain |
| 22:00 - 6:00 | Very Warm (3500K) | Minimal blue light |

### Break Scheduling

| Session Duration | Break Type | Duration |
|------------------|------------|----------|
| 25 minutes | Micro-break | 5 minutes |
| 90 minutes | Short break | 10 minutes |
| 4 hours | Extended break | 30 minutes |

## Nexus Dashboard

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER                                                         │
│  ┌─────────┐ ┌──────────────────────────────┐ ┌─────────────┐  │
│  │  Logo   │ │     K-Palette (Cmd+K)        │ │   Profile   │  │
│  └─────────┘ └──────────────────────────────┘ └─────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MAIN CONTENT                                                   │
│  ┌─────────────────────────────────────────┐ ┌───────────────┐ │
│  │                                         │ │               │ │
│  │            AGENT FEED                   │ │   DECISION    │ │
│  │                                         │ │    INBOX      │ │
│  │   Real-time agent activity stream       │ │               │ │
│  │                                         │ │   Pending     │ │
│  │                                         │ │   approvals   │ │
│  └─────────────────────────────────────────┘ └───────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### K-Palette (Cmd+K)

The K-Palette is the primary command interface, providing instant access to all KOSMOS functions.

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open K-Palette | Cmd+K |
| New Task | Cmd+N |
| Search | Cmd+F |
| Decision Inbox | Cmd+I |
| Settings | Cmd+, |
| Agent Focus | Cmd+1-9 |
| Help | Cmd+? |

## Accessibility

### WCAG 2.1 AA Compliance

| Requirement | Implementation |
|-------------|----------------|
| Color contrast | 4.5:1 minimum (7:1 for important text) |
| Keyboard navigation | Full tab support, visible focus states |
| Screen readers | ARIA labels, live regions |
| Motion | Reduced motion preference respected |
| Text scaling | Support 200% zoom |

## Responsive Design

### Breakpoints

| Breakpoint | Width | Target |
|------------|-------|--------|
| Mobile | < 640px | Phone |
| Tablet | 640px - 1024px | Tablet |
| Desktop | 1024px - 1440px | Laptop |
| Wide | > 1440px | Desktop |

### Touch Targets

- Minimum touch target: 44x44px
- Spacing between targets: 8px minimum
- Mobile-first interaction design

## Configuration

```yaml
# ui-config.yaml
theme:
  default: "dark"
  auto_switch: true  # Based on system preference
  
ergonomics:
  color_temperature:
    enabled: true
    schedule: "automatic"  # Based on time
    
  break_reminders:
    enabled: true
    pomodoro: 25
    long_break_interval: 4

accessibility:
  high_contrast: false
  reduced_motion: "system"  # Respect system preference
  font_scaling: 1.0
```

---

## See Also

- [HESTIA Agent](../02-architecture/agents/hestia-personal.md) — Personalization
- [Philosophy](../00-executive/philosophy.md) — Human-agent harmony

---

**Last Updated:** December 2025

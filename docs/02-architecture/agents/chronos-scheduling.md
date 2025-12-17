# Chronos Scheduling Agent

**Domain:** Scheduling, Calendar & Temporal Operations  
**Greek Deity:** Chronos - God of Time  
**Status:** Active  
**Version:** 1.0.0

---

## Overview

Chronos is the **scheduling and time management** agent, handling calendar operations, meeting scheduling, reminders, and temporal queries. Named after the god of time, Chronos coordinates all time-sensitive operations within KOSMOS.

### Key Capabilities

- **Meeting Scheduling** - Find available times, create meetings
- **Calendar Management** - View, create, update calendar events
- **Reminder System** - Set and trigger reminders
- **Availability Queries** - Check user/resource availability
- **Timezone Handling** - Proper timezone conversions

### Supported Actions

| Action | Description | Required Params |
|--------|-------------|-----------------|
| `schedule_meeting` | Create calendar event | `title`, `attendees`, `duration` |
| `find_availability` | Find free time slots | `attendees`, `duration`, `range` |
| `set_reminder` | Create reminder | `message`, `trigger_time` |
| `get_calendar` | Retrieve calendar events | `user_id`, `start`, `end` |

### MCP Connections

| MCP Server | Purpose |
|------------|---------|
| calendar-mcp | Google/Outlook calendar integration |
| scheduler-mcp | Cron-based scheduling |

---

**Last Updated:** 2025-12-12  
**Document Owner:** Chief Architect

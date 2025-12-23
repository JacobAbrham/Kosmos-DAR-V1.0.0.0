# Hermes Communications Agent

**Domain:** Communications, Messaging & Notifications  
**Greek Deity:** Hermes - Messenger of the Gods  
**Status:** Active  
**Version:** 1.1.0

---

## Overview

Hermes is the **communications** agent of KOSMOS, responsible for all outbound messaging across channels including email, Slack, SMS, and push notifications. Named after the messenger god, Hermes ensures messages are delivered reliably and formatted appropriately for each channel.

### Key Capabilities

- **Multi-channel Messaging** - Send via email, Slack, SMS, push
- **Template Management** - Render dynamic message templates
- **Delivery Tracking** - Monitor message delivery status
- **Rate Limiting** - Respect channel rate limits
- **Preference Management** - Honor user notification preferences

### Supported Actions

| Action | Description | Required Params |
|--------|-------------|-----------------|
| `send_email` | Send email message | `to`, `subject`, `body` |
| `send_slack` | Post Slack message | `channel`, `message` |
| `send_sms` | Send SMS message | `phone`, `message` |
| `send_notification` | Push notification | `user_id`, `title`, `body` |
| `check_status` | Check delivery status | `message_id` |

### MCP Connections

| MCP Server | Purpose |
|------------|---------|
| slack-mcp | Slack API integration |
| email-mcp | SMTP/API email sending |

---

**Last Updated:** 2025-12-12  
**Document Owner:** Chief Architect


## Auto-Detected Tools

| Tool Name | Status | Source |
|-----------|--------|--------|
| `evaluate_proposal` | Active | `src/agents/hermes/main.py` |
| `send_email` | Active | `src/agents/hermes/main.py` |
| `send_notification` | Active | `src/agents/hermes/main.py` |
| `send_slack` | Active | `src/agents/hermes/main.py` |
| `send_sms` | Active | `src/agents/hermes/main.py` |

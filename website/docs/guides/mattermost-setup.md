# Mattermost Setup Guide for KOSMOS

This guide walks you through setting up Mattermost notifications for KOSMOS.

## Quick Start

### 1. Start Mattermost with Docker Compose

```powershell
# Start all services including Mattermost
docker-compose -f config/environments/development/docker-compose.yml up -d mattermost

# Check Mattermost is running
docker-compose -f config/environments/development/docker-compose.yml ps mattermost
```

### 2. Access Mattermost

Open your browser and navigate to: **http://localhost:8065**

### 3. Initial Setup

1. **Create Admin Account**
   - Email: `admin@kosmos.local`
   - Username: `admin`
   - Password: (your secure password)

2. **Create Team**
   - Team Name: `kosmos-team`
   - Team URL: `kosmos-team`

3. **Create Channels**
   - `#deployments` - For CI/CD notifications
   - `#agent-activity` - For agent event notifications
   - `#alerts` - For system alerts

### 4. Create Incoming Webhook

1. Go to **Main Menu** → **Integrations** → **Incoming Webhooks**
2. Click **Add Incoming Webhook**
3. Configure:
   - **Title**: KOSMOS Notifications
   - **Description**: Automated notifications from KOSMOS system
   - **Channel**: #deployments
   - **Lock to this channel**: No (allows posting to any channel)
4. Click **Save**
5. **Copy the Webhook URL** - you'll need this for GitHub Secrets

### 5. Configure GitHub Secrets

Add the webhook URL to your GitHub repository secrets:

```bash
# Go to: https://github.com/JacobAbrham/Kosmos-DAR-V1.0.0.0/settings/secrets/actions
# Add new secret:
# Name: MATTERMOST_WEBHOOK_URL
# Value: http://your-mattermost-url:8065/hooks/xxxxxxxxxxxxx
```

### 6. Update Local Environment

```bash
# Edit .env file
MATTERMOST_ENABLED=true
MATTERMOST_URL=http://localhost:8065
MATTERMOST_WEBHOOK_URL=http://localhost:8065/hooks/xxxxxxxxxxxxx
MATTERMOST_CHANNEL=deployments
```

## Testing Notifications

### Test from Python

```python
import asyncio
from src.integrations.notifications import get_mattermost_client

async def test_notification():
    client = get_mattermost_client(webhook_url="YOUR_WEBHOOK_URL")
    
    # Test simple message
    from src.integrations.notifications import MattermostMessage
    message = MattermostMessage(
        text="🎉 KOSMOS is now connected to Mattermost!",
        channel="deployments"
    )
    await client.send_message(message)
    
    # Test deployment notification
    await client.send_deployment_notification(
        environment="development",
        status="success",
        repository="Kosmos-DAR-V1.0.0.0",
        branch="master",
        commit="abc123",
        author="admin"
    )

# Run test
asyncio.run(test_notification())
```

### Test from CLI

```bash
# Test webhook directly
curl -X POST http://localhost:8065/hooks/YOUR_WEBHOOK_ID \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "✅ Test notification from KOSMOS",
    "channel": "deployments",
    "username": "KOSMOS Bot",
    "icon_emoji": ":rocket:"
  }'
```

## Notification Types

### Deployment Notifications
- ✅ Success (green)
- ❌ Failure (red)  
- ⚠️ Rollback (orange)
- ⏳ Pending (yellow)

### Agent Notifications
- 🚀 Task Started
- ✅ Task Completed
- ❌ Task Failed
- ⚠️ Warning
- ℹ️ Info

## Troubleshooting

### Webhook Not Working

1. **Check webhook URL is correct**
   ```bash
   echo $MATTERMOST_WEBHOOK_URL
   ```

2. **Test webhook manually**
   ```bash
   curl -X POST $MATTERMOST_WEBHOOK_URL -d '{"text":"test"}'
   ```

3. **Check Mattermost logs**
   ```bash
   docker-compose -f config/environments/development/docker-compose.yml logs mattermost
   ```

### Messages Not Appearing

1. **Verify channel exists**: Messages will fail silently if channel doesn't exist
2. **Check webhook permissions**: Ensure webhook can post to target channel
3. **Enable integrations**: System Console → Integrations → Enable Incoming Webhooks

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose -f config/environments/development/docker-compose.yml ps postgres

# Check Mattermost can connect
docker-compose -f config/environments/development/docker-compose.yml logs mattermost | grep -i "database"
```

## Production Deployment

For production, use HTTPS and proper authentication:

1. **Use HTTPS webhook URLs**
2. **Store webhook URL in secrets manager**
3. **Restrict webhook IP access** in Mattermost settings
4. **Enable rate limiting** to prevent abuse
5. **Monitor webhook usage** in Mattermost analytics

## References

- [Mattermost Webhook Documentation](https://developers.mattermost.com/integrate/webhooks/incoming/)
- [Message Formatting](https://docs.mattermost.com/developer/message-attachments.html)

# Zeus Conversation Recovery Runbook

**Last Updated:** 2025-12-13

## Overview

Procedures for recovering Zeus orchestration conversation state after failures.

## Conversation State Storage

Zeus stores conversation state in:
- Redis (active sessions)
- PostgreSQL (conversation history)
- S3 (archived conversations)

## Recovery Procedures

### 1. Recover Active Conversation

```bash
# List active sessions
kubectl exec -it redis-cluster-0 -n kosmos -- \
  redis-cli KEYS "zeus:conversation:*"

# Export conversation state
kubectl exec -it redis-cluster-0 -n kosmos -- \
  redis-cli GET "zeus:conversation:${CONVERSATION_ID}" > conversation_backup.json

# Restore conversation state
kubectl exec -it redis-cluster-0 -n kosmos -- \
  redis-cli SET "zeus:conversation:${CONVERSATION_ID}" "$(cat conversation_backup.json)"
```

### 2. Recover from Database

```bash
# Query conversation history
kubectl exec -it postgres-0 -n kosmos -- psql -U kosmos -c \
  "SELECT * FROM conversations WHERE id='${CONVERSATION_ID}';"

# Restore conversation to Redis
python scripts/restore_conversation.py --id ${CONVERSATION_ID}
```

### 3. Recover from Archive

```bash
# List archived conversations
aws s3 ls s3://kosmos-conversations/archive/

# Download and restore
aws s3 cp s3://kosmos-conversations/archive/${CONVERSATION_ID}.json .
python scripts/restore_conversation.py --file ${CONVERSATION_ID}.json
```

## Conversation Replay

```bash
# Replay conversation from checkpoint
curl -X POST https://api.kosmos.internal/zeus/replay \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "'${CONVERSATION_ID}'",
    "from_step": 5
  }'
```

## Validation

```bash
# Verify conversation state
curl https://api.kosmos.internal/zeus/conversation/${CONVERSATION_ID}/status

# Check conversation integrity
python scripts/validate_conversation.py --id ${CONVERSATION_ID}
```

## Related Documentation

- [Zeus Architecture](../../02-architecture/agents/zeus-orchestrator)
- [Agent Recovery](agent-recovery)

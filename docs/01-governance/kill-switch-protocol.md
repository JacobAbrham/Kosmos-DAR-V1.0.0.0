# Kill Switch Protocol

!!! danger "Emergency Intervention"
    The Kill Switch Protocol provides immediate human override capability at any point in KOSMOS operations, ensuring meaningful human control over AI agent activities.

## Protocol Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    KILL SWITCH LEVELS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  LEVEL 1: AGENT                                                │
│  ├── Stops single agent                                        │
│  ├── Other agents continue                                     │
│  └── Automatic recovery possible                               │
│                                                                 │
│  LEVEL 2: SUBSYSTEM                                            │
│  ├── Stops related agent group                                 │
│  ├── Core services continue                                    │
│  └── Manual restart required                                   │
│                                                                 │
│  LEVEL 3: SYSTEM                                               │
│  ├── Full KOSMOS halt                                          │
│  ├── Only infrastructure remains                               │
│  └── Full restart procedure required                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Activation Methods

### 1. Dashboard Button

Primary method via Nexus Dashboard.

### 2. CLI Command

```bash
# Agent-level kill
kosmos kill --level agent --target hermes --reason "erratic behavior"

# Subsystem-level kill
kosmos kill --level subsystem --target knowledge --reason "data corruption"

# System-level kill
kosmos kill --level system --reason "security incident"
```

### 3. API Endpoint

```bash
curl -X POST https://kosmos.nuvanta.local/api/v1/kill-switch \
  -H "Authorization: Bearer $OPERATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "agent",
    "target": "hermes",
    "reason": "suspected compromise",
    "operator": "alpha"
  }'
```

## Authorization Requirements

| Level | Required Authorization |
|-------|----------------------|
| Agent | Operator Alpha OR Operator Beta |
| Subsystem | Operator Alpha OR Operator Beta |
| System | Operator Alpha AND confirmation |

## Kill Switch Execution

### Agent Level

```python
async def kill_agent(agent_name: str, reason: str, operator: str):
    """Stop a specific agent immediately."""
    
    # 1. Log the action
    await audit_log.critical(
        event="kill_switch_agent",
        target=agent_name,
        reason=reason,
        operator=operator
    )
    
    # 2. Send NATS halt signal
    await nats.publish(
        subject=f"agent.{agent_name}.halt",
        payload={
            "command": "halt",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    # 3. Update agent state in PostgreSQL
    await db.execute("""
        UPDATE agent_state 
        SET status = 'halted', halted_at = NOW(), halt_reason = $1
        WHERE agent_name = $2
    """, reason, agent_name)
    
    # 4. Notify operators
    await notify_operators(
        severity="critical",
        message=f"Agent {agent_name} halted: {reason}"
    )
```

## Recovery Procedures

### Agent Recovery

```bash
# 1. Review halt reason
kosmos agent status hermes

# 2. Check logs for issues
kosmos logs hermes --since 1h

# 3. Clear halt state
kosmos agent clear-halt hermes

# 4. Restart agent
kosmos agent start hermes

# 5. Verify operation
kosmos agent health hermes
```

### System Recovery

```bash
# 1. Review system state
kosmos system status

# 2. Check for unresolved issues
kosmos audit review --type halt

# 3. Clear system halt
kosmos system clear-halt --confirm

# 4. Execute boot sequence
kosmos system boot

# 5. Verify all agents
kosmos agents health --all
```

## Audit Trail

Every kill switch activation is permanently logged:

```sql
CREATE TABLE kill_switch_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    level VARCHAR(20) NOT NULL,
    target VARCHAR(100),
    reason TEXT NOT NULL,
    operator VARCHAR(100) NOT NULL,
    recovery_timestamp TIMESTAMPTZ,
    recovery_operator VARCHAR(100),
    
    CONSTRAINT valid_level CHECK (
        level IN ('agent', 'subsystem', 'system')
    )
);

-- Immutable - no updates or deletes allowed
REVOKE UPDATE, DELETE ON kill_switch_log FROM ALL;
```

## Testing

### Monthly Drill

```bash
# Run kill switch drill (non-destructive)
kosmos drill kill-switch --level agent --target hermes --dry-run

# Verify response time
kosmos drill report --last
```

### Success Criteria

| Metric | Target |
|--------|--------|
| Activation time | < 5 seconds |
| Agent halt confirmation | < 10 seconds |
| System halt confirmation | < 30 seconds |
| Operator notification | < 1 minute |

---

## See Also

- [AEGIS Security Agent](../02-architecture/agents/aegis-security.md) — Kill switch implementation
- [Pentarchy Governance](pentarchy-governance.md) — Governance framework
- [Incident Response](../04-operations/incident-response.md) — Response procedures

---

**Last Updated:** December 2025

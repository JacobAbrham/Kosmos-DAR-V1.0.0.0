# Falco Runtime Security

**Real-time Threat Detection for Kubernetes**

!!! abstract "Runtime Protection"
    Falco monitors syscalls and Kubernetes audit logs to detect anomalous behavior in real-time, providing the runtime security layer for KOSMOS.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FALCO ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Falco DaemonSet                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │  eBPF Probe │  │   Rules     │  │   Outputs   │  │   │
│  │  │  (syscalls) │  │   Engine    │  │   (alerts)  │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │   │
│  │         │                │                │         │   │
│  │         └────────────────┼────────────────┘         │   │
│  │                          │                          │   │
│  │              ┌───────────▼───────────┐             │   │
│  │              │    Event Processor    │             │   │
│  │              └───────────────────────┘             │   │
│  └──────────────────────────┬──────────────────────────┘   │
│                             │                              │
│           ┌─────────────────┼─────────────────┐           │
│           ▼                 ▼                 ▼           │
│     ┌─────────┐       ┌─────────┐       ┌─────────┐      │
│     │ SigNoz  │       │  Slack  │       │  AEGIS  │      │
│     │  Logs   │       │ Alerts  │       │  Agent  │      │
│     └─────────┘       └─────────┘       └─────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Helm Installation

```bash
# Add Falco Helm repo
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update

# Install Falco with eBPF driver
helm install falco falcosecurity/falco \
  --namespace kosmos-system \
  --set driver.kind=ebpf \
  --set falcosidekick.enabled=true \
  --values falco-values.yaml
```

### `falco-values.yaml`

```yaml
driver:
  kind: ebpf
  ebpf:
    hostNetwork: true

resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

falcosidekick:
  enabled: true
  config:
    slack:
      webhookurl: "${SLACK_WEBHOOK_URL}"
      channel: "#kosmos-security"
      minimumpriority: "warning"
    
    webhook:
      address: "http://aegis-agent.kosmos-agents:8080/falco"
      minimumpriority: "notice"

customRules:
  kosmos-rules.yaml: |-
    # KOSMOS-specific rules included below
```

---

## KOSMOS-Specific Rules

### Agent Container Rules

```yaml
# falco-rules/kosmos-agents.yaml
- rule: KOSMOS Agent Shell Spawn
  desc: Detect shell spawned in KOSMOS agent containers
  condition: >
    spawned_process and
    container and
    container.image.repository contains "kosmos" and
    proc.name in (shell_binaries)
  output: >
    Shell spawned in KOSMOS agent 
    (user=%user.name container=%container.name 
    shell=%proc.name parent=%proc.pname)
  priority: WARNING
  tags: [kosmos, shell, container]

- rule: KOSMOS Agent Network Connection
  desc: Detect unexpected outbound connections from agents
  condition: >
    outbound and
    container.image.repository contains "kosmos" and
    not (
      fd.sip in (trusted_ips) or
      fd.sport in (allowed_ports)
    )
  output: >
    Unexpected network connection from KOSMOS agent
    (container=%container.name connection=%fd.name)
  priority: NOTICE
  tags: [kosmos, network]

- rule: KOSMOS Sensitive File Access
  desc: Detect access to sensitive files in agent containers
  condition: >
    open_read and
    container.image.repository contains "kosmos" and
    (fd.name startswith /etc/shadow or
     fd.name startswith /etc/passwd or
     fd.name contains "secret" or
     fd.name contains "credential")
  output: >
    Sensitive file accessed in KOSMOS agent
    (file=%fd.name container=%container.name)
  priority: WARNING
  tags: [kosmos, filesystem, sensitive]
```

### MCP Server Rules

```yaml
# falco-rules/kosmos-mcp.yaml
- rule: MCP Server Unauthorized Tool Call
  desc: Detect MCP tools being called outside normal flow
  condition: >
    spawned_process and
    container.image.repository contains "mcp-" and
    not proc.pname in (node, python3)
  output: >
    Unauthorized process in MCP server
    (container=%container.name proc=%proc.name)
  priority: CRITICAL
  tags: [kosmos, mcp, unauthorized]

- rule: MCP Database Direct Access
  desc: Detect direct database access bypassing MCP
  condition: >
    outbound and
    fd.sport = 5432 and
    not container.image.repository contains "mcp-database"
  output: >
    Direct database access attempt (container=%container.name)
  priority: WARNING
  tags: [kosmos, mcp, database]
```

### Kill Switch Rules

```yaml
# falco-rules/kosmos-killswitch.yaml
- rule: KOSMOS Kill Switch Triggered
  desc: Log when kill switch is activated
  condition: >
    spawned_process and
    proc.cmdline contains "kill-switch" or
    proc.cmdline contains "emergency-halt"
  output: >
    KOSMOS Kill Switch activated 
    (user=%user.name command=%proc.cmdline)
  priority: CRITICAL
  tags: [kosmos, killswitch, emergency]

- rule: Unauthorized Kill Switch Attempt
  desc: Detect unauthorized kill switch attempts
  condition: >
    spawned_process and
    proc.cmdline contains "kill-switch" and
    not user.name in (aegis, admin, root)
  output: >
    Unauthorized kill switch attempt
    (user=%user.name)
  priority: CRITICAL
  tags: [kosmos, killswitch, unauthorized]
```

---

## Trusted Lists

```yaml
# falco-rules/kosmos-lists.yaml
- list: trusted_ips
  items:
    - 10.42.0.0/16    # K3s pod network
    - 10.43.0.0/16    # K3s service network
    - 10.0.1.0/24     # KOSMOS internal

- list: allowed_ports
  items: [443, 4317, 5432, 6379, 9000]

- list: kosmos_agents
  items:
    - zeus
    - hermes
    - chronos
    - athena
    - aegis
    - hephaestus
    - nur-prometheus
    - iris
    - memorix
    - hestia
    - morpheus
```

---

## AEGIS Integration

The AEGIS agent receives Falco alerts and can trigger responses:

```python
# agents/aegis/falco_handler.py
from fastapi import FastAPI, Request
from enum import Enum

class FalcoPriority(Enum):
    EMERGENCY = "emergency"
    ALERT = "alert"
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"

app = FastAPI()

@app.post("/falco")
async def handle_falco_alert(request: Request):
    alert = await request.json()
    
    priority = FalcoPriority(alert["priority"])
    rule = alert["rule"]
    output = alert["output"]
    
    if priority in [FalcoPriority.CRITICAL, FalcoPriority.EMERGENCY]:
        # Trigger kill switch evaluation
        await evaluate_kill_switch(alert)
    
    if "unauthorized" in rule.lower():
        # Quarantine affected container
        await quarantine_container(alert["container"])
    
    # Log to audit trail
    await audit_log.record(
        event="falco_alert",
        priority=priority.value,
        rule=rule,
        output=output
    )
    
    return {"status": "processed"}
```

---

## Alert Examples

### Sample Alert Output

```json
{
  "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "output": "Shell spawned in KOSMOS agent (user=root container=zeus-orchestrator shell=bash parent=python3)",
  "priority": "Warning",
  "rule": "KOSMOS Agent Shell Spawn",
  "time": "2025-12-14T10:30:00.000000000Z",
  "output_fields": {
    "container.name": "zeus-orchestrator",
    "proc.name": "bash",
    "proc.pname": "python3",
    "user.name": "root"
  },
  "tags": ["kosmos", "shell", "container"]
}
```

---

## Troubleshooting

### Check Falco Status

```bash
# Verify Falco is running
kubectl get pods -n kosmos-system -l app=falco

# Check Falco logs
kubectl logs -n kosmos-system -l app=falco -f

# Verify eBPF driver loaded
kubectl exec -n kosmos-system falco-xxxxx -- falco --version

# Test rule triggering
kubectl exec -it -n kosmos-agents zeus-xxxxx -- /bin/bash
# Should generate alert
```

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| eBPF driver fails | Kernel incompatibility | Use kernel module driver |
| High CPU usage | Too many rules | Optimize rule conditions |
| Missing alerts | Sidekick not configured | Check webhook URLs |

---

## See Also

- [Kyverno Policies](kyverno-policies.md)
- [AEGIS Security Agent](../02-architecture/agents/aegis-security.md)
- [Kill Switch Protocol](../01-governance/kill-switch-protocol.md)

---

**Last Updated:** December 2025

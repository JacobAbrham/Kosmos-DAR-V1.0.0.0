# Disaster Recovery Plan

**Document Type:** Operational Procedure  
**Owner:** Site Reliability Engineering  
**Reviewers:** CTO, Security Lead, Infrastructure Architect  
**Review Cadence:** Quarterly  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active  
**Classification:** Internal - Sensitive

---

## Executive Summary

This document defines the disaster recovery (DR) strategy, procedures, and responsibilities for the KOSMOS AI Operating System. It establishes Recovery Time Objectives (RTO), Recovery Point Objectives (RPO), and detailed runbooks for various failure scenarios.

**Key Metrics:**

| Metric | Target | Tier 1 Services | Tier 2 Services |
|--------|--------|-----------------|-----------------|
| **RTO** | Recovery Time | 1 hour | 4 hours |
| **RPO** | Data Loss Tolerance | 15 minutes | 1 hour |
| **MTTR** | Mean Time to Repair | 30 minutes | 2 hours |

---

## Service Tier Classification

### Tier 1: Critical Services

Services that must be recovered first. System is non-functional without these.

| Service | RTO | RPO | Dependencies |
|---------|-----|-----|--------------|
| PostgreSQL (Primary) | 30 min | 15 min | None |
| Zeus Orchestrator | 30 min | N/A (stateless) | PostgreSQL |
| NATS JetStream | 30 min | 15 min | None |
| API Gateway | 15 min | N/A | Zeus |

### Tier 2: Important Services

Services required for full functionality but system partially works without them.

| Service | RTO | RPO | Dependencies |
|---------|-----|-----|--------------|
| Athena (Knowledge) | 1 hour | 30 min | PostgreSQL, Vector DB |
| Dragonfly (Cache) | 1 hour | N/A | None |
| MinIO (Object Storage) | 2 hours | 1 hour | None |
| Specialist Agents | 2 hours | N/A | Zeus, PostgreSQL |

### Tier 3: Supporting Services

Services that enhance functionality but are not critical for core operations.

| Service | RTO | RPO | Dependencies |
|---------|-----|-----|--------------|
| Prometheus | 4 hours | 24 hours | None |
| Grafana | 4 hours | 24 hours | Prometheus |
| Langfuse | 4 hours | 1 hour | PostgreSQL |
| Jaeger | 8 hours | N/A | None |

---

## Backup Strategy

### Backup Schedule

```
┌────────────────────────────────────────────────────────────────┐
│                    KOSMOS Backup Schedule                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  PostgreSQL:                                                   │
│  ├── WAL Archiving: Continuous (every 60s)                    │
│  ├── Base Backup: Daily @ 02:00 UTC                           │
│  └── Full Backup: Weekly @ Sunday 02:00 UTC                   │
│                                                                │
│  etcd (K3s):                                                   │
│  ├── Snapshot: Every 6 hours                                  │
│  └── Retention: 7 days                                        │
│                                                                │
│  MinIO:                                                        │
│  ├── Bucket Replication: Continuous                           │
│  └── Versioning: Enabled (90 day retention)                   │
│                                                                │
│  Configuration:                                                │
│  ├── Git: Every commit (GitHub)                               │
│  └── Secrets: Daily export to secure vault                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Backup Locations

| Data Type | Primary Location | Backup Location | Offsite |
|-----------|-----------------|-----------------|---------|
| PostgreSQL | Node local SSD | Alibaba OSS | Yes |
| etcd snapshots | `/var/lib/rancher/k3s/server/db/snapshots` | Alibaba OSS | Yes |
| MinIO objects | Node local SSD | Cross-region OSS | Yes |
| Configuration | GitHub | Local clone | Yes |
| Secrets | Infisical | Encrypted OSS | Yes |

### PostgreSQL Backup Configuration

```yaml
# postgresql-backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: kosmos-db
spec:
  schedule: "0 2 * * *"  # Daily at 02:00 UTC
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:16
            command:
            - /bin/bash
            - -c
            - |
              TIMESTAMP=$(date +%Y%m%d_%H%M%S)
              pg_dump -Fc kosmos > /backup/kosmos_${TIMESTAMP}.dump
              # Upload to OSS
              aliyun oss cp /backup/kosmos_${TIMESTAMP}.dump \
                oss://kosmos-backups/postgres/kosmos_${TIMESTAMP}.dump
              # Cleanup old local backups (keep 7 days)
              find /backup -mtime +7 -delete
            env:
            - name: PGHOST
              value: postgres-primary
            - name: PGUSER
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: username
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: password
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: postgres-backup-pvc
          restartPolicy: OnFailure
```

### WAL Archiving Configuration

```ini
# postgresql.conf additions for continuous archiving
wal_level = replica
archive_mode = on
archive_command = 'aliyun oss cp %p oss://kosmos-backups/postgres/wal/%f'
archive_timeout = 60
```

---

## Disaster Scenarios and Recovery Procedures

### Scenario 1: Single Node Failure

**Impact:** Partial service degradation  
**RTO:** 15 minutes  
**Automatic Recovery:** Yes (Kubernetes handles pod rescheduling)

**Detection:**
```bash
# Alert triggers when node goes NotReady
kubectl get nodes
# NAME     STATUS     ROLES                  AGE   VERSION
# node-1   NotReady   control-plane,master   30d   v1.28.0
# node-2   Ready      control-plane,master   30d   v1.28.0
# node-3   Ready      control-plane,master   30d   v1.28.0
```

**Recovery Procedure:**

1. **Verify automatic pod migration** (wait 5 minutes)
   ```bash
   kubectl get pods -A -o wide | grep -v Running
   ```

2. **If pods stuck in Pending**, check resources:
   ```bash
   kubectl describe nodes | grep -A 5 "Allocated resources"
   ```

3. **Investigate failed node:**
   ```bash
   # SSH to node (if accessible)
   ssh node-1
   journalctl -u k3s -n 100
   
   # Check system resources
   df -h
   free -m
   dmesg | tail -50
   ```

4. **If node unrecoverable**, remove and replace:
   ```bash
   # Remove from cluster
   kubectl delete node node-1
   
   # Provision new node and join
   curl -sfL https://get.k3s.io | sh -s - server \
     --server https://node-2:6443 \
     --token $(cat /var/lib/rancher/k3s/server/node-token)
   ```

---

### Scenario 2: Complete Cluster Loss

**Impact:** Total service outage  
**RTO:** 1 hour  
**Automatic Recovery:** No

**Prerequisites:**
- Access to backup storage (Alibaba OSS)
- Infrastructure provisioning access
- Latest etcd snapshot and PostgreSQL backup

**Recovery Procedure:**

**Phase 1: Infrastructure Recovery (20 minutes)**

```bash
# 1. Provision new nodes via Terraform
cd infrastructure/terraform/alibaba
terraform apply -auto-approve

# 2. Initialize first K3s node
ssh new-node-1
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --tls-san kosmos-api.nuvanta-holding.com

# 3. Restore etcd from snapshot
# Download latest snapshot
aliyun oss cp oss://kosmos-backups/etcd/latest-snapshot.db /tmp/

# Restore
k3s server \
  --cluster-reset \
  --cluster-reset-restore-path=/tmp/latest-snapshot.db

# 4. Join remaining nodes
# (On node-2 and node-3)
curl -sfL https://get.k3s.io | sh -s - server \
  --server https://new-node-1:6443 \
  --token <token>
```

**Phase 2: Data Recovery (30 minutes)**

```bash
# 1. Wait for PostgreSQL pod to schedule
kubectl wait --for=condition=ready pod -l app=postgres -n kosmos-db --timeout=300s

# 2. Restore PostgreSQL from backup
# Download latest backup
aliyun oss cp oss://kosmos-backups/postgres/latest.dump /tmp/

# Restore
kubectl exec -it postgres-0 -n kosmos-db -- \
  pg_restore -d kosmos -c /tmp/latest.dump

# 3. Replay WAL logs to minimize data loss
# Download WAL files since last backup
aliyun oss cp -r oss://kosmos-backups/postgres/wal/ /tmp/wal/

# Apply WAL files
kubectl exec -it postgres-0 -n kosmos-db -- \
  pg_wal_replay /tmp/wal/
```

**Phase 3: Service Verification (10 minutes)**

```bash
# 1. Verify all pods running
kubectl get pods -A

# 2. Run health checks
curl -f https://api.kosmos.nuvanta-holding.com/health

# 3. Verify agent connectivity
curl https://api.kosmos.nuvanta-holding.com/api/v1/agents

# 4. Run smoke tests
./scripts/smoke-test.sh production
```

---

### Scenario 3: PostgreSQL Database Corruption

**Impact:** Data integrity issues, potential data loss  
**RTO:** 30 minutes  
**RPO:** 15 minutes (with WAL archiving)

**Detection:**
- Application errors indicating database issues
- PostgreSQL logs showing corruption errors
- Data inconsistency reports

**Recovery Procedure:**

```bash
# 1. Stop write traffic immediately
kubectl scale deployment zeus-orchestrator -n kosmos-core --replicas=0

# 2. Assess corruption scope
kubectl exec -it postgres-0 -n kosmos-db -- psql -c "
  SELECT datname, 
         pg_database_size(datname) as size,
         datconnlimit 
  FROM pg_database;"

# 3. Point-in-Time Recovery
# Identify target recovery time (before corruption)
TARGET_TIME="2025-12-13 14:30:00 UTC"

# Create recovery configuration
kubectl exec -it postgres-0 -n kosmos-db -- bash -c "
cat > /var/lib/postgresql/data/recovery.signal << EOF
restore_command = 'aliyun oss cp oss://kosmos-backups/postgres/wal/%f %p'
recovery_target_time = '${TARGET_TIME}'
recovery_target_action = 'promote'
EOF"

# 4. Restart PostgreSQL to trigger recovery
kubectl delete pod postgres-0 -n kosmos-db

# 5. Monitor recovery progress
kubectl logs -f postgres-0 -n kosmos-db

# 6. Verify data integrity
kubectl exec -it postgres-0 -n kosmos-db -- psql -c "
  SELECT count(*) FROM conversations;
  SELECT count(*) FROM agent_sessions;
  SELECT max(updated_at) FROM conversations;"

# 7. Resume service
kubectl scale deployment zeus-orchestrator -n kosmos-core --replicas=3
```

---

### Scenario 4: Ransomware/Security Breach

**Impact:** Potential data compromise, service integrity  
**RTO:** 4 hours (clean rebuild)  
**Priority:** Containment over speed

**Immediate Actions (First 15 minutes):**

```bash
# 1. ISOLATE - Cut external access immediately
# Update Cloudflare to block all traffic
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/settings/security_level" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -d '{"value":"under_attack"}'

# 2. PRESERVE - Capture forensic evidence
kubectl get pods -A -o yaml > /forensics/pods-state.yaml
kubectl logs --all-containers -n kosmos-core > /forensics/logs.txt

# 3. CONTAIN - Network isolation
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: emergency-lockdown
  namespace: kosmos-core
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
EOF
```

**Investigation Phase (1-2 hours):**

```bash
# 1. Review audit logs
kubectl logs -n kube-system -l component=kube-apiserver | grep -i "unusual"

# 2. Check for unauthorized access
kubectl get secrets -A
kubectl auth can-i --list --as=system:anonymous

# 3. Review recent changes
kubectl get events -A --sort-by='.lastTimestamp' | tail -100
```

**Clean Rebuild (if compromised):**

```bash
# 1. Provision completely new infrastructure
# (Do NOT reuse potentially compromised nodes)

# 2. Restore from known-good backup
# Use backup from BEFORE suspected compromise date

# 3. Rotate ALL credentials
./scripts/rotate-all-secrets.sh

# 4. Apply security patches
# Update all container images to latest patched versions
```

---

## Communication Plan

### Escalation Matrix

| Severity | Response Time | Notify | Approve Recovery |
|----------|---------------|--------|------------------|
| **P1 - Critical** | 5 min | On-call → Team Lead → CTO | Team Lead |
| **P2 - High** | 15 min | On-call → Team Lead | On-call |
| **P3 - Medium** | 1 hour | On-call | On-call |
| **P4 - Low** | 4 hours | Ticket queue | Self |

### Communication Channels

| Channel | Purpose | Access |
|---------|---------|--------|
| PagerDuty | Alerting & escalation | On-call rotation |
| Slack #incidents | Real-time coordination | Engineering |
| Status Page | External communication | Public |
| Email: incidents@ | Formal notifications | Stakeholders |

### Status Page Updates

```markdown
# Template for status page updates

## [INVESTIGATING] Service Degradation
**Posted:** 2025-12-13 14:30 UTC
**Affected Services:** API, Agent Services

We are investigating reports of increased latency and errors. 
Updates will be provided every 30 minutes.

---

## [IDENTIFIED] Database Recovery in Progress  
**Posted:** 2025-12-13 14:45 UTC

Root cause identified as database node failure. Recovery 
procedures initiated. ETA for full recovery: 30 minutes.

---

## [RESOLVED] Services Restored
**Posted:** 2025-12-13 15:10 UTC

All services have been restored. Post-incident review scheduled.
Total downtime: 40 minutes.
```

---

## Testing Schedule

### DR Test Types

| Test Type | Frequency | Scope | Downtime |
|-----------|-----------|-------|----------|
| **Backup Verification** | Weekly | Restore to test env | None |
| **Failover Test** | Monthly | Single node failure | < 5 min |
| **Full DR Test** | Quarterly | Complete cluster rebuild | 4 hours (scheduled) |
| **Tabletop Exercise** | Bi-annually | Process walkthrough | None |

### Quarterly Full DR Test Procedure

```bash
# 1. Schedule maintenance window
# 2. Notify stakeholders 1 week in advance
# 3. Create fresh backups
./scripts/create-dr-backup.sh

# 4. Provision DR environment
terraform -chdir=infrastructure/dr apply

# 5. Execute recovery procedure
./scripts/dr-recovery.sh

# 6. Validate functionality
./scripts/dr-validation.sh

# 7. Document results
# 8. Destroy DR environment
terraform -chdir=infrastructure/dr destroy

# 9. Publish DR test report
```

### Test Success Criteria

| Metric | Target | Pass Criteria |
|--------|--------|---------------|
| Recovery Time | < 1 hour | Complete service restoration |
| Data Loss | < 15 min | Verify latest transactions |
| Functionality | 100% | All smoke tests pass |
| Documentation | Current | No procedure gaps identified |

---

## Post-Incident Procedures

### Incident Report Template

```markdown
# Incident Report: [INCIDENT-2025-12-13-001]

## Summary
- **Duration:** 2025-12-13 14:30 to 2025-12-13 16:45
- **Impact:** [affected users/services]
- **Severity:** P1/P2/P3/P4
- **Root Cause:** [brief description]

## Timeline
| Time (UTC) | Event |
|------------|-------|
| HH:MM | Alert triggered |
| HH:MM | On-call acknowledged |
| HH:MM | Root cause identified |
| HH:MM | Recovery initiated |
| HH:MM | Service restored |

## Root Cause Analysis
[Detailed technical explanation]

## Impact Analysis
- Users affected: X
- Transactions lost: Y
- Revenue impact: $Z

## Corrective Actions
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Restore from backup | Infrastructure Team | 2025-12-15 | Completed |
| Update monitoring alerts | SRE Team | 2025-12-16 | In Progress |
| Review backup procedures | Operations Lead | 2025-12-20 | Pending |

## Lessons Learned
- What went well
- What could be improved
- Process changes recommended
```

---

## Appendix A: Recovery Runbook Quick Reference

### One-Page Recovery Cheatsheet

```
╔══════════════════════════════════════════════════════════════╗
║              KOSMOS DISASTER RECOVERY QUICK REF              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  BACKUP LOCATIONS:                                           ║
║  • PostgreSQL: oss://kosmos-backups/postgres/                ║
║  • etcd:       oss://kosmos-backups/etcd/                    ║
║  • Config:     github.com/nuvanta/kosmos-config              ║
║                                                              ║
║  CRITICAL CREDENTIALS:                                       ║
║  • Infisical: vault.infisical.com/project/kosmos            ║
║  • Alibaba:   RAM console → kosmos-dr-admin                  ║
║  • GitHub:    Settings → Secrets → KOSMOS_DEPLOY_KEY         ║
║                                                              ║
║  RECOVERY COMMANDS:                                          ║
║                                                              ║
║  # Restore etcd                                              ║
║  k3s server --cluster-reset \                                ║
║    --cluster-reset-restore-path=/path/to/snapshot            ║
║                                                              ║
║  # Restore PostgreSQL                                        ║
║  pg_restore -d kosmos -c /path/to/backup.dump               ║
║                                                              ║
║  # Force pod reschedule                                      ║
║  kubectl delete pod <pod> -n <ns> --grace-period=0          ║
║                                                              ║
║  EMERGENCY CONTACTS:                                         ║
║  • On-call: +1-XXX-XXX-XXXX (PagerDuty)                     ║
║  • CTO: cto@nuvanta-holding.com                             ║
║  • Alibaba Support: aliyun.com/support                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-13 | SRE Team | Initial release |

**Next Review:** 2026-03-13  
**Document Owner:** sre@nuvanta-holding.com  
**Emergency Contact:** oncall@nuvanta-holding.com

---

*This document contains sensitive operational procedures. Handle according to data classification policy.*

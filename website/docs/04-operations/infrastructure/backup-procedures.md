# Backup Procedures

**Last Updated:** 2025-12-13  
**Status:** Active

## Overview

Comprehensive backup strategy for KOSMOS to ensure data durability and enable disaster recovery.

## Backup Scope

### Data to Backup
- **Databases:** PostgreSQL (conversations, user data, metadata)
- **Object Storage:** S3 (model artifacts, documents, exports)
- **Configuration:** Kubernetes ConfigMaps, Secrets
- **Agent State:** Conversation history, user preferences
- **Code Repositories:** GitHub (already backed up)
- **Infrastructure as Code:** Terraform state, Helm charts

### Data NOT Backed Up
- Temporary caches (Redis)
- Log files (retained 30 days in log aggregation)
- Test/development data
- Derived/reproducible data

## Backup Schedule

### Automated Backups

| Data Type | Frequency | Retention | Storage |
|-----------|-----------|-----------|---------|
| **Database** | Continuous + Hourly snapshot | 30 days PITR | S3 cross-region |
| **Object Storage** | Real-time replication | Versioned (90 days) | S3 cross-region |
| **Configuration** | On every change (GitOps) | Unlimited | GitHub |
| **Agent State** | Hourly | 7 days | S3 |
| **Full System** | Daily | 30 days | S3 + Glacier |

### Manual Backups
- Before major deployments
- Before destructive operations
- For compliance/audit requirements

## Database Backups

### PostgreSQL Automated Backups

**Continuous WAL Archiving:**
```bash
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'aws s3 cp %p s3://kosmos-backups/wal/%f'
```

**Point-in-Time Recovery (PITR):**
```bash
# Backup base snapshot
pg_basebackup -h $DB_HOST -U backup_user -D /backup -Fp -Xs -P

# Upload to S3
aws s3 sync /backup s3://kosmos-backups/base/$(date +%Y%m%d_%H%M%S)/
```

**RDS Automated Backups:**
```bash
# Enable automated backups (7-35 days)
aws rds modify-db-instance \
  --db-instance-identifier kosmos-prod \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00" \
  --apply-immediately
```

### Restore Testing

**Monthly Restore Test:**
```bash
# Restore to test instance
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier kosmos-restore-test \
  --db-snapshot-identifier kosmos-snapshot-$(date +%Y%m%d)

# Verify data integrity
psql -h kosmos-restore-test -U admin -d kosmos \
  -c "SELECT COUNT(*) FROM conversations;"

# Cleanup
aws rds delete-db-instance \
  --db-instance-identifier kosmos-restore-test \
  --skip-final-snapshot
```

## Object Storage Backups

### S3 Cross-Region Replication

```json
{
  "Role": "arn:aws:iam::ACCOUNT:role/s3-replication",
  "Rules": [
    {
      "Status": "Enabled",
      "Priority": 1,
      "Filter": {},
      "Destination": {
        "Bucket": "arn:aws:s3:::kosmos-backups-dr",
        "ReplicationTime": {
          "Status": "Enabled",
          "Time": {
            "Minutes": 15
          }
        }
      }
    }
  ]
}
```

### Versioning
```bash
# Enable versioning
aws s3api put-bucket-versioning \
  --bucket kosmos-production \
  --versioning-configuration Status=Enabled

# Lifecycle policy for old versions
aws s3api put-bucket-lifecycle-configuration \
  --bucket kosmos-production \
  --lifecycle-configuration file://lifecycle.json
```

## Configuration Backups

### Kubernetes Resources

**Velero Backup:**
```bash
# Install Velero
velero install \
  --provider aws \
  --bucket kosmos-k8s-backups \
  --backup-location-config region=us-east-1 \
  --snapshot-location-config region=us-east-1

# Create backup schedule
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --include-namespaces kosmos \
  --ttl 720h

# Manual backup
velero backup create pre-deployment-$(date +%Y%m%d) \
  --include-namespaces kosmos
```

**GitOps (ArgoCD):**
- All configuration in Git
- Automatic versioning
- Pull request history

## Agent State Backups

### Backup Script
```bash
#!/bin/bash
# backup-agent-state.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/agent-backup-${TIMESTAMP}"

# Export agent state
kubectl exec -n kosmos deployment/zeus-orchestrator -- \
  python -m kosmos.tools.export_state \
  --output /tmp/state.json

# Copy from pod
kubectl cp kosmos/zeus-orchestrator-0:/tmp/state.json \
  ${BACKUP_DIR}/zeus-state.json

# Compress and upload
tar -czf agent-state-${TIMESTAMP}.tar.gz ${BACKUP_DIR}
aws s3 cp agent-state-${TIMESTAMP}.tar.gz \
  s3://kosmos-backups/agent-state/

# Cleanup
rm -rf ${BACKUP_DIR} agent-state-${TIMESTAMP}.tar.gz
```

### Automated Cron
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: agent-state-backup
  namespace: kosmos
spec:
  schedule: "0 * * * *"  # Hourly
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: kosmos/backup-tools:latest
            command: ["/scripts/backup-agent-state.sh"]
```

## Backup Verification

### Automated Integrity Checks
```bash
# Daily verification
./scripts/verify-backups.sh

# Check backup exists
aws s3 ls s3://kosmos-backups/daily/$(date +%Y%m%d)/ || exit 1

# Verify backup size (&gt;100MB expected)
SIZE=$(aws s3 ls s3://kosmos-backups/daily/$(date +%Y%m%d)/backup.tar.gz \
  --summarize | grep "Total Size" | awk '{print $3}')
if [ $SIZE -lt 100000000 ]; then
  echo "ERROR: Backup too small"
  exit 1
fi

# Test restore to staging
./scripts/restore-to-staging.sh --backup $(date +%Y%m%d)
```

## Restoration Procedures

### Database Restore

**Point-in-Time Recovery:**
```bash
# Restore to specific time
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance kosmos-prod \
  --target-db-instance kosmos-restored \
  --restore-time 2025-12-13T10:30:00Z \
  --vpc-security-group-ids sg-xxxxx \
  --db-subnet-group-name kosmos-subnet-group
```

**Snapshot Restore:**
```bash
# List snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier kosmos-prod

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier kosmos-restored \
  --db-snapshot-identifier kosmos-snapshot-20251213
```

### Configuration Restore

**Velero Restore:**
```bash
# List backups
velero backup get

# Restore specific backup
velero restore create --from-backup daily-backup-20251213

# Restore to different namespace
velero restore create --from-backup daily-backup-20251213 \
  --namespace-mappings kosmos:kosmos-restored
```

### Agent State Restore

```bash
# Download backup
aws s3 cp s3://kosmos-backups/agent-state/agent-state-20251213_100000.tar.gz .

# Extract
tar -xzf agent-state-20251213_100000.tar.gz

# Restore to pod
kubectl cp agent-backup-20251213_100000/zeus-state.json \
  kosmos/zeus-orchestrator-0:/tmp/state.json

# Import state
kubectl exec -n kosmos deployment/zeus-orchestrator -- \
  python -m kosmos.tools.import_state \
  --input /tmp/state.json
```

## Backup Monitoring

### Metrics to Track
- Backup completion status (success/failure)
- Backup duration
- Backup size
- Time since last successful backup
- Restore test results

### Alerts
```yaml
# Prometheus alert
- alert: BackupFailed
  expr: backup_last_success_timestamp < (time() - 86400)
  labels:
    severity: critical
  annotations:
    summary: "Backup hasn't succeeded in 24 hours"
```

## Compliance and Retention

### Retention Policies
- **Operational Backups:** 30 days
- **Compliance Backups:** 7 years (Glacier)
- **Audit Logs:** 90 days active, 7 years archive

### Encryption
- At rest: AES-256
- In transit: TLS 1.3
- Key management: AWS KMS

## Related Documentation

- [Disaster Recovery](../../security/disaster-recovery)
- [Business Continuity](../../05-human-factors/business-continuity)
- [SLA/SLO](../sla-slo)

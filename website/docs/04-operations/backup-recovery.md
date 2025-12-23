# Backup & Recovery

**Data Protection and Disaster Recovery for KOSMOS**

:::info RPO/RTO Targets
    - **RPO (Recovery Point Objective):** 1 hour
    - **RTO (Recovery Time Objective):** 4 hours

---

## Backup Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKUP ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │   MinIO     │  │   K3s etcd  │        │
│  │   (Data)    │  │  (Objects)  │  │  (Cluster)  │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │               │
│         ▼                ▼                ▼               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Velero (Backup Orchestrator)            │  │
│  └─────────────────────────┬───────────────────────────┘  │
│                            │                              │
│                            ▼                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         Alibaba Cloud OSS (Backup Storage)          │  │
│  │         kosmos-backups-staging / -production        │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Backup Schedule

| Component | Method | Frequency | Retention |
|-----------|--------|-----------|-----------|
| PostgreSQL | pg_dump + WAL | Hourly + continuous | 30 days |
| MinIO | mc mirror | Daily | 90 days |
| K3s etcd | k3s etcd-snapshot | Every 6 hours | 7 days |
| Kubernetes resources | Velero | Daily | 30 days |
| Secrets | Infisical export | Daily | 90 days |

---

## PostgreSQL Backup

### Continuous WAL Archiving

```yaml
# postgresql-backup-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-backup-config
  namespace: kosmos-data
data:
  archive_command: |
    wal-g wal-push %p --config /etc/wal-g/config.yaml
  restore_command: |
    wal-g wal-fetch %f %p --config /etc/wal-g/config.yaml
```

### WAL-G Configuration

```yaml
# /etc/wal-g/config.yaml
WALG_S3_PREFIX: s3://kosmos-backups-staging/postgres/wal
AWS_ACCESS_KEY_ID: ${OSS_ACCESS_KEY}
AWS_SECRET_ACCESS_KEY: ${OSS_SECRET_KEY}
AWS_ENDPOINT: https://oss-me-central-1.aliyuncs.com
AWS_S3_FORCE_PATH_STYLE: true
PGHOST: localhost
PGPORT: 5432
PGUSER: postgres
```

### Manual Backup

```bash
# Full backup
kubectl exec -n kosmos-data postgres-0 -- \
  wal-g backup-push /var/lib/postgresql/data

# List backups
kubectl exec -n kosmos-data postgres-0 -- \
  wal-g backup-list

# Verify backup
kubectl exec -n kosmos-data postgres-0 -- \
  wal-g backup-verify LATEST
```

### Restore Procedure

```bash
# 1. Scale down consumers
kubectl scale -n kosmos-agents --replicas=0 deployment --all

# 2. Restore to new instance
kubectl exec -n kosmos-data postgres-restore-0 -- \
  wal-g backup-fetch /var/lib/postgresql/data LATEST

# 3. Apply WAL recovery
kubectl exec -n kosmos-data postgres-restore-0 -- \
  wal-g wal-fetch --config /etc/wal-g/config.yaml

# 4. Promote and verify
kubectl exec -n kosmos-data postgres-restore-0 -- \
  pg_ctl promote -D /var/lib/postgresql/data

# 5. Scale up consumers
kubectl scale -n kosmos-agents --replicas=1 deployment --all
```

---

## MinIO Backup

### Mirror to OSS

```bash
# Configure mc client
mc alias set kosmos-local http://minio.kosmos-data:9000 ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}
mc alias set oss-backup https://oss-me-central-1.aliyuncs.com ${OSS_ACCESS_KEY} ${OSS_SECRET_KEY}

# Mirror all buckets
mc mirror --watch kosmos-local/kosmos-documents oss-backup/kosmos-backups-staging/minio/documents
mc mirror --watch kosmos-local/kosmos-media oss-backup/kosmos-backups-staging/minio/media
```

### Backup CronJob

```yaml
# minio-backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: minio-backup
  namespace: kosmos-data
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: mc
              image: minio/mc:latest
              command:
                - /bin/sh
                - -c
                - |
                  mc alias set local http://minio:9000 $MINIO_ACCESS_KEY $MINIO_SECRET_KEY
                  mc alias set oss $OSS_ENDPOINT $OSS_ACCESS_KEY $OSS_SECRET_KEY
                  mc mirror local/ oss/kosmos-backups-staging/minio/
              envFrom:
                - secretRef:
                    name: backup-credentials
          restartPolicy: OnFailure
```

---

## K3s etcd Backup

### Automatic Snapshots

```bash
# K3s automatically creates snapshots
# Location: /var/lib/rancher/k3s/server/db/snapshots/

# Manual snapshot
k3s etcd-snapshot save --name manual-$(date +%Y%m%d-%H%M%S)

# List snapshots
k3s etcd-snapshot ls

# Upload to OSS
aws s3 cp /var/lib/rancher/k3s/server/db/snapshots/ \
  s3://kosmos-backups-staging/etcd/ \
  --recursive --endpoint-url https://oss-me-central-1.aliyuncs.com
```

### etcd Restore

```bash
# Stop K3s
systemctl stop k3s

# Restore from snapshot
k3s server \
  --cluster-reset \
  --cluster-reset-restore-path=/var/lib/rancher/k3s/server/db/snapshots/[snapshot-name]

# Restart K3s
systemctl start k3s
```

---

## Velero Kubernetes Backup

### Installation

```bash
# Install Velero with OSS plugin
velero install \
  --provider alibabacloud \
  --plugins velero/velero-plugin-for-alibabacloud:v1.0.0 \
  --bucket kosmos-backups-staging \
  --secret-file ./credentials-velero \
  --backup-location-config region=me-central-1
```

### Backup Commands

```bash
# Full cluster backup
velero backup create kosmos-full-$(date +%Y%m%d) \
  --include-namespaces kosmos-agents,kosmos-data,kosmos-system

# Specific namespace
velero backup create agents-backup \
  --include-namespaces kosmos-agents

# Schedule daily backups
velero schedule create daily-backup \
  --schedule="0 3 * * *" \
  --include-namespaces kosmos-agents,kosmos-data,kosmos-system \
  --ttl 720h  # 30 days
```

### Restore Commands

```bash
# List available backups
velero backup get

# Restore entire backup
velero restore create --from-backup kosmos-full-20251214

# Restore specific namespace
velero restore create --from-backup kosmos-full-20251214 \
  --include-namespaces kosmos-agents
```

---

## Disaster Recovery Procedure

### Full System Recovery

```
┌─────────────────────────────────────────────────────────────┐
│              DISASTER RECOVERY CHECKLIST                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  □ 1. Provision new infrastructure                         │
│       - K3s cluster (staging: 1 node, prod: 3 nodes)      │
│       - Verify networking and DNS                          │
│                                                             │
│  □ 2. Restore K3s etcd                                     │
│       - Download latest snapshot from OSS                  │
│       - Apply --cluster-reset-restore-path                 │
│                                                             │
│  □ 3. Restore PostgreSQL                                   │
│       - Deploy PostgreSQL StatefulSet                      │
│       - Restore from WAL-G backup                          │
│       - Verify data integrity                              │
│                                                             │
│  □ 4. Restore MinIO                                        │
│       - Deploy MinIO                                       │
│       - Mirror data from OSS backup                        │
│                                                             │
│  □ 5. Restore Kubernetes resources                         │
│       - velero restore from latest backup                  │
│       - Verify all deployments healthy                     │
│                                                             │
│  □ 6. Restore secrets                                      │
│       - Import from Infisical backup                       │
│       - Rotate credentials if security incident            │
│                                                             │
│  □ 7. Verify system health                                 │
│       - All agents responding                              │
│       - MCP servers connected                              │
│       - SigNoz receiving metrics                           │
│                                                             │
│  □ 8. Update DNS and notify users                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Backup Verification

### Monthly DR Test

```bash
# Spin up test environment
terraform apply -var="environment=dr-test"

# Restore all components
./scripts/dr-restore.sh --target=dr-test

# Run verification suite
./scripts/dr-verify.sh

# Document results
# Destroy test environment
terraform destroy -var="environment=dr-test"
```

---

## See Also

- [Disaster Recovery Plan](../security/disaster-recovery)
- [K3s Configuration](infrastructure/k3s-config)
- [Incident Response](incident-response)

---

**Last Updated:** December 2025

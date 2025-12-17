# Data Pipeline Failure

**Runbook for Data Pipeline Incidents**

---

## 🚨 Severity Classification

| Severity | Impact | Response Time |
|----------|--------|---------------|
| P0 (Critical) | Production models receiving no data | 5 minutes |
| P1 (High) | Data freshness >4 hours behind | 15 minutes |
| P2 (Medium) | Data quality issues detected | 1 hour |
| P3 (Low) | Non-critical pipeline delayed | 24 hours |

---

## 📊 Detection Triggers

### Automated Alerts

```yaml
alerts:
  - name: PipelineFailure
    condition: pipeline_status == "failed"
    severity: P0
    
  - name: DataFreshnessLag
    condition: data_lag_hours > 4
    severity: P1
    
  - name: DataQualityAnomaly
    condition: quality_score < 0.90
    severity: P2
    
  - name: ETLJobTimeout
    condition: job_duration > expected * 3
    severity: P2
```

---

## 🔧 Response Procedures

### Phase 1: Immediate Assessment (0-5 minutes)

1. **Check pipeline status**
   ```bash
   # Airflow DAG status
   airflow dags list-runs -d kosmos_etl --state failed
   
   # Check recent failures
   airflow tasks failed-deps -d kosmos_etl
   ```

2. **Identify affected pipelines**
   
   | Pipeline | Data | Impact if Down |
   |----------|------|----------------|
   | training-data-sync | Training data | Model retraining blocked |
   | vector-db-refresh | Embeddings | RAG degradation |
   | metrics-aggregation | Analytics | Dashboard stale |
   | log-processing | Audit logs | Compliance risk |

3. **Check data sources**
   ```bash
   # Source connectivity
   curl -s https://api.nuvanta-holding.com/health
   
   # Database connectivity
   pg_isready -h postgres.internal -p 5432
   ```

### Phase 2: Triage

1. **Identify failure point**

   ```mermaid
   graph LR
       A[Source] --> B[Extract]
       B --> C[Transform]
       C --> D[Load]
       D --> E[Destination]
   ```

   Check each stage for errors:
   ```bash
   # View task logs
   airflow tasks logs -d kosmos_etl -t {task_id} {run_id}
   ```

2. **Common failure causes**

   | Cause | Indicators | Quick Fix |
   |-------|------------|-----------|
   | Source unavailable | Connection timeout | Wait/failover |
   | Schema change | Parse errors | Update schema |
   | Resource exhaustion | OOM/timeout | Scale up |
   | Data corruption | Validation errors | Fix source data |
   | Credential expiry | Auth errors | Rotate credentials |

### Phase 3: Mitigation

#### Option A: Retry Failed Tasks

```bash
# Clear failed task and retry
airflow tasks clear -d kosmos_etl -t {failed_task} -s {start_date} -e {end_date}

# Trigger DAG run
airflow dags trigger kosmos_etl
```

#### Option B: Skip and Continue

```bash
# Mark task as success (use with caution)
airflow tasks set-state -d kosmos_etl -t {task_id} {run_id} success
```

#### Option C: Manual Data Load

```bash
# Load from backup/snapshot
python scripts/manual_data_load.py --source backup --target production
```

#### Option D: Activate Fallback Source

```python
# Switch to secondary data source
config.data_source = "fallback"
```

### Phase 4: Recovery

1. **Verify data integrity**
   ```bash
   # Run data quality checks
   python scripts/validate_data.py --pipeline kosmos_etl
   
   # Check row counts
   psql -c "SELECT COUNT(*) FROM {table} WHERE updated_at > NOW() - INTERVAL '24 hours'"
   ```

2. **Backfill missing data**
   ```bash
   # Backfill for date range
   airflow dags backfill -d kosmos_etl -s 2025-12-10 -e 2025-12-12
   ```

3. **Restore normal operations**
   - Re-enable automated schedules
   - Clear any temporary overrides
   - Verify downstream systems

---

## 📋 Common Issues & Solutions

### Schema Changes

```sql
-- Check for schema differences
\d+ old_table
\d+ new_table

-- Update pipeline schema
ALTER TABLE staging_table ADD COLUMN new_field VARCHAR(255);
```

### Memory Issues

```yaml
# Increase Airflow worker resources
executor:
  resources:
    requests:
      memory: "4Gi"
    limits:
      memory: "8Gi"
```

### Connection Timeouts

```python
# Increase connection timeout
connection_config = {
    "connect_timeout": 30,
    "read_timeout": 300,
    "retries": 3
}
```

---

## 📞 Escalation Path

1. Data Engineering On-Call
2. Data Engineering Lead
3. VP Engineering
4. CTO (P0 only)

---

## 📋 Post-Incident

### Required Documentation

- Pipeline affected
- Duration of outage
- Data loss (if any)
- Root cause
- Prevention measures

### Follow-up Actions

- [ ] Add monitoring for detected issue
- [ ] Update pipeline resilience
- [ ] Document schema changes
- [ ] Update runbook if needed

---

**Last Updated:** 2025-12-12  
**Document Owner:** Data Engineering Lead

[← Back to Incident Response](README.md)

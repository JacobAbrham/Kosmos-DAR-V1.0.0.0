# Grafana Dashboards

**Document Type:** Operations Guide  
**Owner:** SRE Team  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Overview

Grafana is the visualization platform for KOSMOS observability data. This document covers deployment, dashboard provisioning, and the complete dashboard catalog.

---

## Deployment

### Kubernetes Manifest

```yaml
# grafana-deployment.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: kosmos-observability
data:
  datasources.yaml: |
    apiVersion: 1
    datasources:
      - name: Prometheus
        type: prometheus
        access: proxy
        url: http://prometheus:9090
        isDefault: true
        editable: false
        
      - name: Loki
        type: loki
        access: proxy
        url: http://loki:3100
        editable: false
        
      - name: Jaeger
        type: jaeger
        access: proxy
        url: http://jaeger-query:16686
        editable: false
        
      - name: PostgreSQL
        type: postgres
        url: postgres.kosmos-db:5432
        database: kosmos
        user: grafana_reader
        secureJsonData:
          password: ${POSTGRES_PASSWORD}
        jsonData:
          sslmode: require
          maxOpenConns: 5
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards-provider
  namespace: kosmos-observability
data:
  dashboards.yaml: |
    apiVersion: 1
    providers:
      - name: 'kosmos'
        orgId: 1
        folder: 'KOSMOS'
        type: file
        disableDeletion: true
        editable: false
        options:
          path: /var/lib/grafana/dashboards/kosmos
      - name: 'infrastructure'
        orgId: 1
        folder: 'Infrastructure'
        type: file
        disableDeletion: true
        editable: false
        options:
          path: /var/lib/grafana/dashboards/infrastructure
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: kosmos-observability
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:10.2.0
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-credentials
              key: admin-password
        - name: GF_INSTALL_PLUGINS
          value: "grafana-piechart-panel,grafana-clock-panel"
        - name: GF_SERVER_ROOT_URL
          value: "https://grafana.kosmos.nuvanta-holding.com"
        - name: GF_AUTH_GENERIC_OAUTH_ENABLED
          value: "true"
        - name: GF_AUTH_GENERIC_OAUTH_NAME
          value: "Keycloak"
        - name: GF_AUTH_GENERIC_OAUTH_CLIENT_ID
          value: "grafana"
        - name: GF_AUTH_GENERIC_OAUTH_SCOPES
          value: "openid profile email"
        resources:
          requests:
            cpu: "200m"
            memory: "512Mi"
          limits:
            cpu: "1"
            memory: "1Gi"
        volumeMounts:
        - name: datasources
          mountPath: /etc/grafana/provisioning/datasources
        - name: dashboards-provider
          mountPath: /etc/grafana/provisioning/dashboards
        - name: dashboards-kosmos
          mountPath: /var/lib/grafana/dashboards/kosmos
        - name: dashboards-infra
          mountPath: /var/lib/grafana/dashboards/infrastructure
        - name: storage
          mountPath: /var/lib/grafana
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
      volumes:
      - name: datasources
        configMap:
          name: grafana-datasources
      - name: dashboards-provider
        configMap:
          name: grafana-dashboards-provider
      - name: dashboards-kosmos
        configMap:
          name: grafana-dashboards-kosmos
      - name: dashboards-infra
        configMap:
          name: grafana-dashboards-infra
      - name: storage
        persistentVolumeClaim:
          claimName: grafana-storage
```

---

## Dashboard Catalog

### KOSMOS Folder

| Dashboard | ID | Description | Key Panels |
|-----------|-----|-------------|------------|
| **System Overview** | `kosmos-overview` | High-level system health | Request rate, error rate, latency, agent status |
| **Agent Performance** | `kosmos-agents` | Individual agent metrics | Per-agent latency, throughput, errors |
| **LLM Operations** | `kosmos-llm` | LLM provider metrics | Token usage, cost, latency by model |
| **Request Flow** | `kosmos-requests` | End-to-end request tracing | Request journey, bottlenecks |
| **Cost Analytics** | `kosmos-cost` | FinOps metrics | Daily/monthly cost, budget tracking |

### Infrastructure Folder

| Dashboard | ID | Description | Key Panels |
|-----------|-----|-------------|------------|
| **Kubernetes Cluster** | `k8s-cluster` | K3s cluster health | Node status, pod counts, resource usage |
| **PostgreSQL** | `postgres` | Database performance | Connections, queries, replication |
| **Dragonfly Cache** | `dragonfly` | Cache metrics | Hit ratio, memory, evictions |
| **NATS Messaging** | `nats` | Message broker | Messages/sec, subscriptions, streams |

---

## Dashboard Definitions

### System Overview Dashboard

```json
{
  "dashboard": {
    "title": "KOSMOS System Overview",
    "uid": "kosmos-overview",
    "tags": ["kosmos", "overview"],
    "timezone": "browser",
    "refresh": "30s",
    "panels": [
      {
        "title": "System Health",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "sum(up{job=\"kosmos-agents\"}) / count(up{job=\"kosmos-agents\"}) * 100",
            "legendFormat": "Agents Online"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 80},
                {"color": "green", "value": 100}
              ]
            }
          }
        }
      },
      {
        "title": "Request Rate",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4},
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{job=\"kosmos-agents\"}[5m])) by (agent)",
            "legendFormat": "{{agent}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "reqps"
          }
        }
      },
      {
        "title": "Error Rate",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4},
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{job=\"kosmos-agents\",status=~\"5..\"}[5m])) by (agent) / sum(rate(http_requests_total{job=\"kosmos-agents\"}[5m])) by (agent) * 100",
            "legendFormat": "{{agent}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "max": 10
          }
        }
      },
      {
        "title": "P99 Latency",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12},
        "targets": [
          {
            "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{job=\"kosmos-agents\"}[5m])) by (agent, le))",
            "legendFormat": "{{agent}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s"
          }
        }
      },
      {
        "title": "Agent Status",
        "type": "table",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12},
        "targets": [
          {
            "expr": "up{job=\"kosmos-agents\"}",
            "format": "table",
            "instant": true
          }
        ],
        "transformations": [
          {
            "id": "organize",
            "options": {
              "excludeByName": {"Time": true, "Value": false},
              "renameByName": {"agent": "Agent", "Value": "Status"}
            }
          }
        ]
      }
    ]
  }
}
```

### Agent Performance Dashboard

```json
{
  "dashboard": {
    "title": "KOSMOS Agent Performance",
    "uid": "kosmos-agents",
    "tags": ["kosmos", "agents"],
    "templating": {
      "list": [
        {
          "name": "agent",
          "type": "query",
          "query": "label_values(http_requests_total{job=\"kosmos-agents\"}, agent)",
          "multi": true,
          "includeAll": true
        }
      ]
    },
    "panels": [
      {
        "title": "Request Rate by Agent",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{job=\"kosmos-agents\", agent=~\"$agent\"}[5m])) by (agent)",
            "legendFormat": "{{agent}}"
          }
        ]
      },
      {
        "title": "Latency Heatmap",
        "type": "heatmap",
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
        "targets": [
          {
            "expr": "sum(rate(http_request_duration_seconds_bucket{job=\"kosmos-agents\", agent=~\"$agent\"}[5m])) by (le)",
            "format": "heatmap"
          }
        ],
        "options": {
          "calculate": false,
          "yAxis": {"unit": "s"}
        }
      },
      {
        "title": "Task Success Rate",
        "type": "gauge",
        "gridPos": {"h": 6, "w": 8, "x": 0, "y": 16},
        "targets": [
          {
            "expr": "sum(rate(agent_tasks_total{status=\"success\", agent=~\"$agent\"}[1h])) / sum(rate(agent_tasks_total{agent=~\"$agent\"}[1h])) * 100"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 95},
                {"color": "green", "value": 99}
              ]
            }
          }
        }
      },
      {
        "title": "Inter-Agent Handoffs",
        "type": "timeseries",
        "gridPos": {"h": 6, "w": 16, "x": 8, "y": 16},
        "targets": [
          {
            "expr": "sum(rate(agent_handoff_total{source_agent=~\"$agent\"}[5m])) by (source_agent, target_agent)",
            "legendFormat": "{{source_agent}} → {{target_agent}}"
          }
        ]
      }
    ]
  }
}
```

### LLM Operations Dashboard

```json
{
  "dashboard": {
    "title": "KOSMOS LLM Operations",
    "uid": "kosmos-llm",
    "tags": ["kosmos", "llm", "cost"],
    "panels": [
      {
        "title": "LLM Request Rate",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "sum(rate(llm_requests_total[5m])) by (provider, model)",
            "legendFormat": "{{provider}}/{{model}}"
          }
        ]
      },
      {
        "title": "Token Consumption",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "targets": [
          {
            "expr": "sum(rate(llm_tokens_total[5m])) by (type) * 60",
            "legendFormat": "{{type}}"
          }
        ],
        "fieldConfig": {
          "defaults": {"unit": "tokens/min"}
        }
      },
      {
        "title": "LLM Latency P99",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
        "targets": [
          {
            "expr": "histogram_quantile(0.99, sum(rate(llm_request_duration_seconds_bucket[5m])) by (provider, model, le))",
            "legendFormat": "{{provider}}/{{model}}"
          }
        ],
        "fieldConfig": {
          "defaults": {"unit": "s"}
        }
      },
      {
        "title": "Daily Cost",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 8},
        "targets": [
          {
            "expr": "sum(increase(llm_cost_dollars[24h]))"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "currencyUSD",
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 500}
              ]
            }
          }
        }
      },
      {
        "title": "Monthly Cost Projection",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 8},
        "targets": [
          {
            "expr": "sum(increase(llm_cost_dollars[24h])) * 30"
          }
        ],
        "fieldConfig": {
          "defaults": {"unit": "currencyUSD"}
        }
      },
      {
        "title": "Cost by Model (7 days)",
        "type": "piechart",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12},
        "targets": [
          {
            "expr": "sum(increase(llm_cost_dollars[7d])) by (provider, model)",
            "legendFormat": "{{provider}}/{{model}}"
          }
        ]
      }
    ]
  }
}
```

### PostgreSQL Dashboard

```json
{
  "dashboard": {
    "title": "PostgreSQL Performance",
    "uid": "postgres",
    "tags": ["infrastructure", "database"],
    "panels": [
      {
        "title": "Active Connections",
        "type": "gauge",
        "gridPos": {"h": 6, "w": 6, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "pg_stat_activity_count{state=\"active\"}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 80}
              ]
            }
          }
        }
      },
      {
        "title": "Cache Hit Ratio",
        "type": "gauge",
        "gridPos": {"h": 6, "w": 6, "x": 6, "y": 0},
        "targets": [
          {
            "expr": "pg_stat_database_blks_hit{datname=\"kosmos\"} / (pg_stat_database_blks_hit{datname=\"kosmos\"} + pg_stat_database_blks_read{datname=\"kosmos\"}) * 100"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 90},
                {"color": "green", "value": 99}
              ]
            }
          }
        }
      },
      {
        "title": "Transactions/sec",
        "type": "timeseries",
        "gridPos": {"h": 6, "w": 12, "x": 12, "y": 0},
        "targets": [
          {
            "expr": "rate(pg_stat_database_xact_commit{datname=\"kosmos\"}[5m])",
            "legendFormat": "Commits"
          },
          {
            "expr": "rate(pg_stat_database_xact_rollback{datname=\"kosmos\"}[5m])",
            "legendFormat": "Rollbacks"
          }
        ]
      },
      {
        "title": "Query Duration",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 6},
        "targets": [
          {
            "expr": "histogram_quantile(0.99, sum(rate(pg_stat_statements_seconds_bucket[5m])) by (le))",
            "legendFormat": "P99"
          },
          {
            "expr": "histogram_quantile(0.50, sum(rate(pg_stat_statements_seconds_bucket[5m])) by (le))",
            "legendFormat": "P50"
          }
        ],
        "fieldConfig": {
          "defaults": {"unit": "s"}
        }
      },
      {
        "title": "Replication Lag",
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 6},
        "targets": [
          {
            "expr": "pg_replication_lag_bytes",
            "legendFormat": "Lag (bytes)"
          }
        ],
        "fieldConfig": {
          "defaults": {"unit": "bytes"}
        }
      }
    ]
  }
}
```

---

## Alert Annotations

Grafana dashboards integrate with Alertmanager alerts:

```json
{
  "annotations": {
    "list": [
      {
        "name": "Alerts",
        "datasource": "Prometheus",
        "enable": true,
        "expr": "ALERTS{alertstate=\"firing\"}",
        "titleFormat": "{{alertname}}",
        "textFormat": "{{alertname}}: {{message}}"
      }
    ]
  }
}
```

---

## Operations

### Export Dashboard

```bash
# Export dashboard JSON
curl -H "Authorization: Bearer ${GRAFANA_TOKEN}" \
  "https://grafana.kosmos.nuvanta-holding.com/api/dashboards/uid/kosmos-overview" \
  | jq '.dashboard' > kosmos-overview.json
```

### Import Dashboard

```bash
# Import dashboard JSON
curl -X POST \
  -H "Authorization: Bearer ${GRAFANA_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @kosmos-overview.json \
  "https://grafana.kosmos.nuvanta-holding.com/api/dashboards/db"
```

### Backup All Dashboards

```bash
#!/bin/bash
# backup-dashboards.sh

GRAFANA_URL="https://grafana.kosmos.nuvanta-holding.com"
OUTPUT_DIR="./grafana-backup-$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

# Get all dashboard UIDs
UIDS=$(curl -s -H "Authorization: Bearer ${GRAFANA_TOKEN}" \
  "${GRAFANA_URL}/api/search?type=dash-db" | jq -r '.[].uid')

for uid in $UIDS; do
  echo "Exporting $uid..."
  curl -s -H "Authorization: Bearer ${GRAFANA_TOKEN}" \
    "${GRAFANA_URL}/api/dashboards/uid/${uid}" \
    | jq '.dashboard' > "${OUTPUT_DIR}/${uid}.json"
done

echo "Exported $(ls $OUTPUT_DIR | wc -l) dashboards to $OUTPUT_DIR"
```

---

## Related Documentation

- [Prometheus Setup](prometheus)
- [Alerting Rules](alerting)
- [Langfuse Integration](langfuse)

---

**Document Owner:** sre@nuvanta-holding.com

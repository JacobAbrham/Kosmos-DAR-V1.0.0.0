# Deployment Architecture

**Document Type:** Infrastructure Architecture  
**Owner:** Platform Engineering  
**Reviewers:** SRE Lead, Security Lead, Architecture Review Board  
**Review Cadence:** Quarterly  
**Last Updated:** 2025-12-13  
**Status:** 🟢 Active

---

## Executive Summary

This document defines the deployment architecture for KOSMOS across all environments, including CI/CD pipelines, release strategies, environment configurations, and operational procedures for promoting changes from development through production.

---

## Environment Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     KOSMOS Deployment Pipeline                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│   │ Development │────▶│   Staging   │────▶│ Production  │                  │
│   │   (Local)   │     │  (Preview)  │     │    (Live)   │                  │
│   └─────────────┘     └─────────────┘     └─────────────┘                  │
│         │                   │                   │                           │
│         │                   │                   │                           │
│   ┌─────┴─────┐       ┌─────┴─────┐       ┌─────┴─────┐                    │
│   │  Docker   │       │   K3s     │       │   K3s     │                    │
│   │  Compose  │       │  1 Node   │       │  3 Nodes  │                    │
│   └───────────┘       └───────────┘       └───────────┘                    │
│                                                                              │
│   Trigger:            Trigger:            Trigger:                          │
│   git push            PR merge            Manual/Tag                        │
│   to branch           to main             Release                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Environment Specifications

### Development Environment

| Attribute | Value |
|-----------|-------|
| **Infrastructure** | Docker Compose (local) |
| **Purpose** | Local development, unit testing |
| **Data** | Synthetic/seed data |
| **Access** | Developer workstation |
| **Deployment Trigger** | `docker-compose up` |

```yaml
# docker-compose.yml (development)
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: kosmos
      POSTGRES_USER: kosmos
      POSTGRES_PASSWORD: dev-password
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data

  dragonfly:
    image: docker.dragonflydb.io/dragonflydb/dragonfly:v1.15.1
    ports:
      - "6379:6379"

  nats:
    image: nats:2.10-alpine
    command: ["--jetstream", "--store_dir=/data"]
    ports:
      - "4222:4222"
      - "8222:8222"
    volumes:
      - nats-data:/data

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio-data:/data

  zeus:
    build:
      context: .
      dockerfile: Dockerfile.dev
    environment:
      - ENVIRONMENT=development
      - POSTGRES_HOST=postgres
      - DRAGONFLY_HOST=dragonfly
      - NATS_URL=nats://nats:4222
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      - postgres
      - dragonfly
      - nats

volumes:
  postgres-data:
  nats-data:
  minio-data:
```

### Staging Environment

| Attribute | Value |
|-----------|-------|
| **Infrastructure** | K3s Single Node (Alibaba Cloud) |
| **Purpose** | Integration testing, UAT, preview |
| **Data** | Anonymized production subset |
| **Access** | Internal team + stakeholders |
| **Deployment Trigger** | PR merge to `main` |
| **URL** | `https://staging.kosmos.nuvanta-holding.com` |

### Production Environment

| Attribute | Value |
|-----------|-------|
| **Infrastructure** | K3s HA Cluster (3 nodes, Alibaba Cloud) |
| **Purpose** | Live production workloads |
| **Data** | Production data |
| **Access** | End users |
| **Deployment Trigger** | Git tag / manual approval |
| **URL** | `https://kosmos.nuvanta-holding.com` |

---

## CI/CD Pipeline

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CI/CD Pipeline Flow                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │  Commit  │───▶│   Build  │───▶│   Test   │───▶│   Scan   │          │
│  │          │    │          │    │          │    │          │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│                                                        │                 │
│                                                        ▼                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │  Deploy  │◀───│ Approve  │◀───│  Stage   │◀───│  Publish │          │
│  │  Prod    │    │ (Manual) │    │  Deploy  │    │  Image   │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│       │                                                                  │
│       ▼                                                                  │
│  ┌──────────┐    ┌──────────┐                                           │
│  │  Canary  │───▶│  Promote │                                           │
│  │  (10%)   │    │  (100%)  │                                           │
│  └──────────┘    └──────────┘                                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: KOSMOS CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]

env:
  REGISTRY: registry.cn-shanghai.aliyuncs.com
  IMAGE_NAME: nuvanta/kosmos

jobs:
  # ============================================
  # Stage 1: Build and Test
  # ============================================
  build:
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.meta.outputs.tags }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          ruff check .
          mypy src/

      - name: Run unit tests
        run: |
          pytest tests/unit -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: coverage.xml

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Alibaba Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.ALIBABA_REGISTRY_USER }}
          password: ${{ secrets.ALIBABA_REGISTRY_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha,prefix=

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ============================================
  # Stage 2: Security Scanning
  # ============================================
  security-scan:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ needs.build.outputs.image_tag }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run Snyk container scan
        uses: snyk/actions/docker@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          image: ${{ needs.build.outputs.image_tag }}
          args: --severity-threshold=high

  # ============================================
  # Stage 3: Deploy to Staging
  # ============================================
  deploy-staging:
    needs: [build, security-scan]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.28.0'

      - name: Configure kubeconfig
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.STAGING_KUBECONFIG }}" | base64 -d > ~/.kube/config

      - name: Pull secrets from Infisical
        uses: infisical/actions@v1
        with:
          token: ${{ secrets.INFISICAL_TOKEN }}
          env: staging
          projectSlug: kosmos

      - name: Deploy to staging
        run: |
          helm upgrade --install kosmos ./helm/kosmos \
            --namespace kosmos-core \
            --set image.tag=${{ needs.build.outputs.image_tag }} \
            --set environment=staging \
            --values ./helm/kosmos/values-staging.yaml \
            --wait --timeout 10m

      - name: Run smoke tests
        run: |
          ./scripts/smoke-test.sh staging

      - name: Notify deployment
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "✅ Staging deployment successful: ${{ needs.build.outputs.image_tag }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

  # ============================================
  # Stage 4: Deploy to Production (Manual Gate)
  # ============================================
  deploy-production:
    needs: [build, deploy-staging]
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure kubeconfig
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.PROD_KUBECONFIG }}" | base64 -d > ~/.kube/config

      - name: Pull secrets from Infisical
        uses: infisical/actions@v1
        with:
          token: ${{ secrets.INFISICAL_TOKEN }}
          env: production
          projectSlug: kosmos

      - name: Deploy canary (10%)
        run: |
          helm upgrade --install kosmos ./helm/kosmos \
            --namespace kosmos-core \
            --set image.tag=${{ needs.build.outputs.image_tag }} \
            --set environment=production \
            --set canary.enabled=true \
            --set canary.weight=10 \
            --values ./helm/kosmos/values-production.yaml \
            --wait --timeout 10m

      - name: Monitor canary metrics
        run: |
          ./scripts/canary-analysis.sh --duration 10m --threshold 99.5

      - name: Promote to 100%
        run: |
          helm upgrade --install kosmos ./helm/kosmos \
            --namespace kosmos-core \
            --set image.tag=${{ needs.build.outputs.image_tag }} \
            --set environment=production \
            --set canary.enabled=false \
            --values ./helm/kosmos/values-production.yaml \
            --wait --timeout 10m

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
```

---

## Release Strategy

### Semantic Versioning

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

Examples:
  1.0.0        - Initial release
  1.1.0        - New feature (backward compatible)
  1.1.1        - Bug fix
  2.0.0        - Breaking change
  1.2.0-beta.1 - Pre-release
  1.2.0+build.123 - Build metadata
```

### Release Types

| Type | Trigger | Approval | Canary | Rollback Window |
|------|---------|----------|--------|-----------------|
| **Hotfix** | `hotfix/*` branch | Tech Lead | No | Immediate |
| **Patch** | `v*.*.X` tag | Tech Lead | 5 min | 1 hour |
| **Minor** | `v*.X.0` tag | Tech Lead + PM | 10 min | 4 hours |
| **Major** | `vX.0.0` tag | CTO + Architecture | 30 min | 24 hours |

### Release Checklist

```markdown
## Release Checklist: v[X.Y.Z]

### Pre-Release
- [ ] All tests passing on main branch
- [ ] Security scan completed (no critical vulnerabilities)
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] Database migrations tested
- [ ] Feature flags configured
- [ ] Rollback plan documented

### Release
- [ ] Create release tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Push tag: `git push origin vX.Y.Z`
- [ ] Monitor staging deployment
- [ ] Approve production deployment
- [ ] Monitor canary phase
- [ ] Verify production health

### Post-Release
- [ ] Announce in #releases channel
- [ ] Update status page
- [ ] Close release milestone
- [ ] Schedule retrospective (major releases)
```

---

## Canary Deployment

### Argo Rollouts Configuration

```yaml
# rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: zeus-orchestrator
  namespace: kosmos-core
spec:
  replicas: 3
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: zeus-orchestrator
  strategy:
    canary:
      canaryService: zeus-canary
      stableService: zeus-stable
      trafficRouting:
        traefik:
          weightedTrafficRouting:
            canaryService: zeus-canary
            stableService: zeus-stable
      steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - analysis:
          templates:
          - templateName: success-rate
          args:
          - name: service-name
            value: zeus-orchestrator
      - setWeight: 30
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100
      rollbackWindow:
        revisions: 2
  template:
    metadata:
      labels:
        app: zeus-orchestrator
    spec:
      containers:
      - name: zeus
        image: registry.cn-shanghai.aliyuncs.com/nuvanta/kosmos:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "200m"
            memory: "512Mi"
          limits:
            cpu: "1"
            memory: "2Gi"
```

### Analysis Template

```yaml
# analysis-template.yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
  namespace: kosmos-core
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 1m
    successCondition: result[0] >= 0.995
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus.kosmos-observability:9090
        query: |
          sum(rate(http_requests_total{service="{{args.service-name}}",status=~"2.."}[5m]))
          /
          sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))
  - name: latency-p99
    interval: 1m
    successCondition: result[0] <= 500
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus.kosmos-observability:9090
        query: |
          histogram_quantile(0.99, 
            sum(rate(http_request_duration_seconds_bucket{service="{{args.service-name}}"}[5m])) 
            by (le)
          ) * 1000
```

---

## Rollback Procedures

### Automatic Rollback

Argo Rollouts automatically triggers rollback when:
- Analysis metrics fail threshold
- Pod health checks fail
- Manual abort triggered

### Manual Rollback

```bash
# Option 1: Argo Rollouts abort
kubectl argo rollouts abort zeus-orchestrator -n kosmos-core

# Option 2: Argo Rollouts undo
kubectl argo rollouts undo zeus-orchestrator -n kosmos-core

# Option 3: Helm rollback
helm rollback kosmos 1 -n kosmos-core

# Option 4: Direct image update (emergency)
kubectl set image deployment/zeus-orchestrator \
  zeus=registry.cn-shanghai.aliyuncs.com/nuvanta/kosmos:v1.2.3 \
  -n kosmos-core
```

### Rollback Verification

```bash
# Check rollout status
kubectl argo rollouts status zeus-orchestrator -n kosmos-core

# Verify running version
kubectl get pods -n kosmos-core -o jsonpath='{.items[*].spec.containers[*].image}'

# Check health endpoints
curl https://api.kosmos.nuvanta-holding.com/health

# Verify metrics
curl -s http://prometheus:9090/api/v1/query?query=kosmos_version_info
```

---

## Configuration Management

### Helm Values Structure

```
helm/kosmos/
├── Chart.yaml
├── values.yaml              # Default values
├── values-development.yaml  # Dev overrides
├── values-staging.yaml      # Staging overrides
├── values-production.yaml   # Production overrides
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secret.yaml
    └── hpa.yaml
```

### Environment-Specific Configuration

```yaml
# values-production.yaml
replicaCount: 3

image:
  repository: registry.cn-shanghai.aliyuncs.com/nuvanta/kosmos
  pullPolicy: IfNotPresent

resources:
  requests:
    cpu: "500m"
    memory: "1Gi"
  limits:
    cpu: "2"
    memory: "4Gi"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilization: 70

ingress:
  enabled: true
  className: traefik
  hosts:
    - host: api.kosmos.nuvanta-holding.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: kosmos-tls
      hosts:
        - api.kosmos.nuvanta-holding.com

env:
  ENVIRONMENT: production
  LOG_LEVEL: INFO
  OTEL_EXPORTER_OTLP_ENDPOINT: http://jaeger-collector:4317
```

---

## Database Migrations

### Migration Strategy

```bash
# Migrations run as a Kubernetes Job before deployment
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: kosmos-migrate-$(date +%s)
  namespace: kosmos-core
spec:
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      containers:
      - name: migrate
        image: registry.cn-shanghai.aliyuncs.com/nuvanta/kosmos:${TAG}
        command: ["alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: url
      restartPolicy: Never
  backoffLimit: 3
EOF
```

### Migration Best Practices

1. **Backward Compatible**: Migrations must be backward compatible with N-1 version
2. **Additive First**: Add columns/tables before removing old ones
3. **Two-Phase Drops**: Mark deprecated → deploy → remove in next release
4. **Test in Staging**: All migrations tested against production data copy

---

## Feature Flags

### LaunchDarkly Integration

```python
# feature_flags.py
from launchdarkly_server_sdk import LDClient, Config

ld_client = LDClient(Config(os.getenv("LAUNCHDARKLY_SDK_KEY")))

def is_feature_enabled(flag_key: str, user_context: dict) -> bool:
    """Check if feature is enabled for user."""
    return ld_client.variation(
        flag_key,
        {"key": user_context.get("user_id", "anonymous")},
        default=False
    )

# Usage
if is_feature_enabled("new-agent-routing", {"user_id": user.id}):
    # New routing logic
    pass
else:
    # Existing routing logic
    pass
```

### Feature Flag Lifecycle

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Created   │───▶│  Rollout    │───▶│  Enabled    │───▶│  Removed    │
│   (0%)      │    │ (10%→100%)  │    │   (100%)    │    │  (Cleaned)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Related Documentation

- [Kubernetes Architecture](kubernetes.md)
- [Disaster Recovery](disaster-recovery.md)
- [ADR-003: Deployment Pipeline](../../02-architecture/adr/ADR-003-deployment-pipeline.md)
- [Canary Playbooks](../../03-engineering/canary-playbooks.md)

---

**Document Owner:** platform-engineering@nuvanta-holding.com  
**Emergency Contact:** oncall@nuvanta-holding.com

# KOSMOS Infrastructure

This directory contains all infrastructure-as-code for KOSMOS deployment.

## Structure

```
infrastructure/
├── docker/              # Container definitions
│   ├── backend/        # FastAPI application
│   └── frontend/       # Next.js application
├── kubernetes/         # Kubernetes manifests
│   ├── base/          # Kustomize base configurations
│   ├── overlays/      # Environment-specific overlays
│   │   ├── development/
│   │   ├── staging/
│   │   └── production/
│   └── raw-manifests/ # Original K8s YAML files
├── helm/              # Helm charts
│   └── kosmos/        # KOSMOS application chart
├── monitoring/        # Observability stack
│   ├── prometheus/    # Metrics and alerting
│   └── grafana/       # Dashboards
└── terraform/         # Cloud infrastructure (if using)
```

## Deployment Approaches

### Docker Compose (Development)
```bash
docker-compose -f config/environments/development/docker-compose.yml up
```

### Kubernetes (Staging/Production)
```bash
# Using Kustomize
kubectl apply -k infrastructure/kubernetes/overlays/staging

# Using Helm
helm upgrade --install kosmos infrastructure/helm/kosmos \
  -f infrastructure/helm/kosmos/values-staging.yaml
```

## Monitoring

Prometheus and Grafana configurations are in `monitoring/`:
- Custom dashboards for KOSMOS metrics
- Alert rules for agent performance
- Service mesh observability

## Best Practices

1. **Use Kustomize overlays** for environment-specific configs
2. **Version Helm charts** properly (semver)
3. **Test locally** with Docker Compose first
4. **Review security policies** before deploying
5. **Monitor resource usage** in production

## Related Documentation

- [Deployment Guide](../docs/deployment/DEPLOYMENT_SUMMARY.md)
- [Getting Started](../docs/deployment/GETTING_STARTED.md)
- [Kubernetes Setup](../docs/guides/DEVELOPMENT_ENVIRONMENT_GUIDE.md)

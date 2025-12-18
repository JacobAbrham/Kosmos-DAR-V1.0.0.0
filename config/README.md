# KOSMOS Configuration

This directory contains environment-specific configuration files.

## Structure

```
config/
├── environments/
│   ├── development/
│   │   ├── .env.example        # Development environment variables
│   │   └── docker-compose.yml  # Local development stack
│   ├── staging/
│   │   └── .env.example        # Staging environment variables
│   └── production/
│       └── .env.example        # Production environment variables
├── shared/
│   └── base-values.yaml        # Shared Helm values
└── secrets/                    # Git-ignored, local secrets only
    └── .gitkeep
```

## Usage

### Development
```bash
cp config/environments/development/.env.example .env
# Edit .env with your local values
docker-compose -f config/environments/development/docker-compose.yml up
```

### Staging/Production
Use Infisical or GitHub Secrets for credential management.

**Never commit actual .env files with credentials!**

## Environment Variables

Each environment has different requirements:

- **Development**: Uses `kosmos_dev` database, minimal security
- **Staging**: Uses `kosmos_staging` database, similar to production
- **Production**: Uses `kosmos_prod` database, strict security settings

## Secrets Management

For production deployments:
1. Use Infisical for centralized secrets
2. Use GitHub Secrets for CI/CD
3. Use Kubernetes Secrets for cluster deployments
4. Never store secrets in Git

## Adding New Config

When adding environment variables:
1. Add to all three `.env.example` files
2. Use `CHANGEME` placeholder for secrets
3. Document the variable purpose
4. Update this README

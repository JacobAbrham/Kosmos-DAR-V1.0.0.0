# ADR-002: Version Control Strategy

**Status:** Accepted  
**Date:** 2025-12-11  
**Deciders:** Chief Technology Officer, Engineering Leadership, DevOps Team  
**Technical Story:** [KOSMOS-VCS-001] Need for robust version control and collaboration workflow

---

## Context and Problem Statement

KOSMOS requires a version control strategy that supports:

- **Collaboration:** Multiple teams contributing to codebase and documentation
- **Code Review:** Mandatory review process for all changes
- **Branch Management:** Clear branching strategy for features, releases, hotfixes
- **Compliance:** Audit trail of all changes (ISO 42001, GDPR Article 30)
- **CI/CD Integration:** Automated testing and deployment
- **Security:** Access control and secrets management
- **Disaster Recovery:** Protection against data loss
- **Scale:** Support for growing team and codebase

The key decisions are:

1. **Which Git hosting platform?** (GitHub, GitLab, Bitbucket, self-hosted)
2. **What branching strategy?** (Git Flow, GitHub Flow, Trunk-Based Development)
3. **What commit conventions?** (Conventional Commits, custom format)
4. **What merge strategy?** (Merge commits, squash, rebase)

---

## Decision Drivers

- **Team Familiarity:** Minimize learning curve
- **Integration Ecosystem:** CI/CD, security scanning, project management
- **Cost:** Balance features vs. budget
- **Security:** Advanced security features (branch protection, required reviews)
- **Compliance:** Audit logs and retention
- **Performance:** Fast for large repositories
- **Reliability:** 99.9%+ uptime SLA
- **Support:** Quality of documentation and customer support

---

## Decision 1: Git Hosting Platform

### Considered Options

#### Option 1: GitHub ⭐ (Selected)

**Pros:**
- ✅ Industry standard (90% market share for open source)
- ✅ Excellent CI/CD (GitHub Actions)
- ✅ Advanced security features (Dependabot, secret scanning, code scanning)
- ✅ Best-in-class collaboration (PRs, discussions, code review)
- ✅ Large ecosystem of integrations
- ✅ GitHub Copilot integration
- ✅ Strong compliance features (audit logs, SAML SSO)
- ✅ Reliable (99.95% uptime)

**Cons:**
- ❌ Pricing increases with team size
- ❌ Vendor lock-in (but Git is portable)

**Cost:** $0-21/user/month (Team plan: $4/user/month recommended)

---

#### Option 2: GitLab

**Pros:**
- ✅ All-in-one DevOps platform
- ✅ Built-in CI/CD (GitLab CI)
- ✅ Self-hosted option
- ✅ Good security scanning
- ✅ Project management features

**Cons:**
- ❌ Steeper learning curve
- ❌ Smaller ecosystem vs. GitHub
- ❌ UI less polished
- ❌ Self-hosted adds operational burden

**Cost:** $0-99/user/month (Premium: $29/user/month)

**Decision:** Rejected - team prefers GitHub's ecosystem and familiarity

---

#### Option 3: Bitbucket

**Pros:**
- ✅ Atlassian integration (Jira, Confluence)
- ✅ Good for Atlassian ecosystem users
- ✅ Competitive pricing

**Cons:**
- ❌ Smaller community vs. GitHub/GitLab
- ❌ Limited marketplace integrations
- ❌ CI/CD (Pipelines) less mature than GitHub Actions

**Cost:** $0-15/user/month

**Decision:** Rejected - limited ecosystem compared to GitHub

---

#### Option 4: Self-Hosted (Gitea, Gogs, GitLab CE)

**Pros:**
- ✅ Full control over infrastructure
- ✅ No per-user costs
- ✅ Data sovereignty

**Cons:**
- ❌ High operational burden
- ❌ Security responsibility on team
- ❌ Maintenance overhead
- ❌ Limited integrations
- ❌ Backup and DR complexity

**Cost:** Infrastructure costs ($200-500/month)

**Decision:** Rejected - operational burden outweighs benefits

---

### Decision Outcome: GitHub

**Rationale:**
- Team already familiar with GitHub
- Best CI/CD integration (GitHub Actions)
- Superior security scanning and Dependabot
- Largest ecosystem and community
- Compliance features meet requirements
- Cost-effective for team size

---

## Decision 2: Branching Strategy

### Considered Options

#### Option 1: GitHub Flow ⭐ (Selected)

**Model:**
```
main (production-ready)
  ↓
feature/KOSMOS-123-add-ethics-scorecard → PR → main
  ↓
hotfix/fix-critical-bug → PR → main
```

**Rules:**
- `main` branch is always deployable
- Create feature branch from `main`
- Open PR when ready for review
- Deploy from `main` after merge

**Pros:**
- ✅ Simple and easy to understand
- ✅ Continuous deployment friendly
- ✅ Minimal overhead
- ✅ Clear linear history

**Cons:**
- ❌ Less suitable for versioned releases
- ❌ All changes deploy immediately

**Best For:** SaaS applications, continuous deployment

---

#### Option 2: Git Flow

**Model:**
```
main (production)
  ↓
develop
  ↓
feature/xyz → develop → release/v1.2.0 → main (tag v1.2.0)
  ↓
hotfix/xyz → main (tag v1.2.1)
```

**Pros:**
- ✅ Clear release process
- ✅ Parallel development of multiple versions
- ✅ Explicit release branches

**Cons:**
- ❌ Complex for continuous deployment
- ❌ More branches to manage
- ❌ Overhead for fast-moving projects

**Best For:** Versioned software releases, traditional software

**Decision:** Rejected - too complex for documentation and SaaS model

---

#### Option 3: Trunk-Based Development

**Model:**
```
main (trunk)
  ↓
Short-lived feature branches (<1 day) → main
Feature flags for incomplete features
```

**Pros:**
- ✅ Maximum simplicity
- ✅ Encourages small commits
- ✅ Fastest feedback loop

**Cons:**
- ❌ Requires feature flags
- ❌ Higher discipline required
- ❌ Less suitable for distributed teams

**Best For:** Highly disciplined teams, microservices

**Decision:** Rejected - team prefers PR-based review process

---

### Decision Outcome: GitHub Flow (Modified)

**Branch Naming Convention:**
```
main                           # Production-ready code
feature/<ticket>-<description> # New features
fix/<ticket>-<description>     # Bug fixes
docs/<ticket>-<description>    # Documentation changes
refactor/<description>         # Code refactoring
hotfix/<description>           # Emergency fixes
```

**Examples:**
- `feature/KOSMOS-123-add-risk-registry`
- `fix/KOSMOS-456-correct-typo-in-adr`
- `docs/update-deployment-guide`
- `hotfix/fix-broken-build`

---

## Decision 3: Commit Message Convention

### Selected: Conventional Commits

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `perf`: Performance improvements

**Examples:**

```
feat(governance): add AI Ethics Scorecard

- Define 5 fairness metrics
- Integrate with RAGAS
- Add automated alerts

Closes #123
```

```
fix(risk-registry): correct risk score calculation

The likelihood × impact formula was using wrong scale.
Changed from 1-10 to 1-5 as per NIST AI RMF.

Fixes #456
```

```
docs(adr): create ADR-001 for documentation framework

Document decision to use MkDocs with Material theme
over alternatives like Docusaurus and GitBook.
```

**Validation:** Pre-commit hook enforces format

---

## Decision 4: Merge Strategy

### Selected: Squash and Merge (Default)

**Options:**

#### 1. Merge Commit (Create a merge commit)
```
* Merge pull request #123
|\
| * commit 3
| * commit 2
| * commit 1
|/
* previous commit
```

**Pros:** Preserves full history  
**Cons:** Cluttered history with many merge commits

---

#### 2. Squash and Merge ⭐ (Selected)
```
* feat(governance): add AI Ethics Scorecard (#123)
* previous commit
```

**Pros:**
- ✅ Clean, linear history
- ✅ One commit per feature
- ✅ Easy to revert
- ✅ Clear changelog

**Cons:**
- ❌ Loses individual commit history (but preserved in PR)

**When to use:** Most PRs (default)

---

#### 3. Rebase and Merge
```
* commit 3 (from PR)
* commit 2 (from PR)
* commit 1 (from PR)
* previous commit
```

**Pros:**
- ✅ Linear history
- ✅ Preserves individual commits

**Cons:**
- ❌ Requires clean commit history
- ❌ More complex for contributors

**When to use:** Hotfixes with single, well-crafted commit

---

### Strategy by Branch Type

| Branch Type | Merge Strategy | Rationale |
|-------------|----------------|-----------|
| `feature/*` | Squash and Merge | Clean history, one commit per feature |
| `fix/*` | Squash and Merge | Clean history, clear revert point |
| `docs/*` | Squash and Merge | Clean history |
| `hotfix/*` | Rebase and Merge (if single commit) | Preserve urgency context |

---

## Branch Protection Rules

### `main` Branch Protection

**Required:**
- [x] Require pull request reviews (minimum: 1)
- [x] Dismiss stale reviews on new commits
- [x] Require status checks to pass
  - [x] `build` (mkdocs build)
  - [x] `lint` (markdown linting)
  - [x] `test` (validation scripts)
- [x] Require branches to be up to date before merging
- [x] Require signed commits
- [x] Include administrators (no bypass)
- [x] Restrict who can push to matching branches

**Optional:**
- [ ] Require code owner review (enable when CODEOWNERS defined)
- [ ] Restrict force pushes (enabled by default)
- [ ] Allow deletion (disabled)

---

## Code Review Process

### Pull Request Template

```markdown
## Description
<!-- Describe the changes in this PR -->

## Type of Change
- [ ] Feature (new functionality)
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring
- [ ] Hotfix

## Testing
<!-- How was this tested? -->

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No new warnings
- [ ] Dependent changes merged

## Related Issues
Closes #<issue_number>
```

### Review Guidelines

**Approval Requirements:**
- **1 approval minimum** (default)
- **2 approvals for high-risk changes:**
  - Security-related code
  - Compliance documentation
  - Kill switch modifications
  - Data retention policies

**Review Checklist:**
- [ ] Code quality and readability
- [ ] Security vulnerabilities
- [ ] Performance implications
- [ ] Test coverage
- [ ] Documentation accuracy
- [ ] Breaking changes documented

**Review SLA:**
- **Standard PRs:** Review within 24 hours
- **Hotfixes:** Review within 2 hours
- **Draft PRs:** No SLA (for early feedback)

---

## Git Commit Signature Verification

**Requirement:** All commits must be signed

**Setup:**

```bash
# Generate GPG key
gpg --full-generate-key

# Configure Git
git config --global user.signingkey <key-id>
git config --global commit.gpgsign true

# Add to GitHub
gpg --armor --export <key-id>
# Paste into GitHub Settings > SSH and GPG keys
```

**Verification:**
- Commits show "Verified" badge on GitHub
- Unsigned commits rejected by branch protection

---

## Repository Structure

### Mono-repo vs. Multi-repo

**Decision: Multi-repo Strategy**

**Repositories:**

1. **kosmos-docs** (Documentation - this repo)
   - Living Constitution
   - ADRs
   - Runbooks

2. **kosmos-core** (Core AI orchestration service)
   - Python FastAPI application
   - LLM router
   - Guardrails service

3. **kosmos-web** (Web application)
   - React/Next.js frontend
   - User interface

4. **kosmos-infrastructure** (IaC)
   - Terraform configurations
   - Kubernetes manifests
   - Helm charts

5. **kosmos-sdk** (Client SDKs)
   - Python SDK
   - JavaScript SDK
   - Go SDK

**Rationale:**
- Clear separation of concerns
- Independent versioning
- Smaller, focused repositories
- Easier CI/CD per component

---

## Access Control

### Repository Permissions

**Roles:**

| Role | Permissions | Members |
|------|-------------|---------|
| Admin | All permissions | CTO, Engineering Directors |
| Maintainer | Merge PRs, manage issues | Engineering Leads |
| Write | Create branches, open PRs | All Engineers |
| Read | View repository | External auditors, contractors |

**Team Structure:**
- `@kosmos/core-team` - Write access to all repos
- `@kosmos/docs-team` - Admin access to kosmos-docs
- `@kosmos/security-team` - Admin access for security reviews

---

## Compliance and Audit

### Audit Log Retention

**GitHub Enterprise Features:**
- Audit log API enabled
- 180-day audit log retention
- SAML SSO for authentication
- IP allow lists for sensitive repos

**Audit Events Tracked:**
- Repo access changes
- Branch protection changes
- Member additions/removals
- Secrets changes
- Deploy key modifications

**Export Schedule:** Monthly export to S3 for long-term storage (3 years)

---

## Backup and Disaster Recovery

### Backup Strategy

**GitHub as Source of Truth:**
- GitHub provides automatic backups
- 99.95% uptime SLA
- Geo-redundant storage

**Additional Backups:**
- **Daily:** Mirror to GitLab (secondary backup)
- **Weekly:** Export to S3 (archive)
- **Monthly:** Full repo clone to on-prem storage

**Recovery Procedures:**
1. Restore from GitHub (primary)
2. Restore from GitLab mirror (if GitHub unavailable)
3. Restore from S3 archive (if both unavailable)

**Recovery Time Objective (RTO):** 1 hour  
**Recovery Point Objective (RPO):** 24 hours

---

## Integration with CI/CD

### GitHub Actions Workflows

**Automated on Push:**
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build documentation
        run: mkdocs build --strict
      
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint markdown
        run: markdownlint '**/*.md'
      
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: [build, lint]
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Cloudflare Pages
        run: mkdocs build && deploy.sh
```

**See:** [ADR-003: Deployment Pipeline Architecture](ADR-003-deployment-pipeline.md)

---

## Migration Path

### From Current State to Target State

**Current:** Repository initialized, some commits made

**Migration Steps:**
1. ✅ Create branch protection rules on `main`
2. ⏳ Set up commit signing for all contributors
3. ⏳ Configure GitHub Actions workflows
4. ⏳ Create CODEOWNERS file
5. ⏳ Set up GitLab mirror
6. ⏳ Document workflow in CONTRIBUTING.md

**Timeline:** Complete by January 2026

---

## Consequences

### Positive

- ✅ **Clear Process:** Everyone follows same workflow
- ✅ **Code Quality:** Mandatory reviews improve quality
- ✅ **Compliance:** Audit trail meets regulatory requirements
- ✅ **Security:** Signed commits and branch protection
- ✅ **Automation:** CI/CD reduces manual work
- ✅ **Collaboration:** PRs facilitate knowledge sharing

### Negative

- ⚠️ **Learning Curve:** New contributors must learn workflow
- ⚠️ **Overhead:** PR process adds time vs. direct commits
- ⚠️ **Cost:** GitHub Team plan ($4/user/month)

### Neutral

- 📊 **Centralization:** GitHub as single point of collaboration (mitigated with backups)

---

## Alternatives Considered

### Alternative Workflows

**Not Selected:**
- **Git Flow:** Too complex for our needs
- **Trunk-Based Development:** Requires feature flags infrastructure
- **No PRs/Direct Commits:** Unacceptable for compliance and quality

---

## Related Decisions

- [ADR-001: Documentation Framework Selection](ADR-001-documentation-framework.md)
- [ADR-003: Deployment Pipeline Architecture](ADR-003-deployment-pipeline.md)

---

## References

### External Resources

- **GitHub Flow:** https://guides.github.com/introduction/flow/
- **Conventional Commits:** https://www.conventionalcommits.org/
- **Git Best Practices:** https://git-scm.com/book/en/v2

### Internal Documents

- [CONTRIBUTING.md](https://github.com/Nuvanta-Holding/kosmos-docs/blob/main/CONTRIBUTING.md) (to be created)
- [.github/PULL_REQUEST_TEMPLATE.md](https://github.com/Nuvanta-Holding/kosmos-docs/blob/main/.github/PULL_REQUEST_TEMPLATE.md) (to be created)

---

## Change Log

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2025-12-11 | 1.0 | Architecture Team | Initial decision document |

---

**Decision Owner:** Chief Technology Officer  
**Implementation Lead:** DevOps Lead  
**Review Date:** 2026-06-11 (6 months)

---

**Notes:**

This ADR can be revised if:
- Team size grows significantly (may need stricter controls)
- Compliance requirements change
- GitHub pricing becomes prohibitive
- Better alternatives emerge

**Current Status:**
- GitHub repository: ✅ Created
- Branch protection: ✅ Enabled
- Commit signing: ⏳ In progress
- CI/CD: ⏳ In progress (see ADR-003)

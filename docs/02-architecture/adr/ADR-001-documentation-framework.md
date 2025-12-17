# ADR-001: Documentation Framework Selection

**Status:** Accepted  
**Date:** 2025-12-11  
**Deciders:** Chief Technology Officer, Engineering Leadership, Documentation Team  
**Technical Story:** [KOSMOS-DOC-001] Need for centralized, maintainable technical documentation

---

## Context and Problem Statement

KOSMOS requires a comprehensive documentation system to support its AI-native operating system governance, architecture, engineering practices, operations, and human factors. The documentation must be:

- **Developer-friendly:** Easy to write and maintain by technical teams
- **Version-controlled:** Integrated with Git for history and collaboration
- **Automated:** Support CI/CD pipelines for continuous deployment
- **Searchable:** Full-text search capabilities
- **Extensible:** Support for diagrams, code samples, and technical content
- **Compliant:** Meet audit and compliance requirements (ISO 42001, EU AI Act)
- **Living Document:** Easy to update as the system evolves

The key decision is: **Which documentation framework should KOSMOS adopt?**

---

## Decision Drivers

- **Developer Experience:** Must be markdown-based for easy authoring
- **Customization:** Need branding and theming capabilities
- **Plugin Ecosystem:** Support for diagrams (Mermaid, C4), code highlighting
- **Build Speed:** Fast local development and CI/CD builds
- **Hosting Options:** Flexibility to host on GitHub Pages, Cloudflare, etc.
- **Maintenance Burden:** Minimal infrastructure to manage
- **Cost:** Prefer open-source with optional commercial support
- **Community:** Active community and long-term viability
- **Compliance:** Support for audit trails and versioning

---

## Considered Options

### Option 1: MkDocs with Material Theme ⭐ (Selected)

**Pros:**
- ✅ Markdown-based (easy for developers)
- ✅ Material theme is beautiful and professional
- ✅ Excellent plugin ecosystem (Mermaid, search, git-revision-date)
- ✅ Fast build times (~2-3 seconds for KOSMOS docs)
- ✅ Static site generation (secure, fast, cacheable)
- ✅ Free and open-source (MIT license)
- ✅ Active community and frequent updates
- ✅ Easy deployment to GitHub Pages, Cloudflare Pages
- ✅ Built-in search functionality
- ✅ Responsive design (mobile-friendly)
- ✅ Git integration for "Last Updated" timestamps

**Cons:**
- ❌ Python dependency (but team already uses Python)
- ❌ Limited WYSIWYG editing (markdown only)
- ❌ Plugin configuration can be complex

**Cost:** $0 (open-source)

---

### Option 2: Docusaurus (React-based)

**Pros:**
- ✅ React-based (modern web framework)
- ✅ Good plugin ecosystem
- ✅ Version-aware documentation
- ✅ Good search functionality (Algolia)
- ✅ Active Meta/Facebook backing

**Cons:**
- ❌ Node.js dependency (adds complexity)
- ❌ Slower build times vs. MkDocs
- ❌ More complex configuration
- ❌ Heavier runtime (React SPA)
- ❌ Learning curve for non-React developers

**Cost:** $0 (open-source)

**Decision:** Rejected due to complexity and Node.js dependency

---

### Option 3: GitBook

**Pros:**
- ✅ Beautiful UI out of the box
- ✅ WYSIWYG editor available
- ✅ Good collaboration features
- ✅ Version control built-in
- ✅ Cloud hosting included

**Cons:**
- ❌ Commercial pricing ($12-29/user/month)
- ❌ Vendor lock-in (proprietary platform)
- ❌ Limited customization
- ❌ Must use GitBook hosting OR self-host (complex)
- ❌ Less flexibility than static site generators

**Cost:** $12-29/user/month

**Decision:** Rejected due to cost and vendor lock-in

---

### Option 4: Sphinx (Python Documentation Generator)

**Pros:**
- ✅ Industry standard for Python projects
- ✅ Excellent code documentation integration
- ✅ ReStructuredText support
- ✅ Strong plugin ecosystem
- ✅ Autodoc for API documentation

**Cons:**
- ❌ ReStructuredText is less intuitive than Markdown
- ❌ Steeper learning curve
- ❌ Older, less modern UI
- ❌ Slower adoption for non-Python projects
- ❌ Theme customization is complex

**Cost:** $0 (open-source)

**Decision:** Rejected due to ReStructuredText requirement and complexity

---

### Option 5: Confluence (Enterprise Wiki)

**Pros:**
- ✅ Full-featured wiki
- ✅ WYSIWYG editing
- ✅ Collaboration features (comments, mentions)
- ✅ Permission management
- ✅ Atlassian ecosystem integration

**Cons:**
- ❌ Commercial pricing ($5.75-11/user/month)
- ❌ Not Git-native (separate version control)
- ❌ Proprietary format (vendor lock-in)
- ❌ Heavier infrastructure requirements
- ❌ Not CI/CD friendly
- ❌ Poor markdown support

**Cost:** $5.75-11/user/month

**Decision:** Rejected due to lack of Git integration and cost

---

## Decision Outcome

**Chosen Option: MkDocs with Material Theme**

### Rationale

MkDocs with the Material theme provides the optimal balance of:

1. **Developer Experience:** Markdown is ubiquitous and easy to learn
2. **Build Performance:** 2-3 second builds enable rapid iteration
3. **Cost:** $0 with no vendor lock-in
4. **Extensibility:** Rich plugin ecosystem (Mermaid, search, git integration)
5. **Deployment:** Simple static site hosting (Cloudflare Pages, GitHub Pages)
6. **Aesthetics:** Material theme is professional and modern
7. **Compliance:** Git integration provides full audit trail

### Implementation Details

**Configuration File:** `mkdocs.yml`

```yaml
site_name: KOSMOS Living Constitution
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - search.suggest
    - content.code.copy

plugins:
  - search
  - git-revision-date
  - mermaid2

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:mermaid2.fence_mermaid
  - admonition
  - tables
  - toc
```

**Deployment Target:** Cloudflare Pages (https://docs.nuvanta-holding.com)

**Build Command:** `mkdocs build`

**Build Output:** `site/` directory (static HTML/CSS/JS)

---

## Consequences

### Positive

- ✅ **Fast Development:** Developers can write docs in markdown locally
- ✅ **CI/CD Integration:** Automatic deployment on Git push
- ✅ **Version Control:** Full Git history of all documentation changes
- ✅ **Search:** Built-in full-text search (no external service needed)
- ✅ **Mobile-Friendly:** Responsive design works on all devices
- ✅ **Cost Savings:** $0/month vs. $500-2000/month for commercial alternatives
- ✅ **No Vendor Lock-in:** Can migrate to another framework if needed
- ✅ **Fast Loading:** Static site with CDN = <100ms load times

### Negative

- ⚠️ **Python Dependency:** Team must maintain Python environment
- ⚠️ **No WYSIWYG:** Non-technical stakeholders may prefer visual editor
- ⚠️ **Plugin Maintenance:** Must keep plugins updated
- ⚠️ **Limited Collaboration Features:** No inline comments/mentions (use PRs instead)

### Neutral

- 📊 **Static Site:** No dynamic features (forms, user accounts) - acceptable for documentation
- 📊 **Git Workflow:** All changes via Pull Requests - enforces review process

---

## Validation

### Acceptance Criteria

- [x] Documentation builds in <5 seconds
- [x] Supports Mermaid diagrams
- [x] Supports code syntax highlighting
- [x] Full-text search works
- [x] Mobile-responsive design
- [x] Deploys to Cloudflare Pages
- [x] Git revision dates display correctly
- [x] Custom branding (Nuvanta Holding colors/logo)

### Success Metrics

**Build Time:** 2.56 seconds ✅ (Target: <5 seconds)

**Documentation Coverage:**
- Volume I: 100% ✅
- Volume II: 40% 🟡 (in progress)
- Volume III: 40% 🟡 (in progress)
- Volume IV: 30% 🟡 (in progress)
- Volume V: 30% 🟡 (in progress)

**Developer Feedback:** 4.5/5 stars (from pilot team)

**Deployment:** Successful to https://docs.nuvanta-holding.com ✅

---

## Alternatives Considered but Not Documented Above

- **Notion:** Great UI but expensive and proprietary
- **Read the Docs:** Good for open-source projects, less flexible for corporate branding
- **VuePress:** Similar to Docusaurus, adds Vue.js dependency
- **Jekyll:** Older, slower builds, less active development

---

## Related Decisions

- [ADR-002: Version Control Strategy](ADR-002-version-control-strategy.md)
- [ADR-003: Deployment Pipeline Architecture](ADR-003-deployment-pipeline.md)

---

## References

### External Resources

- **MkDocs Documentation:** https://www.mkdocs.org
- **Material for MkDocs:** https://squidfunk.github.io/mkdocs-material
- **Mermaid Plugin:** https://github.com/fralau/mkdocs-mermaid2-plugin
- **Comparison Study:** "Static Site Generators in 2024" (internal report)

### Internal Documents

- [BUILD_PLAN.md](https://github.com/Nuvanta-Holding/kosmos-docs/blob/main/BUILD_PLAN.md)
- [GETTING_STARTED.md](https://github.com/Nuvanta-Holding/kosmos-docs/blob/main/GETTING_STARTED.md)
- [CLOUDFLARE_DEPLOYMENT.md](https://github.com/Nuvanta-Holding/kosmos-docs/blob/main/CLOUDFLARE_DEPLOYMENT.md)

---

## Change Log

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2025-12-11 | 1.0 | Architecture Team | Initial decision document |

---

**Decision Owner:** Chief Technology Officer  
**Implementation Lead:** Documentation Team Lead  
**Review Date:** 2026-06-11 (6 months)

---

**Notes:**

This ADR can be revised if:
- Build times exceed 10 seconds consistently
- Material theme stops being maintained
- Team requirements change significantly (e.g., need for WYSIWYG)
- Better alternatives emerge with compelling advantages

**Status Key:**
- **Proposed:** Under consideration
- **Accepted:** Decision made and implemented ✅
- **Deprecated:** No longer recommended
- **Superseded:** Replaced by newer ADR

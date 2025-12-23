# Docusaurus 3 Migration Plan

**Project:** KOSMOS Documentation Migration  
**From:** MkDocs Material  
**To:** Docusaurus 3 (TypeScript)  
**Timeline:** 2-3 weeks  
**Status:** Planning Phase  
**Date:** December 23, 2025

---

## Executive Summary

This plan outlines the migration of KOSMOS documentation from MkDocs Material (Python-based) to Docusaurus 3 (React/TypeScript-based) to achieve:

- ✅ **Native API documentation** with OpenAPI integration
- ✅ **First-class versioning** for release management (v1.0, v1.1, etc.)
- ✅ **Interactive components** using React from existing Next.js frontend
- ✅ **Superior search** with Algolia DocSearch
- ✅ **Enterprise scalability** for growing documentation needs

**Migration Effort:** 10-15 working days  
**Risk Level:** Low-Medium  
**Rollback Strategy:** Keep MkDocs live until Docusaurus is validated

---

## Table of Contents

1. [Migration Strategy](#migration-strategy)
2. [Phase-by-Phase Plan](#phase-by-phase-plan)
3. [Technical Architecture](#technical-architecture)
4. [File Structure Mapping](#file-structure-mapping)
5. [Content Migration](#content-migration)
6. [Feature Parity Checklist](#feature-parity-checklist)
7. [Testing & Validation](#testing--validation)
8. [Deployment Strategy](#deployment-strategy)
9. [Team Responsibilities](#team-responsibilities)
10. [Success Criteria](#success-criteria)
11. [Risk Mitigation](#risk-mitigation)
12. [Rollback Plan](#rollback-plan)

---

## Migration Strategy

### Approach: Parallel Migration with Blue-Green Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                     MIGRATION FLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Week 1: Setup & POC                                        │
│  ├─ Initialize Docusaurus                                  │
│  ├─ Configure base structure                               │
│  ├─ Migrate 10% docs as POC                               │
│  └─ Validate approach                                      │
│                                                             │
│  Week 2: Content Migration                                  │
│  ├─ Automate markdown migration                           │
│  ├─ Migrate all 214 docs                                  │
│  ├─ Configure navigation                                   │
│  └─ Integrate OpenAPI spec                                │
│                                                             │
│  Week 3: Polish & Deploy                                    │
│  ├─ Theme customization                                    │
│  ├─ Testing & QA                                           │
│  ├─ Deploy to staging                                      │
│  └─ Production cutover                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Zero downtime:** Keep MkDocs live during migration
2. **Incremental validation:** Test each phase before proceeding
3. **Automation first:** Script repetitive tasks
4. **Content fidelity:** Preserve all existing documentation
5. **Feature enhancement:** Add versioning, API docs, search

---

## Phase-by-Phase Plan

### Phase 0: Preparation (Days 1-2)

#### Day 1: Project Setup
**Duration:** 4 hours

**Tasks:**
1. ✅ Create migration branch
   ```bash
   git checkout -b feature/docusaurus-migration
   cd docs
   mkdir docusaurus-new
   ```

2. ✅ Initialize Docusaurus with TypeScript
   ```bash
   cd docusaurus-new
   npx create-docusaurus@latest . classic --typescript
   npm install
   ```

3. ✅ Install required plugins
   ```bash
   npm install --save \
     docusaurus-plugin-openapi-docs \
     docusaurus-plugin-openapi-pages \
     @docusaurus/plugin-ideal-image \
     @docusaurus/plugin-pwa \
     docusaurus-theme-search-algolia \
     @docusaurus/theme-mermaid
   ```

4. ✅ Configure base structure
   - Update `docusaurus.config.ts`
   - Configure plugins
   - Set up base theme

**Deliverable:** Working Docusaurus skeleton

#### Day 2: Content Analysis & Migration Scripts
**Duration:** 6 hours

**Tasks:**
1. ✅ Analyze existing MkDocs content
   ```bash
   # Count files by type
   find ../. -name "*.md" | wc -l
   
   # Identify frontmatter patterns
   grep -r "^---$" ../ --include="*.md" | head -20
   
   # List special features used
   grep -r "!!!" ../ --include="*.md"  # Admonitions
   grep -r "```mermaid" ../ --include="*.md"  # Diagrams
   ```

2. ✅ Create migration script
   - Script: `scripts/migrate-to-docusaurus.py`
   - Converts MkDocs frontmatter to Docusaurus
   - Transforms admonitions syntax
   - Preserves Mermaid diagrams
   - Updates internal links

3. ✅ Test script on sample docs
   - Migrate 5-10 representative docs
   - Verify rendering
   - Identify edge cases

**Deliverable:** Tested migration script

---

### Phase 1: Core Migration (Days 3-7)

#### Day 3-4: Migrate Core Documentation
**Duration:** 2 days

**Tasks:**
1. ✅ Migrate documentation structure
   ```
   docs/                                → docs/
   ├── 00-executive/                    ├── core/
   │   └── *.md                         │   ├── executive/
   ├── 01-governance/                   │   ├── governance/
   │   └── *.md                         │   ├── architecture/
   ├── 02-architecture/                 │   ├── engineering/
   │   └── *.md                         │   ├── operations/
   ├── 03-engineering/                  │   └── security/
   │   └── *.md                         └── ...
   ├── 04-operations/
   │   └── *.md
   └── ...
   ```

2. ✅ Run migration script
   ```bash
   python scripts/migrate-to-docusaurus.py \
     --source ../. \
     --target ./docs \
     --verbose
   ```

3. ✅ Manual review and fixes
   - Check images/assets
   - Verify code blocks
   - Test internal links

**Deliverable:** All markdown files migrated

#### Day 5: Configure Navigation (Sidebars)
**Duration:** 6 hours

**Tasks:**
1. ✅ Create sidebar configuration
   - File: `sidebars.ts`
   - Mirror mkdocs.yml structure
   - Add collapsible sections
   - Configure auto-generated sidebars

2. ✅ Example sidebar structure:
   ```typescript
   // sidebars.ts
   import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';
   
   const sidebars: SidebarsConfig = {
     docs: [
       {
         type: 'category',
         label: 'Quick Start',
         items: [
           'deployment/getting-started',
           'deployment/gui-quick-start',
           'deployment/deployment-summary',
         ],
       },
       {
         type: 'category',
         label: 'Core Documentation',
         collapsible: true,
         collapsed: false,
         items: [
           {
             type: 'category',
             label: 'Governance & Security',
             items: [
               'core/governance/index',
               'core/governance/raci-matrix',
               'core/governance/ethics-scorecard',
               'core/governance/risk-registry',
               'core/governance/kill-switch-protocol',
             ],
           },
           // ... more categories
         ],
       },
       // ... more sections
     ],
   };
   
   export default sidebars;
   ```

3. ✅ Test navigation
   - All links work
   - Breadcrumbs correct
   - Search works

**Deliverable:** Complete navigation structure

#### Day 6: OpenAPI Integration
**Duration:** 6 hours

**Tasks:**
1. ✅ Configure OpenAPI plugin
   ```typescript
   // docusaurus.config.ts
   {
     preset: 'classic',
     docs: {
       // ... other config
     },
     plugins: [
       [
         'docusaurus-plugin-openapi-docs',
         {
           id: 'api',
           docsPluginId: 'classic',
           config: {
             kosmos: {
               specPath: '../openapi.json',
               outputDir: 'docs/api',
               sidebarOptions: {
                 groupPathsBy: 'tag',
               },
             },
           },
         },
       ],
     ],
   }
   ```

2. ✅ Generate API docs
   ```bash
   npm run docusaurus gen-api-docs all
   ```

3. ✅ Add API sidebar
   ```typescript
   // sidebars.ts
   api: [
     {
       type: 'autogenerated',
       dirName: 'api',
     },
   ],
   ```

4. ✅ Customize API docs layout
   - Add code examples
   - Configure authentication display
   - Style request/response

**Deliverable:** Fully integrated API documentation

#### Day 7: Assets & Media
**Duration:** 4 hours

**Tasks:**
1. ✅ Migrate static assets
   ```bash
   # Copy images, diagrams, etc.
   cp -r ../images ./static/img/
   cp -r ../assets ./static/assets/
   ```

2. ✅ Update asset references
   ```bash
   # Find and replace image paths
   find docs -name "*.md" -exec sed -i 's|../images/|/img/|g' {} +
   ```

3. ✅ Optimize images
   ```bash
   # Use ideal-image plugin for responsive images
   npm run optimize-images
   ```

**Deliverable:** All assets migrated and optimized

---

### Phase 2: Enhancement (Days 8-10)

#### Day 8: Theme Customization
**Duration:** 6 hours

**Tasks:**
1. ✅ Configure brand colors
   ```typescript
   // docusaurus.config.ts
   themeConfig: {
     colorMode: {
       defaultMode: 'dark',
       disableSwitch: false,
       respectPrefersColorScheme: true,
     },
     navbar: {
       title: 'KOSMOS',
       logo: {
         alt: 'KOSMOS Logo',
         src: 'img/kosmos-logo.svg',
       },
       items: [
         {
           type: 'doc',
           docId: 'index',
           position: 'left',
           label: 'Docs',
         },
         {
           type: 'doc',
           docId: 'api/index',
           position: 'left',
           label: 'API',
         },
         {
           to: '/blog',
           label: 'Blog',
           position: 'left',
         },
         {
           type: 'docsVersionDropdown',
           position: 'right',
         },
         {
           href: 'https://github.com/JacobAbrham/Kosmos-DAR-V1.0.0.0',
           label: 'GitHub',
           position: 'right',
         },
       ],
     },
     footer: {
       style: 'dark',
       links: [
         {
           title: 'Documentation',
           items: [
             {label: 'Getting Started', to: '/docs/deployment/getting-started'},
             {label: 'Architecture', to: '/docs/core/architecture'},
             {label: 'API Reference', to: '/docs/api'},
           ],
         },
         {
           title: 'Resources',
           items: [
             {label: 'GitHub', href: 'https://github.com/JacobAbrham/Kosmos-DAR-V1.0.0.0'},
             {label: 'Project Management', to: '/docs/project-management'},
             {label: 'Security', to: '/docs/security'},
           ],
         },
       ],
       copyright: `Copyright © ${new Date().getFullYear()} Nuvanta Holding. Built with Docusaurus.`,
     },
   }
   ```

2. ✅ Custom CSS
   ```css
   /* src/css/custom.css */
   :root {
     --ifm-color-primary: #673ab7; /* Deep purple */
     --ifm-color-primary-dark: #5e35b1;
     --ifm-color-primary-darker: #5c33b0;
     --ifm-color-primary-darkest: #4c2a93;
     --ifm-color-primary-light: #7e57c2;
     --ifm-color-primary-lighter: #805dc4;
     --ifm-color-primary-lightest: #9575cd;
     --ifm-code-font-size: 95%;
   }
   
   .hero {
     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
     color: white;
   }
   ```

3. ✅ Add custom components
   - Create React components for special callouts
   - Add interactive demos
   - Custom MDX components

**Deliverable:** Branded documentation site

#### Day 9: Versioning Setup
**Duration:** 6 hours

**Tasks:**
1. ✅ Create first version
   ```bash
   npm run docusaurus docs:version 1.0.0
   ```

2. ✅ Configure version management
   ```typescript
   // docusaurus.config.ts
   presets: [
     [
       'classic',
       {
         docs: {
           lastVersion: 'current',
           versions: {
             current: {
               label: '1.0.0',
               path: '1.0.0',
             },
           },
         },
       },
     ],
   ],
   ```

3. ✅ Test version switching
   - Create sample v1.1.0 docs
   - Verify version dropdown
   - Test version-specific links

**Deliverable:** Working version management

#### Day 10: Search Integration
**Duration:** 4 hours

**Tasks:**
1. ✅ Configure Algolia DocSearch
   ```typescript
   // docusaurus.config.ts
   themeConfig: {
     algolia: {
       appId: 'YOUR_APP_ID',
       apiKey: 'YOUR_SEARCH_API_KEY',
       indexName: 'kosmos',
       contextualSearch: true,
       searchPagePath: 'search',
     },
   }
   ```

2. ✅ Submit for Algolia DocSearch program
   - https://docsearch.algolia.com/apply/
   - Wait for approval (or use alternative search)

3. ✅ Alternative: Local search
   ```bash
   npm install @easyops-cn/docusaurus-search-local
   ```

**Deliverable:** Working search functionality

---

### Phase 3: Testing & Deployment (Days 11-15)

#### Day 11-12: Quality Assurance
**Duration:** 2 days

**Tasks:**
1. ✅ Automated testing
   ```bash
   # Link checking
   npm run build
   npm run serve
   
   # Run link checker
   npx linkinator http://localhost:3000 --recurse --verbosity error
   ```

2. ✅ Manual testing checklist
   - [ ] All pages render correctly
   - [ ] Navigation works (breadcrumbs, sidebar, navbar)
   - [ ] Search finds relevant results
   - [ ] API docs display properly
   - [ ] Code blocks have syntax highlighting
   - [ ] Images load correctly
   - [ ] Mermaid diagrams render
   - [ ] Version switching works
   - [ ] Mobile responsive
   - [ ] Dark/light mode toggle
   - [ ] Print layouts correct

3. ✅ Content validation
   ```bash
   # Check for broken internal links
   grep -r "\[.*\](.*\.md)" docs/ | grep -v "http"
   
   # Find missing images
   grep -r "!\[.*\](.*)" docs/ | while read line; do
     img=$(echo $line | sed 's/.*(\(.*\)).*/\1/')
     if [ ! -f "static/$img" ]; then
       echo "Missing: $img"
     fi
   done
   ```

4. ✅ Performance testing
   - Lighthouse score > 90
   - Build time < 2 minutes
   - Page load time < 2 seconds

**Deliverable:** Tested, validated documentation site

#### Day 13: Staging Deployment
**Duration:** 4 hours

**Tasks:**
1. ✅ Deploy to Cloudflare Pages (staging)
   ```bash
   # Build
   npm run build
   
   # Deploy to Cloudflare
   wrangler pages deploy ./build --project-name=kosmos-docs-staging
   ```

2. ✅ Configure environment
   - Staging URL: https://staging-docs.kosmos.internal
   - Enable preview deployments for PRs
   - Set up analytics

3. ✅ Stakeholder review
   - Share staging link with team
   - Gather feedback
   - Document issues

**Deliverable:** Staging environment deployed

#### Day 14: Production Preparation
**Duration:** 6 hours

**Tasks:**
1. ✅ Update CI/CD pipeline
   ```yaml
   # .github/workflows/docs.yml
   name: Deploy Docusaurus
   
   on:
     push:
       branches: [master]
     pull_request:
       branches: [master]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         
         - name: Setup Node.js
           uses: actions/setup-node@v4
           with:
             node-version: '20'
             cache: 'npm'
             cache-dependency-path: docs/docusaurus-new/package-lock.json
         
         - name: Install dependencies
           working-directory: docs/docusaurus-new
           run: npm ci
         
         - name: Build
           working-directory: docs/docusaurus-new
           run: npm run build
         
         - name: Deploy to Cloudflare Pages
           if: github.ref == 'refs/heads/master'
           run: |
             wrangler pages deploy ./docs/docusaurus-new/build \
               --project-name=kosmos-docs \
               --branch=production
           env:
             CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
   ```

2. ✅ DNS configuration
   - Point docs.kosmos.internal to Cloudflare
   - Set up SSL certificates
   - Configure CDN caching

3. ✅ Monitoring setup
   - Google Analytics
   - Error tracking (Sentry)
   - Uptime monitoring

**Deliverable:** Production-ready deployment pipeline

#### Day 15: Production Cutover
**Duration:** 4 hours

**Tasks:**
1. ✅ Final validation
   - Run full test suite
   - Verify all links
   - Check analytics

2. ✅ Deploy to production
   ```bash
   git checkout master
   git merge feature/docusaurus-migration
   git push origin master
   # CI/CD auto-deploys
   ```

3. ✅ DNS cutover
   - Update docs.nuvanta-holding.com → new Docusaurus site
   - Keep old MkDocs at docs-legacy.nuvanta-holding.com (1 month)

4. ✅ Announcement
   - Email to team
   - Update README.md
   - Document migration notes

**Deliverable:** Live Docusaurus documentation

---

## Technical Architecture

### Directory Structure

```
docusaurus-new/
├── docs/                          # Documentation content
│   ├── index.md                   # Homepage
│   ├── core/                      # Core documentation
│   │   ├── executive/
│   │   ├── governance/
│   │   ├── architecture/
│   │   ├── engineering/
│   │   └── operations/
│   ├── deployment/                # Deployment guides
│   ├── security/                  # Security documentation
│   ├── api/                       # Auto-generated API docs
│   └── tutorials/                 # Tutorials
├── blog/                          # Blog posts (optional)
├── src/
│   ├── components/                # Custom React components
│   ├── css/                       # Custom CSS
│   └── pages/                     # Custom pages
├── static/
│   ├── img/                       # Images
│   └── assets/                    # Other assets
├── versioned_docs/                # Versioned documentation
│   └── version-1.0.0/
├── versioned_sidebars/            # Versioned sidebars
├── docusaurus.config.ts           # Main configuration
├── sidebars.ts                    # Sidebar configuration
├── package.json
└── tsconfig.json
```

### Configuration Files

#### docusaurus.config.ts
```typescript
import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'KOSMOS Documentation',
  tagline: 'AI-Native Enterprise Operating System',
  favicon: 'img/favicon.ico',

  url: 'https://docs.nuvanta-holding.com',
  baseUrl: '/',

  organizationName: 'Nuvanta-Holding',
  projectName: 'Kosmos-DAR-V1.0.0.0',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/JacobAbrham/Kosmos-DAR-V1.0.0.0/tree/master/docs/',
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
          remarkPlugins: [],
          rehypePlugins: [],
        },
        blog: false, // Disable blog if not needed
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/kosmos-social-card.jpg',
    navbar: {
      title: 'KOSMOS',
      logo: {
        alt: 'KOSMOS Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Documentation',
        },
        {
          type: 'docSidebar',
          sidebarId: 'api',
          position: 'left',
          label: 'API',
        },
        {
          type: 'docsVersionDropdown',
          position: 'right',
          dropdownActiveClassDisabled: true,
        },
        {
          href: 'https://github.com/JacobAbrham/Kosmos-DAR-V1.0.0.0',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Copyright © ${new Date().getFullYear()} Nuvanta Holding. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'typescript', 'bash', 'yaml', 'json'],
    },
  } satisfies Preset.ThemeConfig,

  plugins: [
    [
      'docusaurus-plugin-openapi-docs',
      {
        id: 'api',
        docsPluginId: 'classic',
        config: {
          kosmos: {
            specPath: '../openapi.json',
            outputDir: 'docs/api',
            sidebarOptions: {
              groupPathsBy: 'tag',
            },
          },
        },
      },
    ],
  ],

  themes: ['docusaurus-theme-openapi-docs', '@docusaurus/theme-mermaid'],
  markdown: {
    mermaid: true,
  },
};

export default config;
```

---

## File Structure Mapping

### MkDocs → Docusaurus Mapping

| MkDocs | Docusaurus | Notes |
|--------|------------|-------|
| `docs/index.md` | `docs/index.md` | Homepage |
| `docs/00-executive/` | `docs/core/executive/` | Nested under core |
| `docs/01-governance/` | `docs/core/governance/` | Nested under core |
| `docs/02-architecture/` | `docs/core/architecture/` | Nested under core |
| `docs/03-engineering/` | `docs/core/engineering/` | Nested under core |
| `docs/04-operations/` | `docs/core/operations/` | Nested under core |
| `docs/deployment/` | `docs/deployment/` | Same path |
| `docs/security/` | `docs/security/` | Same path |
| `docs/guides/` | `docs/guides/` | Same path |
| `docs/developer-guide/` | `docs/developer-guide/` | Same path |
| `openapi.json` | Auto-generated to `docs/api/` | OpenAPI plugin |
| `images/` | `static/img/` | Static assets |
| `mkdocs.yml` | `sidebars.ts` | Navigation config |

---

## Content Migration

### Automated Migration Script

**File:** `scripts/migrate-to-docusaurus.py`

```python
#!/usr/bin/env python3
"""
Migrate MkDocs markdown files to Docusaurus format.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List

class DocusaurusMigrator:
    """Migrate MkDocs documentation to Docusaurus."""
    
    def __init__(self, source_dir: str, target_dir: str):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
    def migrate_frontmatter(self, content: str) -> str:
        """Convert MkDocs frontmatter to Docusaurus format."""
        if not content.startswith('---'):
            return content
            
        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return content
            
        frontmatter = yaml.safe_load(parts[1])
        body = parts[2]
        
        # Convert to Docusaurus format
        docusaurus_fm = {
            'id': frontmatter.get('id', ''),
            'title': frontmatter.get('title', ''),
            'sidebar_label': frontmatter.get('sidebar_label', ''),
            'description': frontmatter.get('description', ''),
            'keywords': frontmatter.get('keywords', []),
        }
        
        # Remove empty values
        docusaurus_fm = {k: v for k, v in docusaurus_fm.items() if v}
        
        # Reconstruct
        new_frontmatter = yaml.dump(docusaurus_fm, default_flow_style=False)
        return f"---\n{new_frontmatter}---\n{body}"
    
    def convert_admonitions(self, content: str) -> str:
        """Convert MkDocs admonitions to Docusaurus format."""
        # !!! note "Title" → :::note Title
        content = re.sub(
            r'!!! (\w+) "([^"]*)"',
            r':::\1 \2',
            content
        )
        
        # Close admonitions
        # This is complex and may need manual review
        return content
    
    def update_links(self, content: str) -> str:
        """Update internal links to Docusaurus format."""
        # Convert relative links
        content = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\.md\)',
            r'[\1](\2)',
            content
        )
        return content
    
    def migrate_file(self, source_file: Path) -> None:
        """Migrate a single file."""
        # Read content
        content = source_file.read_text(encoding='utf-8')
        
        # Apply transformations
        content = self.migrate_frontmatter(content)
        content = self.convert_admonitions(content)
        content = self.update_links(content)
        
        # Determine target path
        rel_path = source_file.relative_to(self.source_dir)
        target_file = self.target_dir / rel_path
        
        # Create directories
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        target_file.write_text(content, encoding='utf-8')
        print(f"Migrated: {rel_path}")
    
    def migrate_all(self) -> None:
        """Migrate all markdown files."""
        md_files = list(self.source_dir.rglob('*.md'))
        print(f"Found {len(md_files)} markdown files")
        
        for md_file in md_files:
            try:
                self.migrate_file(md_file)
            except Exception as e:
                print(f"Error migrating {md_file}: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate MkDocs to Docusaurus')
    parser.add_argument('--source', required=True, help='Source directory (MkDocs)')
    parser.add_argument('--target', required=True, help='Target directory (Docusaurus)')
    
    args = parser.parse_args()
    
    migrator = DocusaurusMigrator(args.source, args.target)
    migrator.migrate_all()
    
    print("\nMigration complete!")
    print("Next steps:")
    print("1. Review migrated content manually")
    print("2. Update sidebars.ts")
    print("3. Test the documentation site")
```

### Manual Migration Checklist

**Items requiring manual review:**

- [ ] Admonitions with multi-line content
- [ ] Complex code blocks with special formatting
- [ ] Custom HTML/CSS in markdown
- [ ] Mermaid diagrams (should work, verify)
- [ ] Image paths (update to `/img/` prefix)
- [ ] Tables with complex formatting
- [ ] Nested lists with code blocks
- [ ] Special characters in frontmatter

---

## Feature Parity Checklist

### Must-Have Features

- [ ] All 214 markdown files migrated
- [ ] Navigation structure complete
- [ ] Internal links working
- [ ] Images and assets loading
- [ ] Code syntax highlighting
- [ ] Mermaid diagrams rendering
- [ ] Search functionality
- [ ] Mobile responsive
- [ ] Dark mode toggle
- [ ] OpenAPI integration
- [ ] Version management

### Nice-to-Have Features

- [ ] Algolia DocSearch (or alternative)
- [ ] Custom React components
- [ ] Interactive code examples
- [ ] Blog section
- [ ] Changelog automation
- [ ] Edit on GitHub links
- [ ] Last updated timestamps
- [ ] Reading time estimates
- [ ] Table of contents per page
- [ ] Copy code button

---

## Testing & Validation

### Automated Tests

```bash
# 1. Build test
npm run build
# Should complete without errors

# 2. Link checking
npx linkinator http://localhost:3000 --recurse --silent --format json > links.json

# 3. Lighthouse CI
npm install -g @lhci/cli
lhci autorun --config=lighthouserc.json

# 4. Visual regression (optional)
npm install -g backstopjs
backstop test
```

### Manual Testing Matrix

| Test Area | Chrome | Firefox | Safari | Mobile |
|-----------|--------|---------|--------|--------|
| Homepage loads | ⬜ | ⬜ | ⬜ | ⬜ |
| Navigation works | ⬜ | ⬜ | ⬜ | ⬜ |
| Search functions | ⬜ | ⬜ | ⬜ | ⬜ |
| API docs display | ⬜ | ⬜ | ⬜ | ⬜ |
| Code blocks render | ⬜ | ⬜ | ⬜ | ⬜ |
| Images load | ⬜ | ⬜ | ⬜ | ⬜ |
| Dark mode toggle | ⬜ | ⬜ | ⬜ | ⬜ |
| Version switch | ⬜ | ⬜ | ⬜ | ⬜ |
| Print layout | ⬜ | ⬜ | ⬜ | N/A |

---

## Deployment Strategy

### Blue-Green Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                   DEPLOYMENT TIMELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Current State (Blue):                                      │
│  ├─ docs.nuvanta-holding.com → MkDocs (live)              │
│  └─ Users accessing current docs                           │
│                                                             │
│  Staging (Green):                                           │
│  ├─ staging-docs.kosmos.internal → Docusaurus             │
│  └─ Team testing and validation                            │
│                                                             │
│  Cutover:                                                   │
│  ├─ Update DNS: docs.nuvanta-holding.com → Docusaurus     │
│  ├─ Archive MkDocs: docs-legacy.nuvanta-holding.com       │
│  └─ Monitor for 24 hours                                   │
│                                                             │
│  Post-Cutover (Day 2+):                                     │
│  ├─ If successful: Remove MkDocs after 30 days            │
│  └─ If issues: Rollback to MkDocs (< 5 min)               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### DNS Configuration

**Before migration:**
```
docs.nuvanta-holding.com → Cloudflare Pages (MkDocs)
```

**After migration:**
```
docs.nuvanta-holding.com → Cloudflare Pages (Docusaurus)
docs-legacy.nuvanta-holding.com → Cloudflare Pages (MkDocs, read-only)
```

### Rollback Procedure (If Needed)

**Time to rollback:** < 5 minutes

```bash
# 1. Revert DNS
# In Cloudflare dashboard:
# - Point docs.nuvanta-holding.com back to MkDocs deployment
# - TTL: 5 minutes

# 2. Notify team
echo "Rolled back to MkDocs due to [REASON]" | mail -s "Docs Rollback" team@nuvanta.com

# 3. Document issues
# Create GitHub issue with rollback reason
gh issue create --title "Docusaurus migration rollback" --body "[details]"

# 4. Investigate and fix
# Address issues in staging
# Plan re-deployment
```

---

## Team Responsibilities

### Roles & Ownership

| Role | Responsibilities | Time Commitment |
|------|------------------|-----------------|
| **Documentation Lead** | Overall migration coordination, quality assurance | 20h/week |
| **Frontend Developer** | Docusaurus setup, theme customization, React components | 15h/week |
| **DevOps Engineer** | CI/CD setup, deployment automation, monitoring | 10h/week |
| **Technical Writer** | Content review, manual fixes, navigation structure | 15h/week |
| **QA Engineer** | Testing, validation, bug reporting | 10h/week |
| **Product Owner** | Stakeholder communication, priority decisions | 5h/week |

### Communication Plan

**Daily standup (15 min):**
- Progress updates
- Blockers
- Next steps

**Weekly review (1 hour):**
- Demo progress
- Stakeholder feedback
- Adjust timeline

**Channels:**
- Slack: #kosmos-docs-migration
- GitHub: Project board with migration tasks
- Mattermost: Team notifications

---

## Success Criteria

### Functional Requirements

✅ **Must Pass:**
- [ ] All 214 docs migrated with no content loss
- [ ] 100% internal links working
- [ ] API documentation integrated from OpenAPI spec
- [ ] Search returns relevant results
- [ ] Site loads in < 3 seconds (p95)
- [ ] Mobile responsive (Lighthouse score > 90)
- [ ] Dark mode fully functional
- [ ] Version dropdown works correctly
- [ ] Zero broken links (linkinator)

### Business Requirements

✅ **Must Achieve:**
- [ ] Developer satisfaction: > 4/5 in survey
- [ ] Time to find information: < 30 seconds (improved from current)
- [ ] Documentation site uptime: > 99.9%
- [ ] Page views increase: > 20% (due to better discoverability)
- [ ] Support tickets decrease: > 15% (better self-service)

### Technical Requirements

✅ **Must Meet:**
- [ ] Build time: < 2 minutes
- [ ] Deploy time: < 5 minutes
- [ ] Lighthouse score: > 90 (all categories)
- [ ] Accessibility: WCAG 2.1 Level AA
- [ ] SEO: All pages indexed by Google within 1 week
- [ ] Bundle size: < 500KB (initial load)

---

## Risk Mitigation

### Identified Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Content loss during migration | Low | High | Automated script + manual review + git backup |
| Broken links after migration | Medium | Medium | Automated link checking + gradual rollout |
| Search doesn't work well | Medium | Medium | Test with real queries + fallback to local search |
| Team doesn't like new UI | Low | Medium | Early stakeholder demos + customization |
| Deployment issues | Low | High | Staging environment + blue-green deployment |
| Performance degradation | Low | Medium | Lighthouse CI + performance budgets |
| Versioning complexity | Medium | Low | Clear documentation + training |
| Budget overrun (Algolia) | Medium | Low | Use free tier + local search fallback |

### Contingency Plans

**If migration takes longer than expected:**
- Reduce scope: Ship without versioning first
- Extend timeline: Add 1 week buffer
- Increase resources: Add contractor

**If critical bugs found post-deployment:**
- Immediate rollback (< 5 min)
- Fix in staging
- Re-deploy within 24 hours

**If search doesn't work:**
- Use local search plugin as fallback
- Apply for Algolia after deployment
- Implement incremental search improvements

---

## Rollback Plan

### Rollback Decision Criteria

**Rollback if:**
- Critical functionality broken (navigation, search)
- > 10% of links broken
- Site unavailable for > 15 minutes
- Major performance degradation (> 50% slower)
- Accessibility issues preventing usage

### Rollback Procedure

**Step 1: Immediate (< 5 minutes)**
```bash
# 1. DNS switch
# Cloudflare dashboard: Point docs.nuvanta-holding.com back to MkDocs

# 2. Notify team
./scripts/notify-rollback.sh "Critical bug: [description]"

# 3. Update status page
echo "Docs temporarily unavailable, rollback in progress" > status.txt
```

**Step 2: Investigation (< 1 hour)**
```bash
# 1. Document rollback reason
gh issue create --title "Docusaurus rollback: [REASON]" --label "critical"

# 2. Gather logs
kubectl logs -n docs docusaurus-pod > rollback-logs.txt

# 3. Team meeting
# Discuss root cause, fix strategy, re-deployment plan
```

**Step 3: Fix & Re-deploy (24-48 hours)**
```bash
# 1. Fix issues in staging
git checkout feature/docusaurus-migration
# Apply fixes

# 2. Test thoroughly
npm run test:all

# 3. Schedule re-deployment
# Communicate new timeline to stakeholders
```

---

## Post-Migration Tasks

### Week 1 After Deployment

- [ ] Monitor analytics for traffic patterns
- [ ] Collect user feedback via survey
- [ ] Address any reported issues
- [ ] Optimize slow pages
- [ ] Fine-tune search results
- [ ] Add any missing content

### Month 1 After Deployment

- [ ] Decommission MkDocs site
- [ ] Remove legacy DNS records
- [ ] Update all external links
- [ ] Document lessons learned
- [ ] Train team on Docusaurus maintenance
- [ ] Set up documentation governance process

### Ongoing Maintenance

**Weekly:**
- Review broken link reports
- Update changelog
- Merge documentation PRs

**Monthly:**
- Review analytics
- Optimize slow pages
- Update dependencies

**Quarterly:**
- Version management (new releases)
- Performance audit
- Accessibility audit
- SEO review

---

## Appendix A: Migration Scripts

### Script 1: Bulk Frontmatter Conversion

**File:** `scripts/convert-frontmatter.sh`

```bash
#!/bin/bash
# Convert MkDocs frontmatter to Docusaurus format

find docs -name "*.md" | while read file; do
  echo "Processing: $file"
  
  # Use Python to parse and convert YAML frontmatter
  python3 << EOF
import yaml
import sys

with open('$file', 'r') as f:
    content = f.read()

if content.startswith('---'):
    parts = content.split('---', 2)
    if len(parts) >= 3:
        fm = yaml.safe_load(parts[1])
        body = parts[2]
        
        # Convert to Docusaurus format
        new_fm = {
            'id': fm.get('id', ''),
            'title': fm.get('title', ''),
            'sidebar_label': fm.get('sidebar_label', ''),
        }
        
        new_fm = {k: v for k, v in new_fm.items() if v}
        
        new_content = '---\n' + yaml.dump(new_fm) + '---' + body
        
        with open('$file', 'w') as f:
            f.write(new_content)
EOF
done

echo "Frontmatter conversion complete!"
```

### Script 2: Link Validator

**File:** `scripts/validate-links.sh`

```bash
#!/bin/bash
# Validate all internal links

echo "Building site..."
npm run build

echo "Starting local server..."
npm run serve &
SERVER_PID=$!
sleep 5

echo "Running link checker..."
npx linkinator http://localhost:3000 \
  --recurse \
  --format json \
  --verbosity error \
  > link-report.json

echo "Stopping server..."
kill $SERVER_PID

echo "Link validation complete! See link-report.json"
```

---

## Appendix B: Comparison Checklist

### Feature Comparison: MkDocs vs Docusaurus

| Feature | MkDocs Material | Docusaurus 3 | Status |
|---------|-----------------|--------------|--------|
| **Content** |
| Markdown support | ✅ | ✅ | ✅ |
| MDX (React in MD) | ❌ | ✅ | 🆕 |
| Code highlighting | ✅ | ✅ | ✅ |
| Mermaid diagrams | ✅ (plugin) | ✅ (native) | ✅ |
| Admonitions | ✅ | ✅ | ✅ |
| **Navigation** |
| Sidebar | ✅ | ✅ | ✅ |
| Tabs | ✅ | ✅ | ✅ |
| Breadcrumbs | ✅ | ✅ | ✅ |
| Version dropdown | ⚠️ (manual) | ✅ (native) | ✅ |
| **Search** |
| Local search | ✅ | ✅ | ✅ |
| Algolia | ⚠️ (manual) | ✅ (native) | ✅ |
| **API Docs** |
| OpenAPI integration | ⚠️ (iframe) | ✅ (native) | ✅ |
| Interactive API | ❌ | ✅ | 🆕 |
| **Versioning** |
| Version management | ⚠️ (mike plugin) | ✅ (native) | ✅ |
| Multiple versions | ⚠️ | ✅ | 🆕 |
| **Theme** |
| Dark mode | ✅ | ✅ | ✅ |
| Customization | ⚠️ (CSS only) | ✅ (React) | ✅ |
| Mobile responsive | ✅ | ✅ | ✅ |
| **Performance** |
| Build speed | ⚠️ (slower) | ✅ (fast) | ✅ |
| Load time | ✅ | ✅ | ✅ |
| **Developer Experience** |
| Hot reload | ✅ | ✅ | ✅ |
| TypeScript | ❌ | ✅ | 🆕 |
| React components | ❌ | ✅ | 🆕 |
| **Deployment** |
| Static export | ✅ | ✅ | ✅ |
| CDN friendly | ✅ | ✅ | ✅ |
| CI/CD | ✅ | ✅ | ✅ |

**Legend:**
- ✅ Supported
- ⚠️ Limited/Manual
- ❌ Not supported
- 🆕 New capability

---

## Appendix C: Training Materials

### For Documentation Contributors

**Quick Start Guide:**
```markdown
# Contributing to KOSMOS Docs (Docusaurus)

## 1. Local Setup
```bash
cd docs/docusaurus-new
npm install
npm start
# Opens http://localhost:3000
```

## 2. Creating a New Page
```bash
# Create file
touch docs/new-page.md

# Add frontmatter
---
id: new-page
title: My New Page
sidebar_label: New Page
---

# My New Page

Content here...
```

## 3. Adding to Navigation
Edit `sidebars.ts`:
```typescript
{
  type: 'category',
  label: 'My Section',
  items: ['new-page'],
}
```

## 4. Preview Changes
```bash
npm start
# Live reload - changes appear instantly
```

## 5. Submit PR
```bash
git checkout -b docs/my-new-page
git add docs/new-page.md sidebars.ts
git commit -m "docs: add new page"
git push origin docs/my-new-page
# Create PR on GitHub
```

## 6. Review Process
- Auto-deploy preview link
- Team reviews
- Merge to master → auto-deploy to production
```

### For Reviewers

**Documentation PR Review Checklist:**

- [ ] Content is accurate and up-to-date
- [ ] Links work (internal and external)
- [ ] Images load correctly
- [ ] Code examples are tested
- [ ] Frontmatter is complete
- [ ] Sidebar navigation updated
- [ ] Spelling and grammar checked
- [ ] Follows documentation style guide
- [ ] Mobile responsive (check preview)
- [ ] Accessible (headings, alt text)

---

## Conclusion

This migration plan provides a comprehensive, step-by-step approach to migrate KOSMOS documentation from MkDocs to Docusaurus 3. The plan includes:

✅ **Clear timeline:** 15 working days with defined milestones  
✅ **Risk mitigation:** Identified risks with contingency plans  
✅ **Rollback strategy:** < 5 minute rollback if needed  
✅ **Automation:** Scripts to minimize manual work  
✅ **Quality assurance:** Comprehensive testing checklist  
✅ **Team coordination:** Clear roles and responsibilities

**Next Steps:**
1. Review and approve this plan
2. Allocate resources (team members)
3. Create migration branch
4. Begin Phase 0 (project setup)

**Questions?** Contact the Documentation Lead or raise in #kosmos-docs-migration

---

**Prepared by:** GitHub Copilot  
**Date:** December 23, 2025  
**Version:** 1.0  
**Status:** Ready for Approval

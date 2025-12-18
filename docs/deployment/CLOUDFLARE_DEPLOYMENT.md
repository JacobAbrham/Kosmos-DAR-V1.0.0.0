# Cloudflare Pages Deployment Guide

**Deploy KOSMOS Documentation to Cloudflare Pages**

---

## Prerequisites

- [x] GitHub repository: `Nuvanta-Holding/kosmos-docs`
- [x] Cloudflare account
- [x] Wrangler CLI installed (`npm install -g wrangler`)
- [x] Documentation built and tested locally

---

## Deployment Methods

You can deploy using either:
1. **Wrangler CLI** (Recommended for quick deployments)
2. **GitHub Integration** (Recommended for automatic deployments)

---

## Method 1: Deploy with Wrangler CLI

### Step 1: Authenticate with Cloudflare

```bash
# Check authentication status
wrangler whoami

# If not authenticated, log in
wrangler login
```

### Step 2: Build Your Documentation

```bash
# Build the MkDocs site
mkdocs build

# Verify the build output
ls site/
```

### Step 3: Deploy to Cloudflare Pages

```bash
# Deploy the site directory to Cloudflare Pages
wrangler pages deploy site --project-name=kosmos-docs

# Follow the prompts:
# - Create new project (if first time)
# - Set production branch: main
```

**Your site will be live at:** `https://<unique-id>.kosmos-docs.pages.dev`

---

## Method 2: GitHub Integration (Automatic Deployments)

### Step 1: Push to GitHub

```bash
# Add all files
git add .

# Commit changes
git commit -m "feat: update documentation"

# Push to GitHub
git push origin main
```

### Step 2: Connect to Cloudflare Pages

1. **Log in to Cloudflare Dashboard**
   - Go to https://dash.cloudflare.com
   - Select your account

2. **Navigate to Workers & Pages**
   - Click "Workers & Pages" in the left sidebar
   - Click "Create application"
   - Click the "Pages" tab
   - Click "Connect to Git"

3. **Connect GitHub Repository**
   - Select "GitHub"
   - Authorize Cloudflare (if first time)
   - Select repository: `Nuvanta-Holding/kosmos-docs`
   - Click "Begin setup"

4. **Configure Build Settings**
   ```yaml
   Project name: kosmos-docs
   Production branch: main
   Build command: mkdocs build
   Build output directory: site
   Root directory: (leave empty)
   ```

5. **Environment Variables** (Click "Environment variables (advanced)")
   ```yaml
   PYTHON_VERSION: 3.11
   ```

6. **Deploy**
   - Click "Save and Deploy"
   - Wait for first build (2-3 minutes)
   - Future pushes to `main` will auto-deploy

---

## Configure Custom Domain (Optional)

### Add Custom Domain to Your Pages Project

1. **In Cloudflare Pages Project**
   - Go to your project in **Workers & Pages**
   - Click on your project name
   - Navigate to "Custom domains" tab
   - Click "Set up a custom domain"

2. **Add Your Domain**
   - Enter: `docs.nuvanta-holding.com`
   - Click "Continue"

3. **DNS Configuration** (Automatic if using Cloudflare DNS)
   - Cloudflare automatically creates a CNAME record
   - Verify: `docs.nuvanta-holding.com` → `kosmos-docs.pages.dev`

4. **HTTPS**
   - Automatic with Cloudflare Universal SSL
   - Force HTTPS: Enabled by default
   - Certificate provisioned within minutes

---

## Verify Deployment

```bash
# Check DNS propagation (if using custom domain)
nslookup docs.nuvanta-holding.com

# Or visit your Pages URL directly
# https://<unique-id>.kosmos-docs.pages.dev

# Test HTTPS
curl -I https://docs.nuvanta-holding.com

# Open in browser
start https://docs.nuvanta-holding.com  # Windows
open https://docs.nuvanta-holding.com   # Mac
```

**Expected Response:**
- Status: 200 OK
- Server: cloudflare
- SSL: Valid certificate

---

## Continuous Deployment

### Automatic Deployment on Git Push

**Every push to `main` branch automatically:**
1. Triggers Cloudflare Pages build
2. Runs `mkdocs build`
3. Deploys to production
4. Updates `docs.nuvanta-holding.com`

**Preview Deployments:**
- Every pull request gets a unique preview URL
- Format: `https://[commit-hash].kosmos-docs.pages.dev`
- Perfect for reviewing changes before merge

---

## Build Configuration

### Cloudflare Pages Settings

```yaml
# Framework preset: None
# Build command
mkdocs build

# Build output directory
site

# Environment variables (if needed)
# PYTHON_VERSION: 3.9
```

### Build Time Optimization

**Current build time:** ~2-3 minutes

**To speed up:**
1. Cache Python dependencies (automatic)
2. Minimize plugin usage
3. Optimize image sizes

---

## DNS Configuration

### Cloudflare DNS Records

| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| CNAME | docs | kosmos-docs.pages.dev | Proxied (🟠) |

**Proxy Benefits:**
- ✅ DDoS protection
- ✅ CDN caching
- ✅ SSL/TLS encryption
- ✅ Performance optimization
- ✅ Analytics

---

## Security Settings

### Recommended Cloudflare Settings

1. **SSL/TLS Mode:** Full (strict)
2. **Always Use HTTPS:** On
3. **Automatic HTTPS Rewrites:** On
4. **HTTP Strict Transport Security (HSTS):**
   - Enable HSTS: On
   - Max Age: 6 months
   - Include subdomains: On
   - Preload: On

5. **Security Level:** Medium
6. **Bot Fight Mode:** On
7. **Browser Integrity Check:** On

---

## Monitoring & Analytics

### Cloudflare Analytics

**Available Metrics:**
- Requests per second
- Bandwidth usage
- Unique visitors
- Cache hit rate
- Error rate
- Top URLs

**Access:** Dashboard > Pages > kosmos-docs > Analytics

### Custom Analytics

**Optional: Add Google Analytics**

Edit `mkdocs.yml`:
```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX  # Your GA4 property ID
```

---

## Rollback Procedures

### Rollback to Previous Version

1. **In Cloudflare Pages:**
   - Go to "Deployments" tab
   - Find the previous successful deployment
   - Click "..." menu
   - Select "Rollback to this deployment"

2. **Via Git:**
   ```bash
   # Revert to previous commit
   git revert HEAD
   git push origin main
   
   # Or reset to specific commit
   git reset --hard <commit-hash>
   git push --force origin main
   ```

---

## Troubleshooting

### Build Fails

**Error:** `mkdocs: command not found`
```yaml
# Solution: Ensure requirements.txt includes mkdocs
# requirements.txt should have:
mkdocs>=1.5.0
mkdocs-material>=9.0.0
```

**Error:** `Module not found`
```bash
# Solution: Add missing package to requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "fix: add missing dependencies"
git push
```

### DNS Not Resolving

```bash
# Check DNS propagation
dig docs.nuvanta-holding.com

# Check Cloudflare DNS settings
# Ensure CNAME record exists:
# docs → kosmos-docs.pages.dev
```

### SSL Certificate Issues

**Wait 24 hours for certificate provisioning**
```bash
# Check SSL status
curl -vI https://docs.nuvanta-holding.com 2>&1 | grep -i ssl
```

---

## Performance Optimization

### Cache Configuration

**Cloudflare automatically caches:**
- Static assets (CSS, JS, images)
- HTML pages (with smart invalidation)

**Cache Control Headers:**
```yaml
# Cloudflare respects these headers from MkDocs
Cache-Control: public, max-age=3600
```

### CDN Distribution

**Cloudflare's global network:**
- 310+ data centers worldwide
- Automatic routing to nearest edge server
- 99.99% uptime SLA

---

## Cost Estimate

### Cloudflare Pages Pricing

**Free Tier (Included):**
- ✅ Unlimited static requests
- ✅ Unlimited bandwidth
- ✅ 500 builds per month
- ✅ 1 build at a time
- ✅ Free SSL certificates
- ✅ DDoS protection

**Pro Tier ($20/month):**
- 5,000 builds per month
- 5 concurrent builds
- Advanced analytics

**For KOSMOS documentation: FREE TIER IS SUFFICIENT**

---

## Maintenance

### Regular Tasks

**Weekly:**
- [ ] Check build status
- [ ] Review analytics
- [ ] Monitor error rates

**Monthly:**
- [ ] Review DNS configuration
- [ ] Check SSL certificate expiry (auto-renewed)
- [ ] Update dependencies if needed

**Quarterly:**
- [ ] Security audit
- [ ] Performance review
- [ ] Cost analysis

---

## Backup Strategy

### Git as Backup

**Primary backup:** GitHub repository
- All content version controlled
- Complete history preserved
- Easy restoration

### Export Site

```bash
# Build static site locally
mkdocs build

# Backup entire site folder
tar -czf kosmos-docs-backup-$(date +%Y%m%d).tar.gz site/

# Store offsite
# Upload to S3, Dropbox, etc.
```

---

## Support

**Cloudflare Support:**
- Community: https://community.cloudflare.com
- Docs: https://developers.cloudflare.com/pages
- Email: support@cloudflare.com (Pro+ plans)

**MkDocs Support:**
- Docs: https://www.mkdocs.org
- GitHub: https://github.com/mkdocs/mkdocs
- Material: https://squidfunk.github.io/mkdocs-material

**Nuvanta Holding:**
- Technical Issues: engineering@nuvanta-holding.com
- Access Issues: it-support@nuvanta-holding.com

---

## Quick Reference

### Essential Commands

```bash
# Local development
mkdocs serve

# Build static site
mkdocs build

# Deploy to Cloudflare (automatic via Git push)
git add .
git commit -m "docs: update documentation"
git push origin main

# Check deployment status
# Visit: https://dash.cloudflare.com → Pages → kosmos-docs
```

### Important URLs

- **Production:** https://docs.nuvanta-holding.com
- **Cloudflare Dashboard:** https://dash.cloudflare.com
- **GitHub Repo:** https://github.com/Nuvanta-Holding/kosmos-docs
- **Preview Builds:** https://*.kosmos-docs.pages.dev

---

**Last Updated:** 2025-12-11  
**Deployment Status:** 🟢 Ready to Deploy  
**Maintainer:** DevOps Team

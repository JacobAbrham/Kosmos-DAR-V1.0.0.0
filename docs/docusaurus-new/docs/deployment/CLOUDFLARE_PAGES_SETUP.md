# Cloudflare Pages Deployment - Quick Start

## ✅ Pre-Deployment Checklist

- [x] Repository pushed to GitHub: `Nuvanta-Holding/kosmos-docs`
- [x] MkDocs site builds successfully
- [x] Site directory contains all static assets

## 🚀 Deploy to Cloudflare Pages

### Step 1: Access Cloudflare Dashboard

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **Workers & Pages**

### Step 2: Create New Pages Project

1. Click **Create application**
2. Click the **Pages** tab
3. Click **Connect to Git**

### Step 3: Connect GitHub Repository

1. Click **GitHub** (authorize Cloudflare if needed)
2. Select repository: **Nuvanta-Holding/kosmos-docs**
3. Click **Begin setup**

### Step 4: Configure Build Settings

Use these exact settings:

| Setting | Value |
|---------|-------|
| **Project name** | `kosmos-docs` (or custom name) |
| **Production branch** | `main` |
| **Build command** | `mkdocs build` |
| **Build output directory** | `site` |

### Step 5: Set Environment Variables

Click **Environment variables (advanced)** and add:

| Variable | Value |
|----------|-------|
| `PYTHON_VERSION` | `3.11` |

> **Note:** Python 3.11 is recommended for best compatibility with all dependencies

### Step 6: Deploy

1. Click **Save and Deploy**
2. Wait 2-3 minutes for the first build
3. Your site will be live at: `https://<project-name>.pages.dev`

## 🌐 Configure Custom Domain (Optional)

### Add Custom Domain

1. In your Pages project, go to **Custom domains**
2. Click **Set up a custom domain**
3. Enter: `docs.nuvanta-holding.com`
4. Cloudflare will automatically configure DNS (CNAME record)
5. HTTPS will be enabled automatically

## 🔄 Deployment Options

### Option 1: Automatic Deployments (GitHub Integration)

Every push to `main` branch will:
- ✅ Trigger automatic build
- ✅ Deploy to production
- ✅ Update live site

Pull requests get preview deployments:
- Format: `https://<commit-hash>.<project-name>.pages.dev`

### Option 2: Manual Deployment with Wrangler CLI

```bash
# Authenticate (first time only)
wrangler login

# Build your site
mkdocs build

# Deploy to Cloudflare Pages
wrangler pages deploy site --project-name=kosmos-docs
```

This is useful for:
- ✅ Quick deployments without pushing to GitHub
- ✅ Testing changes before committing
- ✅ Emergency deployments

## 📊 What You'll Get

✅ **Free Tier Includes:**
- Unlimited static requests
- Unlimited bandwidth
- 500 builds/month
- Free SSL certificates
- DDoS protection
- Global CDN

## 🔗 Quick Links

- **Production URL:** Will be `https://kosmos-docs.pages.dev`
- **Custom Domain:** `https://docs.nuvanta-holding.com` (after setup)
- **Dashboard:** https://dash.cloudflare.com

## ⚠️ Troubleshooting

**If build fails:**
- Check that `requirements.txt` exists with all dependencies
- Verify `mkdocs.yml` is in the repository root
- Check build logs in Cloudflare dashboard

**Current build output:**
```
✅ Site built successfully
✅ Output directory: site/
✅ Ready for deployment
```

---

**Next:** Click the link above to start deployment in Cloudflare Dashboard!

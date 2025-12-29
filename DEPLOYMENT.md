# Deployment Guide

This guide covers setting up automated deployments for `raveling.devocosm.com`.

## Prerequisites

1. GitHub repository connected
2. Cloudflare account with Workers/Pages access
3. Railway account
4. Domain `devocosm.com` managed in Cloudflare

## Step 1: Cloudflare Workers Setup

### Option A: Direct GitHub Integration (Recommended - Already Set Up)

If you've already connected Cloudflare Workers to your GitHub repository directly:

1. ✅ **Already Done**: Cloudflare Dashboard → Workers & Pages → Your Project
   - Connected to GitHub repository
   - Root directory set to `frontend`
   - Build command: `npm install && npm run build`
   - Deploy command: `npx wrangler deploy`

2. **Configure Custom Domain** (if not done):
   - In Cloudflare Dashboard → Workers & Pages → Your Project → Settings → Domains
   - Add custom domain: `raveling.devocosm.com`
   - Cloudflare will automatically configure DNS

3. **Set Environment Variables** (if needed):
   - In Cloudflare Dashboard → Workers & Pages → Your Project → Settings → Variables
   - Add `VITE_API_URL` = Your Railway backend URL (e.g., `https://your-backend.railway.app`)

### Option B: GitHub Actions Deployment (Alternative)

If you prefer GitHub Actions instead of direct integration:

#### Get Cloudflare API Token

1. Go to Cloudflare Dashboard → My Profile → API Tokens
2. Click "Create Token"
3. Use "Edit Cloudflare Workers" template
4. Set permissions:
   - Account: `Workers:Edit`
   - Zone: `Workers:Edit` (for your domain)
5. Copy the token

#### Get Cloudflare Account ID

1. Go to Cloudflare Dashboard
2. Select your account (right sidebar)
3. Copy the Account ID

#### Add GitHub Secrets (Only if using GitHub Actions)

In your GitHub repository:
1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets (only needed if using GitHub Actions):
   - `CLOUDFLARE_API_TOKEN` - Your API token
   - `CLOUDFLARE_ACCOUNT_ID` - Your account ID
   - `VITE_API_URL` - Your Railway backend URL (optional)

**Note**: If using direct GitHub integration, you don't need these GitHub secrets.

### Configure DNS

1. In Cloudflare Dashboard → DNS → Records (for `devocosm.com`)
2. Add a CNAME record (if not auto-configured):
   - Name: `raveling`
   - Target: Your Cloudflare Workers deployment URL (provided after first deploy, or check Workers & Pages → Your Project → Domains)
   - Proxy: ON (orange cloud)

**Note**: If you added the custom domain in Workers settings, DNS may be auto-configured.

## Step 2: Railway Setup

### Connect GitHub Repository

1. Go to Railway Dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access GitHub
5. Select your `raveling` repository
6. Railway will detect it's a Python project

### Configure Service

1. In Railway project, click on the service
2. Go to Settings → Source
3. Set Root Directory to `backend`
4. Railway will auto-detect `pyproject.toml`

### Get Railway Token

1. Go to Railway Dashboard → Account Settings → Tokens
2. Create a new token
3. Copy the token

### Add GitHub Secret

In your GitHub repository:
1. Go to Settings → Secrets and variables → Actions
2. Add secret:
   - `RAILWAY_TOKEN` - Your Railway token

### Set Environment Variables

In Railway Dashboard → Service → Variables:
- `DATABASE_URL` - Railway will provide this if you add a database
- `SECRET_KEY` - Generate a secure random string (e.g., use a long random string)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - `500` (number, not a string)
- `ALGORITHM` - `HS256`
- `CORS_ORIGINS` - `https://raveling.devocosm.com,http://localhost:3000`
- `GITHUB_TOKEN` - Your GitHub personal access token (REQUIRED)
- `GITHUB_REPO` - `devoprops/raveling` (or your repo in `owner/repo` format)
- `GITHUB_BRANCH` - `main`
- `GITHUB_BASE_PATH` - `src/configs`

## Step 3: First Deployment

### Frontend Deployment

**If using Direct GitHub Integration (Recommended):**
- ✅ Already configured - Cloudflare will auto-deploy on push to `main` branch
- Push to `main` branch and Cloudflare will build and deploy automatically
- Check deployment status in Cloudflare Dashboard → Workers & Pages → Your Project → Deployments

**If using GitHub Actions:**
- Push to `main` branch and GitHub Actions will deploy via Wrangler
- Check deployment status in GitHub → Actions tab

### Backend Auto-Deploy

Railway will automatically deploy when you push to `main` branch (if GitHub integration is connected).

## Step 4: Verify

1. Frontend: Visit `https://raveling.devocosm.com`
2. Backend: Visit `https://your-backend.railway.app/api/health`

## Troubleshooting

### Frontend Not Deploying

**If using Direct GitHub Integration:**
- Check Cloudflare Dashboard → Workers & Pages → Your Project → Deployments → Build logs
- Verify root directory is set to `frontend` in Settings → Source
- Ensure `wrangler.toml` exists in `frontend/` directory
- Check that build command is: `npm install && npm run build`

**If using GitHub Actions:**
- Check GitHub → Actions tab → Latest workflow run
- Verify `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` secrets are set
- Ensure `wrangler.toml` is correct

### Backend Not Deploying

- Check Railway deployment logs
- Verify `RAILWAY_TOKEN` secret
- Ensure `backend/pyproject.toml` exists
- Check that `railway.json` is correct

### CORS Errors

- Verify `CORS_ORIGINS` includes `https://raveling.devocosm.com`
- Check backend logs for CORS errors
- Ensure frontend `VITE_API_URL` points to correct backend URL

## Manual Deployment

If you need to deploy manually:

### Frontend
```bash
cd frontend
npm install
npm run build
npx wrangler deploy --assets=./dist
```

### Backend
```bash
cd backend
railway up
```


# Deployment Guide

This guide covers setting up automated deployments for `raveling.devocosm.com`.

## Prerequisites

1. GitHub repository connected
2. Cloudflare account with Workers/Pages access
3. Railway account
4. Domain `devocosm.com` managed in Cloudflare

## Step 1: Cloudflare Setup

### Get Cloudflare API Token

1. Go to Cloudflare Dashboard → My Profile → API Tokens
2. Click "Create Token"
3. Use "Edit Cloudflare Workers" template
4. Set permissions:
   - Account: `Cloudflare Pages:Edit`
   - Zone: `Workers:Edit` (for your domain)
5. Copy the token

### Get Cloudflare Account ID

1. Go to Cloudflare Dashboard
2. Select your account (right sidebar)
3. Copy the Account ID

### Add GitHub Secrets

In your GitHub repository:
1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `CLOUDFLARE_API_TOKEN` - Your API token
   - `CLOUDFLARE_ACCOUNT_ID` - Your account ID
   - `VITE_API_URL` - Your Railway backend URL (optional, can set in Cloudflare dashboard)

### Configure DNS

1. In Cloudflare Dashboard → DNS → Records
2. Add a CNAME record:
   - Name: `raveling`
   - Target: Your Cloudflare Pages deployment URL (will be provided after first deploy)
   - Proxy: ON (orange cloud)

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
- `SECRET_KEY` - Generate a secure random string
- `CORS_ORIGINS` - `https://raveling.devocosm.com,http://localhost:3000`

## Step 3: First Deployment

### Manual Frontend Deploy (First Time)

1. In Cloudflare Dashboard → Workers & Pages → Create application
2. Select "Pages" → "Connect to Git"
3. Connect your GitHub repository
4. Configure:
   - Project name: `raveling-frontend`
   - Production branch: `main`
   - Build command: `cd frontend && npm install && npm run build`
   - Build output directory: `frontend/dist`
5. Click "Save and Deploy"

### Backend Auto-Deploy

Railway will automatically deploy when you push to `main` branch.

## Step 4: Verify

1. Frontend: Visit `https://raveling.devocosm.com`
2. Backend: Visit `https://your-backend.railway.app/api/health`

## Troubleshooting

### Frontend Not Deploying

- Check GitHub Actions logs
- Verify `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` secrets
- Ensure `wrangler.toml` is correct
- Check build logs in Cloudflare dashboard

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
npx wrangler pages deploy dist --project-name=raveling-frontend
```

### Backend
```bash
cd backend
railway up
```


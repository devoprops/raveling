# Setup Summary for raveling.devocosm.com

## What's Been Set Up

### ✅ Frontend Structure (`frontend/`)
- React + TypeScript + Vite setup
- Basic routing (Home, Designer, Game pages)
- API client utility for backend communication
- Configured for Cloudflare Pages deployment
- Build configuration ready

### ✅ Backend Structure (`backend/`)
- FastAPI application structure
- API routes stubs (auth, items, skills, characters)
- CORS configured for `raveling.devocosm.com`
- Railway deployment configuration
- Environment variable examples

### ✅ CI/CD Workflows (`.github/workflows/`)
- **Frontend**: Auto-deploys to Cloudflare Pages on push to `main`
- **Backend**: Auto-deploys to Railway on push to `main`
- Both workflows trigger only when relevant files change

### ✅ Configuration Files
- `wrangler.toml` - Cloudflare Workers/Pages config
- `railway.json` - Railway deployment config
- `env.example` files for both frontend and backend
- Updated `.gitignore` for new directories

## Next Steps

### 1. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 2. Test Frontend Locally
```bash
cd frontend
npm run dev
```
Visit `http://localhost:3000`

### 3. Test Backend Locally
```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload
```
Visit `http://localhost:8000/docs` for API docs

### 4. Set Up Cloudflare (See DEPLOYMENT.md)
- Get Cloudflare API token
- Get Cloudflare Account ID
- Add secrets to GitHub:
  - `CLOUDFLARE_API_TOKEN`
  - `CLOUDFLARE_ACCOUNT_ID`
  - `VITE_API_URL` (optional, set after Railway is deployed)

### 5. Set Up Railway (See DEPLOYMENT.md)
- Connect GitHub repository to Railway
- Set root directory to `backend`
- Get Railway token
- Add secret to GitHub:
  - `RAILWAY_TOKEN`
- Set environment variables in Railway dashboard

### 6. Configure DNS
- In Cloudflare DNS, add CNAME:
  - Name: `raveling`
  - Target: (Cloudflare Pages URL - provided after first deploy)
  - Proxy: ON

### 7. First Deployment
- Push to `main` branch
- Frontend will deploy to Cloudflare Pages
- Backend will deploy to Railway
- Update DNS CNAME target to Cloudflare Pages URL
- Update `VITE_API_URL` with Railway backend URL

## Project Structure

```
raveling/
├── frontend/          # React frontend → Cloudflare Pages
├── backend/           # FastAPI backend → Railway
├── src/              # Shared Python models (existing)
└── .github/workflows/ # CI/CD automation
```

## Questions to Consider

1. **Database**: What database do you want to use? (PostgreSQL recommended for Railway)
2. **Authentication**: JWT tokens? OAuth? Basic auth?
3. **File Storage**: Where to store uploaded configs? (Railway volumes, S3, etc.)
4. **WebSocket**: Do you need real-time features for the game?

## Notes

- Frontend and backend are completely separate deployments
- They communicate via REST API
- Frontend calls backend at `VITE_API_URL` environment variable
- Both auto-deploy on push to `main` branch
- Development servers run locally for testing


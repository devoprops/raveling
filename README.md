# Raveling MUD

A MUD (Multi-User Dungeon) game with integrated Designer tools for creating items, skills, and characters.

## Project Structure

```
raveling/
├── backend/              # FastAPI backend (Railway deployment)
│   └── src/
│       ├── api/         # API routes
│       ├── database/    # Database models
│       └── main.py     # FastAPI app
├── frontend/            # React frontend (Cloudflare Workers deployment)
│   └── src/
│       ├── pages/      # Page components
│       └── App.tsx     # Main app component
├── src/                # Shared models and utilities
│   ├── models/        # Game models (items, skills, characters)
│   ├── utils/         # Utilities
│   └── ui/            # Desktop Designer (PySide6)
└── .github/workflows/  # CI/CD workflows
```

## Development

### Desktop Designer

Run the desktop Designer application:

```bash
python run_designer.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Backend Development

```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload
```

Backend API will be available at `http://localhost:8000`

## Deployment

### Frontend (Cloudflare Workers)

- Deployed to: `raveling.devocosm.com`
- Auto-deploys on push to `main` branch
- Requires GitHub Secrets:
  - `CLOUDFLARE_API_TOKEN`
  - `CLOUDFLARE_ACCOUNT_ID`
  - `VITE_API_URL` (optional, for API URL)

### Backend (Railway)

- Auto-deploys on push to `main` branch
- Requires GitHub Secret:
  - `RAILWAY_TOKEN`

## Environment Variables

### Frontend

- `VITE_API_URL`: Backend API URL (defaults to Railway URL)

### Backend

- `DATABASE_URL`: Database connection string (Railway provides this)
- `SECRET_KEY`: JWT secret key for authentication
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)


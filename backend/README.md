# Raveling Backend API

FastAPI backend for Raveling MUD game and designer.

## Setup

```bash
uv sync
```

## Run Development Server

```bash
uv run uvicorn src.main:app --reload
```

API docs available at: `http://localhost:8000/docs`

## Environment Variables

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret for authentication
- `CORS_ORIGINS`: Allowed origins (comma-separated)


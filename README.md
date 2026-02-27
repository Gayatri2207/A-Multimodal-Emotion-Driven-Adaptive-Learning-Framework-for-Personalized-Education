# Emotion Adaptive Learning Platform

This repository contains a production-ready Emotion Adaptive Learning Platform.

Overview
- Backend: FastAPI, SQLAlchemy, JWT auth, WebSocket, RL engine, multimodal fusion.
- Frontend: React app that connects to the WebSocket for real-time adaptive actions.
- Docker: Dockerfiles and example docker-compose included.

Quickstart (local)

1. Copy `.env.example` to `.env` and adjust values.

2. Create Python venv and install dependencies (backend):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Run frontend (simple static):

Serve `frontend_app` with any static server. For development, open `frontend_app/src` in a React environment.

Docker

Build and run with docker-compose (example):

```powershell
docker-compose -f docker-compose.generated.yml up --build
```

Endpoints
- `GET /health` - health check
- `POST /auth/register` - register user
- `POST /auth/login` - login and receive JWT
- `GET /analytics/summary` - analytics
- `ws://{host}:8000/ws/emotion` - send emotion data and get adaptive action

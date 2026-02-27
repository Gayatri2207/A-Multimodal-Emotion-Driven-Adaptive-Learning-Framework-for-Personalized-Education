# Emotion-Adaptive Learning Platform — Run Instructions

Backend (FastAPI)

1. Create and activate a Python virtual environment (recommended).

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r "backend/requirements.txt"
```

2. Run the API with uvicorn:
```powershell
cd "backend"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints:
- Health: `GET /health`
- Register: `POST /auth/register` (body: {email, password})
- Login: `POST /auth/login` (body: {email, password})
- Analytics: `GET /analytics/summary`
- WebSocket: `ws://localhost:8000/ws/emotion` (send JSON: {emotion_score, performance_score})

Frontend (React)

This project contains a simple React app under `frontend_app`.
You can run it with any static server or integrate into a React build pipeline.

Development notes:
- The backend stores data in `app.db` by default (SQLite).
- The RL engine will attempt to load a PPO model if `RL_MODEL_PATH` points to an existing model file; otherwise a deterministic heuristic is used.
- Multimodal components attempt to load heavyweight models (transformers) but handle failures gracefully and fall back to reasonable defaults.

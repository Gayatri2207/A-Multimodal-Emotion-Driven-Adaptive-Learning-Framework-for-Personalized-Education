# Emotion-Aware Intelligent Coding Practice Platform

An AI-powered adaptive coding practice system — like LeetCode, but difficulty adapts in real-time based on your emotional state detected via webcam.

---

## System Overview

| Layer | Technology | Notes |
|---|---|---|
| Backend API | FastAPI (Python 3.10) | REST + WebSocket |
| Frontend | React 19 + Monaco Editor | SPA, 5 pages |
| Database | SQLite (SQLAlchemy ORM) | auto-created on startup |
| AI / RL | Heuristic adaptive engine | emotion + performance + attempts + time |
| Emotion Detection | ONNX FER+ model + OpenCV | ~80% accuracy, no PyTorch/TF required |
| AI Tutor | Rule-based AST + Ollama/HF LLM | auto-detects local Ollama at port 11434 |
| Sandbox | subprocess + import blocklist + 5s timeout | safe code execution |

---

## Quick Start

### 1 — Backend

```powershell
cd automated-learning-system\backend

# First time only — create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run the server (auto-seeds 100 problems on first start)
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --reload
```

Server is live at **http://localhost:8000**  
Interactive API docs at **http://localhost:8000/docs**

> **Note:** Delete `emotion_learning.db` to reset the database and re-seed all 100 problems.

### 2 — Frontend

```powershell
cd automated-learning-system\frontend\client

# First time only
npm install

# Development server
npm start
```

App is live at **http://localhost:3000**

For a production build:
```powershell
npm run build
```

> **Environment variables** — create `frontend/client/.env` to override defaults:
> ```
> REACT_APP_API_URL=http://localhost:8000
> REACT_APP_WS_URL=ws://localhost:8000/ws/emotion
> ```

---

## API Reference

### Core Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/health` | Service health & version |
| POST | `/auth/register` | Create account `{email, password, name?}` |
| POST | `/auth/login` | Get JWT token `{email, password}` |

### Coding Platform

| Method | URL | Description |
|---|---|---|
| GET | `/coding/problems` | List all 100 problems. Query: `?difficulty=easy\|medium\|hard`, `?category=math` |
| GET | `/coding/problems/{id}` | Single problem with examples, hints, starter code |
| POST | `/coding/submit` | Submit code → sandboxed execution → pass/fail per test case |
| POST | `/coding/evaluate` | Alias for `/submit` |
| GET | `/coding/stats` | Platform-wide submission stats |
| GET | `/coding/stats/{user_id}` | Per-user stats |
| GET | `/coding/submissions/{user_id}` | Submission history |
| GET | `/coding/progress/{user_id}` | Per-problem solved/attempt tracking |
| GET | `/coding/recommend-problem` | RL-recommended next problem. Query: `?emotion_score=0.3&performance_score=0.4` |

### Adaptive Learning

| Method | URL | Description |
|---|---|---|
| POST | `/adaptive/action` | Get adaptive action `{emotion_score, performance_score, attempts?}` |
| GET | `/adaptive/history/{user_id}` | Emotion + action history timeline |

### Analytics

| Method | URL | Description |
|---|---|---|
| GET | `/analytics/summary` | Class-wide `average_emotion`, `average_performance`, `engagement_score` |
| GET | `/analytics/dashboard` | Per-user analytics for teacher view |
| GET | `/analytics/emotion-trends` | Aggregated emotion score over time (for charts) |
| GET | `/analytics/action-distribution` | Count of each adaptive action taken |
| GET | `/analytics/emotion-timeline/{user_id}` | Per-user emotion log (newest-first, `?limit=100`) |
| GET | `/analytics/difficulty-progression/{user_id}` | Per-user submission difficulty history |

### Emotion Logging

| Method | URL | Description |
|---|---|---|
| POST | `/emotion/log` | Log emotion reading `{user_id?, emotion_score, performance_score?}` → returns `adaptive_action` |
| GET | `/emotion/timeline/{user_id}` | All emotion entries for a user |

### Real-time

| Protocol | URL | Description |
|---|---|---|
| WebSocket | `/ws/emotion` | Send `{typing_data, facial_frame}` → receive `{adaptive_action, emotion_score, performance_score}` |

### AI Tutor

| Method | URL | Description |
|---|---|---|
| POST | `/ai-tutor` | Analyze student code `{code, problem_description?, language?}` → hints + suggestions |

---

## Submit Payload & Response

**Request** `POST /coding/submit`
```json
{
  "problem_id": 1,
  "code": "print('Hello, World!')",
  "user_id": 1,
  "emotion_score": 0.6,
  "performance_score": 0.8
}
```

**Response**
```json
{
  "submission_id": 42,
  "score": 1.0,
  "passed": 1,
  "total": 1,
  "adaptive_action": "challenge",
  "recommended_difficulty": "hard",
  "details": [
    {
      "test_case": 1,
      "passed": true,
      "expected": "Hello, World!",
      "stdout": "Hello, World!\n",
      "stderr": "",
      "timed_out": false,
      "exec_time_ms": 312
    }
  ]
}
```

---

## Adaptive Learning Logic

The engine maps `(emotion_score, performance_score, attempts, time_taken_s)` to an action:

| Condition | Action | Difficulty |
|---|---|---|
| emotion < 0.30 AND performance < 0.40 | `relax` | easy |
| attempts > 5 AND performance ≤ 0.60 | `relax` | easy |
| emotion < 0.50 AND performance < 0.40 | `hint` | easy |
| time < 60s AND performance > 0.80 AND attempts = 1 | `challenge` | hard |
| performance > 0.70 AND emotion > 0.60 | `challenge` | hard |
| emotion ≥ 0.50 AND performance > 0.70 | `challenge` | hard |
| otherwise | `practice` | medium |

Every `/adaptive/action` and `/coding/submit` call stores an entry in `EmotionHistory` for analytics.

---

## Problem Bank

100 problems auto-seeded on first startup:

| Difficulty | Count | Colour |
|---|---|---|
| Easy | 40 | 🟢 |
| Medium | 40 | 🟡 |
| Hard | 20 | 🔴 |

**16 categories:** math, string, arrays, sorting, conditionals, hash_table, two_pointers, stack, queue, recursion, binary_search, dynamic_programming, graphs, trees, loops, output

Each problem includes: title, description, difficulty, category, starter code, examples, hints, and hidden test cases.

---

## Datasets & Models

### Emotion Detection

The backend uses a 3-tier detection system (automatic fallback):

| Tier | Method | Accuracy | Notes |
|---|---|---|---|
| 1 | ONNX FER+ model | ~80% | Auto-downloads ~2 MB on first webcam use |
| 2 | OpenCV brightness heuristic | ~50% | Always available, no download |
| 3 | Pixel-seeded heuristic | ~40% | Zero-dependency final fallback |

**To use a custom trained model** — set in `backend/.env`:
```env
FACIAL_MODEL_PATH=./models/my_emotion.onnx
```

### Download Free Training Datasets

```powershell
cd automated-learning-system\backend

# Download FER2013 (35k images, 7 emotions) — requires Kaggle API token
python scripts/download_datasets.py --fer2013

# Download RAVDESS speech emotion dataset (no auth required)
python scripts/download_datasets.py --ravdess

# Download all datasets
python scripts/download_datasets.py --all
```

**Kaggle setup** (for FER2013, RAF-DB, Keystroke datasets):
1. Go to https://www.kaggle.com → Account → Create API Token
2. Save `kaggle.json` to `C:\Users\<you>\.kaggle\kaggle.json`
3. `pip install kaggle`

| Dataset | Size | Emotions | Source |
|---|---|---|---|
| FER2013 | 35k images | 7 (angry, disgust, fear, happy, neutral, sad, surprise) | Kaggle: `msambare/fer2013` |
| RAF-DB | 30k images | 7 (real-world photos) | Kaggle: `shuvoalok/raf-db-dataset` |
| AffectNet | 450k images | 8 | https://mohammadmahoor.com/affectnet/ |
| RAVDESS | 1.4k clips | 8 speech emotions | https://zenodo.org/record/1188976 |
| Keystroke | CSV | stress/focus patterns | Kaggle: `rtatman/keystroke-dynamics` |

### Train a Custom Emotion CNN

```powershell
# After downloading FER2013:
cd automated-learning-system\backend
python ml_training/train_emotion_cnn.py --epochs 25 --batch-size 64
# Output: models/facial_emotion.pth  (~80-85% accuracy on FER2013 test set)
```

### AI Tutor — Ollama Local LLM

For best AI tutor feedback, install Ollama (free, runs locally):

```powershell
# Install from https://ollama.ai
# Then pull a model:
ollama pull llama3         # general purpose (4.7 GB)
ollama pull codellama      # code-specialized (3.8 GB)
ollama pull deepseek-coder # best for coding tasks (3.8 GB)
```

The AI tutor auto-detects Ollama at `http://localhost:11434`. No configuration needed.

**HuggingFace Inference API** (free tier, no local GPU needed):
```env
# backend/.env
HF_API_TOKEN=hf_your_token_here
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1
```

---

| Route | Page | Description |
|---|---|---|
| `/login` | Login / Register | JWT auth with guest mode |
| `/` | Student Dashboard | Live emotion/performance chart, analytics cards, quick-nav |
| `/problems` | Problem Bank | Searchable table — filter by difficulty, category; sortable; Solved badges |
| `/code/:id` | Code Editor | Monaco editor, webcam emotion capture, adaptive hint panel, rich results table |
| `/teacher` | Teacher Dashboard | Class-wide charts (area, bar, radar), student table with status badges, CSV export |

---

## Code Sandbox Security

User code runs in a subprocess with:
- **5-second execution timeout**
- **Import blocklist:** `os`, `sys`, `subprocess`, `socket`, `shutil`, `pathlib`, `importlib`, `ctypes`, `multiprocessing`, `threading`, `http`, `urllib`, `requests`, `pickle`, `sqlite3`, `signal`, and more
- **Output truncated** at 4096 chars
- **Temp file** per execution, deleted immediately after

---

## Database Models

| Model | Key Columns |
|---|---|
| `User` | id, email, hashed_password, name |
| `EmotionLog` | user_id, emotion_score, performance_score, action, timestamp |
| `CodingProblem` | id, title, difficulty, category, description, starter_code, examples, hints |
| `TestCase` | id, problem_id, stdin, expected_stdout, is_hidden |
| `Submission` | id, user_id, problem_id, code, score, passed, total, adaptive_action, created_at |
| `UserProgress` | user_id, problem_id, attempts, solved, best_score, last_attempt |
| `EmotionHistory` | user_id, session_id, emotion_score, performance_score, adaptive_action, recommended_difficulty, timestamp |

---

## Running Tests

```powershell
cd automated-learning-system\backend
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe -m pytest tests/ -v
# Expected: 37 passed
```

Tests cover: health endpoint, auth, problem CRUD, code submission, sandbox security (blocked imports, timeout, runtime errors), multimodal fusion, RL engine logic.

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env`:

```env
SECRET_KEY=change-this-in-production
DATABASE_URL=sqlite:///./emotion_learning.db
DEBUG=False
RL_MODEL_PATH=./models/ppo_model.zip
FACIAL_MODEL_PATH=./models/facial_emotion.pth
```

---

## Project Structure

```
automated-learning-system/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, startup, seeding
│   │   ├── config.py                # Settings
│   │   ├── database.py              # SQLAlchemy engine + session
│   │   ├── data/
│   │   │   └── problems_dataset.py  # 100-problem bank
│   │   ├── models/
│   │   │   ├── user_model.py
│   │   │   ├── emotion_log.py
│   │   │   └── coding_models.py     # CodingProblem, TestCase, Submission,
│   │   │                            # UserProgress, EmotionHistory
│   │   ├── routes/
│   │   │   ├── auth_routes.py
│   │   │   ├── coding_routes.py     # /problems, /submit, /evaluate, /recommend-problem
│   │   │   ├── adaptive_routes.py   # /adaptive/action, /adaptive/history
│   │   │   ├── analytics_routes.py  # /analytics/* (6 endpoints)
│   │   │   ├── emotion_routes.py    # /emotion/log, /emotion/timeline
│   │   │   └── ai_tutor_routes.py   # /ai-tutor
│   │   ├── services/
│   │   │   ├── sandbox.py           # Subprocess code execution + timing
│   │   │   ├── rl_engine.py         # Adaptive heuristic engine
│   │   │   └── auth_service.py
│   │   ├── multimodal/
│   │   │   ├── fusion.py            # Weighted emotion fusion
│   │   │   ├── facial_emotion/
│   │   │   ├── speech_emotion/
│   │   │   └── typing_behavior/
│   │   └── utils/
│   │       ├── logger.py
│   │       └── security.py
│   ├── tests/
│   │   ├── test_endpoints.py        # 14 endpoint tests
│   │   ├── test_sandbox.py          # 14 sandbox security tests
│   │   └── test_fusion_rl.py        # 9 RL + fusion tests
│   └── requirements.txt
└── frontend/
    └── client/
        ├── .env                        # API URL overrides
        ├── src/
        │   ├── App.js                  # Router + navbar + auth
        │   └── pages/
        │       ├── LoginPage.jsx       # Login / Register / Guest
        │       ├── Dashboard.js        # Student home + live charts
        │       ├── ProblemsPage.jsx    # 100-problem filtered table
        │       ├── CodingInterface.jsx # Monaco editor + webcam + results
        │       └── TeacherDashboard.jsx # Class analytics + student table
        └── package.json
```

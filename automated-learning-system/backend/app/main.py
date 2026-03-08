"""Emotion-Adaptive Learning System API Server."""

import contextlib
import json
import base64

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.utils.logger import logger
from app.utils.emotion_utils import get_emotion_label

# Register all ORM models with Base metadata before create_all
from app.models.user_model import User  # noqa: F401
from app.models.emotion_log import EmotionLog  # noqa: F401
from app.models.coding_models import CodingProblem, TestCase, Submission, UserProgress, EmotionHistory  # noqa: F401

from app.routes import auth_routes, analytics_routes, emotion_routes
from app.routes.coding_routes import router as coding_router
from app.routes.adaptive_routes import router as adaptive_router
from app.routes.ai_tutor_routes import router as tutor_router
from app.data.problems_dataset import PROBLEMS as PROBLEM_DATASET


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all DB tables, run column migrations, and seed sample problems on startup."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created/verified")
        _upgrade_database()
        _seed_problems()
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    yield


def _upgrade_database():
    """Add any new columns to existing tables (safe for SQLite)."""
    from sqlalchemy import text
    with engine.connect() as conn:
        # Add columns to coding_problems if missing
        try:
            conn.execute(text("SELECT examples FROM coding_problems LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE coding_problems ADD COLUMN examples TEXT"))
                conn.execute(text("ALTER TABLE coding_problems ADD COLUMN hints TEXT"))
                conn.execute(text("ALTER TABLE coding_problems ADD COLUMN category TEXT"))
                conn.commit()
                logger.info("✓ Migrated coding_problems table — added examples/hints/category")
            except Exception as e:
                logger.warning(f"Migration warning (non-fatal): {e}")

        # Add emotion_label column to emotion_logs if missing
        try:
            conn.execute(text("SELECT emotion_label FROM emotion_logs LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE emotion_logs ADD COLUMN emotion_label TEXT"))
                conn.commit()
                logger.info("✓ Migrated emotion_logs table — added emotion_label column")
            except Exception as e:
                logger.warning(f"Migration warning (non-fatal): {e}")


def _seed_problems():
    """Insert 100 coding problems from the dataset if the table is empty."""
    db = SessionLocal()
    try:
        if db.query(CodingProblem).count() > 0:
            return
        for entry in PROBLEM_DATASET:
            entry = dict(entry)          # shallow copy so we can pop 'tests'
            tests = entry.pop("tests")
            entry["examples"] = json.dumps(entry.get("examples", []))
            entry["hints"] = json.dumps(entry.get("hints", []))
            prob = CodingProblem(**entry)
            db.add(prob)
            db.flush()
            for t in tests:
                db.add(TestCase(
                    problem_id=prob.id,
                    stdin=t["stdin"],
                    expected_stdout=t["expected_stdout"],
                ))
        db.commit()
        logger.info(f"✓ Seeded {len(PROBLEM_DATASET)} coding problems")
    except Exception as e:
        logger.warning(f"Problem seeding failed (non-fatal): {e}")
        db.rollback()
    finally:
        db.close()




app = FastAPI(
    title="Emotion-Adaptive Learning API",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# ── Routes ──────────────────────────────────────────────────────────────────
app.include_router(auth_routes.router)
app.include_router(analytics_routes.router)
app.include_router(emotion_routes.router)
app.include_router(coding_router)
app.include_router(adaptive_router)
app.include_router(tutor_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "emotion-adaptive-learning", "version": "1.0.0"}


def _get_emotion_label(score: float) -> str:
    """Alias for backward compatibility — delegates to shared utility."""
    return get_emotion_label(score)


# ── WebSocket ────────────────────────────────────────────────────────────────

@app.websocket("/ws/emotion")
async def websocket_emotion(websocket: WebSocket):
    """
    Real-time multimodal emotion processing WebSocket.

    Accepted payload (JSON):
        facial_frame   (str, base64 JPEG, optional)
        audio_chunk    (list[float], optional)  raw PCM samples at 16kHz
        typing_data    (object, optional) { intervals: [...], mistakes: int, total_chars: int }
        performance_score (float, optional, default 0.5)

    Response (JSON):
        emotion_score, performance_score, adaptive_action, message
    """
    await websocket.accept()
    logger.info("✓ WebSocket /ws/emotion connected")

    from app.multimodal.fusion import weighted_fusion
    from app.services.rl_engine import rl_engine
    from app.multimodal.facial_emotion.model import FacialEmotionModel
    from app.multimodal.speech_emotion.model import SpeechEmotionModel
    from app.multimodal.typing_behavior.analyzer import TypingBehaviorAnalyzer

    facial_model = FacialEmotionModel()
    speech_model = SpeechEmotionModel()
    typing_analyzer = TypingBehaviorAnalyzer()

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)

                # ── Facial ──
                facial_score = None
                frame_b64 = payload.get("facial_frame")
                if frame_b64:
                    try:
                        import numpy as np
                        img_bytes = base64.b64decode(frame_b64)
                        arr = np.frombuffer(img_bytes, dtype=np.uint8)
                        import cv2
                        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                        facial_score = facial_model.predict(img)
                    except Exception as e:
                        logger.debug(f"Facial decode error: {e}")

                # ── Speech ──
                speech_score = None
                audio_chunk = payload.get("audio_chunk")
                if audio_chunk:
                    try:
                        import numpy as np
                        audio_arr = np.array(audio_chunk, dtype=np.float32)
                        speech_score = speech_model.predict(audio_arr)
                    except Exception as e:
                        logger.debug(f"Speech decode error: {e}")

                # ── Typing ──
                typing_score = None
                typing_data = payload.get("typing_data")
                if typing_data:
                    try:
                        intervals = typing_data.get("intervals", [])
                        mistakes = int(typing_data.get("mistakes", 0))
                        total_chars = int(typing_data.get("total_chars", 0))
                        typing_score = typing_analyzer.analyze(intervals, mistakes, total_chars)
                    except Exception as e:
                        logger.debug(f"Typing analysis error: {e}")

                # ── Allow direct score pass-through for testing ──
                if facial_score is None:
                    facial_score = payload.get("facial_score")
                if speech_score is None:
                    speech_score = payload.get("speech_score")
                if typing_score is None:
                    typing_score = payload.get("typing_score")

                emotion_score = payload.get("emotion_score")
                if emotion_score is None:
                    emotion_score = weighted_fusion(facial_score, speech_score, typing_score)

                performance_score = float(payload.get("performance_score", typing_score or 0.5))
                emotion_score = max(0.0, min(1.0, float(emotion_score)))
                performance_score = max(0.0, min(1.0, performance_score))

                action = rl_engine.get_adaptive_action(emotion_score, performance_score)
                emotion_label = _get_emotion_label(emotion_score)

                # Persist log
                db = SessionLocal()
                try:
                    log = EmotionLog(
                        user_id=payload.get("user_id"),
                        emotion_score=emotion_score,
                        emotion_label=emotion_label,
                        performance_score=performance_score,
                        adaptive_action=action,
                    )
                    db.add(log)
                    db.commit()
                finally:
                    db.close()

                await websocket.send_text(json.dumps({
                    "emotion_score": round(emotion_score, 3),
                    "emotion_label": emotion_label,
                    "performance_score": round(performance_score, 3),
                    "adaptive_action": action,
                    "message": f"Recommended: {action}",
                }))

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
            except Exception as e:
                logger.error(f"WebSocket processing error: {e}")
                await websocket.send_text(json.dumps({"error": "Processing failed"}))

    except WebSocketDisconnect:
        logger.info("✓ WebSocket /ws/emotion disconnected")
    except Exception as e:
        logger.error(f"WebSocket unexpected error: {e}")


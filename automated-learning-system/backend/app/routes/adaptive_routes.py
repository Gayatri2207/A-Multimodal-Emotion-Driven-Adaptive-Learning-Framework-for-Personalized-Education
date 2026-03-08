"""Adaptive learning routes — REST interface to the RL engine."""

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.services.rl_engine import rl_engine
from app.models.coding_models import EmotionHistory
from app.utils.logger import logger


router = APIRouter(prefix="/adaptive", tags=["adaptive"])


class AdaptiveRequest(BaseModel):
    user_id: int = 0
    emotion_score: float = 0.5
    performance_score: float = 0.5


@router.post("/action")
def get_action(payload: AdaptiveRequest, db: Session = Depends(get_db)):
    """
    Return the recommended adaptive action based on emotion + performance scores.

    Actions: relax | hint | challenge | practice
    Also returns recommended problem difficulty:
        relax/hint  → easy
        practice    → medium
        challenge   → hard
    """
    action = rl_engine.get_adaptive_action(payload.emotion_score, payload.performance_score)
    difficulty_map = {"relax": "easy", "hint": "easy", "practice": "medium", "challenge": "hard"}
    difficulty = difficulty_map.get(action, "medium")

    # Persist to EmotionHistory
    try:
        db.add(EmotionHistory(
            user_id=payload.user_id,
            session_id=str(uuid.uuid4()),
            emotion_score=payload.emotion_score,
            performance_score=payload.performance_score,
            adaptive_action=action,
            recommended_difficulty=difficulty,
        ))
        db.commit()
    except Exception as e:
        logger.error(f"Failed to persist adaptive action to DB: {e}")
        db.rollback()

    return {
        "action": action,
        "recommended_difficulty": difficulty,
        "emotion_score": round(payload.emotion_score, 3),
        "performance_score": round(payload.performance_score, 3),
    }


@router.post("/update")
def update_performance(user_id: int, score: int, emotion: str, db: Session = Depends(get_db)):
    """Legacy endpoint — maps string emotion + int score to adaptive action."""
    emotion_map = {"happy": 0.8, "neutral": 0.5, "sad": 0.2, "frustrated": 0.15, "bored": 0.7}
    emotion_score = emotion_map.get(emotion.lower(), 0.5)
    performance_score = max(0.0, min(1.0, score / 100.0))
    action = rl_engine.get_adaptive_action(emotion_score, performance_score)
    return {"adaptive_action": action, "user_id": user_id}


@router.get("/history/{user_id}")
def get_emotion_history(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Return the last N emotion + adaptive action records for a user."""
    records = (
        db.query(EmotionHistory)
        .filter(EmotionHistory.user_id == user_id)
        .order_by(EmotionHistory.timestamp.desc())
        .limit(limit)
        .all()
    )
    return {
        "user_id": user_id,
        "history": [
            {
                "session_id": r.session_id,
                "emotion_score": r.emotion_score,
                "performance_score": r.performance_score,
                "adaptive_action": r.adaptive_action,
                "recommended_difficulty": r.recommended_difficulty,
                "timestamp": str(r.timestamp),
            }
            for r in records
        ],
    }


from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.emotion_log import EmotionLog
from app.services.rl_engine import rl_engine
from app.utils.emotion_utils import get_emotion_label

router = APIRouter(prefix="/emotion", tags=["emotion"])


class EmotionLogRequest(BaseModel):
    user_id: Optional[int] = None
    emotion_score: float
    emotion_label: Optional[str] = None    # e.g. "Frustrated", "Focused"
    performance_score: float = 0.5
    adaptive_action: Optional[str] = None


@router.post("/log")
def log_emotion(req: EmotionLogRequest, db: Session = Depends(get_db)):
    """Log an emotion entry for a user (accepts JSON body)."""
    action = req.adaptive_action or rl_engine.get_adaptive_action(
        req.emotion_score, req.performance_score
    )
    label = req.emotion_label or get_emotion_label(req.emotion_score)
    log = EmotionLog(
        user_id=req.user_id,
        emotion_score=max(0.0, min(1.0, req.emotion_score)),
        emotion_label=label,
        performance_score=max(0.0, min(1.0, req.performance_score)),
        adaptive_action=action,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {
        "message": "Emotion logged",
        "id": log.id,
        "adaptive_action": action,
    }


@router.get("/timeline/{user_id}")
def emotion_timeline(
    user_id: int,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Return recent emotion logs for a user (newest-first)."""
    logs = (
        db.query(EmotionLog)
        .filter(EmotionLog.user_id == user_id)
        .order_by(desc(EmotionLog.created_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "id":               l.id,
            "emotion_score":    round(l.emotion_score, 3),
            "emotion_label":    l.emotion_label or "",
            "performance_score": round(l.performance_score, 3),
            "adaptive_action":  l.adaptive_action,
            "created_at":       str(l.created_at),
        }
        for l in reversed(logs)
    ]

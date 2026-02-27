from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.emotion_log import EmotionLog
from app import schemas
from sqlalchemy import func

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=schemas.AnalyticsOut)
def summary(db: Session = Depends(get_db)):
    total = db.query(func.count(EmotionLog.id)).scalar() or 0
    avg_emotion = db.query(func.avg(EmotionLog.emotion_score)).scalar() or 0.0
    avg_perf = db.query(func.avg(EmotionLog.performance_score)).scalar() or 0.0
    # simple engagement metric: normalized combination
    engagement = float((avg_perf * 0.6) + (avg_emotion * 0.4))
    return {"average_emotion": float(avg_emotion), "average_performance": float(avg_perf), "engagement_score": engagement}
from fastapi import APIRouter
import random

router = APIRouter()

@router.get("/analytics")
def get_analytics():
    return {
        "average_emotion": round(random.uniform(0.3, 0.9), 2),
        "average_performance": round(random.uniform(0.4, 0.95), 2),
        "engagement_score": round(random.uniform(0.5, 1.0), 2)
    }

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from app.database import get_db
from app.models.emotion_log import EmotionLog
from app.models.coding_models import Submission, CodingProblem
from app import schemas

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _engagement(emotion: float, performance: float) -> float:
    """
    Engagement score formula:
    - Performance (50%) — test pass rate is the primary signal
    - Emotion (30%)     — positive affect correlates with engagement
    - Consistency (20%) — weighted mean of both signals (not binary)

    Clipped to [0, 1].
    """
    consistency = (emotion + performance) / 2.0 if (emotion > 0 or performance > 0) else 0.0
    return round(float(performance * 0.5 + emotion * 0.3 + consistency * 0.2), 3)


@router.get("/summary", response_model=schemas.AnalyticsOut)
def get_summary(db: Session = Depends(get_db)):
    """Return aggregated emotion/performance analytics."""
    avg_emotion = db.query(func.avg(EmotionLog.emotion_score)).scalar() or 0.0
    avg_perf    = db.query(func.avg(EmotionLog.performance_score)).scalar() or 0.0
    total_logs  = db.query(func.count(EmotionLog.id)).scalar() or 0
    engagement  = _engagement(float(avg_emotion), float(avg_perf))
    return {
        "average_emotion":    round(float(avg_emotion), 3),
        "average_performance": round(float(avg_perf), 3),
        "engagement_score":   engagement,
        "total_sessions":     total_logs,
    }


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """Per-user aggregated dashboard data for teacher view."""
    rows = (
        db.query(
            EmotionLog.user_id,
            func.avg(EmotionLog.emotion_score).label("avg_emotion"),
            func.avg(EmotionLog.performance_score).label("avg_performance"),
            func.count(EmotionLog.id).label("sessions"),
            func.max(EmotionLog.created_at).label("last_active"),
        )
        .group_by(EmotionLog.user_id)
        .all()
    )
    return [
        {
            "user_id":         r.user_id,
            "avg_emotion":     round(float(r.avg_emotion), 3),
            "avg_performance": round(float(r.avg_performance), 3),
            "engagement_score": _engagement(float(r.avg_emotion), float(r.avg_performance)),
            "sessions":        r.sessions,
            "last_active":     str(r.last_active) if r.last_active else None,
        }
        for r in rows
    ]


@router.get("/emotion-timeline/{user_id}")
def get_emotion_timeline(
    user_id: Optional[int],
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return recent emotion log entries for a specific user (chronological)."""
    q = db.query(EmotionLog)
    if user_id is not None:
        q = q.filter(EmotionLog.user_id == user_id)
    rows = q.order_by(desc(EmotionLog.created_at)).limit(limit).all()
    return [
        {
            "id":               r.id,
            "emotion_score":    round(r.emotion_score, 3),
            "emotion_label":    r.emotion_label or "",
            "performance_score": round(r.performance_score, 3),
            "adaptive_action":  r.adaptive_action,
            "engagement_score": _engagement(r.emotion_score, r.performance_score),
            "timestamp":        str(r.created_at),
        }
        for r in reversed(rows)
    ]


@router.get("/difficulty-progression/{user_id}")
def get_difficulty_progression(user_id: int, db: Session = Depends(get_db)):
    """Return submission history with difficulty, score, and emotion context."""
    subs = (
        db.query(Submission, CodingProblem.difficulty, CodingProblem.category)
        .join(CodingProblem, Submission.problem_id == CodingProblem.id)
        .filter(Submission.user_id == user_id)
        .order_by(Submission.created_at.asc())
        .limit(100)
        .all()
    )
    return [
        {
            "submission_id": s.Submission.id,
            "problem_id":    s.Submission.problem_id,
            "difficulty":    s.difficulty,
            "category":      s.category,
            "score":         round(s.Submission.score, 3),
            "passed":        s.Submission.passed,
            "total":         s.Submission.total,
            "timestamp":     str(s.Submission.created_at),
        }
        for s in subs
    ]


@router.get("/emotion-trends")
def get_emotion_trends(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """Return average emotion per hour bucket over the last N hours."""
    from sqlalchemy import text
    from datetime import datetime, timedelta, timezone

    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = (
        db.query(EmotionLog)
        .filter(EmotionLog.created_at >= since)
        .order_by(EmotionLog.created_at.asc())
        .all()
    )
    # Group by hour
    buckets: dict = {}
    for r in rows:
        if r.created_at:
            key = r.created_at.strftime("%Y-%m-%d %H:00")
            if key not in buckets:
                buckets[key] = {"emotion": [], "performance": [], "count": 0}
            buckets[key]["emotion"].append(r.emotion_score)
            buckets[key]["performance"].append(r.performance_score)
            buckets[key]["count"] += 1

    return [
        {
            "hour":             k,
            "avg_emotion":      round(sum(v["emotion"]) / len(v["emotion"]), 3) if v["emotion"] else 0.0,
            "avg_performance":  round(sum(v["performance"]) / len(v["performance"]), 3) if v["performance"] else 0.0,
            "count":            v["count"],
        }
        for k, v in sorted(buckets.items())
    ]


@router.get("/action-distribution")
def get_action_distribution(db: Session = Depends(get_db)):
    """Return count of each adaptive action recommendation."""
    rows = (
        db.query(EmotionLog.adaptive_action, func.count(EmotionLog.id).label("count"))
        .group_by(EmotionLog.adaptive_action)
        .all()
    )
    return {r.adaptive_action: r.count for r in rows}

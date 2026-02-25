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

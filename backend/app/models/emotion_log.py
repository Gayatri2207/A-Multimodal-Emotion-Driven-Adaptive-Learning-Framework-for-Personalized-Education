from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


try:
    class EmotionLog(Base):
        __tablename__ = "emotion_logs"
        __table_args__ = {"extend_existing": True}

        id = Column(Integer, primary_key=True, index=True)
        user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
        emotion_score = Column(Float, nullable=False)
        performance_score = Column(Float, nullable=False)
        adaptive_action = Column(String, nullable=False)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
except Exception as e:
    from sqlalchemy.exc import InvalidRequestError
    if isinstance(e, InvalidRequestError):
        pass
    else:
        raise

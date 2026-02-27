from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EmotionIn(BaseModel):
    emotion_score: float
    performance_score: float


class EmotionOut(BaseModel):
    adaptive_action: str


class AnalyticsOut(BaseModel):
    average_emotion: float
    average_performance: float
    engagement_score: float

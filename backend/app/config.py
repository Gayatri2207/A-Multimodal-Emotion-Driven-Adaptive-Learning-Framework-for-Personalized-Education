import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Emotion-Adaptive Learning API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    RL_MODEL_PATH: str = os.getenv("RL_MODEL_PATH", "./rl_model.zip")
    WAV2VEC_MODEL: str = os.getenv("WAV2VEC_MODEL", "facebook/wav2vec2-base")


settings = Settings()
DATABASE_URL = "sqlite:///./emotion_learning.db"

SECRET_KEY = "supersecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

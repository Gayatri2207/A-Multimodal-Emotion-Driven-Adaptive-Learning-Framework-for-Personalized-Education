import os


class Settings:
    """Application settings and configuration."""
    APP_NAME: str = "Emotion-Adaptive Learning API"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./emotion_learning.db")

    # Security — SECRET_KEY must be set via environment variable in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # ML/RL Models
    RL_MODEL_PATH: str = os.getenv("RL_MODEL_PATH", "./models/ppo_model.zip")
    FACIAL_MODEL_PATH: str = os.getenv("FACIAL_MODEL_PATH", "./models/facial_emotion.pth")

    # CORS — browsers reject allow_credentials=True with allow_origins=["*"].
    # Accept explicit origins from env, fall back to localhost dev origins.
    _raw_origins: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000",
    )
    CORS_ORIGINS: list = [o.strip() for o in _raw_origins.split(",") if o.strip()]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]


settings = Settings()

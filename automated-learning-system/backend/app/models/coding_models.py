"""ORM models for the coding platform."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class CodingProblem(Base):
    __tablename__ = "coding_problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String, default="easy")       # easy | medium | hard
    starter_code = Column(Text, default="")
    # JSON-encoded strings for rich problem display (nullable for migration safety)
    examples = Column(Text, nullable=True)            # JSON: [{"input": "...", "output": "..."}]
    hints = Column(Text, nullable=True)               # JSON: ["hint1", "hint2"]
    category = Column(String, nullable=True)          # e.g. "string", "array", "math"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<CodingProblem(id={self.id}, title={self.title!r})>"


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("coding_problems.id"), nullable=False)
    stdin = Column(Text, default="")
    expected_stdout = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False)       # hidden cases not shown to student

    def __repr__(self):
        return f"<TestCase(id={self.id}, problem_id={self.problem_id})>"


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    problem_id = Column(Integer, ForeignKey("coding_problems.id"), nullable=False)
    code = Column(Text, nullable=False)
    score = Column(Float, default=0.0)
    passed = Column(Integer, default=0)
    total = Column(Integer, default=0)
    stdout = Column(Text, default="")
    stderr = Column(Text, default="")
    timed_out = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Submission(id={self.id}, user_id={self.user_id}, score={self.score})>"


class UserProgress(Base):
    """Tracks per-user per-problem solve status and best score."""

    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    problem_id = Column(Integer, ForeignKey("coding_problems.id"), nullable=False, index=True)
    attempts = Column(Integer, default=0)
    solved = Column(Boolean, default=False)
    best_score = Column(Float, default=0.0)
    last_attempt = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        return f"<UserProgress(user={self.user_id}, problem={self.problem_id}, solved={self.solved})>"


class EmotionHistory(Base):
    """Stores per-session emotion snapshots for analytics and RL training."""

    __tablename__ = "emotion_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String, nullable=True)
    emotion_score = Column(Float, nullable=False)
    performance_score = Column(Float, default=0.5)
    adaptive_action = Column(String, nullable=True)    # relax | hint | practice | challenge
    recommended_difficulty = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<EmotionHistory(user={self.user_id}, emotion={self.emotion_score}, action={self.adaptive_action})>"

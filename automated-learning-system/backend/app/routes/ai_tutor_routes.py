"""AI Coding Tutor API routes."""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from app.services.ai_tutor_service import analyze_code
from app.utils.logger import logger

router = APIRouter(prefix="/ai-tutor", tags=["ai-tutor"])


# ── Request / Response schemas ───────────────────────────────────────────────

class TutorRequest(BaseModel):
    problem: str = Field(..., description="Problem title and description")
    code: str = Field(..., description="Student's Python code")
    emotion_score: float = Field(0.5, ge=0.0, le=1.0, description="Emotion score from 0 (frustrated) to 1 (engaged)")
    user_id: Optional[int] = Field(None, description="User ID for personalised feedback context")

    class Config:
        schema_extra = {
            "example": {
                "problem": "Two Sum: Given an array of integers, return indices of the two numbers that add up to target.",
                "code": "def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n",
                "emotion_score": 0.4,
                "user_id": 1,
            }
        }


class TutorResponse(BaseModel):
    tutor_feedback: str           # human-readable plain-text summary (legacy compat)
    summary: str
    mistakes: list[str]
    improvements: list[str]
    algorithm_insight: str
    hints: list[str]
    time_complexity: str
    space_complexity: str
    readability_score: int
    efficiency_score: int
    emotion_note: str
    source: str                   # "rules" | "llm"


# ── Endpoint ─────────────────────────────────────────────────────────────────

@router.post("", response_model=TutorResponse, summary="Get AI tutor feedback on submitted code")
async def get_tutor_feedback(request: TutorRequest) -> TutorResponse:
    """
    Analyse student code and return structured, educational tutor feedback.

    - **problem**: problem title + description text
    - **code**: the student's Python submission
    - **emotion_score**: real-time emotion value (0 = frustrated → verbose guidance,
      1 = bored/confident → terse optimisation hints)
    """
    logger.info(f"AI Tutor request — emotion={request.emotion_score:.2f}, "
                f"code_lines={len(request.code.splitlines())}")

    try:
        result = analyze_code(
            problem=request.problem,
            code=request.code,
            emotion_score=request.emotion_score,
        )
    except Exception as e:
        logger.error(f"AI Tutor analyze_code failed: {e}")
        # Graceful fallback — return a minimal valid response
        result = {
            "summary": "Could not fully analyse code. Please check your syntax.",
            "mistakes": [],
            "improvements": ["Ensure your code runs without errors before requesting feedback."],
            "algorithm_insight": "",
            "hints": ["Try running your code step by step to find the issue."],
            "time_complexity": "Unknown",
            "space_complexity": "Unknown",
            "readability_score": 50,
            "efficiency_score": 50,
            "emotion_note": "",
            "source": "fallback",
            "raw_text": "",
        }

    # Build the legacy plain-text field for simple consumers
    parts: list[str] = []

    if result["emotion_note"]:
        parts.append(result["emotion_note"])

    parts.append(f"Summary: {result['summary']}")

    if result["mistakes"]:
        parts.append("\nMistakes detected:")
        parts.extend(f"  • {m}" for m in result["mistakes"])

    if result["improvements"]:
        parts.append("\nSuggested improvements:")
        parts.extend(f"  • {s}" for s in result["improvements"])

    if result["algorithm_insight"]:
        parts.append(f"\nAlgorithm insight: {result['algorithm_insight']}")

    if result["hints"]:
        parts.append("\nHints (without the solution):")
        parts.extend(f"  💡 {h}" for h in result["hints"])

    parts.append(f"\nComplexity  — Time: {result['time_complexity']}  |  Space: {result['space_complexity']}")
    parts.append(f"Code quality — Readability: {result['readability_score']}/100  |  Efficiency: {result['efficiency_score']}/100")

    if result.get("raw_text"):
        parts.append(f"\n--- AI Analysis ---\n{result['raw_text']}")

    plain_text = "\n".join(parts)

    return TutorResponse(
        tutor_feedback=plain_text,
        summary=result["summary"],
        mistakes=result["mistakes"],
        improvements=result["improvements"],
        algorithm_insight=result["algorithm_insight"],
        hints=result["hints"],
        time_complexity=result["time_complexity"],
        space_complexity=result["space_complexity"],
        readability_score=result["readability_score"],
        efficiency_score=result["efficiency_score"],
        emotion_note=result["emotion_note"],
        source=result["source"],
    )

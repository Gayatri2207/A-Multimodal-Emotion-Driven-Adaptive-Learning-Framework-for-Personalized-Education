"""REST API routes for the coding platform."""

import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.coding_models import CodingProblem, TestCase, Submission
from app.services.sandbox import evaluate_against_tests
from app.services.rl_engine import rl_engine
from app.utils.logger import logger

router = APIRouter(prefix="/coding", tags=["coding"])


# ── Pydantic schemas ────────────────────────────────────────────────────────

class ProblemCreate(BaseModel):
    title: str
    description: str
    difficulty: str = "easy"
    starter_code: str = ""
    examples: Optional[str] = None   # JSON string
    hints: Optional[str] = None      # JSON string
    category: Optional[str] = None


class TestCaseCreate(BaseModel):
    stdin: str = ""
    expected_stdout: str
    is_hidden: bool = False


class ProblemOut(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    starter_code: str
    examples: Optional[str] = None
    hints: Optional[str] = None
    category: Optional[str] = None

    class Config:
        orm_mode = True


class SubmitRequest(BaseModel):
    user_id: Optional[int] = None
    problem_id: int
    code: str
    emotion_score: Optional[float] = None
    performance_score: Optional[float] = None


class SubmitResult(BaseModel):
    submission_id: int
    score: float
    passed: int
    total: int
    details: list
    adaptive_action: Optional[str] = None
    recommended_difficulty: Optional[str] = None


# ── Problem endpoints ───────────────────────────────────────────────────────

@router.get("/problems", response_model=List[ProblemOut])
def list_problems(
    difficulty: Optional[str] = Query(None, description="Filter: easy | medium | hard"),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Return all coding problems, optionally filtered by difficulty or category."""
    q = db.query(CodingProblem).order_by(CodingProblem.id)
    if difficulty:
        q = q.filter(CodingProblem.difficulty == difficulty.lower())
    if category:
        q = q.filter(CodingProblem.category == category.lower())
    return q.all()


@router.get("/problems/{problem_id}", response_model=ProblemOut)
def get_problem(problem_id: int, db: Session = Depends(get_db)):
    problem = db.query(CodingProblem).filter(CodingProblem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.post("/problems", response_model=ProblemOut, status_code=201)
def create_problem(payload: ProblemCreate, db: Session = Depends(get_db)):
    problem = CodingProblem(**payload.dict())
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


@router.post("/problems/{problem_id}/test-cases", status_code=201)
def add_test_case(problem_id: int, payload: TestCaseCreate, db: Session = Depends(get_db)):
    if not db.query(CodingProblem).filter(CodingProblem.id == problem_id).first():
        raise HTTPException(status_code=404, detail="Problem not found")
    tc = TestCase(problem_id=problem_id, **payload.dict())
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return {"id": tc.id, "problem_id": tc.problem_id}


# ── Adaptive Recommend endpoint ─────────────────────────────────────────────

@router.get("/recommend")
def recommend_problem(
    emotion_score: float = Query(0.5, ge=0.0, le=1.0),
    performance_score: float = Query(0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
):
    """
    Return a recommended problem based on adaptive RL action.

    Maps:
        relax/hint   → easy problem
        practice     → medium problem
        challenge    → hard problem
    """
    action = rl_engine.get_adaptive_action(emotion_score, performance_score)
    difficulty_map = {"relax": "easy", "hint": "easy", "practice": "medium", "challenge": "hard"}
    target_difficulty = difficulty_map.get(action, "medium")

    problem = (
        db.query(CodingProblem)
        .filter(CodingProblem.difficulty == target_difficulty)
        .order_by(func.random())
        .first()
    )
    if not problem:
        # Fallback: return any problem
        problem = db.query(CodingProblem).order_by(func.random()).first()

    return {
        "action": action,
        "recommended_difficulty": target_difficulty,
        "problem": {
            "id": problem.id if problem else None,
            "title": problem.title if problem else None,
            "difficulty": problem.difficulty if problem else None,
        } if problem else None,
        "emotion_score": round(emotion_score, 3),
        "performance_score": round(performance_score, 3),
    }


# ── Submission endpoint ─────────────────────────────────────────────────────

@router.post("/submit", response_model=SubmitResult)
def submit_code(payload: SubmitRequest, db: Session = Depends(get_db)):
    """Execute submitted code against the problem's test cases."""
    problem = db.query(CodingProblem).filter(CodingProblem.id == payload.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    test_cases = (
        db.query(TestCase)
        .filter(TestCase.problem_id == payload.problem_id)
        .all()
    )
    tc_list = [{"stdin": t.stdin, "expected_stdout": t.expected_stdout} for t in test_cases]

    if not tc_list:
        raise HTTPException(status_code=400, detail="No test cases defined for this problem")

    try:
        result = evaluate_against_tests(payload.code, tc_list)
    except Exception as e:
        logger.error(f"Sandbox error: {e}")
        raise HTTPException(status_code=500, detail="Code execution failed")

    score = result["score"]
    emotion = max(0.0, min(1.0, float(payload.emotion_score or 0.5)))

    # Count previous attempts — guest users (no user_id) start fresh at 0
    if payload.user_id:
        prev_attempts = (
            db.query(func.count(Submission.id))
            .filter(
                Submission.problem_id == payload.problem_id,
                Submission.user_id == payload.user_id,
            )
            .scalar() or 0
        )
    else:
        prev_attempts = 0
    adaptive_action = rl_engine.get_adaptive_action(
        emotion, score,
        attempts=prev_attempts + 1,
    )
    diff_map = {"relax": "easy", "hint": "easy", "practice": "medium", "challenge": "hard"}

    # Persist submission — store all test results as JSON for full auditability
    all_stdout = json.dumps([d["stdout"] for d in result["details"]]) if result["details"] else ""
    all_stderr = json.dumps([d["stderr"] for d in result["details"]]) if result["details"] else ""
    sub = Submission(
        user_id=payload.user_id,
        problem_id=payload.problem_id,
        code=payload.code,
        score=result["score"],
        passed=result["passed"],
        total=result["total"],
        stdout=all_stdout,
        stderr=all_stderr,
        timed_out=any(d["timed_out"] for d in result["details"]),
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    return {
        "submission_id": sub.id,
        "score": result["score"],
        "passed": result["passed"],
        "total": result["total"],
        "details": result["details"],
        "adaptive_action": adaptive_action,
        "recommended_difficulty": diff_map.get(adaptive_action, "medium"),
    }


@router.get("/submissions/{user_id}")
def get_submissions(user_id: int, db: Session = Depends(get_db)):
    """Return all submissions for a user."""
    subs = (
        db.query(Submission)
        .filter(Submission.user_id == user_id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "problem_id": s.problem_id,
            "score": s.score,
            "passed": s.passed,
            "total": s.total,
            "timed_out": s.timed_out,
            "created_at": str(s.created_at),
        }
        for s in subs
    ]


# ── Coding Stats endpoints ──────────────────────────────────────────────────

@router.get("/stats")
def get_coding_stats(db: Session = Depends(get_db)):
    """Overall coding platform statistics."""
    total_subs = db.query(func.count(Submission.id)).scalar() or 0
    avg_score = db.query(func.avg(Submission.score)).scalar() or 0.0
    total_problems = db.query(func.count(CodingProblem.id)).scalar() or 0

    # Pass rate by difficulty
    by_diff = (
        db.query(
            CodingProblem.difficulty,
            func.avg(Submission.score).label("avg_score"),
            func.count(Submission.id).label("submissions"),
        )
        .join(Submission, Submission.problem_id == CodingProblem.id, isouter=True)
        .group_by(CodingProblem.difficulty)
        .all()
    )

    return {
        "total_submissions": total_subs,
        "total_problems": total_problems,
        "overall_avg_score": round(float(avg_score), 3),
        "by_difficulty": [
            {
                "difficulty": r.difficulty,
                "avg_score": round(float(r.avg_score or 0), 3),
                "submissions": r.submissions or 0,
            }
            for r in by_diff
        ],
    }


@router.get("/stats/{user_id}")
def get_user_coding_stats(user_id: int, db: Session = Depends(get_db)):
    """Per-user coding statistics."""
    subs = db.query(Submission).filter(Submission.user_id == user_id).all()
    if not subs:
        return {"user_id": user_id, "total_submissions": 0, "avg_score": 0.0, "problems_attempted": 0}

    total = len(subs)
    avg_score = sum(s.score for s in subs) / total
    problems_attempted = len({s.problem_id for s in subs})
    best_score = max(s.score for s in subs)

    return {
        "user_id": user_id,
        "total_submissions": total,
        "avg_score": round(avg_score, 3),
        "best_score": round(best_score, 3),
        "problems_attempted": problems_attempted,
    }


# ── Additional routes ────────────────────────────────────────────────────────

@router.post("/evaluate", response_model=SubmitResult)
def evaluate_submission(payload: SubmitRequest, db: Session = Depends(get_db)):
    """Alias for /submit — kept for API compatibility."""
    return submit_code(payload, db)


@router.get("/recommend-problem")
def recommend_problem_by_emotion(
    emotion_score: float = Query(0.5),
    performance_score: float = Query(0.5),
    db: Session = Depends(get_db),
):
    """Return a recommended problem based on emotion + performance scores (alias route)."""
    action = rl_engine.get_adaptive_action(emotion_score, performance_score)
    difficulty_map = {
        "relax":     "easy",
        "hint":      "easy",
        "practice":  "medium",
        "challenge": "hard",
    }
    difficulty = difficulty_map.get(action, "medium")
    problems = db.query(CodingProblem).filter(CodingProblem.difficulty == difficulty).all()
    if not problems:
        problems = db.query(CodingProblem).all()
    import random
    problem = random.choice(problems) if problems else None
    return {
        "adaptive_action": action,
        "recommended_difficulty": difficulty,
        "problem": {
            "id": problem.id,
            "title": problem.title,
            "difficulty": problem.difficulty,
            "category": problem.category,
        } if problem else None,
    }


@router.get("/progress/{user_id}")
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    """Return per-problem progress for a user using the Submission table."""
    subs = (
        db.query(Submission)
        .filter(Submission.user_id == user_id)
        .order_by(Submission.created_at.asc())
        .all()
    )
    progress: dict = {}
    for s in subs:
        pid = s.problem_id
        if pid not in progress:
            progress[pid] = {
                "problem_id": pid,
                "attempts": 0,
                "solved": False,
                "best_score": 0.0,
                "last_attempt": None,
            }
        progress[pid]["attempts"] += 1
        if s.score > progress[pid]["best_score"]:
            progress[pid]["best_score"] = round(s.score, 3)
        if s.score == 1.0:
            progress[pid]["solved"] = True
        progress[pid]["last_attempt"] = str(s.created_at)
    return {"user_id": user_id, "problems": list(progress.values())}


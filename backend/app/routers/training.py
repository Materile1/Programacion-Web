from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import current_user
from ..models import Challenge, Submission, User
from ..schemas import ExecuteOut, ExecuteRequest, SubmissionOut, SubmissionRequest, TutorOut, TutorRequest
from ..services.code_runner import execute_code, run_submission
from ..services.mastery import review_result
from ..services.tutor import ask_tutor

router = APIRouter(prefix="/training", tags=["training"])
progress_router = APIRouter(tags=["progress"])
execution_router = APIRouter(tags=["training"])

def update_streak(user: User, activity_at: datetime) -> None:
    activity_day = activity_at.astimezone(timezone.utc).date()
    if user.last_activity_at is None:
        user.streak = 1
    else:
        last_day = user.last_activity_at.astimezone(timezone.utc).date()
        gap = (activity_day - last_day).days
        if gap > 1:
            user.streak = 1
        elif gap == 1:
            user.streak += 1
    user.last_activity_at = activity_at

@router.post("/submit", response_model=SubmissionOut)
@progress_router.post("/progress", response_model=SubmissionOut)
def submit(payload: SubmissionRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    challenge = db.get(Challenge, payload.challenge_id)
    if not challenge:
        raise HTTPException(404, "Reto no encontrado")
    execution = run_submission(payload.code, payload.language, challenge.test_cases, challenge.evaluator_type, challenge.setup_sql)
    result = review_result(execution.passed, execution.passed_tests / execution.total_tests, len(payload.code))
    db.add(Submission(user_id=user.id, challenge_id=challenge.id, score=result.score, quality=result.quality, passed=execution.passed, feedback=execution.feedback))
    if execution.passed:
        user.level = max(user.level, challenge.level.number + 1)
        update_streak(user, datetime.now(timezone.utc))
    db.commit()
    return SubmissionOut(passed=execution.passed, score=result.score, quality=result.quality, feedback=f"{result.label}. {execution.feedback}", next_review_at=result.next_review_at)

@router.post("/execute", response_model=ExecuteOut)
@execution_router.post("/execute", response_model=ExecuteOut, include_in_schema=False)
def execute(payload: ExecuteRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    challenge = db.get(Challenge, payload.challenge_id)
    if not challenge:
        raise HTTPException(404, "Reto no encontrado")
    return execute_code(payload.code, payload.language, challenge.test_cases, challenge.evaluator_type, challenge.setup_sql)

@router.post("/tutor", response_model=TutorOut)
def tutor(payload: TutorRequest, user: User = Depends(current_user)):
    answer, mode = ask_tutor(payload.question, payload.context)
    return TutorOut(answer=answer, mode=mode)

@router.post("/review", response_model=TutorOut)
def review(payload: TutorRequest, user: User = Depends(current_user)):
    answer, mode = ask_tutor(payload.question, f"Revisión de código. {payload.context}")
    return TutorOut(answer=answer, mode=mode)

@router.post("/interview", response_model=TutorOut)
def interview(payload: TutorRequest, user: User = Depends(current_user)):
    answer, mode = ask_tutor(payload.question, f"Entrevista técnica. {payload.context}")
    return TutorOut(answer=answer, mode=mode)

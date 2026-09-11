from fastapi import APIRouter, Depends, HTTPException
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

@router.post("/submit", response_model=SubmissionOut)
@progress_router.post("/progress", response_model=SubmissionOut)
def submit(payload: SubmissionRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    challenge = db.get(Challenge, payload.challenge_id)
    if not challenge: raise HTTPException(404, "Reto no encontrado")
    execution = run_submission(payload.code, payload.language, challenge.test_cases)
    result = review_result(execution.passed, execution.passed_tests / execution.total_tests, len(payload.code))
    db.add(Submission(user_id=user.id, challenge_id=challenge.id, score=result.score, quality=result.quality, passed=execution.passed, feedback=execution.feedback))
    if execution.passed:
        user.level = max(user.level, challenge.level.number + 1)
    db.commit()
    return SubmissionOut(passed=execution.passed, score=result.score, quality=result.quality, feedback=f"{result.label}. {execution.feedback}", next_review_at=result.next_review_at)

@router.post("/execute", response_model=ExecuteOut)
def execute(payload: ExecuteRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    challenge = db.get(Challenge, payload.challenge_id)
    if not challenge:
        raise HTTPException(404, "Reto no encontrado")
    return execute_code(payload.code, payload.language, challenge.test_cases)

@router.post("/tutor", response_model=TutorOut)
def tutor(payload: TutorRequest, user: User = Depends(current_user)):
    answer, mode = ask_tutor(payload.question, payload.context)
    return TutorOut(answer=answer, mode=mode)

@router.post("/review", response_model=TutorOut)
def review(payload: TutorRequest, user: User = Depends(current_user)):
    return TutorOut(answer="Empieza por separar legibilidad, corrección y coste. ¿Qué evidencia tienes para cada una? Busca nombres ambiguos, ramas sin cubrir y complejidad innecesaria.", mode="code-review")

@router.post("/interview", response_model=TutorOut)
def interview(payload: TutorRequest, user: User = Depends(current_user)):
    return TutorOut(answer="Tienes 25 minutos. Explica primero el enfoque y su complejidad; después implementa y valida con un caso límite. ¿Qué pregunta harías antes de codificar?", mode="interview")

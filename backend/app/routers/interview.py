import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..deps import current_user
from ..models import InterviewAnswer, InterviewQuestion, InterviewSession, User
from ..schemas import InterviewAnswerOut, InterviewAnswerRequest, InterviewQuestionOut, InterviewSessionOut, InterviewSummaryOut
from ..services.code_runner import run_submission

router = APIRouter(prefix="/interview", tags=["interview"])

@router.get("/session", response_model=InterviewSessionOut)
def create_session(db: Session = Depends(get_db), user: User = Depends(current_user)):
    questions = db.scalars(select(InterviewQuestion).order_by(InterviewQuestion.id).limit(5)).all()
    if not questions:
        raise HTTPException(503, "No hay preguntas de entrevista disponibles")
    session = InterviewSession(user_id=user.id)
    db.add(session)
    db.flush()
    db.commit()
    return InterviewSessionOut(id=session.id, questions=[InterviewQuestionOut.model_validate(question) for question in questions])

@router.post("/session/{session_id}/answer", response_model=InterviewAnswerOut)
def answer(session_id: int, payload: InterviewAnswerRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    session = db.scalar(select(InterviewSession).where(InterviewSession.id == session_id, InterviewSession.user_id == user.id))
    question = db.get(InterviewQuestion, payload.question_id)
    if not session or not question:
        raise HTTPException(404, "Sesión o pregunta no encontrada")
    if db.scalar(select(InterviewAnswer).where(InterviewAnswer.session_id == session.id, InterviewAnswer.question_id == question.id)):
        raise HTTPException(409, "La pregunta ya fue respondida")
    if question.kind == "coding":
        execution = run_submission(payload.answer, "python", question.test_cases)
        score = 100.0 if execution.passed else (execution.passed_tests / execution.total_tests * 100 if execution.total_tests else 0)
        feedback = execution.feedback
    else:
        points = json.loads(question.expected_points or "[]")
        answer_text = payload.answer.lower()
        found = sum(point.lower() in answer_text for point in points)
        score = found / len(points) * 100 if points else 0
        feedback = f"Mencionaste {found} de {len(points)} puntos esperados."
    db.add(InterviewAnswer(session_id=session.id, question_id=question.id, answer=payload.answer, score=score, feedback=feedback))
    db.commit()
    return InterviewAnswerOut(question_id=question.id, score=score, feedback=feedback)

@router.get("/session/{session_id}/summary", response_model=InterviewSummaryOut)
def summary(session_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    session = db.scalar(select(InterviewSession).options(selectinload(InterviewSession.answers)).where(InterviewSession.id == session_id, InterviewSession.user_id == user.id))
    if not session:
        raise HTTPException(404, "Sesión no encontrada")
    total = 5
    answers = [InterviewAnswerOut(question_id=item.question_id, score=item.score, feedback=item.feedback) for item in session.answers]
    return InterviewSummaryOut(session_id=session.id, total_questions=total, answered_questions=len(answers), score=round(sum(item.score for item in answers) / len(answers), 1) if answers else 0, answers=answers)
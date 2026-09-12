from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from ..database import get_db
from ..deps import current_user
from ..models import Challenge, LearningPath, Level, Submission, User
from ..schemas import LevelOut, NewsOut, ProgressOut, UserOut
from ..services.news_feeder import fetch_news

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
progress_router = APIRouter(tags=["progress"])

def level_status(level_number: int, user_level: int) -> str:
    if level_number < user_level:
        return "completed"
    if level_number == user_level:
        return "active"
    return "locked"

@router.get("/me", response_model=UserOut)
def dashboard_user(user: User = Depends(current_user)):
    return user

@router.get("/path", response_model=list[LevelOut])
def learning_path(db: Session = Depends(get_db), user: User = Depends(current_user)):
    path = db.scalar(select(LearningPath).options(selectinload(LearningPath.levels).selectinload(Level.challenges)))
    if not path:
        return []
    completed_query = select(Submission.challenge_id).where(Submission.user_id == user.id, Submission.passed.is_(True))
    completed_ids = set(db.scalars(completed_query).all()) if hasattr(db, "scalars") else set()
    for level in path.levels:
        level.status = level_status(level.number, user.level)
        for challenge in getattr(level, "challenges", []):
            challenge.completed = challenge.id in completed_ids
    return path.levels

@router.get("/news", response_model=list[NewsOut])
def news(user: User = Depends(current_user)):
    return fetch_news()

@progress_router.get("/users/me/progress", response_model=ProgressOut)
def progress(db: Session = Depends(get_db), user: User = Depends(current_user)):
    completed = db.scalar(select(func.count(func.distinct(Submission.challenge_id))).where(Submission.user_id == user.id, Submission.passed.is_(True))) or 0
    total = db.scalar(select(func.count(Submission.id)).where(Submission.user_id == user.id)) or 0
    rows = db.execute(select(Submission, Challenge, Level).join(Challenge, Submission.challenge_id == Challenge.id).join(Level, Challenge.level_id == Level.id).where(Submission.user_id == user.id).order_by(Submission.created_at.desc()).limit(10)).all()
    skill_scores: dict[str, list[float]] = {}
    recent = []
    for submission, challenge, level in rows:
        skill_scores.setdefault(level.skill, []).append(submission.score)
        recent.append({"title": challenge.title, "created_at": submission.created_at, "passed": submission.passed, "score": submission.score})
    breakdown = {skill: round(sum(scores) / len(scores), 1) for skill, scores in skill_scores.items()}
    return ProgressOut(level=user.level + 1, streak=user.streak, completed_challenges=completed, total_submissions=total, skill_breakdown=breakdown, recent_submissions=recent)

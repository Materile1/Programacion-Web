from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from ..database import get_db
from ..deps import current_user
from ..models import LearningPath, Level, Submission, User
from ..schemas import LevelOut, NewsOut, ProgressOut, UserOut
from ..services.news_feeder import fetch_news

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
progress_router = APIRouter(tags=["progress"])

@router.get("/me", response_model=UserOut)
def dashboard_user(user: User = Depends(current_user)):
    return user

@router.get("/path", response_model=list[LevelOut])
def learning_path(db: Session = Depends(get_db), user: User = Depends(current_user)):
    path = db.scalar(select(LearningPath).options(selectinload(LearningPath.levels).selectinload(Level.challenges)))
    return path.levels if path else []

@router.get("/news", response_model=list[NewsOut])
def news(user: User = Depends(current_user)):
    return fetch_news()

@progress_router.get("/users/me/progress", response_model=ProgressOut)
def progress(db: Session = Depends(get_db), user: User = Depends(current_user)):
    completed = db.scalar(select(func.count(Submission.id)).where(Submission.user_id == user.id, Submission.passed.is_(True))) or 0
    total = db.scalar(select(func.count(Submission.id)).where(Submission.user_id == user.id)) or 0
    return ProgressOut(level=user.level, streak=user.streak, completed_challenges=completed, total_submissions=total)

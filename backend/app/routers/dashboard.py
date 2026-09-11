from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from ..database import get_db
from ..deps import current_user
from ..models import LearningPath, Level, User
from ..schemas import LevelOut, NewsOut, UserOut
from ..services.news_feeder import fetch_news

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

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

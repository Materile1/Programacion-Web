from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import User
from ..schemas import ContentRefreshOut
from ..services.content_curator import refresh_content

router = APIRouter(prefix="/admin", tags=["admin"])

def admin_user(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(403, "Se requiere rol administrador")
    return user

@router.post("/content/refresh", response_model=ContentRefreshOut)
def refresh(db: Session = Depends(get_db), user: User = Depends(admin_user)):
    created, discarded, topics, detail = refresh_content(db)
    return ContentRefreshOut(created=created, discarded=discarded, topics=topics, detail=detail)
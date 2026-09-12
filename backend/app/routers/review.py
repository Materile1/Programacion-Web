import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import ReviewSnippet, User
from ..schemas import ReviewSnippetOut, ReviewSubmitOut, ReviewSubmitRequest

router = APIRouter(prefix="/review", tags=["review"])

@router.get("/snippets", response_model=list[ReviewSnippetOut])
def list_snippets(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.scalars(select(ReviewSnippet).order_by(ReviewSnippet.id)).all()

@router.get("/snippets/{snippet_id}", response_model=ReviewSnippetOut)
def get_snippet(snippet_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    snippet = db.get(ReviewSnippet, snippet_id)
    if not snippet:
        raise HTTPException(404, "Snippet no encontrado")
    return snippet

@router.post("/snippets/{snippet_id}/submit", response_model=ReviewSubmitOut)
def submit_review(snippet_id: int, payload: ReviewSubmitRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    snippet = db.get(ReviewSnippet, snippet_id)
    if not snippet:
        raise HTTPException(404, "Snippet no encontrado")
    issues = json.loads(snippet.known_issues or "[]")
    text = payload.review.lower()
    detected = [issue for issue in issues if issue.lower() in text]
    missed = [issue for issue in issues if issue not in detected]
    score = round((len(detected) / len(issues)) * 100, 1) if issues else 100.0
    feedback = f"Detectaste {len(detected)} de {len(issues)} problemas conocidos."
    return ReviewSubmitOut(detected=detected, missed=missed, score=score, feedback=feedback)
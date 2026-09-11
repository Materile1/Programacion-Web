from fastapi import APIRouter, Depends, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import current_user
from ..models import User
from ..config import get_settings
from ..schemas import GoogleTokenRequest, Token, UserCreate, UserLogin, UserOut
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(409, "El email ya está registrado")
    user = User(email=payload.email, name=payload.name.strip(), password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return Token(access_token=create_access_token(str(user.id)))

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Credenciales inválidas")
    return Token(access_token=create_access_token(str(user.id)))

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user

@router.get("/google/login")
def google_login():
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(503, "Google OAuth no está configurado")
    return {"client_id": settings.google_client_id}

@router.post("/google/callback", response_model=Token)
def google_callback(payload: GoogleTokenRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(503, "Google OAuth no está configurado")
    try:
        profile = id_token.verify_oauth2_token(payload.id_token, google_requests.Request(), settings.google_client_id)
    except ValueError as exc:
        raise HTTPException(401, "Token de Google inválido") from exc
    email = profile.get("email")
    if not email or not profile.get("email_verified", False):
        raise HTTPException(401, "La cuenta de Google no tiene un email verificado")
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        user = User(email=email, name=profile.get("name") or email.split("@")[0], avatar=profile.get("picture"), password_hash="oauth-google")
        db.add(user)
    else:
        user.name = profile.get("name") or user.name
        user.avatar = profile.get("picture") or user.avatar
    db.commit()
    db.refresh(user)
    return Token(access_token=create_access_token(str(user.id)))

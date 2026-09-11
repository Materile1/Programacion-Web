from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    level: Mapped[int] = mapped_column(Integer, default=7)
    streak: Mapped[int] = mapped_column(Integer, default=12)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    submissions: Mapped[list["Submission"]] = relationship(back_populates="user")

class LearningPath(Base):
    __tablename__ = "learning_paths"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    total_levels: Mapped[int] = mapped_column(Integer, default=15)
    levels: Mapped[list["Level"]] = relationship(back_populates="path", order_by="Level.number")

class Level(Base):
    __tablename__ = "levels"
    id: Mapped[int] = mapped_column(primary_key=True)
    path_id: Mapped[int] = mapped_column(ForeignKey("learning_paths.id"))
    number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(160))
    skill: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30), default="locked")
    path: Mapped[LearningPath] = relationship(back_populates="levels")
    challenges: Mapped[list["Challenge"]] = relationship(back_populates="level")

class Challenge(Base):
    __tablename__ = "challenges"
    id: Mapped[int] = mapped_column(primary_key=True)
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"))
    title: Mapped[str] = mapped_column(String(180))
    prompt: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(30), default="python")
    difficulty: Mapped[str] = mapped_column(String(30), default="Intermedio")
    starter_code: Mapped[str] = mapped_column(Text)
    test_cases: Mapped[str] = mapped_column(Text, default="[]")
    level: Mapped[Level] = relationship(back_populates="challenges")

class Submission(Base):
    __tablename__ = "submissions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id"))
    score: Mapped[float] = mapped_column(Float)
    quality: Mapped[float] = mapped_column(Float)
    passed: Mapped[bool] = mapped_column(Boolean)
    feedback: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    user: Mapped[User] = relationship(back_populates="submissions")

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: str
    level: int
    streak: int

class ChallengeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    prompt: str
    language: str
    difficulty: str
    starter_code: str

class LevelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    number: int
    title: str
    skill: str
    status: str
    challenges: list[ChallengeOut] = []

class SubmissionRequest(BaseModel):
    challenge_id: int
    code: str = Field(min_length=1, max_length=20000)
    language: str = Field(default="python", pattern="^(python|javascript)$")

class SubmissionOut(BaseModel):
    passed: bool
    score: float
    quality: float
    feedback: str
    next_review_at: datetime

class TutorRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    context: str = Field(default="", max_length=8000)

class TutorOut(BaseModel):
    answer: str
    mode: str

class NewsOut(BaseModel):
    title: str
    summary: str
    url: str
    source: str
    kind: str

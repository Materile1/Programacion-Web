import json
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

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
    avatar: str | None = None
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
    test_cases: list[dict] = []

    @field_validator("test_cases", mode="before")
    @classmethod
    def parse_test_cases(cls, value):
        return json.loads(value) if isinstance(value, str) else value

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

class ProgressOut(BaseModel):
    level: int
    streak: int
    completed_challenges: int
    total_submissions: int

class GoogleTokenRequest(BaseModel):
    id_token: str

class ExecuteRequest(BaseModel):
    challenge_id: int
    code: str = Field(min_length=1, max_length=20000)
    language: str = Field(default="python", pattern="^(python|javascript)$")

class ExecuteOut(BaseModel):
    stdout: str
    stderr: str
    passed: bool
    feedback: str

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

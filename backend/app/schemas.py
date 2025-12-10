from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any, Union
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    role: str  # "educator" or "student"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Content Generation Schemas ---
class GenerateRequest(BaseModel):
    topic: str
    type: str       # "MCQ" or "WRITTEN"
    difficulty: str # "EASY", "MEDIUM", "HARD"

# --- Assignment Schemas ---
class Question(BaseModel):
    id: str
    text: str
    options: Optional[List[str]] = None
    correctAnswer: Optional[str] = None
    rubric: Optional[str] = None

class AssignmentBase(BaseModel):
    id: str
    title: str
    subject: str
    topic: str
    type: str
    difficulty: str
    due_date: Optional[str] = None
    status: str = "Draft"
    questions: List[Question]

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentResponse(AssignmentBase):
    created_at: datetime

    class Config:
        from_attributes = True

# --- Submission & Grading Schemas ---
class GradingRequest(BaseModel):
    question: str
    answer: str
    rubric: Optional[str] = None

class GradingResponse(BaseModel):
    score: float
    feedback: str

class SubmissionCreate(BaseModel):
    assignment_id: str
    student_id: int
    answer_text: str
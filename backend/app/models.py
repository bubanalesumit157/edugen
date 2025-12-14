# app/models.py
from sqlalchemy import Column, Integer,Boolean, String, Enum, ForeignKey, DateTime, JSON, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # "educator" or "student"

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(String, primary_key=True) # Using String ID to match frontend UUID
    title = Column(String)
    subject = Column(String)
    topic = Column(String)
    type = Column(String) # MCQ, WRITTEN
    difficulty = Column(String) # EASY, MEDIUM, HARD
    status = Column(String, default="Draft")
    due_date = Column(String)
    questions = Column(JSON) # Storing questions as JSON for flexibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    submissions = relationship("Submission", back_populates="assignment")
    
class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(String, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    answer_text = Column(Text)
    score = Column(Float)
    feedback = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    assignment = relationship("Assignment", back_populates="submissions")
    
    # NEW: Relationship to the detailed interaction records
    interactions = relationship("QuestionInteraction", back_populates="submission")


class QuestionInteraction(Base):
    __tablename__ = "question_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    student_id = Column(Integer, ForeignKey("users.id")) # Denormalized for read speed
    
    # Interaction Details
    question_id = Column(String) 
    is_correct = Column(Boolean)          # CORRECTED: Use SQLAlchemy Boolean type
    time_spent = Column(Integer)          # Required for ML Engagement metrics
    difficulty = Column(String)           # Required for ML Personalization
    topic = Column(String)                # Required for ML Topic metrics
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # NEW: Relationship back to the Submission this interaction belongs to
    submission = relationship("Submission", back_populates="interactions")
    # NEW: Relationship back to the Student who performed the interaction
    student = relationship("User", backref="interactions")
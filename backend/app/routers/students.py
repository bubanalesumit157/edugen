from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
import pandas as pd
import json

# ML Services
from app.ml_core.personalization.adaptive_personalizer import AdaptivePersonalizer
from ..services.ml_engine import grade_submission as ml_grade_submission

router = APIRouter()
personalizer = AdaptivePersonalizer()

# --- RECOMMENDATION ENDPOINT (Unchanged) ---
@router.get("/{student_id}/recommendations")
def get_student_recommendations(student_id: int, db: Session = Depends(get_db)):
    submissions = db.query(models.Submission)\
        .filter(models.Submission.student_id == student_id)\
        .order_by(models.Submission.submitted_at.asc())\
        .all()
    
    if not submissions:
        sequences_df = pd.DataFrame(columns=[
            'student_id', 'is_correct', 'difficulty', 'topic', 'subject', 
            'score', 'timestamp', 'time_spent_seconds'
        ])
        perf_df = pd.DataFrame(columns=['student_id', 'topic', 'accuracy', 'total_attempts'])
    else:
        data = [{
            'student_id': str(s.student_id),
            'subject': s.assignment.subject,
            'topic': s.assignment.topic,
            'difficulty': s.assignment.difficulty,
            'is_correct': s.score > 70,
            'score': s.score,
            'timestamp': s.submitted_at,
            'time_spent_seconds': 60
        } for s in submissions]
        
        sequences_df = pd.DataFrame(data)
        perf_df = sequences_df.groupby(['student_id', 'subject', 'topic']).agg(
            accuracy=('is_correct', 'mean'),
            total_attempts=('is_correct', 'count')
        ).reset_index()

    try:
        recommendation = personalizer.personalize_assignment(
            student_id=str(student_id),
            learning_sequences=sequences_df,
            performance_history=perf_df,
            num_questions=5
        )
        return recommendation
    except Exception as e:
        print(f"Personalization Error: {e}")
        return {
            "difficulty_recommendation": {"primary_difficulty": "Medium"},
            "topic_recommendations": [],
            "message": "Generated via fallback logic."
        }

# --- FIXED GRADING ENDPOINT ---
@router.post("/grade", response_model=schemas.GradingResponse)
async def grade_submission(submission: schemas.SubmissionCreate, db: Session = Depends(get_db)):
    # 1. Fetch Assignment
    assignment = db.query(models.Assignment).filter(models.Assignment.id == submission.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # 2. Parse ALL Questions & Answers from DB
    try:
        questions_data = assignment.questions
        if isinstance(questions_data, str):
            questions_data = json.loads(questions_data)
        
        # ✅ FIX: Construct a "Master Key" containing ALL questions and their correct answers
        reference_context = "Here is the OFFICIAL ANSWER KEY for the assignment:\n\n"
        
        for idx, q in enumerate(questions_data):
            q_text = q.get('text', 'Unknown Question')
            q_ans = q.get('correctAnswer') or q.get('answer_key') or "Check manually"
            q_rubric = q.get('rubric') or q.get('explanation') or "No rubric"
            
            reference_context += f"Q{idx+1}: {q_text}\nCORRECT ANSWER: {q_ans}\nEXPLANATION/RUBRIC: {q_rubric}\n\n"
            
    except Exception as e:
        print(f"Error parsing questions: {e}")
        reference_context = "Error loading answer key. Grade based on general knowledge."

    # 3. Grade using AI (Compare Student Input vs. Master Key)
    # We use the AI for BOTH MCQ and Written because it handles the "Q1: A..." string format best.
    print(f"🤖 Sending to AI Grader. \nStudent: {submission.answer_text[:50]}...\nContext Length: {len(reference_context)}")
    
    ai_result = await ml_grade_submission(
        question_text=reference_context, # Passing the full key as context
        student_answer=submission.answer_text,
        rubric="Compare the student's answers strictly against the provided ANSWER KEY. For MCQs, ensure the option matches."
    )

    score_value = ai_result.get('score', 0.0)
    feedback_text = ai_result.get('feedback', 'No feedback provided.')

    # 4. Save Submission
    new_submission = models.Submission(
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        answer_text=submission.answer_text,
        score=score_value,
        feedback=feedback_text
    )
    db.add(new_submission)
    db.commit()
    
    return {
        "score": score_value,
        "feedback": feedback_text
    }
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
import pandas as pd
from app.ml_core.personalization.adaptive_personalizer import AdaptivePersonalizer
from ..ml_core.grading.feedback_generator import FeedbackGenerator
from ..ml_core.grading.partial_credit import PartialCreditEngine
from .. import schemas
router = APIRouter()

feedback_gen = FeedbackGenerator()
credit_engine = PartialCreditEngine()
personalizer = AdaptivePersonalizer()
@router.get("/{student_id}/recommendations")
def get_student_recommendations(student_id: int, db: Session = Depends(get_db)):
    # 1. Fetch History (Sorted by Time!)
    submissions = db.query(models.Submission)\
        .filter(models.Submission.student_id == student_id)\
        .order_by(models.Submission.submitted_at.asc())\
        .all()
    
    # 2. Convert to DataFrame
    if not submissions:
        # Cold start structure with ALL required columns to be safe
        sequences_df = pd.DataFrame(columns=[
            'student_id', 'is_correct', 'difficulty', 'topic', 'subject', 
            'score', 'timestamp', 'time_spent_seconds'
        ])
        perf_df = pd.DataFrame(columns=['student_id', 'topic', 'accuracy', 'total_attempts'])
    else:
        data = [{
            'student_id': str(s.student_id),
            'subject': s.assignment.subject,  # Added Subject
            'topic': s.assignment.topic,
            'difficulty': s.assignment.difficulty,
            'is_correct': s.score > 70,       # Heuristic
            'score': s.score,
            'timestamp': s.submitted_at,      # Added Timestamp
            'time_spent_seconds': 60          # Added Dummy Time
        } for s in submissions]
        
        sequences_df = pd.DataFrame(data)
        
        # Calculate performance metrics
        # We also count total_attempts, which is useful for the personalizer
        perf_df = sequences_df.groupby(['student_id', 'subject', 'topic']).agg(
            accuracy=('is_correct', 'mean'),
            total_attempts=('is_correct', 'count')
        ).reset_index()

    # 3. Run Personalizer
    # We wrap this in a try-catch because ML models can be fragile with data shapes
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
        # Fallback response if ML fails
        return {
            "difficulty_recommendation": {"primary_difficulty": "Medium"},
            "topic_recommendations": [],
            "message": "Generated via fallback logic."
        }
        



@router.post("/grade")
def grade_submission(submission: schemas.SubmissionCreate, db: Session = Depends(get_db)):
    # 1. Fetch the Assignment to get the correct answer
    assignment = db.query(models.Assignment).filter(models.Assignment.id == submission.assignment_id).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Logic to find the specific question's answer from the assignment's JSON data
    # (Assuming submission relates to a single question for now, or you need a question_id in the schema)
    # For this example, let's assume we are grading the first question or the schema has a question_index
    
    target_question = assignment.questions[0] # Simplification! Needs robust logic.
    correct_answer = target_question.get('correctAnswer') or "Standard Answer"

    # 2. Calculate Score
    grading_result = credit_engine.calculate_partial_credit(
        student_answer=submission.answer_text,
        correct_answer=correct_answer,
        max_points=100
    )
    
    # 3. Generate Feedback
    perf_data = {
        'percentage': grading_result['percentage'],
        'mistakes': [grading_result['mistake_type']] if grading_result['mistake_type'] else [],
        'strengths': ['correct_method'] if grading_result['percentage'] > 80 else []
    }
    
    detailed_feedback = feedback_gen.generate_feedback(perf_data)
    
    # 4. Save Submission to DB
    new_submission = models.Submission(
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        answer_text=submission.answer_text,
        score=grading_result['points_earned'],
        feedback=detailed_feedback['feedback_text']
    )
    db.add(new_submission)
    db.commit()
    
    return {
        "score": grading_result['points_earned'],
        "feedback": detailed_feedback['feedback_text']
    }
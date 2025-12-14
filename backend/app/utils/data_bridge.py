import pandas as pd
from sqlalchemy.orm import Session
from .. import models

def fetch_student_history_as_dataframe(student_id: int, db: Session):
    # 1. Join Submission and Assignment tables
    results = db.query(
        models.Submission, models.Assignment
    ).join(
        models.Assignment, models.Submission.assignment_id == models.Assignment.id
    ).filter(
        models.Submission.student_id == student_id
    ).order_by(models.Submission.submitted_at.asc()).all()

    data = []
    for sub, asm in results:
        data.append({
            'student_id': str(sub.student_id),
            'topic': asm.topic,
            'subject': asm.subject,
            'difficulty': asm.difficulty,
            # ML needs explicit Correct/Incorrect boolean. 
            # We infer it from score (assuming >70% is "correct") if not stored explicitly
            'is_correct': sub.score >= 70, 
            'score': sub.score,
            'timestamp': sub.submitted_at,
            # DUMMY DATA: Your DB doesn't track time yet, but ML needs it.
            'time_spent_seconds': 60, 
            'bloom_level': 'Apply' # Default
        })

    return pd.DataFrame(data)
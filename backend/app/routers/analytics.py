from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models, schemas
import pandas as pd

# Import the Personalizer
from app.ml_core.personalization.adaptive_personalizer import AdaptivePersonalizer

router = APIRouter()
personalizer = AdaptivePersonalizer()

# --- HELPER FUNCTION (Was missing) ---
def get_student_history_dataframe(db: Session, student_id: int):
    """
    Fetches a student's submission history and converts it to a Pandas DataFrame
    formatted for the ML Personalizer.
    """
    submissions = db.query(models.Submission)\
        .filter(models.Submission.student_id == student_id)\
        .order_by(models.Submission.submitted_at.asc())\
        .all()
    
    if not submissions:
        return pd.DataFrame(columns=[
            'student_id', 'is_correct', 'difficulty', 'topic', 'subject', 
            'score', 'timestamp', 'time_spent_seconds'
        ])
    
    data = [{
        'student_id': str(s.student_id),
        'subject': s.assignment.subject if s.assignment.subject else "General",
        'topic': s.assignment.topic,
        'difficulty': s.assignment.difficulty,
        'is_correct': s.score >= 70, # Threshold for "Correct"
        'score': s.score,
        'timestamp': s.submitted_at,
        'time_spent_seconds': 60 # Placeholder
    } for s in submissions]
    
    return pd.DataFrame(data)

# --- ENDPOINTS ---

@router.get("/dashboard")
def get_analytics_dashboard(db: Session = Depends(get_db)):
    """
    Returns aggregated stats for the Analytics Dashboard.
    """
    # 1. Overall Class Average
    avg_score = db.query(func.avg(models.Submission.score)).scalar() or 0
    
    # 2. Total Submissions
    total_submissions = db.query(func.count(models.Submission.id)).scalar()
    
    # 3. Performance by Topic (Bar Chart Data)
    topic_stats = db.query(
        models.Assignment.topic,
        func.avg(models.Submission.score).label('avg_score'),
        func.count(models.Submission.id).label('count')
    ).join(models.Submission).group_by(models.Assignment.topic).all()
    
    topic_data = [
        {"name": t[0], "score": round(t[1], 1), "attempts": t[2]} 
        for t in topic_stats
    ]

    # 4. Recent Activity (Line Chart - Last 7 days)
    timeline_stats = db.query(
        func.date(models.Submission.submitted_at).label('date'),
        func.avg(models.Submission.score).label('avg_score')
    ).group_by(func.date(models.Submission.submitted_at)).order_by('date').limit(7).all()

    timeline_data = [
        {"date": str(t[0]), "score": round(t[1], 1)} 
        for t in timeline_stats
    ]

    return {
        "overall_average": round(avg_score, 1),
        "total_submissions": total_submissions,
        "topic_performance": topic_data,
        "timeline_data": timeline_data
    }

@router.get("/class-insights")
def get_class_insights(db: Session = Depends(get_db)):
    """
    Analyzes every student and returns their learning needs for the Teacher Dashboard.
    """
    students = db.query(models.User).filter(models.User.role == "Student").all()
    insights = []
    
    for student in students:
        # 1. Fetch History using the Helper
        history = get_student_history_dataframe(db, student.id)
        
        # Default values
        recommended_topic = "General Assessment"
        rec_diff = "Medium"
        tier = "Unknown"
        needs = "Initial Assessment"
        
        if len(history) >= 0:
            # 2. Run AI Analysis
            state = personalizer._analyze_current_state(history, history)
            tier = state['performance_tier']
            
            # 3. Find Weakest Topic
            # Sort by accuracy ascending, get the top one
            try:
                topic_performance = history.groupby('topic')['is_correct'].mean().sort_values()
                if not topic_performance.empty:
                    recommended_topic = topic_performance.index[0]
            except Exception:
                recommended_topic = "General Review"

            # 4. Determine Needs & Difficulty
            if tier in ["Struggling", "Below Average"]:
                needs = f"Remedial Support in {recommended_topic}"
                rec_diff = "Easy"
            elif tier == "Excellent":
                needs = "Advanced Challenge"
                rec_diff = "Hard"
            else:
                needs = "Standard Practice"
                rec_diff = "Medium"

        insights.append({
            "id": student.id,
            "name": student.email.split("@")[0],
            "tier": tier,
            "needs": needs,
            "recommended_topic": recommended_topic,
            "recommended_difficulty": rec_diff,
            "accuracy": f"{history['is_correct'].mean():.0%}" if len(history) > 0 else "0%",
            "weak_topics": len(history[history['is_correct'] == False]['topic'].unique()) if len(history) > 0 else 0
        })
    
    return insights
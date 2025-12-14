import pandas as pd
from app.ml_core.grading.partial_credit import PartialCreditEngine
from app.ml_core.grading.feedback_generator import FeedbackGenerator
from app.ml_core.grading.rubric_manager import RubricManager
import re
# Initialize singletons
grader_engine = PartialCreditEngine(strategy='standard')
feedback_gen = FeedbackGenerator()
rubric_mgr = RubricManager()

async def grade_submission(question: str, student_answer: str, rubric_text: str = None):
    """
    Integrates PartialCreditEngine and FeedbackGenerator.
    """
    # 1. Calculate Score (Simplified logic for text comparison or use LLM grader from src/chains/grading.py)
    # If using the rule-based PartialCreditEngine, we need numeric or exact matches.
    # For text essays, we should use the LLM grader in ml_core/src/chains/grading.py
    
    from app.ml_core.src.chains.grading import grade_student_answer
    
    # Use the LangChain Grader for text/conceptual answers
    ai_grading_result = grade_student_answer(question, student_answer)
    
    # Attempt to parse score from AI text result (e.g., "Score: 8/10")
    # This is a basic fallback extraction
    match = re.search(r"Score:?\*?\*?\s*([\d\.]+)", ai_grading_result, re.IGNORECASE)
    
    score = 70.0 # Default fallback
    if match:
        try:
            raw_score = float(match.group(1))
            # Normalize: If score is 0-10, convert to 0-100
            if raw_score <= 10:
                score = raw_score * 10
            else:
                score = raw_score
        except ValueError:
            pass
        
    # 2. Generate Constructive Feedback
    # Convert AI result into format expected by FeedbackGenerator
    performance_data = {
        'percentage': score,
        'mistakes': [], # AI grader can populate this
        'strengths': ['completed_submission']
    }
    
    detailed_feedback = feedback_gen.generate_feedback(performance_data)
    
    return {
        "score": score,
        "feedback": f"{ai_grading_result}\n\n{detailed_feedback['feedback_text']}"
    }

async def analyze_assignment_pedagogy(assignment_dict: dict):
    """
    Uses SHAP analyzer or Bloom validator from ML Core
    """
    from app.ml_core.src.chains.bloom_validator import validate_question_difficulty
    
    analysis_report = []
    
    # Analyze the first few questions
    questions = assignment_dict.get('questions', [])
    target_difficulty = assignment_dict.get('difficulty', 'Medium')
    
    for q in questions[:3]: # Limit to 3 for performance
        q_text = q.get('text', '')
        # Map difficulty to Bloom's
        bloom_target = "Analyze" if target_difficulty == "Hard" else "Apply"
        
        result = validate_question_difficulty(q_text, bloom_target)
        analysis_report.append(f"Q: {q_text[:30]}... -> {result}")
        
    return "\n\n".join(analysis_report)
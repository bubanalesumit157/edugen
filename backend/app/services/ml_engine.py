# backend/app/services/ml_engine.py

from app.ml_core.src.chains.grading import get_grading_chain
from app.ml_core.src.chains.bloom_validator import get_bloom_chain

async def grade_submission(question_text: str, student_answer: str, rubric: str = ""):
    """
    Grades a student's submission using the AI grading chain.
    
    Args:
        question_text: The Master Answer Key / Context (passed from students.py)
        student_answer: The text submitted by the student
        rubric: Specific instructions for grading
    """
    try:
        # Get the AI Chain
        chain = get_grading_chain()
        
        # Invoke the chain with the matched arguments
        # We map 'question_text' (which contains the full context) to 'question'
        response = chain.invoke({
            "question": question_text, 
            "student_answer": student_answer,
            "rubric": rubric
        })
        
        # The chain should return a Dictionary with 'score' and 'feedback'
        # If it returns a string (older version), we might need to parse it, 
        # but the JSON update should handle this.
        return response

    except Exception as e:
        print(f"❌ Grading Engine Error: {e}")
        return {
            "score": 0, 
            "feedback": "Error during AI grading. Please try again."
        }

async def analyze_assignment_pedagogy(assignment_data: dict):
    """
    Analyzes the pedagogical quality of an assignment using Bloom's Taxonomy.
    """
    try:
        chain = get_bloom_chain()
        
        # Convert assignment dict to a readable string for the AI
        content_str = f"Title: {assignment_data.get('title')}\n"
        for q in assignment_data.get('questions', []):
            content_str += f"- {q.get('text')}\n"

        result = chain.invoke({"assignment_content": content_str})
        return result
    except Exception as e:
        print(f"Analysis Error: {e}")
        return "Could not analyze assignment at this time."
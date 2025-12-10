import google.generativeai as genai
import os
import json
from .schemas import Question

# Configure API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-2.0-flash')

def generate_questions_with_ai(topic: str, type: str, difficulty: str) -> list[dict]:
    """
    Generates questions in strict JSON format for the frontend.
    """
    prompt = f"""
    You are an expert educator. Create a {difficulty} level {type} assignment on the topic: "{topic}".
    
    Output strictly valid JSON. 
    Format for MCQ:
    [
        {{"id": 1, "text": "Question?", "options": ["A", "B", "C", "D"], "correctAnswer": "A"}}
    ]
    
    Format for WRITTEN:
    [
        {{"id": 1, "text": "Essay Question?", "rubric": "Key points to include..."}}
    ]
    
    Generate 3 questions. Do not include markdown formatting like ```json.
    """
    
    response = model.generate_content(prompt)
    try:
        # Clean response string to ensure JSON parsing
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_text)
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return []

def grade_submission_with_ai(context: str, answer: str, rubric: str):
    prompt = f"""
    Grade this student submission.
    Question/Context: {context}
    Rubric: {rubric}
    Student Answer: {answer}
    
    Output strictly valid JSON:
    {{
        "score": (integer 0-100),
        "feedback": "Short constructive feedback"
    }}
    """
    response = model.generate_content(prompt)
    try:
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_text)
    except:
        return {"score": 0, "feedback": "Error grading submission."}

def audit_assignment_with_ai(questions: list):
    prompt = f"""
    Analyze these questions for pedagogical quality, bias, and clarity:
    {json.dumps(questions)}
    
    Provide a 2-sentence summary of the quality and one suggestion for improvement.
    """
    response = model.generate_content(prompt)
    return response.text
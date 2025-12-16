import uuid
from app.ml_core.src.chains.question_generator import get_exam_chain

async def generate_questions(topic: str, difficulty: str, type: str, count: int = 5):
    """
    Real integration with LangChain RAG pipeline.
    Expects the chain to return a structured Python dictionary (via JsonOutputParser).
    """
    questions = []
    
    # Initialize the chain with the specific type (MCQ vs Subjective)
    # Note: 'type' from frontend is usually "MCQ" or "WRITTEN"
    # We map "WRITTEN" to "subjective" for the generator
    gen_type = "mcq" if type.upper() == "MCQ" else "subjective"
    
    chain = get_exam_chain(question_type=gen_type)
    
    if not chain:
        return [{"id": "error", "text": "RAG Database not initialized. Please run ingestion.", "options": []}]

    print(f"🧠 Generating {count} {difficulty} {gen_type} questions for {topic}...")

    for i in range(count):
        try:
            # Invoke the RAG chain
            # The result is now a Python Dictionary (e.g., {'question': '...', 'correct_answer': '...'})
            ai_data = chain.invoke({"topic": topic, "difficulty": difficulty})
            
            # Construct the object expected by the Frontend and Database
            q_id = str(uuid.uuid4())
            
            new_question = {
                "id": q_id,
                
                # VISIBLE TO STUDENT
                "text": ai_data.get("question", "Error generating question text."),
                "options": ai_data.get("options", []), # Will be empty for subjective
                
                # HIDDEN (Stored in DB for grading)
                # 'correctAnswer' maps to either 'correct_answer' (MCQ) or 'answer_key' (Subjective)
                "correctAnswer": ai_data.get("correct_answer") or ai_data.get("answer_key") or "Refer to explanation",
                
                # 'rubric' maps to 'rubric' (Subjective) or 'explanation' (MCQ)
                "rubric": ai_data.get("rubric") or ai_data.get("explanation") or "No rubric provided."
            }
            
            questions.append(new_question)
            
        except Exception as e:
            print(f"❌ Generation Error on Question {i+1}: {e}")
            # Optional: Add a placeholder error question so the UI doesn't break
            questions.append({
                "id": str(uuid.uuid4()),
                "text": "Error generating this question. Please try again.",
                "options": []
            })

    return questions
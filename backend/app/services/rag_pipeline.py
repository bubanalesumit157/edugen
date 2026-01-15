import uuid
from app.ml_core.src.chains.question_generator import get_exam_chain

async def generate_questions(topic: str, difficulty: str, type: str, count: int = 5):
    """
    Real integration with LangChain RAG pipeline.
    """
    questions = []
    
    clean_type = type.strip().upper()
    print(f"🔍 DEBUG: Request received - Topic: {topic}, Type: '{clean_type}'")

    if clean_type in ["MCQ", "MULTIPLE CHOICE", "OBJECTIVE", "QUIZ"]:
        gen_type = "mcq"
    else:
        gen_type = "subjective"
        
    chain = get_exam_chain(question_type=gen_type)
    
    if not chain:
        return [{"id": "error", "text": "Database error.", "options": []}]

    print(f"🧠 Generating {count} {difficulty} {gen_type} questions for {topic}...")

    for i in range(count):
        try:
            # --- FIX: ADD VARIATION TO TOPIC ---
            # By adding "(Question X)", we force the LLM to generate a new variation
            # The RAG retriever will still find relevant docs for the main keyword
            variation_topic = f"{topic} (Question {i+1})"
            
            ai_data = chain.invoke({"topic": variation_topic, "difficulty": difficulty})
            
            q_id = str(uuid.uuid4())
            
            new_question = {
                "id": q_id,
                "text": ai_data.get("question", "Error generating question text."),
                "options": ai_data.get("options", []), 
                # Ensure we capture the answer key correctly
                "correctAnswer": ai_data.get("correct_answer") or ai_data.get("answer_key") or "Refer to explanation",
                "rubric": ai_data.get("rubric") or ai_data.get("explanation") or "No rubric provided."
            }
            
            questions.append(new_question)
            
        except Exception as e:
            print(f"❌ Generation Error on Question {i+1}: {e}")
            # Add a placeholder so the loop continues
            questions.append({
                "id": str(uuid.uuid4()),
                "text": "Failed to generate unique question.",
                "options": []
            })

    return questions
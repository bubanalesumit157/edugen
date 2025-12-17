import uuid
from app.ml_core.src.chains.question_generator import get_exam_chain

async def generate_questions(topic: str, difficulty: str, type: str, count: int = 5):
    """
    Real integration with LangChain RAG pipeline.
    Expects the chain to return a structured Python dictionary.
    """
    questions = []
    
    # --- FIX: Robust Type Detection ---
    # 1. Clean the input (remove spaces, make uppercase)
    clean_type = type.strip().upper()
    
    # 2. Log what we received (Check your terminal when you run this!)
    print(f"🔍 DEBUG: Request received - Topic: {topic}, Raw Type: '{type}', Parsed: '{clean_type}'")

    # 3. Flexible matching
    if clean_type in ["MCQ", "MULTIPLE CHOICE", "OBJECTIVE", "QUIZ"]:
        gen_type = "mcq"
    else:
        gen_type = "subjective"
        
    print(f"⚙️  DEBUG: Generator switching to mode: {gen_type.upper()}")
    # ----------------------------------
    
    chain = get_exam_chain(question_type=gen_type)
    
    if not chain:
        return [{"id": "error", "text": "RAG Database not initialized. Please run ingestion.", "options": []}]

    print(f"🧠 Generating {count} {difficulty} {gen_type} questions for {topic}...")

    for i in range(count):
        try:
            # Invoke the RAG chain
            ai_data = chain.invoke({"topic": topic, "difficulty": difficulty})
            
            # Construct the object
            q_id = str(uuid.uuid4())
            
            new_question = {
                "id": q_id,
                "text": ai_data.get("question", "Error generating question text."),
                "options": ai_data.get("options", []), 
                "correctAnswer": ai_data.get("correct_answer") or ai_data.get("answer_key") or "Refer to explanation",
                "rubric": ai_data.get("rubric") or ai_data.get("explanation") or "No rubric provided."
            }
            
            questions.append(new_question)
            
        except Exception as e:
            print(f"❌ Generation Error on Question {i+1}: {e}")
            questions.append({
                "id": str(uuid.uuid4()),
                "text": "Error generating this question. Please try again.",
                "options": []
            })

    return questions
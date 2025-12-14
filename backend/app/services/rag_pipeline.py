import uuid
import json
# Import the real chain from the moved ML core
from app.ml_core.src.chains.question_generator import get_exam_chain

async def generate_questions(topic: str, difficulty: str, type: str, count: int = 5):
    """
    Real integration with LangChain RAG pipeline.
    """
    questions = []
    
    # Initialize the chain (Llama 3 via Groq)
    chain = get_exam_chain()
    
    if not chain:
        # Fallback if DB not loaded
        return [{"id": "error", "text": "RAG Database not initialized.", "options": []}]

    print(f"🧠 Generating {count} {difficulty} questions for {topic}...")

    for i in range(count):
        try:
            # Invoke the RAG chain
            # Note: The prompt in question_generator.py might need adjustment 
            # to return strict JSON if you want to parse it programmatically.
            response_text = chain.invoke({"topic": topic, "difficulty": difficulty})
            
            # PARSING STRATEGY:
            # The current LLM output is text. You need to parse it into JSON.
            # Ideally, update the prompt in question_generator.py to output JSON.
            
            # Constructing object assuming text response for now:
            q_id = str(uuid.uuid4())
            questions.append({
                "id": q_id,
                "text": response_text, # Contains Question, Answer, Explanation
                "options": [], # Llama needs to be prompted specifically for options if MCQ
                "correctAnswer": "See Explanation",
                "rubric": "Refer to generated answer key"
            })
            
        except Exception as e:
            print(f"Generation Error: {e}")

    return questions
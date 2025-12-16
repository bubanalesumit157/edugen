from app.ml_core.src.retrieval.retriever import get_retriever
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser  # Changed to JSON Parser
from langchain_core.pydantic_v1 import BaseModel, Field

# Load API Keys
load_dotenv()

# --- Define Output Structures ---
# These classes tell the AI exactly what JSON format we want
class MCQOutput(BaseModel):
    question: str = Field(description="The question text")
    options: list[str] = Field(description="List of 4 options (A, B, C, D)")
    correct_answer: str = Field(description="The correct option letter (e.g., 'A')")
    explanation: str = Field(description="Reasoning for the correct answer")

class SubjectiveOutput(BaseModel):
    question: str = Field(description="The question text")
    answer_key: str = Field(description="The comprehensive model answer")
    rubric: str = Field(description="Key points required for full marks")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_exam_chain(question_type="subjective"):
    """
    Creates a chain that returns a JSON object separating Question from Answer.
    """
    # Initialize LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.5, # Lower temp for more strict JSON adherence
        model_kwargs={"response_format": {"type": "json_object"}} # Force JSON mode
    )
    
    retriever = get_retriever()
    if not retriever:
        print("❌ Error: Could not load the retriever (Database).")
        return None

    # --- Setup Parser based on Type ---
    if question_type.lower() == "mcq":
        parser = JsonOutputParser(pydantic_object=MCQOutput)
        format_instructions = parser.get_format_instructions()
        
        template = """
        You are an expert NCERT Examiner. Create a high-quality Multiple Choice Question (MCQ).
        
        Based ONLY on the following textbook content:
        {context}
        
        Create a {difficulty} level MCQ about the topic: "{topic}".
        
        {format_instructions}
        
        Ensure the 'options' list contains exactly 4 strings including the option letter (e.g., "A) Option text").
        """
    else:
        # Subjective
        parser = JsonOutputParser(pydantic_object=SubjectiveOutput)
        format_instructions = parser.get_format_instructions()
        
        template = """
        You are an expert NCERT Examiner. Create a high-quality subjective exam question.
        
        Based ONLY on the following textbook content:
        {context}
        
        Create a {difficulty} level question about the topic: "{topic}".
        
        {format_instructions}
        """
    
    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {
            "context": (lambda x: x["topic"]) | retriever | format_docs, 
            "topic": lambda x: x["topic"], 
            "difficulty": lambda x: x["difficulty"],
            "format_instructions": lambda x: format_instructions
        }
        | prompt
        | llm
        | parser # Now returns a Dictionary, not a String
    )
    
    return chain

# --- Testing Block ---
if __name__ == "__main__":
    print("📝 --- NCERT EXAM SETTER (JSON Mode) ---")
    
    topic = input("Enter Topic (e.g., Photosynthesis): ")
    difficulty = input("Enter Difficulty (Medium): ")
    q_type = "mcq" # Hardcoded test for brevity

    chain = get_exam_chain(question_type=q_type)

    if chain:
        print(f"\n⏳ Generating JSON for {topic}...")
        try:
            # The result is now a Python Dictionary
            result = chain.invoke({"topic": topic, "difficulty": difficulty})
            
            print("\n✅ GENERATED OBJECT:")
            print(result)
            
            print("\n--- WHAT THE STUDENT SEES ---")
            print(f"Q: {result['question']}")
            if 'options' in result:
                print(f"Options: {result['options']}")
                
            print("\n--- HIDDEN (STORED IN DB) ---")
            if 'correct_answer' in result:
                print(f"Answer: {result['correct_answer']}")
            if 'answer_key' in result:
                print(f"Key: {result['answer_key']}")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
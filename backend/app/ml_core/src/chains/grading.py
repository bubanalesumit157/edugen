# backend/app/ml_core/src/chains/grading.py

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Define the expected JSON structure
class GradingOutput(BaseModel):
    score: int = Field(description="Score between 0 and 100")
    feedback: str = Field(description="Detailed feedback explaining the score and any mistakes")

def get_grading_chain():
    # Use JSON mode for the LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.1, # Low temp for consistent grading
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    parser = JsonOutputParser(pydantic_object=GradingOutput)
    
    # Template includes {format_instructions}
    template = """
    You are an expert AI Grader. 
    
    Compare the Student Submission against the Master Answer Key.
    
    MASTER KEY:
    {question}
    
    STUDENT SUBMISSION:
    {student_answer}
    
    RUBRIC/INSTRUCTIONS:
    {rubric}
    
    GRADING RULES:
    1. If the student answers "A" and the key matches "A", give full points.
    2. For written answers, look for key concepts rather than exact wording.
    3. Be fair but strict.
    
    {format_instructions}
    """

    # --- FIX IS HERE: We pre-fill 'format_instructions' so the caller doesn't have to ---
    prompt = ChatPromptTemplate.from_template(template).partial(
        format_instructions=parser.get_format_instructions()
    )

    chain = (
        prompt 
        | llm 
        | parser
    )

    return chain
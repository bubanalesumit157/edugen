import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load Keys
load_dotenv()

def get_bloom_chain():
    """
    Creates a chain that analyzes an entire assignment's pedagogical quality.
    Called by ml_engine.py -> analyze_assignment_pedagogy
    """
    # 1. Setup the Analyst AI
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.3
    )

    # 2. The Analyst Prompt
    template = """
    You are an expert Pedagogy Consultant specialized in Bloom's Taxonomy.
    
    Task: Analyze the following exam assignment and provide a pedagogical audit.
    
    ASSIGNMENT CONTENT:
    {assignment_content}
    
    Please provide a report covering:
    1. **Bloom's Level Distribution:** (e.g., mostly Recall vs. Critical Thinking?)
    2. **Topic Coverage:** Is the assignment focused or scattered?
    3. **Difficulty Consistency:** Are the questions consistent with a single difficulty level?
    4. **Improvement Suggestions:** 2-3 specific ways to make this assignment better.
    
    Keep the tone professional and constructive.
    """
    
    prompt = ChatPromptTemplate.from_template(template)

    # 3. Return the Chain
    chain = prompt | llm | StrOutputParser()
    
    return chain

# --- Legacy/Test Function (Optional, kept if you want to run manually) ---
if __name__ == "__main__":
    print("⚖️ --- BLOOM'S TAXONOMY AUDITOR (TEST MODE) ---")
    
    chain = get_bloom_chain()
    
    test_content = """
    Title: Photosynthesis Quiz
    - What is the chemical formula for glucose?
    - Define chlorophyll.
    - List the stages of the Calvin Cycle.
    """
    
    print("⏳ Analyzing test content...")
    result = chain.invoke({"assignment_content": test_content})
    print(result)
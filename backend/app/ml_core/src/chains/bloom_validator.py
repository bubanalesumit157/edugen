import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load Keys
load_dotenv()

def validate_question_difficulty(question, target_level):
    """
    Checks if a generated question actually matches the requested Bloom's Taxonomy level.
    Levels: Remember, Understand, Apply, Analyze, Evaluate, Create.
    """
    
    # 1. Setup the Auditor AI (Llama 3.3)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.0 # Zero temp for strict logical analysis
    )

    # 2. The Auditor Prompt
    template = """
    You are an expert Pedagogy Consultant specialized in Bloom's Taxonomy.
    
    Task: Verify if the question matches the target Cognitive Level.
    
    Target Level: {target_level}
    Question to Check: "{question}"
    
    Bloom's Levels Reference:
    - Remember: Recall facts, define terms.
    - Understand: Explain ideas, summarize.
    - Apply: Use information in new situations.
    - Analyze: Draw connections, differentiate.
    - Evaluate: Justify a stand or decision.
    - Create: Produce new or original work.
    
    Output exactly in this format:
    **Match:** [Yes/No]
    **Actual Level:** [The level you think it is]
    **Reasoning:** [Brief explanation]
    **Improvement:** [If No, rewrite the question to match the Target Level]
    """
    
    prompt = ChatPromptTemplate.from_template(template)

    # 3. Run the Chain
    chain = prompt | llm | StrOutputParser()
    
    print(f"🕵️  Auditing question against level: '{target_level}'...")
    result = chain.invoke({
        "question": question, 
        "target_level": target_level
    })
    
    return result

if __name__ == "__main__":
    print("⚖️ --- BLOOM'S TAXONOMY AUDITOR ---")
    
    # Test Data
    # Let's try to trick it with a mismatch
    q_input = input("Enter a Question to check: ")
    level_input = input("What level SHOULD it be? (e.g., Analyze, Remember): ")
    
    feedback = validate_question_difficulty(q_input, level_input)
    
    print("\n" + "="*40)
    print(feedback)
    print("="*40)
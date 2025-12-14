import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.retrieval.retriever import get_retriever

# Load API Keys
load_dotenv()

def grade_student_answer(question, student_answer):
    """
    Grades a student's answer by comparing it to the textbook content.
    """
    
    # 1. Retrieve the "Ground Truth" from the textbook
    print(f"🔍 Fetching official answers for: '{question}'...")
    retriever = get_retriever()
    if not retriever:
        return "Error: Database not found."
    
    docs = retriever.invoke(question)
    if not docs:
        return "❌ Error: Could not find relevant textbook content to grade this."
    
    context_text = "\n\n".join(doc.page_content for doc in docs)

    # 2. Setup the Grader AI (Llama 3.3)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.3 # Low temp = strict and consistent grading
    )

    # 3. The Grading Prompt
    template = """
    You are a strict academic grader for Grade 11/12 Physics & Chemistry.
    
    Reference Material (from NCERT):
    {context}
    
    Question: {question}
    Student Answer: {student_answer}
    
    Task:
    Evaluate the student's answer based ONLY on the Reference Material.
    
    Output Format:
    **Score:** [0-10]
    **Verdict:** [Correct / Partially Correct / Incorrect]
    **Feedback:** [One sentence explaining the mistake or praise]
    **Missing Concepts:** [List key terms/concepts missing from the answer, if any]
    """
    
    prompt = ChatPromptTemplate.from_template(template)

    # 4. Run the Chain
    grading_chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    
    print("📝 Grading the answer...")
    result = grading_chain.invoke({
        "context": context_text,
        "question": question,
        "student_answer": student_answer
    })
    
    return result

if __name__ == "__main__":
    print("🎓 --- AI AUTOMATED GRADER ---")
    
    # Inputs
    q = input("Enter Question: ")
    ans = input("Enter Student Answer: ")
    
    # Run Grading
    feedback = grade_student_answer(q, ans)
    
    print("\n" + "="*40)
    print(feedback)
    print("="*40)
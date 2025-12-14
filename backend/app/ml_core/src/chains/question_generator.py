import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.retrieval.retriever import get_retriever

# Load API Keys
load_dotenv()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_exam_chain():
    """
    Creates a chain specifically for generating exam questions using Groq (Llama 3).
    """
    # Initialize Groq
    # We use 'llama3-70b-8192' for high intelligence, or 'llama3-8b-8192' for speed.
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.7
    )
    
    retriever = get_retriever()
    if not retriever:
        print("❌ Error: Could not load the retriever (Database).")
        return None

    # The "Exam Setter" Prompt
    template = """
    You are an expert NCERT Examiner. Your goal is to create a high-quality exam question.
    
    Based ONLY on the following textbook content:
    {context}
    
    Create a {difficulty} level question about the topic: "{topic}".
    
    The question should be:
    - Strictly within the provided context.
    - Conceptual and clear.
    
    Format your output exactly like this:
    **Question:** [The Question Here]
    **Marks:** [Suggested Marks, e.g., 2, 5]
    **Answer Key:** [The Correct Answer]
    **Explanation:** [Why this is the answer, citing the concept]
    """
    
    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {
            "context": (lambda x: x["topic"]) | retriever | format_docs, 
            "topic": lambda x: x["topic"], 
            "difficulty": lambda x: x["difficulty"]
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

if __name__ == "__main__":
    print("📝 --- NCERT EXAM SETTER (Powered by Groq) ---")
    topic = input("Enter Topic (e.g., Work, Energy, Gravity): ")
    difficulty = input("Enter Difficulty (Easy, Medium, Hard): ")
    
    chain = get_exam_chain()
    if chain:
        print(f"\n⏳ Generating a {difficulty} question on {topic}...")
        try:
            response = chain.invoke({"topic": topic, "difficulty": difficulty})
            print("\n" + "="*40)
            print(response)
            print("="*40)
        except Exception as e:
            print(f"\n❌ Error: {e}")
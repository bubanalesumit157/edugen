# import logging
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# DB_FAISS_PATH = "vectorstore/db_faiss"

# def get_retriever():
#     """
#     Loads the FAISS database and returns a 'retriever' interface.
#     This retriever can be used by LangChain to fetch documents.
#     """
#     logger.info("Loading Embedding Model...")
#     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
#     logger.info(f"Loading Vector Database from {DB_FAISS_PATH}...")
#     try:
#         vector_store = FAISS.load_local(
#             DB_FAISS_PATH, 
#             embeddings, 
#             allow_dangerous_deserialization=True
#         )
        
#         # Create a retriever that looks for the top 3 most relevant chunks
#         retriever = vector_store.as_retriever(
#             search_type="similarity",
#             search_kwargs={"k": 3} 
#         )
#         return retriever
        
#     except Exception as e:
#         logger.error(f"❌ Failed to load database: {e}")
#         return None

# if __name__ == "__main__":
#     # TEST AREA: This runs only if you run this file directly
#     print("\n🔎 --- TESTING RETRIEVAL ---")
#     query = "What is the definition of work in physics?"
    
#     retriever = get_retriever()
#     if retriever:
#         print(f"❓ Question: {query}")
#         print("⏳ Searching database...")
        
#         docs = retriever.invoke(query)
        
#         print(f"\n✅ Found {len(docs)} relevant results!")
#         for i, doc in enumerate(docs):
#             print(f"\n--- Result {i+1} ---")
#             print(f"📄 Source: {doc.metadata.get('source', 'Unknown')}")
#             print(f"📝 Content Snippet: {doc.page_content[:300]}...") # Show first 300 chars


import logging
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define path relative to where the script is run
# Assuming run from backend/ root
DB_FAISS_PATH = os.path.join(os.getcwd(), "app", "ml_core", "vectorstore", "db_faiss")

def get_embeddings():
    """
    Returns the embedding model. 
    Exported so ingest.py can use the exact same model.
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_retriever():
    """
    Loads the FAISS database and returns a 'retriever' interface.
    """
    logger.info("Loading Embedding Model...")
    embeddings = get_embeddings()
    
    logger.info(f"Loading Vector Database from {DB_FAISS_PATH}...")
    try:
        vector_store = FAISS.load_local(
            DB_FAISS_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3} 
        )
        return retriever
        
    except Exception as e:
        logger.error(f"❌ Failed to load database from {DB_FAISS_PATH}: {e}")
        return None

if __name__ == "__main__":
    # Test block
    print("\n🔎 --- TESTING RETRIEVAL ---")
    retriever = get_retriever()
    if retriever:
        docs = retriever.invoke("What is physics?")
        print(f"✅ Found {len(docs)} results.")
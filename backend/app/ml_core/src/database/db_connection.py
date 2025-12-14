import os
import logging
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_FAISS_PATH = "vectorstore/db_faiss"

def get_db_connection():
    """
    Returns the FAISS vector store.
    If the database exists locally, it loads it.
    If not, it creates a new empty one.
    """
    logger.info("Initializing Embedding Model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if os.path.exists(DB_FAISS_PATH):
        logger.info(f"📂 Loading existing FAISS database from {DB_FAISS_PATH}...")
        try:
            vector_store = FAISS.load_local(
                DB_FAISS_PATH, 
                embeddings, 
                allow_dangerous_deserialization=True # Safe since we created the DB ourselves
            )
            return vector_store
        except Exception as e:
            logger.error(f"Error loading DB: {e}")
            return None
    else:
        logger.info("⚠️ No existing database found. You need to run the ingestion script first.")
        # Return None or a temporary empty store if needed, but usually we just want to load
        return None

def create_new_db(chunks):
    """
    Creates a new FAISS database from text chunks and saves it locally.
    """
    logger.info("Initializing Embedding Model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    logger.info("🚀 Creating FAISS vector store from documents...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    logger.info(f"💾 Saving database to {DB_FAISS_PATH}...")
    vector_store.save_local(DB_FAISS_PATH)
    return vector_store

if __name__ == "__main__":
    # Test if the folder exists
    if os.path.exists(DB_FAISS_PATH):
        print("✅ SUCCESS: Found local FAISS database!")
    else:
        print("ℹ️ Note: No database found yet. Run 'src/ingestion/ingest.py' to create one.")
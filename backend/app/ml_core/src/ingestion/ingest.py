import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.database.db_connection import create_new_db

def load_and_process_pdfs(data_folder="./data/raw"):
    """
    Loads all PDFs, splits them, and creates a local FAISS index.
    """
    # 1. Find all PDF files (recursive)
    pdf_files = glob.glob(os.path.join(data_folder, "**", "*.pdf"), recursive=True)
    
    if not pdf_files:
        print(f"❌ No PDFs found in {data_folder}. Please add files to data/raw/physics etc.")
        return

    print(f"🔎 Found {len(pdf_files)} PDF(s). Processing...")

    all_chunks = []

    # 2. Process each PDF
    for pdf_path in pdf_files:
        print(f"   👉 Loading: {os.path.basename(pdf_path)}...")
        
        try:
            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()
            
            # Split Text
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(raw_docs)
            
            # Add metadata
            for chunk in chunks:
                chunk.metadata["source"] = pdf_path
            
            all_chunks.extend(chunks)
            print(f"      ✅ Generated {len(chunks)} chunks.")
            
        except Exception as e:
            print(f"      ❌ Error reading {pdf_path}: {e}")

    # 3. Save to FAISS (The Local Database)
    if all_chunks:
        print(f"\n🧠 Vectorizing {len(all_chunks)} total chunks... (This might take a minute)")
        create_new_db(all_chunks)
        print("🎉 SUCCESS: Database created at 'vectorstore/db_faiss'")
    else:
        print("❌ No text extracted. Database was not created.")

if __name__ == "__main__":
    load_and_process_pdfs()
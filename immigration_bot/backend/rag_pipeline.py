from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings  # ⬅️ Optimized package
from pathlib import Path
import os

def get_rag_chain():
    print("🚀 Initializing RAG pipeline...")

    # Path to your existing FAISS index
    index_path = Path(__file__).resolve().parent / "faiss_index"

    if not index_path.exists():
        raise FileNotFoundError(f"❌ FAISS index not found at: {index_path}. Please run ingest_docs.py locally and commit the index.")

    print("✅ FAISS index found. Loading...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")

    # Load the FAISS vector store
    db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

    print("📚 FAISS index loaded successfully.")
    
    # Construct a basic retriever chain (example)
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    # You can return retriever directly or build a full chain
    return retriever  # or return your chain if using LangChain chains

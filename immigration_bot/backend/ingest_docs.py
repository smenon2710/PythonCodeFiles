from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path
import os

def ingest():
    print("📥 Starting document ingestion...")

    file_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "uscis_policy_manual.pdf"
    
    if not file_path.exists():
        raise FileNotFoundError(f"❌ PDF not found at {file_path}")
    else:
        print(f"✅ Found PDF at {file_path}")

    loader = PyPDFLoader(str(file_path))
    docs = loader.load()
    print(f"📄 Loaded {len(docs)} pages from PDF.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(docs)
    print(f"🧩 Split into {len(texts)} chunks.")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("🔍 Embeddings initialized.")

    index_path = Path(__file__).resolve().parent.parent / "faiss_index"
    FAISS.from_documents(texts, embeddings).save_local(index_path)
    print(f"✅ FAISS index saved to {index_path}")

if __name__ == "__main__":
    ingest()

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI  # You can use any LLM here
from pathlib import Path
import os

def get_rag_chain():
    print("🚀 Initializing RAG pipeline...")

    index_path = Path(__file__).resolve().parent / "faiss_index"

    if not index_path.exists():
        raise FileNotFoundError(f"❌ FAISS index not found at: {index_path}")

    print("✅ FAISS index found. Loading...")
    embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-small-v2")

    db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    print("📚 FAISS index loaded successfully.")

    retriever = db.as_retriever(search_kwargs={"k": 3})

    # 👉 Wrap retriever with an LLM-powered QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
        retriever=retriever,
        return_source_documents=True  # optional for debugging / frontend
    )

    return qa_chain

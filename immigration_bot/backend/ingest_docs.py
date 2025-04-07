from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from tqdm import tqdm
import os

def ingest():
    # Load your PDF
    file_path = "data/raw/uscis_policy_manual.pdf"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found at: {file_path}")

    print("📄 Loading document...")
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    # Chunk the document
    print("✂️ Splitting document into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(f"✅ Split into {len(chunks)} chunks.")

    # Embedding
    print("🧠 Starting embedding process...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")   # Or use a smaller model for faster dev
    db = FAISS.from_documents(tqdm(chunks, desc="🔄 Embedding chunks"), embeddings)

    # Save the index
    db.save_local("faiss_index")
    print("✅ Embedding complete. FAISS index saved to 'faiss_index/'.")

if __name__ == "__main__":
    ingest()

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from tqdm import tqdm
from pathlib import Path
import os
import requests

def download_pdf_if_missing(file_path, url):
    if not os.path.exists(file_path):
        print(f"📥 PDF not found. Downloading from: {url}")
        response = requests.get(url)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(response.content)
        print("✅ Download complete.")
    else:
        print("📄 PDF already exists, skipping download.")

def ingest():
    # PDF settings
    
    file_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "uscis_policy_manual.pdf"
    pdf_url = "https://www.uscis.gov/sites/default/files/document/policy-manual/uscis_policy_manual.pdf"

    # Download PDF if not present
    download_pdf_if_missing(file_path, pdf_url)

    print("📄 Loading document...")
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()

    # Split into chunks
    print("✂️ Splitting document into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=300,   # was 500
    chunk_overlap=20  # was 50)
    chunks = splitter.split_documents(docs)
    print(f"✅ Split into {len(chunks)} chunks.")

    # Embed
    print("🧠 Starting embedding process...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.from_documents(tqdm(chunks, desc="🔍 Embedding chunks"), embeddings)

    # Save index
    db.save_local("faiss_index")
    print("✅ Embedding complete. FAISS index saved to 'faiss_index/'.")

if __name__ == "__main__":
    ingest()

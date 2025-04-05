
from langchain.text_splitter import RecursiveCharacterTextSplitter

# OLD (deprecated):
# from langchain.document_loaders import PyPDFLoader
# from langchain.vectorstores import FAISS
# from langchain.embeddings import HuggingFaceEmbeddings

# ✅ NEW (future-proof):
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


import os

def ingest():
    loader = PyPDFLoader("data/raw/uscis_policy_manual.pdf")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-xl")
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local("faiss_index")

if __name__ == "__main__":
    ingest()

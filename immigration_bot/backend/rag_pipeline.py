from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import OpenAI  # Replace with your LLM if local
import os

def get_rag_chain():
    embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-xl")
    db = FAISS.load_local("faiss_index", embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 5})

    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(temperature=0),  # Replace with Ollama or Mistral if local
        retriever=retriever,
        return_source_documents=True
    )
    return qa

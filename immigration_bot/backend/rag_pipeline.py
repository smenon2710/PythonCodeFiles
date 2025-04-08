from dotenv import load_dotenv
load_dotenv()

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from pathlib import Path
import os

def get_rag_chain():
    load_dotenv()

    # Load embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # FAISS index path
    index_path = Path(__file__).resolve().parent.parent / "faiss_index"
    index_file = index_path / "index.faiss"

    # If index is missing, ingest on-the-fly (e.g., on Render)
    if not index_file.exists():
        print("🛠 FAISS index not found. Running ingestion to rebuild it...")
        from ingest_docs import ingest
        ingest()

    # Load vector DB
    db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 5})

    # Define LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    # Conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # Build chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False
    )

    return chain

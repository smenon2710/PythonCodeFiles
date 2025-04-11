from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from immigration_bot.backend.rag_pipeline import get_rag_chain
import logging
import psutil
from dotenv import load_dotenv
load_dotenv()


# ---- Logging Setup ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_memory(stage: str):
    mem = psutil.Process().memory_info().rss / 1024 ** 2  # in MB
    logger.info(f"🧠 Memory at {stage}: {mem:.2f} MB")

# ---- FastAPI App ----
logger.info("🟡 Starting FastAPI app...")
app = FastAPI()

# ---- CORS Settings ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Load QA Chain ----
try:
    logger.info("🧠 Loading RAG chain...")
    log_memory("Before loading RAG chain")
    qa_chain = get_rag_chain()
    log_memory("After loading RAG chain")
    logger.info("✅ RAG chain loaded successfully.")
except Exception as e:
    logger.error(f"❌ Failed to load RAG chain: {e}")
    qa_chain = None

# ---- API Endpoints ----
@app.get("/")
def root():
    return {"status": "RAG backend is running 🎉"}

@app.post("/ask")
async def ask_question(query: dict):
    if qa_chain is None:
        return {"error": "RAG chain not loaded."}
    
    question = query.get("question")
    if not question:
        return {"error": "No question provided."}
    
    logger.info(f"📥 Received question: {question}")
    
    output = qa_chain.invoke({"query": question})
    response = output.get("result", "Sorry, I couldn't find an answer.")
    sources = output.get("source_documents", [])
    
    logger.info(f"📤 Response: {response}")
    return {
        "response": response,
        "sources": [doc.metadata.get("source", "N/A") for doc in sources]
    }

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .rag_pipeline import get_rag_chain

print("🟡 Starting FastAPI app...")

app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🧠 Loading RAG chain...")
try:
    qa_chain = get_rag_chain()
    print("✅ RAG chain loaded successfully.")
except Exception as e:
    print(f"❌ Failed to load RAG chain: {e}")
    raise

@app.get("/")
async def root():
    return {"message": "RAG API is running ✅"}

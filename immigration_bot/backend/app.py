from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.rag_pipeline import get_rag_chain

app = FastAPI()
qa_chain = get_rag_chain()

# Allow frontend access (e.g., from Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
async def query_api(req: Request):
    body = await req.json()
    query = body.get("query", "")
    if not query:
        return {"error": "No query provided."}

    result = qa_chain(query)
    return {
        "answer": result["result"],
        "sources": [doc.metadata.get("source", "Unknown") for doc in result["source_documents"]],
    }

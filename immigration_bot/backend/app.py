from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.rag_pipeline import get_rag_chain

app = FastAPI()
qa_chain = get_rag_chain()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def query_api(request: Request):
    body = await request.json()
    question = body.get("query", "")
    result = qa_chain({"question": question})
    answer = result["answer"]
    sources = [doc.metadata.get("source", "unknown") for doc in result.get("source_documents", [])]
    return {"answer": answer, "sources": sources}

@app.get("/health")
def health_check():
    return {"status": "ok"}

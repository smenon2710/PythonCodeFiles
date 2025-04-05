from fastapi import FastAPI, Request
from backend.rag_pipeline import get_rag_chain
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
qa_chain = get_rag_chain()

# CORS for Streamlit
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
    response = qa_chain(query)
    return {"answer": response['result'], "sources": [doc.metadata for doc in response["source_documents"]]}

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from .schemas import QueryRequest, DecisionResponse
from .llm_service import GeminiService
from .vector_store import VectorStore
from .document_processor import DocumentProcessor
from .helpers import log_request, timeit
import os

app = FastAPI(title="HackRx 6.0 Document Processor", docs_url="/docs")

LLM = GeminiService()
VS  = VectorStore(persist_path=os.getenv("CHROMA_DIR", "/data/chroma"))

DP  = DocumentProcessor(vector_store=VS)

@app.post("/ingest")
@timeit
async def ingest(file: UploadFile = File(...)):
    content = await file.read()
    DP.ingest_binary(content, file.filename)
    return {"status": "indexed", "filename": file.filename}

@app.post("/query", response_model=DecisionResponse)
@log_request
@timeit
async def query(q: QueryRequest):
    docs = VS.semantic_search(q.query, k=8)
    decision = LLM.reason(query=q.query, documents=docs)
    return decision

@app.get("/health")
def health():
    return {"status": "ok"}

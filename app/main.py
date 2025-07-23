import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class QueryRequest(BaseModel):
    query: str = Field(..., example="46-year-old male knee surgery Pune 3-month policy")

class Clause(BaseModel):
    text: str
    source: str

class DecisionResponse(BaseModel):
    decision: str  # approved / rejected / partial
    amount: Optional[float]
    justification: str
    clauses: List[Clause]

# Initialize FastAPI app
app = FastAPI(
    title="HackRx 6.0 Document Processor", 
    description="AI-powered document processing for insurance queries",
    version="1.0.0",
    docs_url="/docs"
)

# Global variables for services
LLM = None
VS = None
DP = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global LLM, VS, DP
    
    try:
        logger.info("Initializing services...")
        
        # Import services here to avoid import errors during module loading
        from app.llm_service import GeminiService
        from app.vector_store import VectorStore
        from app.document_processor import DocumentProcessor
        
        # Initialize services
        LLM = GeminiService()
        VS = VectorStore(persist_path=os.getenv("CHROMA_DIR", "/data/chroma"))
        DP = DocumentProcessor(vector_store=VS)
        
        logger.info("Services initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise e

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "HackRx 6.0 Document Processing API", "status": "running"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "Service is healthy"}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """Ingest and process document"""
    try:
        if not DP:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        content = await file.read()
        DP.ingest_binary(content, file.filename)
        
        return {
            "status": "indexed", 
            "filename": file.filename,
            "message": "Document successfully processed and indexed"
        }
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/query", response_model=DecisionResponse)
async def query(q: QueryRequest):
    """Process query and return decision"""
    try:
        if not LLM or not VS:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Perform semantic search
        docs = VS.semantic_search(q.query, k=8)
        
        # Get LLM reasoning
        decision = LLM.reason(query=q.query, documents=docs)
        
        return decision
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        return {
            "status": "operational",
            "services": {
                "llm_service": "initialized" if LLM else "not_initialized",
                "vector_store": "initialized" if VS else "not_initialized", 
                "document_processor": "initialized" if DP else "not_initialized"
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
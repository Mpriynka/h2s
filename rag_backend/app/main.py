# app/main.py
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from app.rag import RAGSystem
from app.models import Query

app = FastAPI(title="RAG PDF Processor")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag_system = RAGSystem()

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Save the file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        # Process the PDF
        result = rag_system.ingest_pdf(file_path)
        
        # Clean up
        os.remove(file_path)
        
        return {"status": "success", "message": "PDF processed successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/")
async def query_knowledge_base(query: Query):
    try:
        results = rag_system.query(query.text, query.top_k)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/")
def health_check():
    return {"status": "healthy"}
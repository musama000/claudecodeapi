from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from app.anthropic_client import AnthropicClient
from rag.rag_engine import RAGEngine

# Load environment variables
load_dotenv('.env.example')

app = FastAPI(title="ThreeJS Code Generator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
    temperature: Optional[float] = 0.7

class GenerateResponse(BaseModel):
    code: str


anthropic_client = AnthropicClient()
rag_engine = RAGEngine("/home/musamaclaude/threejs-rag-generator/dataset")

@app.get("/")
async def root():
    return {"message": "ThreeJS Code Generator API"}

@app.post("/generate", response_model=GenerateResponse)
async def generate_threejs_code(request: GenerateRequest):
    try:
        relevant_docs = rag_engine.search(request.prompt, k=5)
        
        context = "\n\n".join([doc["content"] for doc in relevant_docs])
        if request.context:
            context += f"\n\nAdditional context: {request.context}"
        
        response = await anthropic_client.generate_threejs_code(
            prompt=request.prompt,
            context=context,
            temperature=request.temperature
        )
        
        return GenerateResponse(
            code=response["code"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/index-dataset")
async def index_dataset():
    try:
        rag_engine.index_documents()
        return {"message": "Dataset indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
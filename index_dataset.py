#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from rag.rag_engine import RAGEngine

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if GEMINI_API_KEY is set (needed for the app, though not for indexing)
    if not os.getenv("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY not set in .env file")
        print("You'll need to set it before using the /generate endpoint")
    
    print("Starting dataset indexing...")
    
    # Initialize RAG engine
    rag_engine = RAGEngine("dataset")
    
    # Index all documents
    rag_engine.index_documents()
    
    print("Dataset indexing complete!")

if __name__ == "__main__":
    main()
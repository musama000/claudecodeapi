#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from rag.rag_engine import RAGEngine

def main():
    # Load environment variables
    load_dotenv()
    
    
    print("Starting dataset indexing...")
    
    # Initialize RAG engine
    rag_engine = RAGEngine("dataset")
    
    # Index all documents
    rag_engine.index_documents()
    
    print("Dataset indexing complete!")

if __name__ == "__main__":
    main()
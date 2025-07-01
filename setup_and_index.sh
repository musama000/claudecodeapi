#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
pip3 install fastapi uvicorn python-multipart pydantic google-generativeai chromadb python-dotenv

# Index the dataset
echo "Indexing dataset..."
cd /home/musamaclaude/threejs-rag-generator
python3 index_dataset.py

echo "Setup complete!"
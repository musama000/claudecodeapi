# ThreeJS RAG Code Generator

FastAPI application that uses Gemini 2.5 Pro and RAG to generate Three.js code based on documentation in the dataset folder.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. Add Three.js documentation to the `dataset` folder

4. Run the application:
```bash
uvicorn main:app --reload
```

## API Endpoints

- `GET /` - API info
- `POST /generate` - Generate Three.js code
- `POST /index-dataset` - Index documents in dataset folder
- `GET /health` - Health check

## Usage

1. First index your dataset:
```bash
curl -X POST http://localhost:8000/index-dataset
```

2. Generate Three.js code:
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a rotating cube with lighting",
    "temperature": 0.7
  }'
```# claudecodeapi

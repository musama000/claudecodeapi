# ThreeJS RAG Code Generator

FastAPI application that uses Anthropic Claude and RAG to generate Three.js code based on documentation in the dataset folder.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
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
- `POST /find-khan-video` - Find relevant Khan Academy videos by topic

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
```

3. Find Khan Academy videos for topics:
```bash
curl -X POST http://localhost:8000/find-khan-video \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "vectors"
  }'
```

## API Integration

### Main Generation Endpoint

**Endpoint**: `/generate`

Example request:
```json
{
  "prompt": "Create a rotating cube with lighting",
  "temperature": 0.7
}
```

### Khan Academy Video Search

**Endpoint**: `/find-khan-video`

Example request:
```json
{
  "topic": "linear algebra"
}
```

Example response:
```json
{
  "title": "Introduction to vectors and scalars | Vectors | Precalculus | Khan Academy",
  "url": "https://youtube.com/watch?v=fNk_zzaMoSs",
  "description": "Introduction to vectors and scalars. Understanding that vectors have both magnitude and direction...",
  "duration": "8:12"
}

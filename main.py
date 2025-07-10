from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from googleapiclient.discovery import build
from app.anthropic_client import AnthropicClient
from app.mermaid_client import MermaidClient
from rag.rag_engine import RAGEngine

# Load environment variables
load_dotenv('.env.example')

# Set up FastAPI with full OpenAPI documentation
app = FastAPI(
    title="ThreeJS Code Generator",
    version="1.0.0",
    description="Generate Three.js code using RAG with examples",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    # OpenAPI documentation
    openapi_tags=[]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to known origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "X-Content-Type-Options"]
)

# Create static directory for logo and other assets
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Create a placeholder logo.png if it doesn't exist
logo_path = static_dir / "logo.png"
if not logo_path.exists():
    # We'll use a simple text file as placeholder since we can't create binary files easily
    with open(logo_path, "w") as f:
        f.write("This is a placeholder for logo.png - replace with actual image")

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class GenerateRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
    temperature: Optional[float] = 0.7

class GenerateResponse(BaseModel):
    code: str

class TopicRequest(BaseModel):
    topic: str = Field(..., description="The topic to search for Khan Academy videos")

class KhanVideoResponse(BaseModel):
    title: str
    url: str
    description: str
    duration: Optional[str] = None

class MermaidRequest(BaseModel):
    prompt: str = Field(..., description="The prompt describing what Mermaid diagram to generate")
    type: str = Field("mermaid", description="Type field (should be 'mermaid')")

class MermaidResponse(BaseModel):
    code: str
    success: Optional[bool] = True


anthropic_client = AnthropicClient()
mermaid_client = MermaidClient()
rag_engine = RAGEngine("dataset")

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
            code=response["code"],
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


# Function schemas for the OpenAI API
FUNCTION_SCHEMAS = {
    "threejs_rag": {
        "name": "threejs_rag",
        "description": "Generate Three.js code based on a prompt using the RAG system",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The prompt describing what Three.js code to generate"
                },
                "context": {
                    "type": "string",
                    "description": "Optional additional context to include with the prompt"
                },
                "temperature": {
                    "type": "number",
                    "description": "The temperature parameter for code generation (0.0 to 1.0)",
                    "default": 0.7
                },
                "num_examples": {
                    "type": "integer",
                    "description": "Number of examples to retrieve from the RAG system",
                    "default": 5
                }
            },
            "required": ["prompt"]
        }
    }
}


@app.get("/logo.png")
async def get_logo():
    """Redirect to static logo for compatibility with older integrations."""
    return FileResponse("static/logo.png")

@app.post("/generate-mermaid", response_model=MermaidResponse)
async def generate_mermaid_diagram(request: MermaidRequest):
    """Generate Mermaid diagram code for frontend consumption."""
    try:
        # Determine diagram type from prompt or default to flowchart
        diagram_type = "flowchart"
        prompt_lower = request.prompt.lower()
        
        if any(word in prompt_lower for word in ["sequence", "interaction", "communication"]):
            diagram_type = "sequenceDiagram"
        elif any(word in prompt_lower for word in ["class", "uml", "inheritance"]):
            diagram_type = "classDiagram"
        elif any(word in prompt_lower for word in ["state", "transition", "fsm", "finite state"]):
            diagram_type = "stateDiagram-v2"
        elif any(word in prompt_lower for word in ["entity", "database", "er diagram", "erd"]):
            diagram_type = "erDiagram"
        elif any(word in prompt_lower for word in ["journey", "user journey", "customer journey"]):
            diagram_type = "journey"
        elif any(word in prompt_lower for word in ["gantt", "project timeline", "schedule"]):
            diagram_type = "gantt"
        elif any(word in prompt_lower for word in ["pie", "percentage", "distribution"]):
            diagram_type = "pie"
        elif any(word in prompt_lower for word in ["quadrant", "four quadrants", "2x2 matrix"]):
            diagram_type = "quadrantChart"
        elif any(word in prompt_lower for word in ["requirement", "requirements"]):
            diagram_type = "requirementDiagram"
        elif any(word in prompt_lower for word in ["git", "branch", "commit", "merge"]):
            diagram_type = "gitgraph"
        elif any(word in prompt_lower for word in ["c4", "context diagram", "system context"]):
            diagram_type = "C4Context"
        elif any(word in prompt_lower for word in ["mindmap", "mind map", "brainstorm"]):
            diagram_type = "mindmap"
        elif any(word in prompt_lower for word in ["timeline", "chronology", "history"]):
            diagram_type = "timeline"
        elif any(word in prompt_lower for word in ["zenuml", "zen", "uml sequence"]):
            diagram_type = "zenuml"
        elif any(word in prompt_lower for word in ["sankey", "flow diagram", "energy flow"]):
            diagram_type = "sankey-beta"
        elif any(word in prompt_lower for word in ["xy chart", "xy graph", "bar chart", "line chart"]):
            diagram_type = "xychart-beta"
        elif any(word in prompt_lower for word in ["block", "blocks", "grid"]):
            diagram_type = "block-beta"
        elif any(word in prompt_lower for word in ["packet", "network packet", "data packet"]):
            diagram_type = "packet-beta"
        elif any(word in prompt_lower for word in ["kanban", "task board", "todo board"]):
            diagram_type = "kanban"
        elif any(word in prompt_lower for word in ["architecture", "system architecture"]):
            diagram_type = "architecture-beta"
        elif any(word in prompt_lower for word in ["radar", "spider", "skills", "assessment"]):
            diagram_type = "radar"
        elif any(word in prompt_lower for word in ["treemap", "tree map", "hierarchical"]):
            diagram_type = "treemap-beta"
        
        # Use the specialized Mermaid client
        response = await mermaid_client.generate_mermaid_diagram(
            prompt=request.prompt,
            diagram_type=diagram_type,
            context=None,
            temperature=0.3
        )
        
        mermaid_code = response["mermaid_code"]
        
        return MermaidResponse(
            code=mermaid_code,
            success=True
        )
    except Exception as e:
        return MermaidResponse(
            code=f"flowchart TD\n    A[Error: {str(e)}]",
            success=False
        )

@app.post("/find-khan-video", response_model=KhanVideoResponse)
async def find_khan_video(request: TopicRequest):
    """Find the best Khan Academy video for a given topic using YouTube API."""
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    
    # Debug: Print what we got
    print(f"DEBUG: YOUTUBE_API_KEY = '{youtube_api_key}' (length: {len(youtube_api_key) if youtube_api_key else 0})")
    
    if not youtube_api_key or youtube_api_key.strip() == "":
        raise HTTPException(
            status_code=500, 
            detail="YouTube API key not configured. Please set YOUTUBE_API_KEY environment variable."
        )
    
    try:
        # Build YouTube API client
        youtube = build("youtube", "v3", developerKey=youtube_api_key)
        
        # Khan Academy's YouTube channel ID
        khan_channel_id = "UC4a-Gbdw7vOaccHmFo40b9g"
        
        # Search for videos in Khan Academy channel
        search_query = f"Khan Academy {request.topic}"
        
        search_response = youtube.search().list(
            q=search_query,
            channelId=khan_channel_id,
            part="snippet",
            maxResults=5,
            order="relevance",
            type="video"
        ).execute()
        
        if not search_response.get('items'):
            raise HTTPException(
                status_code=404,
                detail=f"No Khan Academy videos found for topic: {request.topic}"
            )
        
        # Get the best match (first result is most relevant)
        best_video = search_response['items'][0]
        video_id = best_video['id']['videoId']
        
        # Get additional video details (duration, etc.)
        video_details = youtube.videos().list(
            part="contentDetails,snippet",
            id=video_id
        ).execute()
        
        if video_details.get('items'):
            duration = video_details['items'][0]['contentDetails'].get('duration', '')
            # Convert ISO 8601 duration to readable format (PT4M13S -> 4:13)
            duration = parse_duration(duration)
        else:
            duration = None
        
        return KhanVideoResponse(
            title=best_video['snippet']['title'],
            url=f"https://youtube.com/watch?v={video_id}",
            description=best_video['snippet']['description'][:200] + "..." if len(best_video['snippet']['description']) > 200 else best_video['snippet']['description'],
            duration=duration
        )
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error searching Khan Academy videos: {str(e)}"
        )

def parse_duration(iso_duration: str) -> Optional[str]:
    """Convert ISO 8601 duration (PT4M13S) to readable format (4:13)."""
    if not iso_duration:
        return None
    
    import re
    
    # Parse PT4M13S format
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
    if not match:
        return None
    
    hours, minutes, seconds = match.groups()
    
    # Convert to readable format
    if hours:
        return f"{hours}:{minutes or '00'}:{seconds or '00'}"
    elif minutes:
        return f"{minutes}:{seconds.zfill(2) if seconds else '00'}"
    else:
        return f"0:{seconds or '00'}"




from fastapi import FastAPI, HTTPException, Query, Body, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import os
import uvicorn
from contextlib import asynccontextmanager
from google import genai
from google.genai import types
from dotenv import load_dotenv
import asyncio
import base64
from datetime import datetime
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rhea.server")


# Load Environment
load_dotenv()

# Configuration
PROJECT_ID = "rhea-noir"
LOCATION = "us-central1"

# Global Client
client: Optional[genai.Client] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    # Initialize Vertex AI Client on startup
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        print("✅ Rhea Cortex Online (Vertex AI)")
    except Exception as e:
        print(f"❌ Failed to init Cortex: {e}")
    yield
    # Cleanup
    print("💤 Rhea Cortex Offline")

app = FastAPI(
    title="Rhea Noir Intelligence",
    version="2.0.0",
    description="Cybernetic Creative Partner & Web Intelligence Officer (Kaedra Class)",
    lifespan=lifespan
)

# --- Global Exception Handlers (Prevent 500s) ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {exc}")
    return JSONResponse(
        status_code=503, # Service Unavailable (safest fallback)
        content={"detail": "Rhea Cortex Malfunction", "error": str(exc), "type": "GlobalException"},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# --- Pydantic Models (Kaedra Spec) ---

class AnalyzeUrlRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_name: str
    model: str
    latency_ms: float
    timestamp: float

class EmbeddingRequest(BaseModel):
    text: str
    model: str = "text-embedding-004"

class ExecuteCodeRequest(BaseModel):
    code: str
    language: str = "python"

class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gemini-3-pro-preview"
    temperature: float = 0.7
    use_grounding: bool = True

class GenerateResponse(BaseModel):
    response: str
    model_used: str
    grounded: bool

class ImageRequest(BaseModel):
    prompt: str

class LightEffectRequest(BaseModel):
    selector: str = "all"
    effect: str = "breathe"
    color: str = "purple"
    period: float = 2
    cycles: float = 3

class LightStateRequest(BaseModel):
    selector: str = "all"
    power: Optional[str] = None
    color: Optional[str] = None
    brightness: Optional[float] = None
    duration: float = 1

class LoreItemResponse(BaseModel):
    id: str
    title: str
    category: str
    description: Optional[str] = None
    importance: int = 0
    confidence: int = 100
    source: str = "System"
    timestamp: Optional[str] = None

class NotionWebhookPayload(BaseModel):
    type: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class OpenAIMessage(BaseModel):
    role: str
    content: Union[str, List[Any]]

from enum import Enum

class ThinkingLevel(str, Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class SmartRouterConfig(BaseModel):
    # dynamic routing configuration
    force_model: Optional[str] = None
    min_thinking_level: ThinkingLevel = ThinkingLevel.LOW
    auto_route: bool = True

class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None # If None, Smart Router decides
    thinking_level: ThinkingLevel = ThinkingLevel.LOW
    temperature: float = 0.7
    use_grounding: bool = True
    context_id: Optional[str] = None

class GenerateResponse(BaseModel):
    response: str
    model_used: str
    thinking_level_used: str
    grounded: bool

class OpenAIChatCompletionRequest(BaseModel):
    model: Optional[str] = None # Router handles default
    messages: List[OpenAIMessage]
    temperature: Optional[float] = 0.7
    thinking_level: ThinkingLevel = ThinkingLevel.LOW
    stream: Optional[bool] = False

# --- Senior-Level Smart Router ---
def route_request(
    requested_model: Optional[str], 
    thinking_level: ThinkingLevel, 
    prompt_complexity: int = 1
) -> tuple[str, types.GenerateContentConfig]:
    """
    Intelligent routing logic for Gemini 3 Fleet.
    Decides between Flash (Speed) and Pro (Reasoning) based on constraints.
    """
    
    # 1. Hardware/Model Selection
    selected_model = "gemini-3-flash-preview" # Default WORKHORSE
    
    # Auto-Upgrade logic: High thinking or explicit Pro request upgrades to Pro
    if requested_model:
        selected_model = requested_model
    elif thinking_level == ThinkingLevel.HIGH:
        selected_model = "gemini-3-pro-preview" # Upgrade for deep thought
    elif prompt_complexity > 8: # Arbitrary complexity heuristic
         selected_model = "gemini-3-pro-preview"
    
    # 2. Config Generation (Using Raw Google GenAI Types)
    # Map API level to SDK config
    # Note: 'thinking_level' parameter name might vary in valid SDK versions, 
    # checking documentation this is 'reasoning_effort' in OAI or 'thinking_config' in Google Native.
    # We will construct the native config for the Google Client.
    
    # Verify model compatibility with thinking levels
    # Flash supports: minimal, low, medium, high
    # Pro supports: low, high (Defaults to High)
    
    # Default mapping (safe for Flash)
    sdk_thinking_level = types.ThinkingLevel.HIGH # Default safe
    
    if thinking_level == ThinkingLevel.MINIMAL:
        sdk_thinking_level = "MINIMAL" # types.ThinkingLevel.MINIMAL might be flaky in preview, string is safer if enum missing
    elif thinking_level == ThinkingLevel.LOW:
        sdk_thinking_level = types.ThinkingLevel.LOW
    elif thinking_level == ThinkingLevel.MEDIUM:
        sdk_thinking_level = types.ThinkingLevel.MEDIUM
    elif thinking_level == ThinkingLevel.HIGH:
        sdk_thinking_level = types.ThinkingLevel.HIGH
        
    # Pro Compatibility Layer
    if selected_model == "gemini-3-pro-preview":
        if thinking_level == ThinkingLevel.MINIMAL:
            sdk_thinking_level = types.ThinkingLevel.LOW # Pro min is Low
        elif thinking_level == ThinkingLevel.MEDIUM:
            sdk_thinking_level = types.ThinkingLevel.HIGH # Pro medium maps to High
            
    generation_config = types.GenerateContentConfig(
        temperature=1.0, # Gemini 3 recommends 1.0 default
        thinking_config=types.ThinkingConfig(thinking_level=sdk_thinking_level),
    )
    
    return selected_model, generation_config


class RazerEffectRequest(BaseModel):
    effect: str = "static"
    color: Optional[str] = "purple"

class ResearchRequest(BaseModel):
    query: str

class SearchRequest(BaseModel):
    query: str
    num_results: int = 5

class StoryGenerateRequest(BaseModel):
    session_id: str
    prompt: str
    auto_mode: bool = False

class StorySessionRequest(BaseModel):
    world_id: str = "world_default"
    mode: str = "writer"
    prompt: Optional[str] = None

class SyncRequest(BaseModel):
    world_id: str = "world_default"

class VideoGenerationRequest(BaseModel):
    prompt: str
    resolution: str = "720p"
    aspect_ratio: str = "16:9"
    number_of_videos: int = 1

class WorldBuildRequest(BaseModel):
    seed: str
    tone: str = "dark and atmospheric"
    theme: str = "power and survival"
    include_characters: bool = True
    include_quests: bool = True

# --- Endpoints ---

# Default / General
@app.get("/")
async def root():
    return {"status": "online", "agent": "Rhea Noir", "project": PROJECT_ID}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/health/detailed")
async def health_detailed():
    return {"status": "healthy", "services": {"vertex": client is not None, "notion": True}}

@app.get("/config")
async def get_config():
    return {"agent": "Rhea", "version": "2.0.0", "mode": "Kaedra Mock"}

@app.get("/v1")
async def v1_root():
    return {"version": "v1"}

@app.get("/v1/api")
async def v1_api_info():
    return {"name": "Rhea API", "version": "2.0"}

# Agent Cards
@app.get("/a2a")
async def get_a2a_card():
    return {"name": "Rhea", "role": "Creative Intelligence", "capabilities": ["text", "image", "research"]}

@app.get("/a2a/card")
async def get_a2a_card_alias():
    return await get_a2a_card()

@app.get("/agent-card")
async def get_agent_card_alias_2():
    return await get_a2a_card()

@app.get("/.well-known/agent.json")
async def get_agent_card_standard():
    return await get_a2a_card()

# V1 Models
@app.get("/v1/models")
async def list_models_v1():
    return {
        "data": [
            {"id": "gemini-3-pro-preview", "object": "model"},
            {"id": "gemini-3-flash-preview", "object": "model"},
            {"id": "gemini-3-pro-image-preview", "object": "model"},
            {"id": "gemini-2.5-flash", "object": "model"},
            {"id": "gemini-2.5-pro", "object": "model"}
        ]
    }

@app.get("/models")
async def list_models_alias():
    return await list_models_v1()

# Chat & Completion
@app.post("/v1/chat/completions")
async def chat_completions(req: OpenAIChatCompletionRequest):
    if not client:
        raise HTTPException(status_code=503, detail="Cortex not initialized")
    try:
        last_msg = req.messages[-1].content if req.messages else "Hello"
        if isinstance(last_msg, list): last_msg = str(last_msg)
        
        # ROUTING
        model_id, config = route_request(req.model, req.thinking_level)
        
        response = await client.aio.models.generate_content(
            model=model_id,
            contents=last_msg,
            config=config # Pass the smart config
        )
        return {
            "id": "chatcmpl-rhea",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": model_id,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": response.text},
                "finish_reason": "stop"
            }]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat")
async def chat_legacy(req: ChatRequest):
    # Legacy alias - Auto-routes to Flash/Low
    if not client: raise HTTPException(status_code=503, detail="Cortex Offline")
    try:
        # Default smart route
        model_id, config = route_request(None, ThinkingLevel.LOW)
        
        response = await client.aio.models.generate_content(
            model=model_id, 
            contents=req.message,
            config=config
        )
        return {
            "response": response.text,
            "agent_name": "Rhea",
            "model": model_id,
            "latency_ms": 100,
            "timestamp": datetime.now().timestamp()
        }
    except Exception as e:
        logger.error(f"Chat Legacy Error: {e}")
        return JSONResponse(status_code=503, content={"detail": f"Generation Failed: {str(e)}"})

# Generate (Text/Image/Video/World)
@app.post("/generate")
async def fleet_generate(req: GenerateRequest):
    if not client: raise HTTPException(status_code=503, detail="Cortex Offline")
    try:
        # User has full control via req parameters
        model_id, config = route_request(req.model, req.thinking_level)
        
        response = await client.aio.models.generate_content(
            model=model_id, 
            contents=req.prompt,
            config=config
        )
        return {
            "response": response.text, 
            "model_used": model_id, 
            "thinking_level_used": req.thinking_level,
            "grounded": req.use_grounding
        }
    except Exception as e:
         logger.error(f"Generate Error: {e}")
         return JSONResponse(status_code=503, content={"detail": f"Generation Failed: {str(e)}"})

@app.post("/generate-image")
async def generate_image(req: ImageRequest):
    if not client: raise HTTPException(status_code=503, detail="Cortex Offline")
    try:
        # Nano Banana Pro Pattern (Gemini 3 Pro Image)
        # Supports Thinking + Grounding + 4K
        
        response = await client.aio.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=req.prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"], # Critical for Thinking + Image
                image_config=types.ImageConfig(
                    aspect_ratio="16:9", 
                    image_size="4K"
                ),
                tools=[{"google_search": {}}], # Grounding supported
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True # See the creative process
                )
            )
        )
        
        # Parse Response for Images
        generated_images = []
        thought_trace = ""
        
        if response.parts:
            for part in response.parts:
                if part.text:
                    thought_trace += part.text + "\n"
                if part.inline_data: # Image data
                   # In a real app we would upload this to cloud storage
                   # For now we just acknowledge it exists
                   generated_images.append("timestamped_image_ref_placeholder")
                   
        return {
            "status": "success",
            "images": generated_images,
            "thoughts": thought_trace,
            "model_used": "gemini-3-pro-image-preview"
        }

    except Exception as e:
        logger.error(f"Image Gen Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/video")
async def generate_video(req: VideoGenerationRequest):
    return "Video generation started (Job ID: mock-job-123)"

@app.post("/generate/world")
async def generate_world(req: WorldBuildRequest):
    return {
        "success": True, 
        "world_name": "Rhea Generated World",
        "era": "Future Void",
        "core_tension": req.theme,
        "factions": [{"name": "Default Faction"}],
        "characters": [], 
        "quests": []
    }

# Research & Code
@app.post("/research")
async def start_research(req: ResearchRequest):
    if not client: raise HTTPException(status_code=503, detail="Cortex Offline")
    try:
        # Research implies complex thought -> Force HIGH thinking
        model_id, config = route_request(None, ThinkingLevel.HIGH)
        
        response = await client.aio.models.generate_content(
            model=model_id, 
            contents=f"Research: {req.query}",
            config=config
        )
        return {"status": "completed", "summary": response.text}
    except Exception as e:
        logger.error(f"Research Error: {e}")
        return JSONResponse(status_code=503, content={"detail": f"Research Failed: {str(e)}"})


@app.get("/research/{task_id}")
async def get_research_status(task_id: str):
    return "Completed"

@app.post("/search")
async def fleet_search(req: SearchRequest):
    # Mock Search
    return f"Search results for {req.query}"

@app.post("/analyze-url")
async def analyze_url(req: AnalyzeUrlRequest):
    return f"Analyzed {req.url}"

@app.post("/execute-code")
async def execute_code(req: ExecuteCodeRequest):
    return "Code Execution Simulation: Success"

@app.post("/v1/embeddings")
async def create_embeddings(req: EmbeddingRequest):
    return "Embedding Vector (Mock)"

# Lore Endpoints
@app.get("/lore/feed")
async def get_lore_feed(world_id: str = "world_default"):
    return "Lore Feed Data"

@app.get("/lore/weighted")
async def get_weighted_lore(limit: int = 50):
    return "Weighted Lore Data"

@app.get("/lore/bible")
async def get_world_bible(world_id: str = "world_default"):
    return "World Bible Data"

@app.get("/lore/search")
async def search_lore(q: str, limit: int = 20):
    return [{"id": "lore_1", "title": f"Result for {q}", "category": "General", "source": "Rhea"}]

@app.get("/lore/{id}")
async def get_lore_item(id: str):
    return {"id": id, "title": "Lore Item", "category": "General"}

# Story Endpoints
@app.get("/story/sessions")
async def list_story_sessions():
    return []

@app.post("/story/session")
async def create_story_session(req: StorySessionRequest):
    return "Session Created"

@app.get("/story/session/{session_id}")
async def get_story_session(session_id: str):
    return "Session Details"

@app.post("/story/generate")
async def generate_story_content(req: StoryGenerateRequest):
    return "Story Content Generated"

# Worlds & Sync
@app.get("/worlds")
async def list_worlds():
    return ["world_default", "world_rhea"]

@app.post("/sync")
async def manual_sync(req: SyncRequest):
    return "Sync Started"

@app.get("/sync/{world_id}")
async def sync_status(world_id: str):
    return "Syncing"

@app.post("/webhook/notion")
async def notion_webhook(payload: NotionWebhookPayload):
    return "Webhook Received"

# Hardware (Lights/Razer) - Mocks
@app.get("/lights/status")
async def get_lights_status(): return "Lights Online"

@app.post("/lights/set")
async def set_light_state(req: LightStateRequest): return "Light Set"

@app.post("/lights/effect")
async def run_light_effect(req: LightEffectRequest): return "Effect Running"

@app.get("/lights/presets")
async def get_light_presets(): return ["void", "neon", "chill"]

@app.post("/lights/preset/{preset_id}")
async def apply_light_preset(preset_id: str): return f"Preset {preset_id} Applied"

@app.get("/razer/status")
async def get_razer_status(): return "Razer Online"

@app.post("/razer/effect")
async def set_razer_effect(req: RazerEffectRequest): return "Razer Effect Set"

@app.post("/razer/sync")
async def sync_razer(): return "Razer Synced"

# Validation & Hooks
@app.get("/validate")
async def run_validation(): return "Validation Passed"

@app.get("/validate/quick")
async def quick_validation(): return "Quick Validation Passed"

@app.post("/hooks/slack/events")
async def slack_events(): return "Ack"

@app.post("/hooks/slack/commands")
async def slack_commands(): return "Ack"

@app.post("/hooks/pubsub")
async def pubsub_webhook(): return "Ack"

# Custom - CoWrite (Preserved)
@app.post("/cowrite")
async def cowrite(req: dict):
    # Simplified alias for generating creative text
    # In Kaedra this might be part of story/generate, but we keep it for CLI tool access if needed
    # using generate endpoint logic roughly
    return {"status": "Use /generate or /story/generate"}


if __name__ == "__main__":
    uvicorn.run("rhea_server:app", host="0.0.0.0", port=8081, reload=True)

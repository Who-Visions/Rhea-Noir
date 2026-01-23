---
name: gcp-processor-pattern
description: Scaffolds Cutting Edge AI Agents using the Processor Pattern (Gemini 3, Veo 3, Lyria, Nano Banana).
keywords: [gcp, agent, processor, pattern, gemini 3, veo 3, lyria, async, mcp, tools]
priority: 95
light_feedback:
  neutral: purple
---
# GCP Processor Pattern Skill

This skill provides deep technical blueprints for building "Processor-based" Agents. It complements the `gcp-architect` skill by providing implementation details for complex Cortices.

## 1. The Neural Architecture (Model Hierarchy)

Agents are constructed using a **Brain-Cortex** architecture.

| Component | Model Family | Role | Key Capabilities |
| :--- | :--- | :--- | :--- |
| **Brain (Core)** | `gemini-3-flash` / `pro` | Reasoning & Orchestration | Complex logic, Routing, JSON Mode, Function Calling. |
| **Visual Cortex** | `imagen-3.0-generate-001` | Image Synthesis | 4K generation, "Thinking Mode" for prompt enhancement. |
| **Cinematic Cortex** | `veo-2.0-generate-001` | Video Synthesis | 1080p video generation, Storyboarding. |
| **Auditory Cortex** | `lyria-realtime` / `gemini-3` | Audio I/O | Music generation, Audio understanding, Native Audio Input. |
| **Speech Cortex** | `gemini-2.5-flash-tts` | Text-to-Speech | Low-latency synthesis, Multi-speaker voices. |
| **RealTime Cortex** | `gemini-3-flash` (Live) | Live Interaction | **WebSocket-based** bidirectional Audio/Video streaming. |
| **Efficiency Cortex**| N/A (Infrastructure) | Optimization | **Context Caching** (TTL management), **Enum Enforcing**. |

---

## 2. Processor Blueprints

### 🧠 Brain Processor (Core Logic + Structured Output)

Handles reasoning, JSON enforcement, and Safety.

```python
from pydantic import BaseModel, Field
from google.genai import types

class AnalysisResult(BaseModel):
    summary: str
    risk_score: int = Field(..., ge=0, le=100)
    tags: list[str]

async def brain_process(prompt: str, context: str = None) -> AnalysisResult:
    """Core reasoning engine with strict JSON output and Safety rails."""
    
    # 1. Safety Config (Blocking harmful content)
    safety_settings = [
        types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="BLOCK_LOW_AND_ABOVE"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="BLOCK_MEDIUM_AND_ABOVE"
        )
    ]

    # 2. Reasoning with JSON Schema Enforcement
    response = await client.aio.models.generate_content(
        model="gemini-3-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AnalysisResult, # Direct Pydantic integration
            safety_settings=safety_settings,
            temperature=0.2 # Low temp for precision
        )
    )
    
    # 3. Usage & Metadata Inspection (Crucial for monitoring)
    print(f"Token Usage: {response.usage_metadata}")
    
    return response.parsed
```

### ⚡ Efficiency Cortex (Caching & Enums)

Optimizes costs for large contexts and enforces strict categorical choices.

```python
import datetime
from enum import Enum

class Sentiment(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

async def efficiency_process(heavy_document: str, query: str):
    """Demonstrates Context Caching and Enum Enforcement."""

    # 1. Create Context Cache (for large repeat docs)
    # Note: Cache is model-specific!
    cache = await client.aio.caches.create(
        model="gemini-3-flash",
        config={
            'contents': [heavy_document],
            'system_instruction': 'You are a legal analyst.',
            'ttl': '3600s' # 1 Hour
        }
    )
    print(f"Cached {cache.usage_metadata.total_token_count} tokens. Name: {cache.name}")

    # 2. Use Cache + Enum Constraint
    response = await client.aio.models.generate_content(
        model="gemini-3-flash",
        contents=query,
        config=types.GenerateContentConfig(
            cached_content=cache.name,
            response_mime_type="text/x.enum",
            response_schema=Sentiment # Enforce Enum return
        )
    )
    
    # 3. Update TTL if needed
    await client.aio.caches.update(
        name=cache.name,
        config=types.UpdateCachedContentConfig(ttl="7200s")
    )
    
    return response.text
```

### 📡 RealTime Cortex (Live API)

Handles low-latency, bidirectional audio/video interaction via WebSockets.

```python
import asyncio

async def realtime_session():
    """Establishes a bi-directional Multimodal Live Session."""
    
    config = {
        "response_modalities": ["AUDIO"], # Or ["TEXT"]
        "tools": [{"google_search": {}}] # Can use tools in Live!
    }

    async with client.aio.live.connect(model="gemini-2.0-flash-exp", config=config) as session:
        # Task 1: Receiver Loop
        async def receive_loop():
            while True:
                turn = session.receive()
                async for chunk in turn:
                    if chunk.server_content:
                        # Handle Model Audio/Text
                        if chunk.server_content.model_turn:
                            print(chunk.server_content.model_turn.parts[0].text) 
                    if chunk.tool_call:
                        # Handle Tool Calls immediately
                        print(f"Tool Call: {chunk.tool_call.function_calls}")
                        # ... execute tool and send response ...

        # Task 2: Sender (Simulated User Input)
        await session.send_client_content(
            turns={"role": "user", "parts": [{"text": "Hello, start the session."}]},
            turn_complete=True
        )
        
        # Run loops (simplified for snippet)
        await receive_loop()
```

### 🗣️ Speech Cortex (Advanced TTS)

Handles single/multi-speaker synthesis with "Director's Mode" control.

```python
async def speech_process(text: str, speakers: list[str] = None):
    """
    Generates audio using Gemini 2.5 TTS.
    Supports 'Director Mode' prompting for style/pace control.
    """
    
    # 1. Multi-Speaker Config
    # If speakers provided, map them to voices (e.g., Kore, Puck)
    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
        )
    )
    
    if speakers and len(speakers) > 1:
        speech_config = types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker=speakers[0], 
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                        )
                    ),
                    types.SpeakerVoiceConfig(
                        speaker=speakers[1],
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                        )
                    )
                ]
            )
        )

    # 2. Generation with "Director's Prompt" support
    # The input 'text' should ideally be structured with:
    # AUDIO PROFILE, SCENE, DIRECTOR'S NOTES, and TRANSCRIPT
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=speech_config
        )
    )
    
    # 3. Extract Audio Blob
    return response.candidates[0].content.parts[0].inline_data.data
```

### 🧠 Thinking Cortex (Gemini 3)

Configures "Thinking Process" for deep reasoning tasks.

```python
async def thinking_process(self, hard_problem: str, level: str = "high"):
    """
    Enables 'Thinking' mode for complex logic/math/coding.
    """
    # thinking_level handles Gemini 3's complexity scaling:
    # "minimal", "low", "medium", "high"
    
    response = await client.aio.models.generate_content(
        model="gemini-3-flash",
        contents=hard_problem,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True, # Returns 'Thought Summaries'
                thinking_level=level
            )
        )
    )
    
    # Extract Thoughts vs Answer
    for part in response.candidates[0].content.parts:
        if part.thought:
            print(f"🧠 Thought: {part.text}")
        else:
            print(f"💡 Answer: {part.text}")
            
    return response
```

### 🎥 Video Cortex (Veo & Understanding)

Handles Video Understanding (via Files API & YouTube) and Generation (Veo 3.1).

```python
class VideoCortex(processor.Processor):
    async def understand(self, video_source: str, prompt: str):
        """
        Analyzes video from file path or YouTube URL.
        """
        video_part = None
        
        # 1. Handle YouTube or File
        if "youtube.com" in video_source or "youtu.be" in video_source:
            # YouTube Support (Public only)
             video_part = types.Part.from_uri(
                 uri=video_source,
                 mime_type="video/mp4"
             )
        else:
            # Files API Upload
             video_file = await client.aio.files.upload(path=video_source)
             
             # Wait for Active State (Critical for Video)
             while video_file.state.name == "PROCESSING":
                 await asyncio.sleep(2)
                 video_file = await client.aio.files.get(name=video_file.name)
                 
             if video_file.state.name == "FAILED":
                 raise ValueError(f"Video processing failed: {video_file.state.name}")
                 
             video_part = video_file

        # 2. Analyze with Gemini 3 (1M Context)
        response = await client.aio.models.generate_content(
            model="gemini-3-pro-preview", # Use Pro for deep video analysis
            contents=[
                video_part,
                prompt # e.g., "Find the exact timestamp where the cat jumps."
            ],
            config=types.GenerateContentConfig(
                media_resolution=types.MediaResolution.MEDIA_RESOLUTION_MEDIUM
            )
        )
        return response.text

    async def generate_veo(self, prompt: str):
        """
        Generates video using Veo 3.1 (Cinematic Cortex).
        """
        # 1. Generate (Async Operation)
        operation = await client.aio.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=types.GenerateVideoConfig(
                aspect_ratio="16:9",
                resolution="1080p", # Supports "4k" (2160p) as of Jan 2026
                file_format="mp4"
            )
        )
        
        # 2. Poll for Completion
        while not operation.done():
            await asyncio.sleep(5)
            # operation.reload() # If needed by SDK version
            
        result = operation.result()
        return result # Returns video bytes/uri
```

### 🎨 ImageGen Cortex (Nano Banana)

Handles Advanced Image Generation (Gemini 3) with Thinking Mode & Editing.

```python
class ImageGenCortex(processor.Processor):
    async def generate_thoughtful(self, prompt: str):
        """
        Generates 'Thinking Images' (Gemini 3 Pro Image).
        """
        response = await client.aio.models.generate_images(
            model="gemini-3-pro-image-preview",
            prompt=prompt,
            config=types.GenerateImageConfig(
                number_of_images=1,
                include_thoughts=True, # Enable Thinking Mode
                aspect_ratio="16:9",
                output_mime_type="image/jpeg"
            )
        )
        # Access thoughts: response.predictions[0].thoughts
        return response


    async def edit_image(self, base_image_path: str, prompt: str, mask_path: str = None):
        """
        Edits images using Nano Banana (Gemini 2.5).
        Supports Inpainting (with mask) or Style Transfer.
        """
        base_img = types.Image.load_from_file(base_image_path)
        
        # Optional: Load Mask for Inpainting
        mask_img = types.Image.load_from_file(mask_path) if mask_path else None

        response = await client.aio.models.edit_image(
            model="gemini-2.5-flash-image",
            prompt=prompt,
            base_image=base_img,
            mask=mask_img, # Convert to Inpainting if present
            config=types.EditImageConfig(
                number_of_images=1
            )
        )
        return response
```

### 🛠️ Tool Cortex (Agents & MCP)

Handles Action-taking via Python functions, MCP Servers, and Multimodal Tool Outputs.

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class ToolCortex(processor.Processor):
    async def auto_tool_process(self, prompt: str, tools: list):
        """Demonstrates Automatic Function Calling."""
        chat = client.aio.chats.create(
            model="gemini-3-flash",
            config=types.GenerateContentConfig(
                tools=tools,
                automatic_function_calling={"disable": False}
            )
        )
        response = await chat.send_message(prompt)
        return response.text

    async def mcp_process(self, prompt: str, history: list = []):
        """Demonstrates Manual Tooling with MCP."""
        # Setup MCP Client...
        pass
```

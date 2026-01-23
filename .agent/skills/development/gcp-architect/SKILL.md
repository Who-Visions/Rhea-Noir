---
name: gcp-architect
description: Blueprint for state-of-the-art GCP Agents (Gemini 3.0, Veo 3.1, Lyria RealTime).
---

# GCP Architect Skill

This skill defines the "Cutting-Edge Architect" patterns for building advanced multimodal agents on Google Cloud Platform. It integrates the latest experimental models for Vision, Video, and Audio.

## Tier 4: Audio Cortex (Lyria RealTime)

**Model**: `models/lyria-realtime-exp`
**Protocol**: WebSocket (Bidirectional Streaming)
**Output**: Raw 16-bit PCM Audio @ 48kHz, Stereo

### 1. Connection & Streaming (Python)

Use the `google.genai` SDK with `asyncio`. The connection must be handled asynchronously.

```python
import asyncio
from google import genai
from google.genai import types

client = genai.Client(http_options={'api_version': 'v1alpha'})

async def receive_audio(session):
    """Background task to process incoming PCM audio chunks."""
    while True:
        async for message in session.receive():
            if message.server_content.audio_chunks:
                # audio_data is Raw 16-bit PCM
                audio_data = message.server_content.audio_chunks[0].data
                # Buffer and play or save...
        await asyncio.sleep(0.001) # Yield to event loop

async def start_audio_cortex():
    async with (
        client.aio.live.music.connect(model='models/lyria-realtime-exp') as session,
        asyncio.TaskGroup() as tg,
    ):
        tg.create_task(receive_audio(session))

        # Initial Setup
        await session.set_weighted_prompts(
            prompts=[types.WeightedPrompt(text='minimal techno', weight=1.0)]
        )
        await session.set_music_generation_config(
            config=types.LiveMusicGenerationConfig(bpm=120, temperature=1.0)
        )

        await session.play()
        
        # Keep alive...
        await asyncio.sleep(60) 
```

### 2. Live Steering (Real-Time Control)

You can steer the music generation dynamically without stopping the stream.

**Steering Prompts**:
Smoothly transition genres or moods.

```python
await session.set_weighted_prompts(
    prompts=[
        {"text": "Cyberpunk Ambience", "weight": 0.8},
        {"text": "Heavy Bass", "weight": 1.2},
    ]
)
```

**Live Configuration**:
Change BPM or Scale. Note: Changing BPM/Scale requires `reset_context()` for immediate effect (hard transition).

```python
await session.set_music_generation_config(
    config=types.LiveMusicGenerationConfig(
        bpm=140,
        scale=types.Scale.D_MAJOR_B_MINOR,
        music_generation_mode=types.MusicGenerationMode.QUALITY
    )
)
await session.reset_context() # Required for BPM/Scale changes
```

### 3. Best Practices

- **Audio Format**: Always handle `PCM 16-bit` @ `48kHz` Stereo.
- **Buffering**: Implement a jitter buffer on the client client side to handle network variance.
- **Weights**: Use weights (`0.0` - `inf`) to blend prompts. `1.0` is standard. Avoid `0`.
- **Safety**: Monitor `filtered_prompt` in responses to handle safety blocks gracefully.

## Tier 3: Cinematic (Veo 3.1) [Placeholder]

*Integration details for Veo 3.1 video generation would go here.*

## Tier 2: Vision (Gemini 2.0 Flash) [Placeholder]

*Integration details for Multimodal Vision would go here.*

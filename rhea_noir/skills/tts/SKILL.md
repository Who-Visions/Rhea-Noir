# TTS Skill

Text-to-Speech synthesis using Gemini TTS.

## Description

Rhea's voice - synthesize speech with her personality using Gemini 2.5 Flash TTS. Supports style prompts for tone, emotion, and pacing.

## Voice

- **Model**: `gemini-2.5-flash-tts`
- **Voice**: `Kore` (young female)
- **Language**: `en-US`
- **Style**: Warm, confident, expressive with Caribbean energy

## Actions

- `speak` — Synthesize text to speech
- `stream` — Stream speech synthesis for real-time playback

## Usage

```python
# Basic synthesis
skill.execute("speak", text="What's good? Let me break this down for you.")

# With custom style prompt
skill.execute("speak", 
    text="That's fire! You really understood the assignment.",
    style="Speak with enthusiasm and a warm, encouraging tone"
)

# Stream for real-time
skill.execute("stream", text="Long form content here...")
```

## Style Prompt Tips

Rhea's default style:
- Warm and confident
- Expressive with natural emphasis
- Caribbean-American energy
- Can switch to calm/professional for explanations

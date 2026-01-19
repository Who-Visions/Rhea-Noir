# Audio Skill

Audio understanding - transcription and analysis using Gemini.

## Description

Rhea can listen and understand audio input. Uses Gemini's native audio understanding for transcription, summarization, and analysis.

## Actions

- `transcribe` — Generate transcript from audio
- `analyze` — Describe and analyze audio content
- `summarize` — Summarize audio content

## Usage

```python
# Transcribe audio file
skill.execute("transcribe", audio_file="path/to/audio.mp3")

# Analyze audio content
skill.execute("analyze", audio_file="path/to/audio.mp3", prompt="What instruments are playing?")

# Summarize a podcast
skill.execute("summarize", audio_file="path/to/podcast.mp3")
```

## Supported Formats

- WAV (`audio/wav`)
- MP3 (`audio/mp3`)
- AIFF (`audio/aiff`)
- AAC (`audio/aac`)
- OGG Vorbis (`audio/ogg`)
- FLAC (`audio/flac`)

## Technical Notes

- 1 second of audio = 32 tokens
- Max audio length: 9.5 hours per prompt
- Audio is downsampled to 16 Kbps

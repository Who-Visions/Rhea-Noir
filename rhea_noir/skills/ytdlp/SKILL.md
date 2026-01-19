---
name: yt-dlp
version: 1.0.0
description: Video downloading skill using yt-dlp for YouTube and 1000+ other sites
---

# yt-dlp Skill

A powerful video downloading skill that leverages `yt-dlp`, a feature-rich command-line audio/video downloader supporting YouTube and 1000+ other sites.

## Capabilities

| Action | Description |
|--------|-------------|
| `download_video` | Download video from URL with format selection |
| `download_audio` | Extract audio only from video URL |
| `get_info` | Extract video metadata without downloading |
| `download_playlist` | Download entire playlist |
| `download_subtitles` | Download video subtitles |

## Requirements

```bash
pip install yt-dlp
```

For audio extraction, [FFmpeg](https://ffmpeg.org/) must be installed and in PATH.

## Usage Examples

### Download Video
```python
from rhea_noir.skills.ytdlp.actions import skill as ytdlp

# Download best quality video
result = ytdlp.download_video(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    output_dir="./downloads",
    format="best"
)
```

### Extract Audio Only
```python
# Download as MP3
result = ytdlp.download_audio(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    output_dir="./downloads",
    codec="mp3"
)
```

### Get Video Info
```python
# Get metadata without downloading
info = ytdlp.get_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(info['title'], info['duration'], info['view_count'])
```

### Download Playlist
```python
result = ytdlp.download_playlist(
    url="https://www.youtube.com/playlist?list=PLxxxxx",
    output_dir="./downloads",
    max_videos=10  # Optional limit
)
```

## Supported Sites

yt-dlp supports 1000+ sites including:
- YouTube (videos, shorts, playlists, channels)
- Vimeo
- TikTok
- Twitter/X
- Instagram
- SoundCloud
- Twitch
- And many more...

Full list: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## Output Templates

The skill uses smart naming: `%(title)s [%(id)s].%(ext)s`

Custom templates can be passed via `output_template` parameter.

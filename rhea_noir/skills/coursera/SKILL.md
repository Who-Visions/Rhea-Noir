---
name: coursera-dl
version: 1.0.0
description: Download Coursera courses, videos, subtitles, and materials
---

# Coursera Downloader Skill

Download Coursera course materials using `coursera-dl`. Supports both old platform and on-demand courses.

## Capabilities

| Action | Description |
|--------|-------------|
| `download_course` | Download full course with videos and materials |
| `download_videos_only` | Download only video files |
| `download_subtitles` | Download only subtitle files |
| `list_courses` | List enrolled courses |

## Requirements

```bash
pip install coursera-dl
```

## Authentication

Requires Coursera credentials. Set via environment variables:

```bash
export COURSERA_USER="your@email.com"
export COURSERA_PASS="yourpassword"
```

Or use CAUTH cookie from browser (recommended):
```bash
export COURSERA_CAUTH="your-cauth-value"
```

## Usage Examples

### Download Full Course
```python
from rhea_noir.skills.coursera.actions import skill as coursera

result = coursera.download_course(
    course_slug="machine-learning",
    output_dir="./courses",
    video_resolution="720p"
)
```

### Download Only Videos
```python
result = coursera.download_videos_only(
    course_slug="deep-learning",
    output_dir="./courses",
    video_resolution="540p"
)
```

### Download Subtitles Only
```python
result = coursera.download_subtitles(
    course_slug="python-programming",
    languages=["en", "es"]
)
```

### Filter by Section/Lecture
```python
result = coursera.download_course(
    course_slug="algorithms",
    section_filter="Week_3",  # Regex filter
    lecture_filter="Sorting"
)
```

## Video Resolutions

- `360p` - Low quality, smallest files
- `540p` - Default, balanced
- `720p` - HD quality

## Notes

> [!IMPORTANT]
> Only download courses you are enrolled in. This tool respects Coursera's Terms of Service.

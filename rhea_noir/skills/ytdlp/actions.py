"""
yt-dlp Skill for Rhea-Noir
Video downloading capabilities using yt-dlp
"""


from pathlib import Path
from typing import Optional, Dict, Any, List


class YtdlpSkill:
    """Skill for downloading videos using yt-dlp."""

    name = "ytdlp"
    version = "1.0.0"
    description = "Download videos from YouTube and 1000+ sites using yt-dlp"

    def __init__(self):
        self.default_output_template = "%(title)s [%(id)s].%(ext)s"

    def _get_ydl(self, opts: Optional[Dict] = None):
        """Get YoutubeDL instance with options."""
        try:
            import yt_dlp
        except ImportError:
            raise ImportError("yt-dlp not installed. Run: pip install yt-dlp")

        default_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        if opts:
            default_opts.update(opts)

        return yt_dlp.YoutubeDL(default_opts)

    def _success(self, data: Any) -> Dict:
        """Return success response."""
        return {"success": True, "data": data}

    def _error(self, message: str) -> Dict:
        """Return error response."""
        return {"success": False, "error": message}

    def get_info(self, url: str) -> Dict:
        """
        Extract video information without downloading.

        Args:
            url: Video URL

        Returns:
            Dict with video metadata (title, duration, views, etc.)
        """
        try:
            with self._get_ydl() as ydl:
                info = ydl.extract_info(url, download=False)
                # Sanitize for JSON serialization
                sanitized = ydl.sanitize_info(info)
                return self._success({
                    "id": sanitized.get("id"),
                    "title": sanitized.get("title"),
                    "description": sanitized.get("description"),
                    "duration": sanitized.get("duration"),
                    "view_count": sanitized.get("view_count"),
                    "like_count": sanitized.get("like_count"),
                    "channel": sanitized.get("channel"),
                    "channel_url": sanitized.get("channel_url"),
                    "upload_date": sanitized.get("upload_date"),
                    "thumbnail": sanitized.get("thumbnail"),
                    "formats_available": len(sanitized.get("formats", [])),
                    "webpage_url": sanitized.get("webpage_url"),
                })
        except Exception as e:
            return self._error(str(e))

    def download_video(
        self,
        url: str,
        output_dir: str = "./downloads",
        format: str = "best",
        output_template: Optional[str] = None,
        max_filesize: Optional[str] = None
    ) -> Dict:
        """
        Download video from URL.

        Args:
            url: Video URL
            output_dir: Directory to save video
            format: Format selection (best, worst, bestvideo+bestaudio, etc.)
            output_template: Custom output filename template
            max_filesize: Maximum filesize (e.g., "500M")

        Returns:
            Dict with download status and file path
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            template = output_template or self.default_output_template
            full_template = str(output_path / template)

            opts = {
                'format': format,
                'outtmpl': full_template,
            }

            if max_filesize:
                opts['max_filesize'] = max_filesize

            with self._get_ydl(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            return self._success({
                "message": "Video downloaded successfully",
                "title": info.get("title"),
                "filename": filename,
                "format": format
            })
        except Exception as e:
            return self._error(str(e))

    def download_audio(
        self,
        url: str,
        output_dir: str = "./downloads",
        codec: str = "mp3",
        quality: str = "192",
        output_template: Optional[str] = None
    ) -> Dict:
        """
        Download audio only from video URL.

        Args:
            url: Video URL
            output_dir: Directory to save audio
            codec: Audio codec (mp3, m4a, wav, flac, opus)
            quality: Audio quality/bitrate (128, 192, 256, 320)
            output_template: Custom output filename template

        Returns:
            Dict with download status and file path
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            template = output_template or self.default_output_template
            full_template = str(output_path / template)

            opts = {
                'format': 'bestaudio/best',
                'outtmpl': full_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': codec,
                    'preferredquality': quality,
                }]
            }

            with self._get_ydl(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # Audio files get extension changed
                base_filename = ydl.prepare_filename(info)
                audio_filename = Path(base_filename).with_suffix(f'.{codec}')

            return self._success({
                "message": "Audio downloaded successfully",
                "title": info.get("title"),
                "filename": str(audio_filename),
                "codec": codec,
                "quality": quality
            })
        except Exception as e:
            return self._error(str(e))

    def download_playlist(
        self,
        url: str,
        output_dir: str = "./downloads",
        format: str = "best",
        max_videos: Optional[int] = None,
        output_template: Optional[str] = None
    ) -> Dict:
        """
        Download entire playlist.

        Args:
            url: Playlist URL
            output_dir: Directory to save videos
            format: Format selection
            max_videos: Maximum number of videos to download
            output_template: Custom output filename template

        Returns:
            Dict with download status and count
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Use playlist-aware template
            template = output_template or "%(playlist_title)s/%(playlist_index)s - %(title)s [%(id)s].%(ext)s"
            full_template = str(output_path / template)

            opts = {
                'format': format,
                'outtmpl': full_template,
                'ignoreerrors': True,  # Continue on errors
            }

            if max_videos:
                opts['playlistend'] = max_videos

            with self._get_ydl(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                entries = info.get('entries', [])
                downloaded = [e for e in entries if e is not None]

            return self._success({
                "message": "Playlist downloaded successfully",
                "playlist_title": info.get("title"),
                "total_videos": len(entries),
                "downloaded": len(downloaded),
                "output_dir": str(output_path)
            })
        except Exception as e:
            return self._error(str(e))

    def download_subtitles(
        self,
        url: str,
        output_dir: str = "./downloads",
        languages: Optional[List[str]] = None,
        fmt: str = "srt"
    ) -> Dict:
        """
        Download subtitles for a video.

        Args:
            url: Video URL
            output_dir: Directory to save subtitles
            languages: List of language codes (e.g., ['en', 'es'])
            format: Subtitle format (srt, vtt, ass)

        Returns:
            Dict with subtitle file paths
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            template = str(output_path / self.default_output_template)

            opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,  # Also get auto-generated
                'subtitlesformat': fmt,
                'outtmpl': template,
            }

            if languages:
                opts['subtitleslangs'] = languages
            else:
                opts['subtitleslangs'] = ['en']  # Default to English

            with self._get_ydl(opts) as ydl:
                info = ydl.extract_info(url, download=True)

            return self._success({
                "message": "Subtitles downloaded",
                "title": info.get("title"),
                "languages_requested": languages or ['en'],
                "format": fmt,
                "output_dir": str(output_path)
            })
        except Exception as e:
            return self._error(str(e))

    def search_youtube(
        self,
        query: str,
        max_results: int = 5
    ) -> Dict:
        """
        Search YouTube and return video info.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of video info dicts
        """
        try:
            search_url = f"ytsearch{max_results}:{query}"

            with self._get_ydl() as ydl:
                info = ydl.extract_info(search_url, download=False)
                entries = info.get('entries', [])

                results = []
                for entry in entries:
                    if entry:
                        sanitized = ydl.sanitize_info(entry)
                        results.append({
                            "id": sanitized.get("id"),
                            "title": sanitized.get("title"),
                            "url": sanitized.get("webpage_url"),
                            "duration": sanitized.get("duration"),
                            "channel": sanitized.get("channel"),
                            "view_count": sanitized.get("view_count"),
                            "thumbnail": sanitized.get("thumbnail"),
                        })

            return self._success({
                "query": query,
                "results": results,
                "count": len(results)
            })
        except Exception as e:
            return self._error(str(e))


# Singleton instance
skill = YtdlpSkill()

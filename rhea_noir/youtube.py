"""
Rhea Noir - YouTube Video Ingestion Module
Fetch transcripts, chunk them, and store in memory for context.
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False


class YouTubeIngestor:
    """Ingest YouTube videos for Rhea Noir's knowledge."""
    
    def __init__(self, console=None):
        self.console = console
        self.transcript_api = YouTubeTranscriptApi if TRANSCRIPT_API_AVAILABLE else None
        
    def _log(self, message: str, style: str = ""):
        """Log message to console or print."""
        if self.console:
            self.console.print(f"[{style}]{message}[/{style}]" if style else message)
        else:
            print(message)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from various URL formats."""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_info(self, video_id: str) -> Dict:
        """Get video metadata using yt-dlp (more reliable than pytube)."""
        info = {
            "video_id": video_id,
            "title": f"Video {video_id}",
            "author": "Unknown",
            "length": 0,
            "description": ""
        }
        
        if YTDLP_AVAILABLE:
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'skip_download': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    video_info = ydl.extract_info(
                        f"https://www.youtube.com/watch?v={video_id}", 
                        download=False
                    )
                    info["title"] = video_info.get("title", info["title"])
                    info["author"] = video_info.get("uploader", video_info.get("channel", info["author"]))
                    info["length"] = video_info.get("duration", 0)
                    info["description"] = video_info.get("description", "")
            except Exception as e:
                self._log(f"⚠️ Could not fetch video info: {e}", "yellow")
        
        return info
    
    def fetch_transcript(self, video_id: str, languages: List[str] = None) -> Optional[List[Dict]]:
        """Fetch transcript from YouTube video using updated API."""
        if not TRANSCRIPT_API_AVAILABLE:
            self._log("❌ youtube-transcript-api not installed", "red")
            return None
            
        languages = languages or ['en', 'en-US', 'en-GB']
        
        try:
            # New API: create instance and use list() then fetch()
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            
            # Try to find transcript in preferred languages
            for transcript in transcript_list:
                if transcript.language_code in languages or transcript.language_code.split('-')[0] in ['en']:
                    return transcript.fetch()
            
            # If no preferred language, try first available or auto-generated
            try:
                generated = transcript_list.find_generated_transcript(languages)
                return generated.fetch()
            except:
                # Just get first available
                for transcript in transcript_list:
                    return transcript.fetch()
                    
        except Exception as e:
            self._log(f"⚠️ Could not fetch transcript: {e}", "yellow")
            return None
    
    def _normalize_entries(self, transcript) -> List[Dict]:
        """Convert FetchedTranscriptSnippet objects to dict format for compatibility."""
        normalized = []
        for entry in transcript:
            if isinstance(entry, dict):
                normalized.append(entry)
            else:
                # FetchedTranscriptSnippet has .text, .start, .duration attributes
                normalized.append({
                    "text": getattr(entry, 'text', str(entry)),
                    "start": getattr(entry, 'start', 0),
                    "duration": getattr(entry, 'duration', 0)
                })
        return normalized
    
    def chunk_transcript(
        self, 
        transcript: List, 
        chunk_duration: int = 120,  # 2 minutes per chunk
        overlap_duration: int = 10   # 10 second overlap
    ) -> List[Dict]:
        """Chunk transcript by time duration."""
        if not transcript:
            return []
        
        # Normalize entries to dicts
        transcript = self._normalize_entries(transcript)
            
        chunks = []
        current_chunk = {
            "text": "",
            "start_time": transcript[0]["start"],
            "end_time": 0,
            "entries": []
        }
        
        for entry in transcript:
            entry_end = entry["start"] + entry.get("duration", 0)
            
            # Check if we should start a new chunk
            if entry["start"] - current_chunk["start_time"] > chunk_duration:
                # Save current chunk
                current_chunk["end_time"] = entry["start"]
                current_chunk["text"] = " ".join([e["text"] for e in current_chunk["entries"]])
                chunks.append(current_chunk)
                
                # Start new chunk (with overlap)
                overlap_entries = [e for e in current_chunk["entries"] 
                                   if e["start"] > current_chunk["end_time"] - overlap_duration]
                current_chunk = {
                    "text": "",
                    "start_time": entry["start"] - overlap_duration if overlap_entries else entry["start"],
                    "end_time": 0,
                    "entries": overlap_entries
                }
            
            current_chunk["entries"].append(entry)
        
        # Add final chunk
        if current_chunk["entries"]:
            current_chunk["end_time"] = transcript[-1]["start"] + transcript[-1].get("duration", 0)
            current_chunk["text"] = " ".join([e["text"] for e in current_chunk["entries"]])
            chunks.append(current_chunk)
        
        return chunks
    
    def format_chunk_for_memory(
        self,
        chunk: Dict,
        video_info: Dict,
        source: str = "YouTube",
        categories: List[str] = None,
        chunk_index: int = 0
    ) -> Dict:
        """Format a chunk for Rhea's memory storage."""
        categories = categories or ["youtube", "video"]
        
        start_min = int(chunk['start_time'] // 60)
        start_sec = int(chunk['start_time'] % 60)
        end_min = int(chunk['end_time'] // 60)
        end_sec = int(chunk['end_time'] % 60)
        
        content = f"""Source: {source}
Video: {video_info.get('title', 'Unknown')}
Creator: {video_info.get('author', 'Unknown')}
Timestamp: {start_min}:{start_sec:02d} - {end_min}:{end_sec:02d}
Categories: {', '.join(categories)}

{chunk['text'].strip()}"""
        
        metadata = {
            "source": source,
            "video_id": video_info.get('video_id'),
            "video_title": video_info.get('title'),
            "author": video_info.get('author'),
            "chunk_index": chunk_index,
            "start_time": chunk['start_time'],
            "end_time": chunk['end_time'],
            "categories": categories,
            "ingested_at": datetime.now().isoformat()
        }
        
        return {
            "content": content,
            "metadata": metadata
        }
    
    def ingest_video(
        self,
        url_or_id: str,
        source: str = "YouTube",
        categories: List[str] = None,
        memory_store = None,
        dry_run: bool = False
    ) -> Tuple[bool, List[Dict]]:
        """
        Ingest a YouTube video into Rhea's memory.
        
        Args:
            url_or_id: YouTube URL or video ID
            source: Source name for metadata
            categories: Categories to tag content with
            memory_store: Memory store instance for saving
            dry_run: If True, preview without saving
            
        Returns:
            Tuple of (success, list of formatted chunks)
        """
        # Extract video ID
        video_id = self.extract_video_id(url_or_id)
        if not video_id:
            self._log(f"❌ Could not extract video ID from: {url_or_id}", "red")
            return False, []
        
        self._log(f"🎬 Processing video: {video_id}", "bright_magenta")
        
        # Get video info
        video_info = self.get_video_info(video_id)
        self._log(f"📺 Title: {video_info['title']}", "cyan")
        self._log(f"👤 Creator: {video_info['author']}", "cyan")
        
        # Fetch transcript
        self._log("📝 Fetching transcript...", "dim")
        transcript = self.fetch_transcript(video_id)
        
        if not transcript:
            self._log("❌ No transcript available for this video", "red")
            return False, []
        
        self._log(f"✓ Got {len(transcript)} transcript entries", "green")
        
        # Chunk transcript
        chunks = self.chunk_transcript(transcript)
        self._log(f"📦 Created {len(chunks)} chunks", "green")
        
        # Format chunks for memory
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            formatted = self.format_chunk_for_memory(
                chunk=chunk,
                video_info=video_info,
                source=source,
                categories=categories,
                chunk_index=i
            )
            formatted_chunks.append(formatted)
        
        if dry_run:
            self._log("🔍 DRY RUN - Preview only", "yellow")
            return True, formatted_chunks
        
        # Store in memory
        if memory_store:
            for fc in formatted_chunks:
                try:
                    memory_store.store(fc['content'], fc['metadata'])
                except Exception as e:
                    self._log(f"⚠️ Failed to store chunk: {e}", "yellow")
            
            self._log(f"✅ Ingested {len(formatted_chunks)} chunks into memory!", "bright_green")
        
        return True, formatted_chunks
    
    def ingest_from_file(
        self,
        transcript_path: Path,
        source: str = "YouTube",
        categories: List[str] = None,
        memory_store = None,
        dry_run: bool = False
    ) -> Tuple[bool, List[Dict]]:
        """Ingest from a saved transcript JSON file."""
        if not transcript_path.exists():
            self._log(f"❌ File not found: {transcript_path}", "red")
            return False, []
        
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            video_info = {
                "video_id": data.get('video_id', transcript_path.stem),
                "title": data.get('title', 'Unknown'),
                "author": data.get('author', data.get('guest', 'Unknown')),
                "length": data.get('length', 0)
            }
            
            chunks = data.get('chunks', [])
            if not chunks and 'transcript' in data:
                # Raw transcript format
                chunks = self.chunk_transcript(data['transcript'])
            
            formatted_chunks = []
            for i, chunk in enumerate(chunks):
                formatted = self.format_chunk_for_memory(
                    chunk=chunk,
                    video_info=video_info,
                    source=source,
                    categories=categories,
                    chunk_index=i
                )
                formatted_chunks.append(formatted)
            
            if not dry_run and memory_store:
                for fc in formatted_chunks:
                    memory_store.store(fc['content'], fc['metadata'])
                self._log(f"✅ Ingested {len(formatted_chunks)} chunks!", "bright_green")
            
            return True, formatted_chunks
            
        except Exception as e:
            self._log(f"❌ Failed to ingest file: {e}", "red")
            return False, []


# CLI command handlers
def cmd_youtube_ingest(cli, args: str) -> str:
    """Handle /youtube command to ingest a video."""
    if not args.strip():
        return """📺 **YouTube Ingestion**

Usage:
  `/youtube <url>` - Ingest video transcript
  `/youtube <url> --source "Podcast Name"`
  `/youtube <url> --dry-run` - Preview without saving

Examples:
  `/youtube https://youtube.com/watch?v=abc123`
  `/youtube dQw4w9WgXcQ --source "Music Video"`
"""
    
    # Parse arguments
    parts = args.split()
    url_or_id = parts[0]
    
    source = "YouTube"
    dry_run = "--dry-run" in args or "-n" in args
    
    if "--source" in args:
        try:
            idx = parts.index("--source")
            source = parts[idx + 1].strip('"\'')
        except:
            pass
    
    # Create ingestor
    ingestor = YouTubeIngestor(console=cli.console)
    
    # Get memory store
    memory_store = getattr(cli, 'short_term_memory', None)
    
    success, chunks = ingestor.ingest_video(
        url_or_id=url_or_id,
        source=source,
        memory_store=memory_store,
        dry_run=dry_run
    )
    
    if success:
        if dry_run:
            return f"✅ Would ingest {len(chunks)} chunks (dry run)"
        return f"✅ Ingested {len(chunks)} chunks from video"
    else:
        return "❌ Failed to ingest video. Check if transcript is available."

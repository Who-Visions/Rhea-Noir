import os
from google import genai
from google.genai import types
from typing import Optional, Dict, Tuple
from models.veilverse import VeilEntity, VeilVerseCategory, UniverseEra, RenderStatus, VeilLore
from services.notion import NotionService
import json
import asyncio
import yt_dlp

class IngestorService:
    """
    Intelligent Ingestion for Rhea.
    Uses Gemini (Vertex AI) to parse unstructured text into VeilVerse Entities.
    Supports YouTube URLs via yt-dlp.
    """
    
    def __init__(self):
        # Vertex AI Configuration
        # User requested Vertex AI Auth (ADC) without API Key
        self.project_id = "rhea-noir"
        self.location = "global" # Preview models are Global 
        
        try:
            print(f"🧠 Rhea Ingestor: Initializing Vertex AI Client ({self.project_id})...")
            # Official docs pattern for global endpoint (preview models)
            # https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations
            self.client = genai.Client(
                vertexai=True, 
                project=self.project_id, 
                location='global'
            )
            self.model_id = "gemini-3-flash-preview" 
 
        except Exception as e:
            print(f"⚠️ Warning: Vertex AI Init Failed: {e}")
            self.client = None
            
        self.notion = NotionService()

    async def ingest_transcript(self, text: str, hint: str = "") -> bool:
        """
        Analyzes transcript and pushes to Notion.
        If 'text' is a URL, it fetches the transcript first.
        """
        print("🧠 Rhea Ingestor: analyzing input...")
        
        content_to_analyze = text
        source_meta = ""

        # Check for URL
        # Check for URL
        final_content_for_notion = text
        llm_input = text

        if text.startswith("http"):
            print(f"   Detected URL: {text}")
            fetched_data = await self._fetch_transcript_from_url(text)
            if fetched_data:
                title, desc, transcript = fetched_data
                # We save the fetched text to Notion
                final_content_for_notion = f"Title: {title}\nDescription: {desc}\n\nTranscript:\n{transcript}\nSource: {text}"
                # We pass the fetched content (Text) to the LLM for analysis.
                # This bypasses the Native Video Analysis (which requires GCS URI) and uses the transcript we just got.
                llm_input = final_content_for_notion 
            else:
                print("❌ Failed to fetch transcript from URL.")
                return False

        else:
            # Handle Raw Text Input
            # Detect if likely non-English (simple heuristic)
            non_english_indicators = ['é', 'è', 'ê', 'ë', 'à', 'â', 'ô', 'ù', 'û', 'ç', 'ñ', 'ü', 'ö', 'ä', 'ß']
            if any(char in text for char in non_english_indicators):
                print("   🌐 Detected non-English text input, translating...")
                translated = await self._translate_text(text, source_lang="auto", target_lang="en")
                if translated and translated != text:
                    final_content_for_notion = f"[TRANSLATED FROM ORIGINAL]\n\n{translated}\n\n---\n[ORIGINAL TRANSCRIPT]\n{text}"
                    llm_input = final_content_for_notion
                else:
                    print("   ⚠️ Translation skipped or failed.")

        entity = await self._analyze_with_llm(llm_input, hint)
        
        if not entity:
            print("❌ Analysis failed.")
            return False
            
        print(f"   Identified: {entity.name} [{entity.category}]")

        # Generate Deep Lore Analysis (Rhea's Thoughts)
        print("🧠 Rhea: Generating Deep Lore Analysis...")
        analysis = await self._generate_lore_analysis(llm_input, entity)
        
        # Prepend Analysis to Content
        enhanced_content = f"# 🧠 Rhea's Lore Analysis\n\n{analysis}\n\n---\n\n{final_content_for_notion}"
        
        # Use the fetched transcript content for Notion
        success = await self.notion.create_entity(entity, content=enhanced_content)
        await self.notion.close()
        return success

    async def _generate_lore_analysis(self, text: str, entity: VeilEntity) -> str:
        """
        Generates a creative world-building analysis of the content.
        """
        if not self.client: return "Analysis Unavailable (No Client)"
        
        prompt = f"""You are Rhea, the Archivist of the VeilVerse. 
The user has provided a transcript for: "{entity.name}" ({entity.category}).

Analyze this content and generate a Markdown report for the creative writer.

# Structure matches the VeilVerse needs:

1. **Core Concept Extraction**
   - Bullet points of the most "game-able" or narrative-rich mechanics/ideas found in the text.
   - Ignore generic fluff. Focus on unique specific details (e.g. specific chemical names, specific depths, specific star alignments).

2. **VeilVerse Resonance**
   - How does this map to existing concepts?
   - Connect it to: The Veil (Memory Layer), The Syndicate (Cognitive Entrapment), The Shadow Dwellers (Genetic Memory), or Mars (Cyclical Collapse).
   - Use VeilVerse terminology.

3. **Potential Hooks / Story Beats**
   - 2-3 specific ideas for how this could appear in a scene.
   - Example: "A Shadow Dweller discovers a buried helical coil that hums when they approach."

4. **Archivist's Classification**
   - One sentence on the "Canon Reliability". 
   - E.g. "This is Earth-based pseudoscience, but valid as 'Pre-Collapse' mythology." or "Useful structural references for Mars underground."

Keep it concise but dense with creative value.
"""
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=[text[:50000], prompt] # Increased context limit for analysis
            )
            return response.text if response.text else "(Analysis Empty)"
        except Exception as e:
            print(f"⚠️ Analysis generation failed: {e}")
            return "(Analysis Failed)"

    async def _fetch_transcript_from_url(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        Uses yt-dlp for metadata and youtube-transcript-api for actual transcript.
        Returns (Title, Description, TranscriptText).
        """
        print("   Running yt-dlp for metadata...")
        
        # Extract video ID from URL
        import re
        video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
        video_id = video_id_match.group(1) if video_id_match else None
        
        def run_ytdlp():
            ydl_opts = {
                'skip_download': True,
                'quiet': True,
                'noplaylist': True,
                'no_warnings': True,
                'nocheckcertificate': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    return info
                except Exception as e:
                    print(f"yt-dlp error: {e}")
                    return None

        # Run blocking yt-dlp in a thread
        info = await asyncio.to_thread(run_ytdlp)
        
        if not info:
            return None
            
        title = info.get('title', 'Unknown Title')
        description = info.get('description', '')
        
        # Fetch transcript - Strategy Priority:
        # 1. youtube-transcript-api (Free, faster, existing captions)
        # 2. Gemini 3 Native Audio Transcription (Fallback: Expensive, high quality)
        
        transcript_text = ""
        
        # Strategy 1: youtube-transcript-api
        if not transcript_text and video_id:
            print(f"   Fetching transcript for video ID: {video_id}...")
            
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                api = YouTubeTranscriptApi()
                
                # First, try to list available transcripts
                try:
                    transcript_list_obj = await asyncio.to_thread(
                        lambda: api.list(video_id)
                    )
                    # Get all available languages
                    available_langs = [t.language_code for t in transcript_list_obj]
                    print(f"   Available transcript languages: {available_langs}")
                    
                    # Try to get transcript (prefer English, but accept any)
                    transcript_list = None
                    for lang in ['en', 'en-US', 'en-GB'] + available_langs:
                        try:
                            transcript_list = await asyncio.to_thread(
                                lambda l=lang: api.fetch(video_id, languages=[l])
                            )
                            print(f"   Fetched transcript in language: {lang}")
                            break
                        except Exception:
                            continue
                    
                    if transcript_list:
                        transcript_text = " ".join([entry.text for entry in transcript_list])
                        print(f"   ✅ Fetched {len(transcript_list)} transcript segments.")
                    else:
                        raise Exception("No transcript found in any language")
                        
                except Exception as list_err:
                    # Fallback: try simple fetch without language filter
                    print(f"   Trying simple fetch: {list_err}")
                    transcript_list = await asyncio.to_thread(
                        lambda: api.fetch(video_id)
                    )
                    transcript_text = " ".join([entry.text for entry in transcript_list])
                    print(f"   ✅ Fetched {len(transcript_list)} transcript segments (youtube-transcript-api).")
                    
            except Exception as e:
                print(f"   ⚠️ youtube-transcript-api failed: {e}")
                transcript_text = ""

        # Strategy 2: Gemini 3 Native Audio Transcription (Fallback)
        if not transcript_text and self.client:
            print(f"   🎤 Fallback: Gemini 3 Native Audio Transcription (No captions found)...")
            transcript_text = await self._transcribe_with_gemini(url)
            
            if not transcript_text.startswith("("):
                print(f"   ✅ Gemini transcription successful!")
            else:
                print(f"   ❌ Gemini fallback also failed.")
                transcript_text = ""
        
        if not transcript_text:
            transcript_text = "(Transcript unavailable)"
        # Skip this if Gemini has already provided a translation (indicated by [TRANSLATION] marker)
        if transcript_text and not transcript_text.startswith("(") and "[TRANSLATION]" not in transcript_text:
            # Detect if likely non-English (simple heuristic)
            non_english_indicators = ['é', 'è', 'ê', 'ë', 'à', 'â', 'ô', 'ù', 'û', 'ç', 'ñ', 'ü', 'ö', 'ä', 'ß']
            if any(char in transcript_text for char in non_english_indicators):
                print("   🌐 Detected non-English transcript, translating...")
                translated = await self._translate_text(transcript_text, source_lang="auto", target_lang="en")
                if translated != transcript_text:
                    transcript_text = f"[TRANSLATED FROM ORIGINAL]\n\n{translated}\n\n---\n[ORIGINAL TRANSCRIPT]\n{transcript_text[:2000]}..."
        
        return title, description, transcript_text
    
    async def _transcribe_with_gemini(self, url: str) -> str:
        """
        Uses Gemini 3 to transcribe audio from a YouTube video.
        Gemini can understand and transcribe speech in multiple languages.
        """
        try:
            video_part = types.Part.from_uri(file_uri=url, mime_type="video/mp4")
            
            prompt = """Watch this video and transcribe ALL spoken words verbatim.

RULES FOR TRANSLATION:
1. If the speech is in ENGLISH:
   - Provide the verbatim [ENGLISH TRANSCRIPT]
   - Provide a [HAITIAN CREOLE TRANSLATION]

2. If the speech is in HAITIAN CREOLE (or other foreign language):
   - Provide the verbatim [ORIGINAL TRANSCRIPT]
   - Provide an [ENGLISH TRANSLATION]

Format:
[ORIGINAL LANGUAGE: language_name]
[Original transcription here]

[TRANSLATION]
[Translated text here]"""

            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=[video_part, prompt]
            )
            
            if response.text:
                print(f"   ✅ Gemini transcription complete ({len(response.text)} chars)")
                return response.text
            else:
                return "(Gemini transcription returned empty)"
                
        except Exception as e:
            print(f"   ❌ Gemini transcription failed: {e}")
            return f"(Transcription failed: {e})"

    async def _translate_text(self, text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
        """
        Translates text using Vertex AI Translation LLM.
        Model: cloud-translate-text (Translation LLM powered by Gemini)
        """
        if not text or len(text.strip()) < 10:
            return text
            
        print(f"   🌐 Translating from {source_lang} to {target_lang}...")
        
        try:
            import requests
            import google.auth
            import google.auth.transport.requests
            
            # Get ADC credentials
            credentials, project = google.auth.default()
            auth_req = google.auth.transport.requests.Request()
            credentials.refresh(auth_req)
            
            # Translation LLM endpoint
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-central1/publishers/google/models/cloud-translate-text:predict"
            
            headers = {
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "instances": [{
                    "source_language_code": source_lang if source_lang != "auto" else "",
                    "target_language_code": target_lang,
                    "contents": [text[:5000]],  # Limit for API
                    "mimeType": "text/plain",
                    "model": f"projects/{self.project_id}/locations/us-central1/models/general/translation-llm"
                }]
            }
            
            response = await asyncio.to_thread(
                lambda: requests.post(url, headers=headers, json=payload)
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result.get("predictions", [{}])[0].get("translations", [{}])[0].get("translatedText", "")
                if translated:
                    print(f"   ✅ Translation complete ({len(translated)} chars)")
                    return translated
            else:
                print(f"   ⚠️ Translation API error: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"   ⚠️ Translation failed: {e}")
        
        return text  # Return original if translation fails

    async def _analyze_with_llm(self, text: str, hint: str) -> Optional[VeilEntity]:
        """Uses Vertex AI to analyze text or YouTube URL and extract a VeilEntity."""
        if not self.client:
            print("❌ No Vertex AI Client available.")
            return None

        print("🧠 Rhea Ingestor: analyzing input...")
        
        # Prepare contents for the LLM
        contents = []
        
        # Check if input is a YouTube URL to use Native Video Analysis
        # Only treat as video if it's a short string starting with http (strict URL check)
        if (text.strip().startswith("http") and len(text) < 500) and ("youtube.com" in text or "youtu.be" in text):
            print(f"   Detected YouTube URL: {text}")
            print("   Requesting Native Video Analysis (Gemini 3)...")
            try:
                video_part = types.Part.from_uri(file_uri=text, mime_type="video/mp4")
                contents.append(video_part)
            except Exception as e:
                print(f"❌ Failed to create Video Part: {e}")
                contents.append(text)
        else:
            contents.append(text[:1000000])

        # Add the prompt
        prompt_text = f"""You are Rhea, the Archivist of the VeilVerse.
Analyze this content (Video or Text) and extract a VeilEntity.

User Hint: {hint}

Output strictly in JSON."""
        contents.append(prompt_text)

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=VeilEntity,
                )
            )
            
            if not response.parsed:
                print(f"❌ LLM Error: No parsed JSON. Text: {response.text}")
                return None
            
            return response.parsed

        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return None
            


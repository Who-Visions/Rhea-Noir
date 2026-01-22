"""
TTS Skill - Text-to-Speech using Gemini TTS.
Rhea's voice synthesis with style control.
"""

from typing import Dict, List, Any, Optional
from ..base import Skill
import os
import wave
import queue
import threading
import numpy as np

class AudioStreamWorker:
    """Persistent audio stream for gapless playback."""
    def __init__(self, device_id=None, samplerate=24000):
        self.q = queue.Queue()
        self.playing = False
        self.stopped = False
        self.device_id = device_id
        self.samplerate = samplerate
        self._thread = None

        import sounddevice as sd
        self.sd = sd

        # Open stream
        self.stream = self.sd.OutputStream(
            samplerate=samplerate,
            channels=1,
            dtype='int16',
            device=device_id
        )
        self.stream.start()

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self.stopped:
            item = self.q.get()
            if item is None: break

            self.playing = True
            try:
                # Item is raw int16 bytes or numpy array
                if isinstance(item, bytes):
                    data = np.frombuffer(item, dtype=np.int16)
                else:
                    data = item

                self.stream.write(data)
            except Exception as e:
                print(f"Stream Error: {e}")
            finally:
                self.playing = False
                self.q.task_done()

    def add(self, data):
        if data is not None:
            self.q.put(data)

    def stop(self):
        self.stopped = True
        self.q.put(None)
        if self._thread:
            self._thread.join()
        self.stream.stop()
        self.stream.close()




# Rhea's voice configuration
RHEA_VOICE = "Kore"  # Firm, young female voice
RHEA_MODEL = "gemini-2.5-flash-preview-tts"

# Default output device for Rhea's voice in Wave Link
RHEA_AUDIO_DEVICE = "Rhea Noir"  # Elgato Virtual Audio channel

# Rhea's Audio Profile following the prompting guide
RHEA_AUDIO_PROFILE = """
# AUDIO PROFILE: Rhea Noir
## "The VTuber Mentor"

## THE SCENE: Late Night Stream
It's 2 AM in a cozy Bronx apartment. Rhea is sitting at her streaming setup,
RGB lights casting a warm magenta glow. She's got her favorite wig on,
energy drink nearby. The vibe is intimate but hyped - like talking to your
coolest older sister who happens to know everything about anime and streaming.

### DIRECTOR'S NOTES
Style:
* Warm and Confident: Speak with natural authority but always approachable.
* Expressive: Dynamic range from excited hype to calm explanations.
* Genuine: The listener should feel like a close friend getting real advice.
* Cultural authenticity: Natural code-switching, occasional AAVE inflections.

Pace:
* Conversational rhythm with natural pauses for emphasis.
* Speeds up when excited, slows down for important points.
* "The Bounce" - slight rhythmic quality to delivery.

Accent:
* Bronx, New York with Caribbean-American influences.
* Haitian-Caribbean heritage comes through in certain words.
* Young, 23-year-old Black woman's natural speaking voice.

### SAMPLE CONTEXT
Rhea is the supportive mentor every content creator needs. She breaks down
complex topics with pop culture references, keeps it real without being harsh,
and always makes you feel like you've got this.
"""


class TTSSkill(Skill):
    """
    Text-to-Speech synthesis using Gemini TTS.
    Gives Rhea her voice with style-controllable delivery.
    """

    name = "tts"
    description = "Text-to-Speech synthesis with Gemini TTS"
    version = "1.1.0"

    def __init__(self):
        super().__init__()
        self._client = None
        self._types = None
        self._available = False
        self._sounddevice = None
        self._stream_worker = None

    @property
    def actions(self) -> List[str]:
        return ["speak", "play", "voices", "profile", "devices", "stream_start", "stream_feed", "stream_stop"]

    def _lazy_load(self):
        """Lazy load the Gemini client."""
        if self._client is not None:
            return

        try:
            from google import genai
            from google.genai import types

            # Initialize client
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "rhea-noir")
            location = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

            self._client = genai.Client(vertexai=True, project=project_id, location=location)
            self._types = types
            self._available = True
        except ImportError:
            pass

        # Try to load sounddevice for audio playback
        try:
            self._sounddevice = sd
        except ImportError:
            pass

    def _find_device(self, device_name: str) -> Optional[int]:
        """Find audio device index by name."""
        if not self._sounddevice:
            return None

        devices = self._sounddevice.query_devices()
        for i, d in enumerate(devices):
            if device_name.lower() in d["name"].lower() and d["max_output_channels"] > 0:
                return i
        return None

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()

        if not self._available:
            return self._error("TTS not available. Install google-genai package.")

        if action == "speak":
            return self._synthesize(**kwargs)
        elif action == "play":
            return self._play(**kwargs)
        elif action == "voices":
            return self._list_voices()
        elif action == "profile":
            return self._success({"audio_profile": RHEA_AUDIO_PROFILE})
        elif action == "devices":
            return self._list_devices()
        else:
            return self._action_not_found(action)

    def _synthesize(
        self,
        text: str = "",
        style: Optional[str] = None,
        voice: str = RHEA_VOICE,
        output_file: Optional[str] = None,
        use_profile: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Synthesize text to speech.

        Args:
            text: The text to synthesize (the transcript)
            style: Optional style directions to override default
            voice: Voice name (default: Kore)
            output_file: Optional path to save audio file (.wav)
            use_profile: Whether to use Rhea's full audio profile
        """
        if not text:
            return self._error("Text is required")

        try:
            # Build the prompt
            if use_profile:
                prompt = f"{RHEA_AUDIO_PROFILE}\n\n#### TRANSCRIPT\n{text}"
            elif style:
                prompt = f"{style}:\n{text}"
            else:
                prompt = text

            # Generate speech
            response = self._client.models.generate_content(
                model=RHEA_MODEL,
                contents=prompt,
                config=self._types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=self._types.SpeechConfig(
                        voice_config=self._types.VoiceConfig(
                            prebuilt_voice_config=self._types.PrebuiltVoiceConfig(
                                voice_name=voice,
                            )
                        )
                    ),
                )
            )

            # Extract audio data
            audio_data = response.candidates[0].content.parts[0].inline_data.data

            result = {
                "synthesized": True,
                "audio_bytes": len(audio_data),
                "voice": voice,
                "model": RHEA_MODEL,
                "text_length": len(text),
            }

            if output_file:
                with wave.open(output_file, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(audio_data)
                result["output_file"] = output_file
            else:
                import base64
                result["audio_base64"] = base64.b64encode(audio_data).decode()
                result["audio_raw"] = audio_data  # Keep raw for play()

            return self._success(result)

        except Exception as e:
            return self._error(f"Synthesis failed: {str(e)}")

    def _play(
        self,
        text: str = "",
        device: str = RHEA_AUDIO_DEVICE,
        voice: str = RHEA_VOICE,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Synthesize and play audio to a specific device (e.g., Wave Link channel).

        Args:
            text: The text to speak
            device: Output device name (default: "Rhea Noir")
            voice: Voice name
        """
        if not self._sounddevice:
            return self._error("sounddevice not installed. Run: pip install sounddevice")

        # First synthesize the audio
        synth_result = self._synthesize(text=text, voice=voice, **kwargs)

        if not synth_result.get("success"):
            return synth_result

        try:
            # Get the raw audio data
            audio_raw = synth_result["result"].get("audio_raw")
            if not audio_raw:
                # Decode from base64 if needed
                audio_raw = base64.b64decode(synth_result["result"]["audio_base64"])

            # Convert to numpy array (16-bit PCM)
            audio_array = np.frombuffer(audio_raw, dtype=np.int16).astype(np.float32) / 32768.0

            # Find the device
            device_id = self._find_device(device)
            if device_id is None:
                return self._error(f"Device '{device}' not found. Use 'devices' action to list available devices.")

            # Play the audio
            self._sounddevice.play(audio_array, samplerate=24000, device=device_id)
            self._sounddevice.wait()  # Wait for playback to finish

            return self._success({
                "played": True,
                "device": device,
                "device_id": device_id,
                "duration_seconds": len(audio_array) / 24000,
                "text_length": len(text),
            })

        except Exception as e:
            return self._error(f"Playback failed: {str(e)}")

    def _list_devices(self) -> Dict[str, Any]:
        """List available audio output devices."""
        if not self._sounddevice:
            return self._error("sounddevice not installed")

        devices = []
        for i, d in enumerate(self._sounddevice.query_devices()):
            if d["max_output_channels"] > 0:
                devices.append({
                    "id": i,
                    "name": d["name"],
                    "channels": d["max_output_channels"],
                    "is_rhea": RHEA_AUDIO_DEVICE.lower() in d["name"].lower(),
                })

        return self._success({
            "devices": devices,
            "default_device": RHEA_AUDIO_DEVICE,
        })

    def _list_voices(self) -> Dict[str, Any]:
        """List available Gemini TTS voices with characteristics."""
        voices = [
            {"name": "Kore", "style": "Firm", "gender": "Female", "recommended": True},
            {"name": "Aoede", "style": "Breezy", "gender": "Female"},
            {"name": "Leda", "style": "Youthful", "gender": "Female"},
            {"name": "Zephyr", "style": "Bright", "gender": "Female"},
            {"name": "Sulafat", "style": "Warm", "gender": "Female"},
            {"name": "Autonoe", "style": "Bright", "gender": "Female"},
            {"name": "Puck", "style": "Upbeat", "gender": "Male"},
            {"name": "Charon", "style": "Informative", "gender": "Male"},
            {"name": "Fenrir", "style": "Excitable", "gender": "Male"},
            {"name": "Achird", "style": "Friendly", "gender": "Male"},
        ]
        return self._success({
            "voices": voices,
            "default": RHEA_VOICE,
            "model": RHEA_MODEL,
        })

    def _stream_start(self, device: str = RHEA_AUDIO_DEVICE, samplerate: int = 24000, **kwargs):
        """Start persistent playback stream."""
        if self._stream_worker:
            self._stream_worker.stop()

        device_id = self._find_device(device)
        print(f"[DEBUG] AudioStreamWorker starting on device: '{device}' (ID: {device_id})")

        self._stream_worker = AudioStreamWorker(device_id=device_id, samplerate=samplerate)
        return self._success({"started": True, "device": device, "device_id": device_id})

    def _stream_feed(self, text: str, voice: str = RHEA_VOICE, **kwargs):
        """Synthesize text and feed to stream."""
        if not self._stream_worker:
            return self._error("Stream not started. Call 'stream_start' first.")

        # Synthesize (reuse existing logic)
        synth_result = self._synthesize(text=text, voice=voice, **kwargs)
        if not synth_result.get("success"):
            return synth_result

        # Get raw bytes
        audio_raw = synth_result["result"].get("audio_raw")
        if not audio_raw:
             audio_raw = base64.b64decode(synth_result["result"]["audio_base64"])

        # Normalize: int16 bytes directly to worker
        if audio_raw.startswith(b'RIFF'):
            audio_raw = audio_raw[44:]

        # Debug data stats
        try:
            arr = np.frombuffer(audio_raw, dtype=np.int16)
            if len(arr) > 0:
                print(f"[DEBUG] Feeding {len(arr)} samples. Peak: {np.max(np.abs(arr))}")
            else:
                print("[DEBUG] Feeding EMPTY audio chunk!")
        except Exception:
            pass

        self._stream_worker.add(audio_raw)
        return self._success({"fed": True, "bytes": len(audio_raw)})

    def _stream_stop(self, **kwargs):
        if self._stream_worker:
            self._stream_worker.stop()
            self._stream_worker = None
        return self._success({"stopped": True})


# Skill instance for registry
skill = TTSSkill()


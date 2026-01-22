"""
Audio Skill - Audio understanding with Faster Whisper + Gemini.
Local transcription, analysis, summarization, and live recording.
"""

import base64
import os
import queue
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from ..base import Skill


# Supported audio MIME types
AUDIO_MIME_TYPES = {
    ".wav": "audio/wav",
    ".mp3": "audio/mp3",
    ".aiff": "audio/aiff",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
}

# Default input device for mic capture (Chat Mix in Wave Link)
DEFAULT_INPUT_DEVICE = "Chat Mix"

# Whisper model config
WHISPER_MODEL = "base.en"  # Options: tiny.en, base.en, small.en, medium.en, large-v3


class AudioSkill(Skill):
    """
    Audio understanding with Faster Whisper (local) + Gemini (cloud).
    Transcribe, analyze, summarize, and record audio content.
    """

    name = "audio"
    description = "Audio understanding - fast local transcription + cloud analysis"
    version = "1.2.0"

    def __init__(self):
        super().__init__()
        self._client = None
        self._types = None
        self._available = False
        self._sounddevice = None
        self._whisper_model = None
        self._whisper_available = False

    @property
    def actions(self) -> List[str]:
        return ["transcribe", "analyze", "summarize", "record", "listen", "devices"]

    def _lazy_load(self):
        """Lazy load the Gemini client and Whisper model."""
        if self._client is not None:
            return

        try:
            from google import genai
            from google.genai import types

            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "rhea-noir")
            location = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

            self._client = genai.Client(vertexai=True, project=project_id, location=location)
            self._types = types
            self._available = True
        except ImportError:
            pass

        # Try to load sounddevice for recording
        try:
            import sounddevice as sd
            self._sounddevice = sd
        except ImportError:
            pass

        # Try to load Faster Whisper for local transcription
        try:
            from faster_whisper import WhisperModel
            self._whisper_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
            self._whisper_available = True
        except ImportError:
            pass
        except Exception:
            pass  # Model download issues etc


    def _find_device(self, device_name: str, input_device: bool = True) -> Optional[int]:
        """Find audio device index by name."""
        if not self._sounddevice:
            return None

        devices = self._sounddevice.query_devices()
        for i, d in enumerate(devices):
            channel_key = "max_input_channels" if input_device else "max_output_channels"
            if device_name.lower() in d["name"].lower() and d[channel_key] > 0:
                return i
        return None

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()

        if not self._available:
            return self._error("Audio skill not available. Install google-genai package.")

        if action == "transcribe":
            return self._transcribe(**kwargs)
        elif action == "analyze":
            return self._analyze(**kwargs)
        elif action == "summarize":
            return self._summarize(**kwargs)
        elif action == "record":
            return self._record(**kwargs)
        elif action == "listen":
            return self._listen(**kwargs)
        elif action == "devices":
            return self._list_devices()
        else:
            return self._action_not_found(action)

    def _get_audio_data(
        self,
        audio_file: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        audio_base64: Optional[str] = None,
    ) -> tuple:
        """Get audio data and MIME type from various sources."""
        if audio_file:
            path = Path(audio_file)
            if not path.exists():
                return None, None, f"File not found: {audio_file}"

            mime_type = AUDIO_MIME_TYPES.get(path.suffix.lower())
            if not mime_type:
                return None, None, f"Unsupported audio format: {path.suffix}"

            with open(path, "rb") as f:
                data = f.read()
            return data, mime_type, None

        elif audio_bytes:
            return audio_bytes, "audio/wav", None

        elif audio_base64:
            data = base64.b64decode(audio_base64)
            return data, "audio/wav", None

        return None, None, "No audio data provided"

    def _pcm_to_wav(self, pcm_data: bytes, samplerate: int = 24000, channels: int = 1) -> bytes:
        """Convert raw PCM data to WAV format with headers."""
        import io
        import wave

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(samplerate)
            wf.writeframes(pcm_data)

        return buffer.getvalue()

    def _record_vad(
        self,
        max_duration: float = 15.0,
        device: str = None,
        threshold: float = 0.015,
        silence_duration: float = 0.8,
        samplerate: int = 24000,
        **kwargs
    ) -> Dict[str, Any]:
        """Record with Voice Activity Detection (VAD)."""
        if not self._sounddevice:
            return self._error("sounddevice not installed")

        device_id = self._find_device(device, input_device=True)
        if device_id is None:
            return self._error(f"Device '{device}' not found")

        q = queue.Queue()
        def callback(indata, frames, time, status):
            q.put(indata.copy())

        audio_data = []
        speech_active = False
        silence_start = None
        start_time = time.time()
        blocksize = int(samplerate * 0.1) # 100ms

        try:
            with self._sounddevice.InputStream(
                samplerate=samplerate, channels=1, callback=callback,
                device=device_id, blocksize=blocksize, dtype='int16'
            ):
                while True:
                    if time.time() - start_time > max_duration:
                        break
                    try:
                        data = q.get(timeout=0.1)
                        audio_data.append(data)

                        # RMS calculation (normalize int16 to -1..1 float)
                        data_float = data.astype(np.float32) / 32768.0
                        rms = np.sqrt(np.mean(data_float**2))

                        if rms > threshold:
                            speech_active = True
                            silence_start = None
                        elif speech_active:
                            if silence_start is None:
                                silence_start = time.time()
                            elif time.time() - silence_start > silence_duration:
                                break # detected silence end of turn
                    except queue.Empty:
                        continue

        except Exception as e:
            return self._error(f"VAD Recording failed: {e}")

        if not audio_data:
            return self._error("No audio recorded")

        # Combine chunks
        pcm_bytes = b"".join([ch.tobytes() for ch in audio_data])
        wav_bytes = self._pcm_to_wav(pcm_bytes, samplerate, 1)

        return self._success({
            "recorded": True,
            "duration_seconds": time.time() - start_time,
            "device": device,
            "audio_bytes": len(wav_bytes),
            "samplerate": samplerate,
            "audio_raw": wav_bytes,
            "vad": True
        })

    def _record(
        self,
        duration: float = 5.0,
        device: str = DEFAULT_INPUT_DEVICE,
        output_file: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Record audio from microphone.

        Args:
            duration: Recording duration in seconds (default: 5)
            device: Input device name (default: "Chat Mix")
            output_file: Optional path to save WAV file
        """
        if not self._sounddevice:
            return self._error("sounddevice not installed. Run: pip install sounddevice")

        if kwargs.get("vad"):
            return self._record_vad(max_duration=duration, device=device, **kwargs)

        try:
            device_id = self._find_device(device, input_device=True)

            if device_id is None:
                return self._error(f"Input device '{device}' not found. Use 'devices' action to list.")

            samplerate = 24000
            channels = 1

            # Record audio
            recording = self._sounddevice.rec(
                int(duration * samplerate),
                samplerate=samplerate,
                channels=channels,
                dtype=np.int16,
                device=device_id
            )
            self._sounddevice.wait()

            # Convert to PCM bytes
            pcm_bytes = recording.tobytes()

            # Convert to WAV format with headers
            wav_bytes = self._pcm_to_wav(pcm_bytes, samplerate, channels)

            result = {
                "recorded": True,
                "duration_seconds": duration,
                "device": device,
                "device_id": device_id,
                "audio_bytes": len(wav_bytes),
                "samplerate": samplerate,
            }

            if output_file:
                with open(output_file, "wb") as f:
                    f.write(wav_bytes)
                result["output_file"] = output_file
            else:
                result["audio_base64"] = base64.b64encode(wav_bytes).decode()
                result["audio_raw"] = wav_bytes  # Now includes WAV headers

            return self._success(result)

        except Exception as e:
            return self._error(f"Recording failed: {str(e)}")

    def _listen(
        self,
        duration: float = 5.0,
        device: str = DEFAULT_INPUT_DEVICE,
        vad: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Record and transcribe audio.

        Args:
            duration: Recording duration (or max duration if VAD)
            device: Input device name
            vad: Enable Voice Activity Detection
        """
        # First record
        record_result = self._record(duration=duration, device=device, vad=vad, **kwargs)
        if not record_result.get("success"):
            return record_result

        # Then transcribe - audio_raw now has proper WAV headers
        audio_bytes = record_result["result"].get("audio_raw")
        if not audio_bytes:
            audio_bytes = base64.b64decode(record_result["result"]["audio_base64"])

        return self._transcribe(audio_bytes=audio_bytes)

    def _list_devices(self) -> Dict[str, Any]:
        """List available audio input devices."""
        if not self._sounddevice:
            return self._error("sounddevice not installed")

        devices = []
        for i, d in enumerate(self._sounddevice.query_devices()):
            if d["max_input_channels"] > 0:
                devices.append({
                    "id": i,
                    "name": d["name"],
                    "channels": d["max_input_channels"],
                    "is_default": DEFAULT_INPUT_DEVICE.lower() in d["name"].lower(),
                })

        return self._success({
            "devices": devices,
            "default_device": DEFAULT_INPUT_DEVICE,
        })

    def _transcribe(
        self,
        audio_file: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        audio_base64: Optional[str] = None,
        timestamps: Optional[str] = None,
        use_whisper: bool = True,  # Use local Whisper by default
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate transcript from audio.
        Uses Faster Whisper (local) by default, falls back to Gemini API.
        """
        data, mime_type, error = self._get_audio_data(audio_file, audio_bytes, audio_base64)
        if error:
            return self._error(error)

        # Try Faster Whisper first (much faster, local)
        if use_whisper and self._whisper_available and self._whisper_model:
            try:
                import tempfile

                # Write to temp file for Whisper
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(data)
                    tmp_path = tmp.name

                # Transcribe with Faster Whisper (optimized)
                segments, info = self._whisper_model.transcribe(
                    tmp_path,
                    beam_size=1,     # Latency optimization (was 5)
                    vad_filter=True,
                )

                # Collect transcript
                transcript = " ".join([segment.text.strip() for segment in segments])

                # Cleanup
                os.unlink(tmp_path)

                return self._success({
                    "transcript": transcript,
                    "audio_bytes": len(data),
                    "engine": "faster-whisper",
                    "language": info.language,
                    "duration": info.duration,
                })

            except Exception as e:
                # Fall back to Gemini
                pass

        # Fallback to Gemini API
        try:
            prompt = "Generate a transcript of the speech."
            if timestamps:
                prompt = f"Provide a transcript of the speech from {timestamps}."

            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    self._types.Part.from_bytes(data=data, mime_type=mime_type),
                ]
            )

            return self._success({
                "transcript": response.text,
                "audio_bytes": len(data),
                "engine": "gemini",
            })

        except Exception as e:
            return self._error(f"Transcription failed: {str(e)}")


    def _analyze(
        self,
        audio_file: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        audio_base64: Optional[str] = None,
        prompt: str = "Describe this audio clip in detail.",
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze audio content."""
        data, mime_type, error = self._get_audio_data(audio_file, audio_bytes, audio_base64)
        if error:
            return self._error(error)

        try:
            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    self._types.Part.from_bytes(data=data, mime_type=mime_type),
                ]
            )

            return self._success({
                "analysis": response.text,
                "prompt": prompt,
                "audio_bytes": len(data),
            })

        except Exception as e:
            return self._error(f"Analysis failed: {str(e)}")

    def _summarize(
        self,
        audio_file: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        audio_base64: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Summarize audio content."""
        return self._analyze(
            audio_file=audio_file,
            audio_bytes=audio_bytes,
            audio_base64=audio_base64,
            prompt="Provide a concise summary of this audio content. Include key points, speakers, and main topics discussed.",
            **kwargs
        )


# Skill instance for registry
skill = AudioSkill()


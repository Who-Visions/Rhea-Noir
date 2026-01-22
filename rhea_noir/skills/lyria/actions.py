"""
Lyria RealTime Music Generation Skill for Rhea-Noir
AI-powered real-time music generation and control
"""
import asyncio
from typing import Optional, Dict, Any, List


class LyriaSkill:
    """Skill for Lyria RealTime music generation."""

    name = "lyria"
    version = "1.0.0"
    description = "Lyria RealTime - AI music generation"

    MODEL = "models/lyria-realtime-exp"

    def __init__(self):
        self._client = None
        self._sessions = {}

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(http_options={'api_version': 'v1alpha'})
        return self._client

    def _success(self, data: Any) -> Dict:
        return {"success": True, "data": data}

    def _error(self, message: str) -> Dict:
        return {"success": False, "error": message}

    async def start_session_async(
        self,
        prompts: List[str],
        weights: Optional[List[float]] = None,
        bpm: int = 120,
        temperature: float = 1.0,
        density: Optional[float] = None,
        brightness: Optional[float] = None,
        scale: Optional[str] = None,
        on_audio: Optional[callable] = None
    ) -> Dict:
        """
        Start a Lyria music generation session (async).

        Args:
            prompts: List of text prompts (genre, instrument, mood)
            weights: Optional weights for each prompt (default 1.0)
            bpm: Beats per minute (60-200)
            temperature: Generation temperature (0.0-3.0)
            density: Note density (0.0-1.0)
            brightness: Tonal brightness (0.0-1.0)
            scale: Musical scale (e.g., "C_MAJOR_A_MINOR")
            on_audio: Callback for audio chunks

        Returns:
            Dict with session info
        """
        try:
            from google.genai import types
            client = self._get_client()

            # Build weighted prompts
            if weights is None:
                weights = [1.0] * len(prompts)

            weighted_prompts = [
                types.WeightedPrompt(text=p, weight=w)
                for p, w in zip(prompts, weights)
            ]

            # Build config
            config_opts = {
                'bpm': bpm,
                'temperature': temperature
            }
            if density is not None:
                config_opts['density'] = density
            if brightness is not None:
                config_opts['brightness'] = brightness
            if scale is not None:
                config_opts['scale'] = getattr(types.Scale, scale, None)

            config = types.LiveMusicGenerationConfig(**config_opts)

            # Connect to Lyria
            session = await client.aio.live.music.connect(model=self.MODEL)

            # Set prompts and config
            await session.set_weighted_prompts(prompts=weighted_prompts)
            await session.set_music_generation_config(config=config)

            # Start playing
            await session.play()

            session_id = id(session)
            self._sessions[session_id] = session

            return self._success({
                "session_id": session_id,
                "prompts": prompts,
                "bpm": bpm,
                "status": "playing"
            })

        except Exception as e:
            return self._error(str(e))

    def start_session(self, **kwargs) -> Dict:
        """Synchronous wrapper for start_session_async."""
        return asyncio.run(self.start_session_async(**kwargs))

    async def update_prompts_async(
        self,
        session_id: int,
        prompts: List[str],
        weights: Optional[List[float]] = None
    ) -> Dict:
        """
        Update prompts for an active session.

        Args:
            session_id: Session ID from start_session
            prompts: New prompts
            weights: Optional weights

        Returns:
            Dict with status
        """
        try:

            session = self._sessions.get(session_id)
            if not session:
                return self._error(f"Session {session_id} not found")

            if weights is None:
                weights = [1.0] * len(prompts)

            weighted_prompts = [
                types.WeightedPrompt(text=p, weight=w)
                for p, w in zip(prompts, weights)
            ]

            await session.set_weighted_prompts(prompts=weighted_prompts)

            return self._success({
                "session_id": session_id,
                "prompts": prompts,
                "status": "updated"
            })
        except Exception as e:
            return self._error(str(e))

    def update_prompts(self, session_id: int, prompts: List[str], **kwargs) -> Dict:
        """Synchronous wrapper."""
        return asyncio.run(self.update_prompts_async(session_id, prompts, **kwargs))

    async def update_config_async(
        self,
        session_id: int,
        bpm: Optional[int] = None,
        density: Optional[float] = None,
        brightness: Optional[float] = None,
        reset_context: bool = False
    ) -> Dict:
        """Update music generation config."""
        try:

            session = self._sessions.get(session_id)
            if not session:
                return self._error(f"Session {session_id} not found")

            config_opts = {}
            if bpm is not None:
                config_opts['bpm'] = bpm
            if density is not None:
                config_opts['density'] = density
            if brightness is not None:
                config_opts['brightness'] = brightness

            if config_opts:
                config = types.LiveMusicGenerationConfig(**config_opts)
                await session.set_music_generation_config(config=config)

            if reset_context:
                await session.reset_context()

            return self._success({"session_id": session_id, "config": config_opts})
        except Exception as e:
            return self._error(str(e))

    async def pause_async(self, session_id: int) -> Dict:
        """Pause music generation."""
        try:
            session = self._sessions.get(session_id)
            if not session:
                return self._error(f"Session {session_id} not found")
            await session.pause()
            return self._success({"session_id": session_id, "status": "paused"})
        except Exception as e:
            return self._error(str(e))

    async def play_async(self, session_id: int) -> Dict:
        """Resume music generation."""
        try:
            session = self._sessions.get(session_id)
            if not session:
                return self._error(f"Session {session_id} not found")
            await session.play()
            return self._success({"session_id": session_id, "status": "playing"})
        except Exception as e:
            return self._error(str(e))

    async def stop_async(self, session_id: int) -> Dict:
        """Stop and close session."""
        try:
            session = self._sessions.pop(session_id, None)
            if not session:
                return self._error(f"Session {session_id} not found")
            await session.stop()
            return self._success({"session_id": session_id, "status": "stopped"})
        except Exception as e:
            return self._error(str(e))

    def pause(self, session_id: int) -> Dict:
        return asyncio.run(self.pause_async(session_id))

    def play(self, session_id: int) -> Dict:
        return asyncio.run(self.play_async(session_id))

    def stop(self, session_id: int) -> Dict:
        return asyncio.run(self.stop_async(session_id))


skill = LyriaSkill()

"""VoiceBox REST API Client.

Interfaces with VoiceBox (local TTS studio) at http://127.0.0.1:17493
Interactive docs at: http://127.0.0.1:17493/docs
OpenAPI spec at: http://127.0.0.1:17493/openapi.json

Full API (86 endpoints). Key ones used by this project:

  POST /generate                          - Generate speech with instruct control
  POST /generate/stream                   - Stream speech generation
  GET  /generate/{id}/status              - Check generation status
  POST /generate/{id}/retry               - Retry failed generation
  POST /generate/{id}/regenerate          - Regenerate with same params
  GET  /profiles                          - List all voice profiles
  POST /profiles                          - Create a new voice profile
  POST /profiles/{id}/samples             - Add audio sample (multipart upload)
  GET  /profiles/{id}/samples             - List profile samples
  PUT  /profiles/{id}/effects             - Set default effects for profile
  GET  /audio/{generation_id}             - Download generated audio
  GET  /audio/version/{version_id}        - Download specific version audio
  GET  /history                           - List generation history
  POST /stories                           - Create a story (multi-voice timeline)
  POST /stories/{id}/items                - Add generation to story timeline
  GET  /stories/{id}/export-audio         - Export full story as single audio
  POST /effects/preview/{generation_id}   - Preview effects on generation
  GET  /effects/available                 - List available audio effects
  POST /models/load                       - Load TTS model
  GET  /models/status                     - Check model status
"""
import logging
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class VoiceBoxClient:
    """Client for the VoiceBox REST API (v0.3.0).

    Wraps the VoiceBox FastAPI backend running at 127.0.0.1:17493.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:17493", timeout: int = 180):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def health_check(self) -> bool:
        """Check if VoiceBox is running. GET /health"""
        try:
            resp = self.session.get(f"{self.base_url}/health", timeout=5)
            return resp.status_code == 200
        except requests.ConnectionError:
            return False

    # ─── Profile Management ────────────────────────────────────────────

    def list_profiles(self) -> list[dict]:
        """GET /profiles — List all voice profiles."""
        resp = self.session.get(f"{self.base_url}/profiles", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_profile(self, profile_id: str) -> dict:
        """GET /profiles/{profile_id}"""
        resp = self.session.get(
            f"{self.base_url}/profiles/{profile_id}",
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def create_profile(self, name: str, language: str = "en", description: str = None) -> dict:
        """POST /profiles — Create a new voice profile."""
        payload = {"name": name, "language": language}
        if description:
            payload["description"] = description
        resp = self.session.post(
            f"{self.base_url}/profiles",
            json=payload,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def add_sample_to_profile(self, profile_id: str, audio_path: str) -> dict:
        """POST /profiles/{profile_id}/samples — Add audio sample (multipart)."""
        with open(audio_path, 'rb') as f:
            resp = self.session.post(
                f"{self.base_url}/profiles/{profile_id}/samples",
                files={"file": f},
                timeout=self.timeout
            )
        resp.raise_for_status()
        return resp.json()

    def get_profile_samples(self, profile_id: str) -> list[dict]:
        """GET /profiles/{profile_id}/samples"""
        resp = self.session.get(
            f"{self.base_url}/profiles/{profile_id}/samples",
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def update_profile_effects(self, profile_id: str, effects_chain: list[dict]) -> dict:
        """PUT /profiles/{profile_id}/effects — Set default effects for profile."""
        resp = self.session.put(
            f"{self.base_url}/profiles/{profile_id}/effects",
            json=effects_chain,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    # ─── Speech Generation ─────────────────────────────────────────────

    def generate(
        self,
        text: str,
        profile_id: str,
        instruct: Optional[str] = None,
        language: str = "en",
        engine: str = "qwen",
        model_size: str = "1.7B",
        seed: Optional[int] = None,
        max_chunk_chars: int = 800,
        crossfade_ms: int = 50,
        normalize: bool = True,
        effects_chain: Optional[list[dict]] = None,
    ) -> dict:
        """POST /generate — Generate speech from text.

        Args:
            text: Text to synthesize (1-50000 chars, auto-chunked)
            profile_id: Voice profile ID (provides the cloned voice)
            instruct: Style/delivery instruction for Qwen3-TTS (max 500 chars).
                      THIS IS THE KEY PARAMETER FOR TONE CONTROL.
                      Examples:
                        "Confident, warm, slightly sarcastic, mentoring tone"
                        "Calm, measured, British, precisely articulated"
                        "Excited, fast-paced, energetic"
            language: Language code. Supported:
                      en, zh, ja, ko, de, fr, ru, pt, es, it, he, ar,
                      da, el, fi, hi, ms, nl, no, pl, sv, sw, tr
            engine: TTS engine — "qwen", "luxtts", "chatterbox", "chatterbox_turbo"
            model_size: Qwen3-TTS model — "1.7B" or "0.6B"
            seed: Random seed for reproducibility (>=0, None for random)
            max_chunk_chars: Max chars per chunk for long texts (100-5000, default 800)
            crossfade_ms: Crossfade between chunks in ms (0-500, default 50)
            normalize: Normalize output audio volume (default True)
            effects_chain: Audio effects to apply (overrides profile defaults)
                           e.g., [{"type": "pitch_shift", "params": {"semitones": -2}}]

        Returns:
            GenerationResponse:
            {
                "id": str,              # Generation ID
                "profile_id": str,
                "text": str,
                "language": str,
                "audio_path": str|null,  # Internal audio path
                "duration": float|null,  # Duration in seconds
                "seed": int|null,
                "instruct": str|null,
                "engine": str,
                "model_size": str|null,
                "status": str,           # "completed" or "failed"
                "error": str|null,
                "is_favorited": bool,
                "created_at": str,
                "versions": list|null,
                "active_version_id": str|null
            }
        """
        payload = {
            "profile_id": profile_id,
            "text": text,
            "language": language,
            "engine": engine,
            "model_size": model_size,
            "max_chunk_chars": max_chunk_chars,
            "crossfade_ms": crossfade_ms,
            "normalize": normalize,
        }

        if instruct:
            payload["instruct"] = instruct
        if seed is not None:
            payload["seed"] = seed
        if effects_chain:
            payload["effects_chain"] = effects_chain

        logger.info(f"Generating [{engine}/{model_size}]: {text[:80]}...")
        if instruct:
            logger.info(f"  Instruct: {instruct[:80]}")

        resp = self.session.post(
            f"{self.base_url}/generate",
            json=payload,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def generate_stream(self, **kwargs) -> requests.Response:
        """POST /generate/stream — Stream speech generation (same params as generate)."""
        resp = self.session.post(
            f"{self.base_url}/generate/stream",
            json=kwargs,
            timeout=self.timeout,
            stream=True
        )
        resp.raise_for_status()
        return resp

    def get_generation_status(self, generation_id: str) -> dict:
        """GET /generate/{generation_id}/status"""
        resp = self.session.get(
            f"{self.base_url}/generate/{generation_id}/status",
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def retry_generation(self, generation_id: str) -> dict:
        """POST /generate/{generation_id}/retry"""
        resp = self.session.post(
            f"{self.base_url}/generate/{generation_id}/retry",
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    # ─── Audio Download ────────────────────────────────────────────────

    def download_audio(self, generation_id: str, output_path: str) -> Path:
        """GET /audio/{generation_id} — Download generated audio.

        Args:
            generation_id: The 'id' from generate() response
            output_path: Local file path to save audio
        """
        resp = self.session.get(
            f"{self.base_url}/audio/{generation_id}",
            timeout=self.timeout,
            stream=True
        )
        resp.raise_for_status()

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Audio saved: {output}")
        return output

    # ─── Stories (Multi-Voice Timeline) ────────────────────────────────

    def create_story(self, name: str, description: str = None) -> dict:
        """POST /stories — Create a new story."""
        payload = {"name": name}
        if description:
            payload["description"] = description
        resp = self.session.post(
            f"{self.base_url}/stories",
            json=payload,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def add_story_item(
        self,
        story_id: str,
        generation_id: str,
        start_time_ms: int = None,
        track: int = 0
    ) -> dict:
        """POST /stories/{story_id}/items — Add a generation to the story timeline.

        Args:
            story_id: Story ID
            generation_id: ID of a previously generated audio
            start_time_ms: Position on timeline in milliseconds
            track: Track number (0 = Tony, 1 = JARVIS, etc.)
        """
        payload = {"generation_id": generation_id}
        if start_time_ms is not None:
            payload["start_time_ms"] = start_time_ms
        if track is not None:
            payload["track"] = track
        resp = self.session.post(
            f"{self.base_url}/stories/{story_id}/items",
            json=payload,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def export_story_audio(self, story_id: str, output_path: str) -> Path:
        """GET /stories/{story_id}/export-audio — Export full story as single file."""
        resp = self.session.get(
            f"{self.base_url}/stories/{story_id}/export-audio",
            timeout=300,  # Stories can be long
            stream=True
        )
        resp.raise_for_status()

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Story audio exported: {output}")
        return output

    def list_stories(self) -> list[dict]:
        """GET /stories"""
        resp = self.session.get(f"{self.base_url}/stories", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    # ─── Effects ───────────────────────────────────────────────────────

    def list_available_effects(self) -> list[dict]:
        """GET /effects/available — List all available audio effects."""
        resp = self.session.get(
            f"{self.base_url}/effects/available",
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def preview_effects(self, generation_id: str, effects_chain: list[dict]) -> dict:
        """POST /effects/preview/{generation_id} — Preview effects on audio."""
        resp = self.session.post(
            f"{self.base_url}/effects/preview/{generation_id}",
            json=effects_chain,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    # ─── Models ────────────────────────────────────────────────────────

    def get_model_status(self) -> dict:
        """GET /models/status"""
        resp = self.session.get(
            f"{self.base_url}/models/status",
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def load_model(self, model_name: str) -> dict:
        """POST /models/load"""
        resp = self.session.post(
            f"{self.base_url}/models/load",
            json={"model_name": model_name},
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    # ─── History ───────────────────────────────────────────────────────

    def list_generations(self, limit: int = 50) -> list[dict]:
        """GET /history"""
        resp = self.session.get(
            f"{self.base_url}/history",
            params={"limit": limit},
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def get_generation(self, generation_id: str) -> dict:
        """GET /history/{generation_id}"""
        resp = self.session.get(
            f"{self.base_url}/history/{generation_id}",
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    # ─── Utility ───────────────────────────────────────────────────────

    def find_profile_by_name(self, name: str) -> Optional[dict]:
        """Find a profile by name (case-insensitive)."""
        profiles = self.list_profiles()
        name_lower = name.lower()
        for p in profiles:
            if p.get("name", "").lower() == name_lower:
                return p
        return None

    def ensure_profile(self, name: str, language: str = "en", description: str = None) -> dict:
        """Get existing profile by name or create it."""
        existing = self.find_profile_by_name(name)
        if existing:
            logger.info(f"Found existing profile: {name} (id={existing.get('id')})")
            return existing

        logger.info(f"Creating new profile: {name}")
        return self.create_profile(name, language, description)

"""VoiceBox REST API Client.

Interfaces with VoiceBox (local TTS studio) running at localhost:17493.
Supports voice profile management, speech generation, and story composition.

API docs: http://localhost:17493/docs
Docs: https://docs.voicebox.sh/
"""
import logging
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class VoiceBoxClient:
    """Client for the VoiceBox REST API."""

    def __init__(self, base_url: str = "http://localhost:17493", timeout: int = 120):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def health_check(self) -> bool:
        """Check if VoiceBox is running and healthy."""
        try:
            resp = self.session.get(f"{self.base_url}/", timeout=5)
            return resp.status_code == 200
        except requests.ConnectionError:
            return False

    # --- Profile Management ---

    def list_profiles(self) -> list[dict]:
        """List all voice profiles."""
        resp = self.session.get(f"{self.base_url}/profiles", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_profile(self, profile_id: str) -> dict:
        """Get a specific voice profile."""
        resp = self.session.get(
            f"{self.base_url}/profiles/{profile_id}",
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def create_profile(self, name: str, language: str = "en") -> dict:
        """Create a new voice profile."""
        resp = self.session.post(
            f"{self.base_url}/profiles",
            json={"name": name, "language": language},
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def add_sample_to_profile(self, profile_id: str, audio_path: str) -> dict:
        """Add an audio sample to a voice profile."""
        with open(audio_path, 'rb') as f:
            resp = self.session.post(
                f"{self.base_url}/profiles/{profile_id}/samples",
                files={"file": f},
                timeout=self.timeout
            )
        resp.raise_for_status()
        return resp.json()

    # --- Speech Generation ---

    def generate(
        self,
        text: str,
        profile_id: str,
        language: str = "en",
        voice_instruction: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Generate speech from text using a voice profile.

        Args:
            text: The text to synthesize
            profile_id: Voice profile ID to use
            language: Language code (default: "en")
            voice_instruction: Style instruction for Qwen3-TTS
            **kwargs: Additional generation parameters

        Returns:
            Generation result dict with audio file info
        """
        payload = {
            "text": text,
            "profile_id": profile_id,
            "language": language,
        }

        if voice_instruction:
            payload["voice_instruction"] = voice_instruction

        payload.update(kwargs)

        logger.info(f"Generating speech: {text[:80]}...")

        resp = self.session.post(
            f"{self.base_url}/generate",
            json=payload,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def get_audio_file(self, generation_id: str, output_path: str) -> Path:
        """Download a generated audio file."""
        resp = self.session.get(
            f"{self.base_url}/generations/{generation_id}/audio",
            timeout=self.timeout,
            stream=True
        )
        resp.raise_for_status()

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return output

    # --- History ---

    def list_generations(self, limit: int = 50) -> list[dict]:
        """List recent generations."""
        resp = self.session.get(
            f"{self.base_url}/history",
            params={"limit": limit},
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    # --- Utility ---

    def find_profile_by_name(self, name: str) -> Optional[dict]:
        """Find a profile by name (case-insensitive)."""
        profiles = self.list_profiles()
        name_lower = name.lower()
        for p in profiles:
            if p.get("name", "").lower() == name_lower:
                return p
        return None

    def ensure_profile(self, name: str, language: str = "en") -> dict:
        """Get existing profile by name or create it."""
        existing = self.find_profile_by_name(name)
        if existing:
            logger.info(f"Found existing profile: {name} (id={existing.get('id')})")
            return existing

        logger.info(f"Creating new profile: {name}")
        return self.create_profile(name, language)

"""Voice profile management for Stark Workshop.

Handles creation and configuration of Tony Stark and JARVIS voice profiles.
"""
import json
import logging
from pathlib import Path
from typing import Optional

from .client import VoiceBoxClient

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


def load_voicebox_config() -> dict:
    """Load VoiceBox configuration."""
    config_path = CONFIG_DIR / "voicebox_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_voicebox_config(config: dict) -> None:
    """Save updated VoiceBox configuration."""
    config_path = CONFIG_DIR / "voicebox_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def setup_profiles(
    client: VoiceBoxClient,
    tony_sample_path: Optional[str] = None,
    jarvis_sample_path: Optional[str] = None
) -> dict:
    """Set up Tony Stark and JARVIS voice profiles in VoiceBox.

    Args:
        client: VoiceBox API client
        tony_sample_path: Path to Tony Stark voice sample (WAV, 10-30s)
        jarvis_sample_path: Path to JARVIS voice sample (WAV, 10-30s)

    Returns:
        Dict with profile IDs for both characters
    """
    config = load_voicebox_config()

    tony_profile = client.ensure_profile("Tony Stark", language="en")
    tony_id = tony_profile.get("id")
    config["profiles"]["tony_stark"]["profile_id"] = tony_id
    logger.info(f"Tony Stark profile ID: {tony_id}")

    if tony_sample_path:
        logger.info(f"Adding Tony sample: {tony_sample_path}")
        client.add_sample_to_profile(tony_id, tony_sample_path)

    jarvis_profile = client.ensure_profile("JARVIS", language="en")
    jarvis_id = jarvis_profile.get("id")
    config["profiles"]["jarvis"]["profile_id"] = jarvis_id
    logger.info(f"JARVIS profile ID: {jarvis_id}")

    if jarvis_sample_path:
        logger.info(f"Adding JARVIS sample: {jarvis_sample_path}")
        client.add_sample_to_profile(jarvis_id, jarvis_sample_path)

    save_voicebox_config(config)

    return {
        "tony_stark": tony_id,
        "jarvis": jarvis_id
    }


def get_voice_instruction(character: str) -> str:
    """Get the voice instruction for a character from config."""
    config = load_voicebox_config()
    profile_key = "tony_stark" if character.lower() in ("tony", "tony_stark", "tony stark") else "jarvis"
    return config["profiles"][profile_key].get("voice_instruction", "")


def get_profile_id(character: str) -> Optional[str]:
    """Get the VoiceBox profile ID for a character."""
    config = load_voicebox_config()
    profile_key = "tony_stark" if character.lower() in ("tony", "tony_stark", "tony stark") else "jarvis"
    return config["profiles"][profile_key].get("profile_id")

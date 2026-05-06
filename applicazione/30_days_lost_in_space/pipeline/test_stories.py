"""Test script for VoiceBox Stories (multi-voice timeline).

Generates two short clips (Tony + JARVIS), creates a Story,
places them on separate tracks, and exports the combined audio.

Usage:
    python -m src.pipeline.test_stories
"""
import json
import sys
import time
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent
APP_DIR = PIPELINE_DIR.parent
PROJECT_ROOT = APP_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PIPELINE_DIR))

from src.voicebox.client import VoiceBoxClient
from voicebox_profiles import get_profile_id, get_instruct
OUTPUT_DIR = APP_DIR / "data" / "output" / "audio" / "test_stories"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TONY_TEXT = "Alright kid, welcome to the workshop. Today we're going to build something that would make NASA jealous."
JARVIS_TEXT = "Good morning, sir. All systems are nominal. I have prepared today's mission briefing."

POLL_INTERVAL = 3
POLL_TIMEOUT = 120


def wait_for_generation(client: VoiceBoxClient, gen_id: str) -> dict:
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        info = client.get_generation_info(gen_id)
        status = info.get("status", "")
        if status == "completed":
            return info
        if status in ("failed", "cancelled"):
            print(f"  Generation {gen_id} {status}: {info.get('error', 'unknown')}")
            return info
        time.sleep(POLL_INTERVAL)
    return {"status": "timeout", "id": gen_id}


def main():
    client = VoiceBoxClient()

    if not client.health_check():
        print("VoiceBox is not running at http://127.0.0.1:17493")
        print("Start VoiceBox and try again.")
        sys.exit(1)

    print("VoiceBox is running.")

    tony_id = get_profile_id("tony")
    jarvis_id = get_profile_id("jarvis")
    tony_instruct = get_instruct("tony")
    jarvis_instruct = get_instruct("jarvis")

    print(f"\nTony profile:  {tony_id}")
    print(f"JARVIS profile: {jarvis_id}")

    # --- Generate Tony clip ---
    print(f"\n[1/2] Generating Tony clip...")
    tony_gen = client.generate(
        text=TONY_TEXT,
        profile_id=tony_id,
        instruct=tony_instruct,
        engine="qwen",
    )
    tony_gen_id = tony_gen["id"]
    print(f"  Generation ID: {tony_gen_id}")

    tony_result = wait_for_generation(client, tony_gen_id)
    if tony_result.get("status") != "completed":
        print("  Tony generation failed. Aborting.")
        sys.exit(1)

    tony_duration_ms = int((tony_result.get("duration") or 5.0) * 1000)
    print(f"  Duration: {tony_duration_ms}ms")

    tony_wav = OUTPUT_DIR / "tony_test.wav"
    client.download_audio(tony_gen_id, str(tony_wav))
    print(f"  Saved: {tony_wav}")

    # --- Generate JARVIS clip ---
    print(f"\n[2/2] Generating JARVIS clip...")
    jarvis_gen = client.generate(
        text=JARVIS_TEXT,
        profile_id=jarvis_id,
        instruct=jarvis_instruct,
        engine="qwen",
    )
    jarvis_gen_id = jarvis_gen["id"]
    print(f"  Generation ID: {jarvis_gen_id}")

    jarvis_result = wait_for_generation(client, jarvis_gen_id)
    if jarvis_result.get("status") != "completed":
        print("  JARVIS generation failed. Aborting.")
        sys.exit(1)

    jarvis_duration_ms = int((jarvis_result.get("duration") or 5.0) * 1000)
    print(f"  Duration: {jarvis_duration_ms}ms")

    jarvis_wav = OUTPUT_DIR / "jarvis_test.wav"
    client.download_audio(jarvis_gen_id, str(jarvis_wav))
    print(f"  Saved: {jarvis_wav}")

    # --- Create Story ---
    print("\n[Story] Creating story: 'Day 01 Test'")
    story = client.create_story(
        name="Day 01 Test",
        description="Test story with Tony intro followed by JARVIS briefing"
    )
    story_id = story["id"]
    print(f"  Story ID: {story_id}")

    # --- Add items to timeline ---
    # JARVIS briefing starts at 0ms on track 1
    print(f"\n[Story] Adding JARVIS at 0ms (track 1)...")
    client.add_story_item(
        story_id=story_id,
        generation_id=jarvis_gen_id,
        start_time_ms=0,
        track=1
    )

    # Tony starts after JARVIS finishes + 500ms gap
    tony_start = jarvis_duration_ms + 500
    print(f"[Story] Adding Tony at {tony_start}ms (track 0)...")
    client.add_story_item(
        story_id=story_id,
        generation_id=tony_gen_id,
        start_time_ms=tony_start,
        track=0
    )

    # --- Export ---
    export_path = OUTPUT_DIR / "story_day01_test.wav"
    print(f"\n[Story] Exporting to {export_path}...")
    client.export_story_audio(story_id, str(export_path))
    print(f"  Exported: {export_path}")

    # --- Summary ---
    story_info = client.get_story(story_id)
    print(f"\n{'='*50}")
    print(f"Story test complete.")
    print(f"  Story: {story_info.get('name')}")
    print(f"  Items: JARVIS (0ms, track 1) + Tony ({tony_start}ms, track 0)")
    print(f"  Export: {export_path}")
    print(f"{'='*50}")

    return story_id


if __name__ == "__main__":
    main()

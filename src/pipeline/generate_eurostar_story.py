"""Generate a VoiceBox Story from the Euro Star Act 1 parsed script.

Pipeline:
  1. Load parsed JSON (character lines + instruct from stage directions)
  2. List available Qwen CustomVoice presets and map to characters
  3. Generate each line via POST /generate (qwen_custom_voice engine)
  4. Create a Story, place clips on timeline (per-character tracks)
  5. Export combined audio
  6. Mix with train ambient sound via pydub

Usage:
    python -m src.pipeline.generate_eurostar_story [--dry-run] [--list-voices] [--start-from N]
"""
import argparse
import json
import logging
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.voicebox.client import VoiceBoxClient

APP_DIR = PROJECT_ROOT / "applicazione" / "teatro"
SCRIPT_JSON = APP_DIR / "eurostar_act1_parsed.json"
OUTPUT_DIR = APP_DIR / "output" / "eurostar_act1"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_AMBIENT = APP_DIR / "Train Ride Experience" / "Train Ride Experience.m4a"

POLL_INTERVAL = 3
POLL_TIMEOUT = 180
GAP_MS = 400

TRACK_MAP = {
    "arthur": 0,
    "marilyn": 1,
    "voice": 2,
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(OUTPUT_DIR / "generation.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def load_script() -> dict:
    with open(SCRIPT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def list_available_voices(client: VoiceBoxClient):
    """List all profiles available in VoiceBox for voice selection."""
    profiles = client.list_profiles()
    print(f"\n{'='*60}")
    print(f"Available voice profiles ({len(profiles)}):")
    print(f"{'='*60}")
    for p in profiles:
        pid = p.get("id", "?")
        name = p.get("name", "unnamed")
        lang = p.get("language", "?")
        print(f"  {pid}  {name} ({lang})")
    print(f"{'='*60}\n")
    return profiles


def select_voice_for_character(profiles: list[dict], character: str, char_info: dict) -> str:
    """Let the user pick a voice profile for a character."""
    print(f"\nSelect voice for '{character}': {char_info['description']}")
    for i, p in enumerate(profiles):
        print(f"  [{i}] {p.get('name', 'unnamed')} (id: {p.get('id', '?')})")

    while True:
        choice = input(f"  Enter number for {character}: ").strip()
        if choice.isdigit() and 0 <= int(choice) < len(profiles):
            selected = profiles[int(choice)]
            print(f"  -> {selected.get('name')} selected for {character}")
            return selected.get("id")
        print("  Invalid choice, try again.")


def wait_for_generation(client: VoiceBoxClient, gen_id: str) -> dict:
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        try:
            info = client.get_generation_info(gen_id)
        except Exception as e:
            logger.warning(f"  Poll error: {e}")
            time.sleep(POLL_INTERVAL)
            continue
        status = info.get("status", "")
        if status == "completed":
            return info
        if status in ("failed", "cancelled"):
            logger.error(f"  Generation {gen_id} {status}: {info.get('error', 'unknown')}")
            return info
        time.sleep(POLL_INTERVAL)
    return {"status": "timeout", "id": gen_id}


def generate_all_lines(
    client: VoiceBoxClient,
    script: dict,
    voice_map: dict[str, str],
    dry_run: bool = False,
    start_from: int = 1,
) -> list[dict]:
    """Generate audio for each line. Returns list of results with timing info."""
    lines = script["lines"]
    results = []

    state_file = OUTPUT_DIR / "generation_state.json"
    if state_file.exists() and start_from == 1:
        with open(state_file, "r") as f:
            results = json.load(f)
        if results:
            last_id = results[-1].get("line_id", 0)
            logger.info(f"Resuming from line {last_id + 1} ({len(results)} already done)")
            start_from = last_id + 1

    for line in lines:
        line_id = line["id"]
        if line_id < start_from:
            continue

        character = line["character"]
        text = line["text"]
        instruct = line["instruct"]
        profile_id = voice_map.get(character)

        logger.info(f"[{line_id}/{len(lines)}] {character}: {text[:60]}...")
        logger.info(f"  instruct: {instruct[:80]}")

        if dry_run:
            results.append({
                "line_id": line_id,
                "character": character,
                "gen_id": f"dry-run-{line_id}",
                "duration_ms": 3000,
                "status": "dry-run",
            })
            continue

        try:
            gen = client.generate(
                text=text,
                profile_id=profile_id,
                instruct=instruct,
                engine="qwen_custom_voice",
                language="en",
            )
        except Exception as e:
            logger.error(f"  Generate failed: {e}")
            results.append({
                "line_id": line_id,
                "character": character,
                "gen_id": None,
                "duration_ms": 0,
                "status": "error",
                "error": str(e),
            })
            with open(state_file, "w") as f:
                json.dump(results, f, indent=2)
            continue

        gen_id = gen.get("id")
        logger.info(f"  gen_id: {gen_id}")

        result = wait_for_generation(client, gen_id)
        status = result.get("status", "unknown")
        duration = result.get("duration", 0) or 0
        duration_ms = int(duration * 1000)

        wav_path = OUTPUT_DIR / f"line_{line_id:03d}_{character}.wav"
        if status == "completed":
            try:
                client.download_audio(gen_id, str(wav_path))
                logger.info(f"  Saved: {wav_path.name} ({duration_ms}ms)")
            except Exception as e:
                logger.error(f"  Download failed: {e}")
                status = "download_error"

        results.append({
            "line_id": line_id,
            "character": character,
            "gen_id": gen_id,
            "duration_ms": duration_ms,
            "status": status,
            "wav": str(wav_path) if status == "completed" else None,
        })

        with open(state_file, "w") as f:
            json.dump(results, f, indent=2)

    return results


def build_story(
    client: VoiceBoxClient,
    results: list[dict],
    dry_run: bool = False,
) -> str:
    """Create a VoiceBox Story and add all generated clips to the timeline."""
    logger.info("\nCreating Story: 'Euro Star - Act 1'")

    if dry_run:
        timeline = []
        current_ms = 0
        for r in results:
            timeline.append({
                "line_id": r["line_id"],
                "character": r["character"],
                "start_ms": current_ms,
                "duration_ms": r["duration_ms"],
                "track": TRACK_MAP.get(r["character"], 0),
            })
            current_ms += r["duration_ms"] + GAP_MS

        with open(OUTPUT_DIR / "timeline_preview.json", "w") as f:
            json.dump(timeline, f, indent=2)
        total_s = current_ms / 1000
        logger.info(f"  Dry-run timeline: {len(timeline)} items, ~{total_s:.1f}s total")
        logger.info(f"  Saved: timeline_preview.json")
        return "dry-run"

    story = client.create_story(
        name="Euro Star - Act 1",
        description="Jean-Pierre Martinez comedy. Arthur, Marilyn, and train PA voice."
    )
    story_id = story["id"]
    logger.info(f"  Story ID: {story_id}")

    current_ms = 0
    timeline = []

    for r in results:
        if r.get("status") != "completed" or not r.get("gen_id"):
            current_ms += GAP_MS
            continue

        track = TRACK_MAP.get(r["character"], 0)
        logger.info(f"  Adding line {r['line_id']} ({r['character']}) at {current_ms}ms, track {track}")

        try:
            client.add_story_item(
                story_id=story_id,
                generation_id=r["gen_id"],
                start_time_ms=current_ms,
                track=track,
            )
        except Exception as e:
            logger.error(f"  Failed to add item: {e}")

        timeline.append({
            "line_id": r["line_id"],
            "character": r["character"],
            "gen_id": r["gen_id"],
            "start_ms": current_ms,
            "duration_ms": r["duration_ms"],
            "track": track,
        })

        current_ms += r["duration_ms"] + GAP_MS

    with open(OUTPUT_DIR / "timeline.json", "w") as f:
        json.dump(timeline, f, indent=2)

    total_s = current_ms / 1000
    logger.info(f"  Timeline: {len(timeline)} items, ~{total_s:.1f}s total")

    return story_id


def export_and_mix(client: VoiceBoxClient, story_id: str, dry_run: bool = False):
    """Export story audio and mix with train ambient."""
    export_path = OUTPUT_DIR / "eurostar_act1_raw.wav"

    if not dry_run:
        logger.info(f"\nExporting story audio...")
        client.export_story_audio(story_id, str(export_path))
        logger.info(f"  Exported: {export_path}")

    if not TRAIN_AMBIENT.exists():
        logger.warning(f"  Train ambient not found at {TRAIN_AMBIENT}")
        logger.info("  Skipping ambient mix.")
        return

    if dry_run:
        logger.info(f"\n[Dry-run] Would mix {export_path} with {TRAIN_AMBIENT}")
        return

    try:
        from pydub import AudioSegment

        logger.info(f"\nMixing with train ambient...")
        dialogue = AudioSegment.from_wav(str(export_path))
        ambient = AudioSegment.from_file(str(TRAIN_AMBIENT))

        # Loop ambient to match dialogue length, reduce volume
        ambient_db_reduction = 18
        ambient = ambient - ambient_db_reduction

        if len(ambient) < len(dialogue):
            repeats = (len(dialogue) // len(ambient)) + 1
            ambient = ambient * repeats
        ambient = ambient[:len(dialogue)]

        # Fade in/out the ambient
        ambient = ambient.fade_in(2000).fade_out(3000)

        mixed = dialogue.overlay(ambient)
        final_path = OUTPUT_DIR / "eurostar_act1_final.wav"
        mixed.export(str(final_path), format="wav")
        logger.info(f"  Final mix saved: {final_path}")

    except ImportError:
        logger.warning("  pydub not installed. Install with: pip install pydub")
        logger.info("  Skipping ambient mix. Raw export available at: {export_path}")
    except Exception as e:
        logger.error(f"  Mix failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate Euro Star Act 1 Story")
    parser.add_argument("--dry-run", action="store_true", help="Parse and preview without generating")
    parser.add_argument("--list-voices", action="store_true", help="List available voices and exit")
    parser.add_argument("--start-from", type=int, default=1, help="Resume from line N")
    args = parser.parse_args()

    client = VoiceBoxClient()

    if not args.dry_run:
        if not client.health_check():
            print("VoiceBox is not running at http://127.0.0.1:17493")
            print("Start VoiceBox and try again.")
            sys.exit(1)
        print("VoiceBox is running.\n")

    script = load_script()
    print(f"Loaded: {script['title']} by {script['author']}")
    print(f"Act {script['act']}: {len(script['lines'])} lines, "
          f"{len(script['characters'])} characters\n")

    if args.dry_run:
        # Use placeholder profile IDs
        voice_map = {c: f"preset-{c}" for c in script["characters"]}
        results = generate_all_lines(client, script, voice_map, dry_run=True)
        build_story(client, results, dry_run=True)
        export_and_mix(client, "dry-run", dry_run=True)
        print("\nDry-run complete. Check output at:", OUTPUT_DIR)
        return

    profiles = list_available_voices(client)

    if args.list_voices:
        return

    if not profiles:
        print("No voice profiles found. Create profiles in VoiceBox first.")
        sys.exit(1)

    # Interactive voice selection
    voice_map = {}
    for char_name, char_info in script["characters"].items():
        voice_map[char_name] = select_voice_for_character(profiles, char_name, char_info)

    print(f"\nVoice mapping:")
    for char, pid in voice_map.items():
        print(f"  {char} -> {pid}")

    confirm = input("\nProceed with generation? (y/n): ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return

    # Generate
    results = generate_all_lines(client, script, voice_map, start_from=args.start_from)

    completed = sum(1 for r in results if r.get("status") == "completed")
    failed = sum(1 for r in results if r.get("status") != "completed")
    print(f"\nGeneration complete: {completed} OK, {failed} failed")

    if completed == 0:
        print("No audio generated. Aborting story creation.")
        return

    # Build Story
    story_id = build_story(client, results)

    # Export and mix
    export_and_mix(client, story_id)

    print(f"\n{'='*60}")
    print(f"Done! Output at: {OUTPUT_DIR}")
    print(f"  Raw export: eurostar_act1_raw.wav")
    print(f"  Final mix:  eurostar_act1_final.wav")
    print(f"  Timeline:   timeline.json")
    print(f"  State:      generation_state.json")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

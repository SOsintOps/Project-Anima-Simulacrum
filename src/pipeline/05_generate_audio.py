"""Pipeline Step 05: Generate audio from Tony/JARVIS scripts via VoiceBox.

Reads rewritten scripts from data/processed/tony_scripts/ and generates
audio using VoiceBox's REST API with the configured voice profiles.

Usage:
    python -m src.pipeline.05_generate_audio [--day N] [--all] [--dry-run]
"""
import json
import sys
import logging
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.voicebox.client import VoiceBoxClient
from src.voicebox.profiles import get_profile_id, get_instruct, load_voicebox_config
from src.voicebox.speed_fix import prepare_tony_text, prepare_jarvis_text, chunk_for_tts

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCRIPTS_DIR = PROJECT_ROOT / "data" / "processed" / "tony_scripts"
AUDIO_DIR = PROJECT_ROOT / "data" / "output" / "audio"


def generate_segment_audio(
    client: VoiceBoxClient,
    segment: dict,
    day: int,
    segment_index: int,
    output_dir: Path,
    dry_run: bool = False
) -> dict:
    """Generate audio for a single script segment."""
    speaker = segment["speaker"].upper()
    text = segment["text"]
    segment_type = segment.get("type", "dialogue")

    if speaker in ("TONY", "TONY STARK", "TONY_STARK"):
        profile_id = get_profile_id("tony")
        instruct = get_instruct("tony")
        prepared_text = prepare_tony_text(text)
        speaker_tag = "tony"
    elif speaker in ("JARVIS", "J.A.R.V.I.S."):
        profile_id = get_profile_id("jarvis")
        instruct = get_instruct("jarvis")
        prepared_text = prepare_jarvis_text(text)
        speaker_tag = "jarvis"
    else:
        logger.warning(f"Unknown speaker: {speaker}, skipping")
        return {"status": "skipped", "reason": f"Unknown speaker: {speaker}"}

    if not profile_id:
        logger.error(f"No profile ID for {speaker}. Run profile setup first.")
        return {"status": "error", "reason": "No profile ID"}

    chunks = chunk_for_tts(prepared_text, max_chars=500)
    output_filename = f"day_{day:02d}_seg_{segment_index:03d}_{speaker_tag}_{segment_type}.wav"

    if dry_run:
        logger.info(f"  [DRY RUN] Would generate: {output_filename}")
        logger.info(f"    Speaker: {speaker_tag}, Text: {len(text)} chars, Chunks: {len(chunks)}")
        return {
            "status": "dry_run",
            "file": output_filename,
            "speaker": speaker_tag,
            "chunks": len(chunks),
            "chars": len(text)
        }

    chunk_results = []
    for i, chunk in enumerate(chunks):
        logger.info(f"  Generating chunk {i+1}/{len(chunks)} for {speaker_tag}...")
        try:
            config = load_voicebox_config()
            result = client.generate(
                text=chunk,
                profile_id=profile_id,
                instruct=instruct,
                language="en",
                engine=config.get("engine", "qwen"),
                model_size=config.get("model_size", "1.7B"),
                max_chunk_chars=config["generation_defaults"].get("max_chunk_chars", 800),
                crossfade_ms=config["generation_defaults"].get("crossfade_ms", 50),
                normalize=config["generation_defaults"].get("normalize", True),
            )
            # Download the audio file using generation ID
            gen_id = result.get("id")
            if gen_id and result.get("status") == "completed":
                chunk_filename = f"day_{day:02d}_seg_{segment_index:03d}_{speaker_tag}_chunk{i:02d}.wav"
                client.download_audio(gen_id, str(output_dir / chunk_filename))
                result["local_file"] = chunk_filename
            chunk_results.append(result)
            if len(chunks) > 1:
                time.sleep(1)
        except Exception as e:
            logger.error(f"  Generation failed for chunk {i+1}: {e}")
            chunk_results.append({"error": str(e)})

    return {
        "status": "generated",
        "file": output_filename,
        "speaker": speaker_tag,
        "chunks": len(chunks),
        "results": chunk_results
    }


def process_day(client: VoiceBoxClient, day: int, dry_run: bool = False) -> dict:
    """Process all segments for a single day."""
    script_file = SCRIPTS_DIR / f"day_{day:02d}_tony.json"

    if not script_file.exists():
        logger.error(f"Script not found: {script_file}")
        return {"status": "error", "reason": "Script not found"}

    with open(script_file, 'r', encoding='utf-8') as f:
        script = json.load(f)

    day_audio_dir = AUDIO_DIR / f"day_{day:02d}"
    day_audio_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Processing Day {day}: {script.get('title', 'Unknown')}")

    results = []
    for i, segment in enumerate(script.get("segments", [])):
        result = generate_segment_audio(
            client=client, segment=segment, day=day,
            segment_index=i, output_dir=day_audio_dir, dry_run=dry_run
        )
        results.append(result)

    manifest = {
        "day": day,
        "title": script.get("title", ""),
        "segments_total": len(results),
        "segments_generated": sum(1 for r in results if r.get("status") == "generated"),
        "results": results
    }

    manifest_file = day_audio_dir / "manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest


def main():
    dry_run = "--dry-run" in sys.argv
    process_day_num = None

    for i, arg in enumerate(sys.argv):
        if arg == "--day" and i + 1 < len(sys.argv):
            process_day_num = int(sys.argv[i + 1])

    config = load_voicebox_config()
    client = VoiceBoxClient(base_url=config["api_base_url"])

    if not dry_run:
        if not client.health_check():
            logger.error("VoiceBox is not running! Start it first.")
            logger.error(f"Expected at: {config['api_base_url']}")
            sys.exit(1)
        logger.info("VoiceBox connection OK")

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    if process_day_num:
        process_day(client, process_day_num, dry_run=dry_run)
    else:
        script_files = sorted(SCRIPTS_DIR.glob("day_*_tony.json"))
        if not script_files:
            logger.error(f"No scripts found in {SCRIPTS_DIR}")
            sys.exit(1)
        for script_file in script_files:
            day = int(script_file.stem.split('_')[1])
            process_day(client, day, dry_run=dry_run)


if __name__ == "__main__":
    main()

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

PIPELINE_DIR = Path(__file__).resolve().parent
APP_DIR = PIPELINE_DIR.parent
PROJECT_ROOT = APP_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PIPELINE_DIR))

from src.voicebox.client import VoiceBoxClient
from voicebox_profiles import get_profile_id, get_instruct, load_voicebox_config
from speed_fix import prepare_tony_text, prepare_jarvis_text, chunk_for_tts
LOG_DIR = APP_DIR / "data" / "output" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

_log_file = LOG_DIR / f"generate_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),                          # terminale
        logging.FileHandler(_log_file, encoding='utf-8') # file
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Log file: {_log_file}")

SCRIPTS_DIR = APP_DIR / "data" / "processed" / "tony_scripts"
AUDIO_DIR = APP_DIR / "data" / "output" / "audio"

POLL_INTERVAL = 5       # seconds between status checks
POLL_TIMEOUT = 300      # max seconds to wait per generation
MAX_RETRIES = 2         # retries on failure


def _poll_until_done(client: VoiceBoxClient, gen_id: str) -> dict:
    """Poll generation status until completed or failed.

    VoiceBox can return status='completed' with audio_path='' if the audio
    is stored internally but the path field is not exposed. In that case we
    still attempt the download and let the caller handle a 500.
    """
    deadline = time.time() + POLL_TIMEOUT
    last_status = ""
    while time.time() < deadline:
        try:
            info = client.get_generation_info(gen_id)
        except Exception as e:
            logger.warning(f"    Poll error: {e}")
            time.sleep(POLL_INTERVAL)
            continue

        status = info.get("status", "")
        if status != last_status:
            logger.info(f"    Status: {status}")
            last_status = status

        if status == "completed":
            # Return regardless of audio_path — caller will attempt download
            return info
        if status == "failed":
            return info
        if status == "timeout":
            return info

        time.sleep(POLL_INTERVAL)

    return {"status": "timeout", "id": gen_id}


def _apply_time_stretch(wav_path: Path, rate: float) -> None:
    """Slow down (rate < 1.0) or speed up (rate > 1.0) a WAV in-place."""
    try:
        import librosa
        import soundfile as sf
        y, sr = librosa.load(str(wav_path), sr=None, mono=True)
        y_stretched = librosa.effects.time_stretch(y, rate=rate)
        sf.write(str(wav_path), y_stretched, sr, subtype='PCM_16')
        new_dur = len(y_stretched) / sr
        logger.info(f"    time_stretch {rate:.3f}x → {new_dur:.1f}s: {wav_path.name}")
    except Exception as e:
        logger.warning(f"    time_stretch failed ({e}), keeping original audio")


def generate_segment_audio(
    client: VoiceBoxClient,
    segment: dict,
    day: int,
    segment_index: int,
    output_dir: Path,
    config: dict,
    dry_run: bool = False
) -> dict:
    """Generate audio for a single script segment."""
    speaker = segment["speaker"].upper()
    text = segment["text"]
    segment_type = segment.get("type", "dialogue")
    # Per-segment instruct takes priority over profile default
    seg_instruct = segment.get("instruct")

    if speaker in ("TONY", "TONY STARK", "TONY_STARK"):
        profile_key = "tony_stark"
        profile_id = get_profile_id("tony")
        instruct = seg_instruct or get_instruct("tony")
        prepared_text = prepare_tony_text(text)
        speaker_tag = "tony"
    elif speaker in ("JARVIS", "J.A.R.V.I.S."):
        profile_key = "jarvis"
        profile_id = get_profile_id("jarvis")
        instruct = seg_instruct or get_instruct("jarvis")
        prepared_text = prepare_jarvis_text(text)
        speaker_tag = "jarvis"
    else:
        logger.warning(f"Unknown speaker: {speaker}, skipping")
        return {"status": "skipped", "reason": f"Unknown speaker: {speaker}"}

    if not profile_id:
        logger.error(f"No profile ID for {speaker}. Run profile setup first.")
        return {"status": "error", "reason": "No profile ID"}

    output_filename = f"day_{day:02d}_seg_{segment_index:03d}_{speaker_tag}_{segment_type}.wav"
    output_path = output_dir / output_filename

    chunks = chunk_for_tts(prepared_text, max_chars=900)

    if dry_run:
        logger.info(f"  [DRY RUN] {output_filename} | {speaker_tag} | {len(text)} chars | {len(chunks)} chunk(s)")
        return {
            "status": "dry_run",
            "file": output_filename,
            "speaker": speaker_tag,
            "chunks": len(chunks),
            "chars": len(text)
        }

    gen_defaults = config.get("generation_defaults", {})
    profile_cfg = config.get("profiles", {}).get(profile_key, {})
    time_stretch_rate = profile_cfg.get("post_process", {}).get("time_stretch")  # None = disabled

    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_filename = f"day_{day:02d}_seg_{segment_index:03d}_{speaker_tag}_chunk{i:02d}.wav"
        chunk_path = output_dir / chunk_filename

        success = False
        for attempt in range(1, MAX_RETRIES + 2):
            logger.info(f"  Chunk {i+1}/{len(chunks)} attempt {attempt}: {len(chunk)} chars")
            try:
                result = client.generate(
                    text=chunk,
                    profile_id=profile_id,
                    instruct=instruct,
                    language="en",
                    engine=config.get("engine", "qwen"),
                    model_size=config.get("model_size", "1.7B"),
                    max_chunk_chars=gen_defaults.get("max_chunk_chars", 800),
                    crossfade_ms=gen_defaults.get("crossfade_ms", 50),
                    normalize=gen_defaults.get("normalize", True),
                )
                gen_id = result.get("id")
                if not gen_id:
                    raise ValueError("No generation ID returned")

                # Poll until audio is ready
                final = _poll_until_done(client, gen_id)
                if final.get("status") == "completed":
                    try:
                        client.download_audio(gen_id, str(chunk_path))
                        if chunk_path.exists() and chunk_path.stat().st_size > 1000:
                            logger.info(f"    OK: {chunk_path.name} ({chunk_path.stat().st_size//1024}KB, {final.get('duration', 0):.1f}s)")
                            success = True
                            break
                        else:
                            sz = chunk_path.stat().st_size if chunk_path.exists() else 0
                            logger.warning(f"    Downloaded but file too small ({sz} bytes), retrying")
                    except Exception as dl_err:
                        logger.warning(f"    Download error: {dl_err}, retrying")
                    time.sleep(3)
                else:
                    logger.warning(f"    Attempt {attempt} failed: status={final.get('status')}")
                    time.sleep(3)
            except Exception as e:
                logger.error(f"    Attempt {attempt} exception: {e}")
                time.sleep(3)

        if not success:
            logger.error(f"  Segment {segment_index} chunk {i} failed after {MAX_RETRIES+1} attempts")
            return {"status": "error", "file": output_filename, "failed_chunk": i}

        chunk_files.append(str(chunk_path))

    # Merge chunks if multiple
    if len(chunk_files) == 1:
        Path(chunk_files[0]).rename(output_path)
    else:
        _merge_wav_chunks(chunk_files, output_path)
        for cf in chunk_files:
            Path(cf).unlink(missing_ok=True)

    # Post-process: time stretch if configured
    if time_stretch_rate and time_stretch_rate != 1.0:
        _apply_time_stretch(output_path, time_stretch_rate)

    return {
        "status": "generated",
        "file": output_filename,
        "speaker": speaker_tag,
        "type": segment_type,
    }


def _merge_wav_chunks(chunk_files: list, output_path: Path) -> None:
    """Concatenate multiple WAV files into one."""
    import wave
    with wave.open(chunk_files[0], 'rb') as first:
        params = first.getparams()

    with wave.open(str(output_path), 'wb') as out:
        out.setparams(params)
        for cf in chunk_files:
            with wave.open(cf, 'rb') as w:
                out.writeframes(w.readframes(w.getnframes()))
    logger.info(f"  Merged {len(chunk_files)} chunks → {output_path.name}")


def process_day(client: VoiceBoxClient, config: dict, day: int, dry_run: bool = False) -> dict:
    """Process all segments for a single day."""
    script_file = SCRIPTS_DIR / f"day_{day:02d}_tony.json"

    if not script_file.exists():
        logger.error(f"Script not found: {script_file}")
        return {"status": "error", "reason": "Script not found"}

    with open(script_file, 'r', encoding='utf-8') as f:
        script = json.load(f)

    day_audio_dir = AUDIO_DIR / f"day_{day:02d}"
    day_audio_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"\n=== Day {day}: {script.get('title', 'Unknown')} ===")

    results = []
    for i, segment in enumerate(script.get("segments", [])):
        logger.info(f"[{i+1}/{len(script['segments'])}] {segment['speaker']} / {segment.get('type','?')}")
        result = generate_segment_audio(
            client=client, segment=segment, day=day,
            segment_index=i, output_dir=day_audio_dir,
            config=config, dry_run=dry_run
        )
        results.append(result)
        if not dry_run:
            time.sleep(2)  # Brief pause between segments to avoid queue overload

    n_ok = sum(1 for r in results if r.get("status") == "generated")
    manifest = {
        "day": day,
        "title": script.get("title", ""),
        "segments_total": len(results),
        "segments_generated": n_ok,
        "results": results
    }

    manifest_file = day_audio_dir / "manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"Day {day} done: {n_ok}/{len(results)} segments generated → {manifest_file}")
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
            logger.error("VoiceBox is not running!")
            sys.exit(1)
        logger.info("VoiceBox connection OK")

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    if process_day_num:
        process_day(client, config, process_day_num, dry_run=dry_run)
    else:
        script_files = sorted(SCRIPTS_DIR.glob("day_*_tony.json"))
        if not script_files:
            logger.error(f"No scripts found in {SCRIPTS_DIR}")
            sys.exit(1)
        for script_file in script_files:
            day = int(script_file.stem.split('_')[1])
            process_day(client, config, day, dry_run=dry_run)


if __name__ == "__main__":
    main()

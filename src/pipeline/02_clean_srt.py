"""Pipeline Step 02: Clean and process all SRT files.

Reads raw SRT files from data/raw/srt/, cleans them, and outputs
structured JSON files to data/processed/clean_scripts/.

Usage:
    python -m src.pipeline.02_clean_srt [--day N] [--all]
"""
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.srt_parser import parse_srt, reconstruct_sentences, extract_full_text
from src.utils.text_cleaner import fix_capitalization, fix_arduino_terms, segment_by_topic


SRT_DIR = PROJECT_ROOT / "data" / "raw" / "srt"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "clean_scripts"


def extract_day_number(filename: str) -> int | None:
    """Extract day number from SRT filename."""
    match = re.search(r'Day\s*(\d+)', filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def process_srt(srt_path: Path) -> dict:
    """Process a single SRT file into a clean structured output."""
    day_num = extract_day_number(srt_path.name)

    entries = parse_srt(srt_path)
    segments = reconstruct_sentences(entries)
    full_text = extract_full_text(segments, speech_only=True)

    full_text = fix_capitalization(full_text)
    full_text = fix_arduino_terms(full_text)

    topic_segments = segment_by_topic(full_text)

    result = {
        "day": day_num,
        "source_file": srt_path.name,
        "total_duration_ms": segments[-1].end_ms if segments else 0,
        "word_count": len(full_text.split()),
        "full_text": full_text,
        "segments": [
            {
                "type": seg["type"],
                "text": seg["text"],
                "word_count": len(seg["text"].split())
            }
            for seg in topic_segments
        ],
        "timed_segments": [
            {
                "start_ms": seg.start_ms,
                "end_ms": seg.end_ms,
                "start_tc": f"{seg.start_ms // 60000:02d}:{(seg.start_ms % 60000) // 1000:02d}",
                "end_tc": f"{seg.end_ms // 60000:02d}:{(seg.end_ms % 60000) // 1000:02d}",
                "text": seg.text,
                "type": seg.segment_type
            }
            for seg in segments
        ]
    }

    return result


def main():
    """Process SRT files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    process_day = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--day" and len(sys.argv) > 2:
            process_day = int(sys.argv[2])
        elif sys.argv[1] != "--all":
            print("Usage: python -m src.pipeline.02_clean_srt [--day N] [--all]")
            sys.exit(1)

    srt_files = sorted(SRT_DIR.glob("*.srt"))

    if not srt_files:
        print(f"No SRT files found in {SRT_DIR}")
        sys.exit(1)

    print(f"Found {len(srt_files)} SRT files in {SRT_DIR}")
    print("=" * 60)

    results = []

    for srt_path in srt_files:
        day_num = extract_day_number(srt_path.name)

        if process_day is not None and day_num != process_day:
            continue

        print(f"\nProcessing: {srt_path.name}")
        print(f"  Day: {day_num}")

        try:
            result = process_srt(srt_path)

            output_file = OUTPUT_DIR / f"day_{day_num:02d}_clean.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"  Words: {result['word_count']}")
            dur_min = result['total_duration_ms'] // 60000
            dur_sec = (result['total_duration_ms'] % 60000) // 1000
            print(f"  Duration: {dur_min}m {dur_sec}s")
            print(f"  Segments: {len(result['segments'])}")
            print(f"  -> Saved: {output_file.name}")

            results.append(result)

        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()

    # Save summary
    if results:
        summary = {
            "total_days": len(results),
            "total_words": sum(r["word_count"] for r in results),
            "days": [
                {
                    "day": r["day"],
                    "words": r["word_count"],
                    "duration_minutes": round(r["total_duration_ms"] / 60000, 1),
                    "segments": len(r["segments"])
                }
                for r in sorted(results, key=lambda x: x["day"] or 0)
            ]
        }

        summary_file = OUTPUT_DIR / "summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n{'=' * 60}")
        print(f"SUMMARY: Processed {len(results)} days, {summary['total_words']} total words")
        print(f"Saved to: {summary_file}")


if __name__ == "__main__":
    main()

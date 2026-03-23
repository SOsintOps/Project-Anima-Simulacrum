"""Pipeline Step 03: Segment clean scripts into structured blocks.

Takes the cleaned scripts from Step 02 and segments them into
blocks suitable for rewriting: intro, tutorial, code, practical, outro.

Usage:
    python -m src.pipeline.03_segment_script [--day N] [--all]
"""
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CLEAN_DIR = PROJECT_ROOT / "data" / "processed" / "clean_scripts"
SEGMENTED_DIR = PROJECT_ROOT / "data" / "processed" / "segmented_scripts"
STORY_BIBLE = PROJECT_ROOT / "config" / "story_bible.json"


def load_story_bible() -> dict:
    with open(STORY_BIBLE, 'r', encoding='utf-8') as f:
        return json.load(f)


def detect_section_boundaries(text: str) -> list[dict]:
    """Detect natural section boundaries in the script text."""
    sections = []
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

    patterns = {
        'narrative_intro': [
            r"(?:rise and shine|good morning|welcome|explorer|today)",
            r"(?:mission|situation|survive|oxygen|ship|space)",
        ],
        'component_intro': [
            r"(?:what is|let's talk about|introducing|meet the)",
            r"(?:breadboard|LED|resistor|component|sensor|display|buzzer|keypad)",
        ],
        'tutorial': [
            r"(?:let's begin|let's start|first thing|to begin|step one|now let's)",
            r"(?:you'll need|grab|take|select|open|navigate|click)",
        ],
        'code_explanation': [
            r"(?:let's (?:look at|take a look at) the code|the code|sketch|program|function|setup\(\)|loop\(\))",
            r"(?:compile|upload|syntax|variable|digital\s*Write|analog)",
        ],
        'practical': [
            r"(?:go ahead|try it|your turn|now you|plug in|connect the)",
        ],
        'narrative_outro': [
            r"(?:well done|great job|congratulations|that's it)",
            r"(?:tomorrow|next time|see you|sweet dreams|rest assured)",
        ],
    }

    current_type = 'narrative_intro'
    current_sentences = []

    for sentence in sentences:
        sentence_lower = sentence.lower()

        scores = {}
        for stype, pats in patterns.items():
            score = sum(1 for p in pats if re.search(p, sentence_lower))
            scores[stype] = score

        best_type = max(scores, key=scores.get) if max(scores.values()) > 0 else current_type

        if best_type != current_type and len(current_sentences) >= 2 and scores[best_type] >= 1:
            sections.append({
                'type': current_type,
                'text': ' '.join(current_sentences),
                'sentence_count': len(current_sentences)
            })
            current_sentences = []
            current_type = best_type

        current_sentences.append(sentence)

    if current_sentences:
        sections.append({
            'type': current_type,
            'text': ' '.join(current_sentences),
            'sentence_count': len(current_sentences)
        })

    return sections


def enrich_with_story_context(day: int, sections: list[dict], story_bible: dict) -> dict:
    """Add narrative context from the story bible."""
    day_mission = None
    for mission in story_bible.get("day_missions", []):
        if mission["day"] == day:
            day_mission = mission
            break

    if day <= 10:
        act = story_bible["narrative_arc"]["act_1_survival"]
        act_name = "Act 1: Survival"
    elif day <= 20:
        act = story_bible["narrative_arc"]["act_2_rebuilding"]
        act_name = "Act 2: Rebuilding"
    else:
        act = story_bible["narrative_arc"]["act_3_breakthrough"]
        act_name = "Act 3: Breakthrough"

    return {
        "day": day,
        "act": act_name,
        "act_tone": act.get("tone", ""),
        "jarvis_state": act.get("jarvis_state", ""),
        "mission": day_mission if day_mission else {"mission": f"Day {day}", "objective": "", "narrative": ""},
        "sections": sections,
        "rewrite_ready": True
    }


def main():
    SEGMENTED_DIR.mkdir(parents=True, exist_ok=True)
    story_bible = load_story_bible()

    process_day_num = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--day" and len(sys.argv) > 2:
            process_day_num = int(sys.argv[2])

    clean_files = sorted(CLEAN_DIR.glob("day_*_clean.json"))

    if not clean_files:
        print(f"No clean scripts found in {CLEAN_DIR}")
        print("Run Step 02 first: python -m src.pipeline.02_clean_srt --all")
        sys.exit(1)

    print(f"Found {len(clean_files)} clean scripts")
    print("=" * 60)

    for clean_file in clean_files:
        day = int(clean_file.stem.split('_')[1])

        if process_day_num is not None and day != process_day_num:
            continue

        print(f"\nSegmenting Day {day}...")

        with open(clean_file, 'r', encoding='utf-8') as f:
            clean_data = json.load(f)

        full_text = clean_data["full_text"]
        sections = detect_section_boundaries(full_text)
        result = enrich_with_story_context(day, sections, story_bible)
        result["source_word_count"] = clean_data["word_count"]
        result["source_duration_ms"] = clean_data["total_duration_ms"]

        output_file = SEGMENTED_DIR / f"day_{day:02d}_segmented.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"  Sections: {len(result['sections'])}")
        for sec in result['sections']:
            print(f"    - {sec['type']}: {sec['sentence_count']} sentences")
        print(f"  Mission: {result['mission'].get('mission', 'N/A')}")
        print(f"  -> Saved: {output_file.name}")

    print(f"\n{'=' * 60}")
    print("Segmentation complete. Ready for rewriting (Step 04).")


if __name__ == "__main__":
    main()

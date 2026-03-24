"""Pipeline Step 04: Rewrite scripts in Tony Stark + JARVIS style.

Takes segmented scripts and produces rewritten versions with:
- Tony Stark as primary narrator (tutorial, intro, outro)
- JARVIS as secondary narrator (briefings, alerts, confirmations)
- Marvel narrative framing from the story bible

This step is SEMI-MANUAL: generates LLM prompts, saves results for review.

Usage:
    python -m src.pipeline.04_rewrite_tony [--day N] [--generate-prompts] [--apply FILE]
"""
import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

SEGMENTED_DIR = PROJECT_ROOT / "data" / "processed" / "segmented_scripts"
TONY_SCRIPTS_DIR = PROJECT_ROOT / "data" / "processed" / "tony_scripts"
PROMPTS_DIR = PROJECT_ROOT / "data" / "processed" / "rewrite_prompts"
CONFIG_DIR = PROJECT_ROOT / "config"


def load_config(name: str) -> dict:
    with open(CONFIG_DIR / name, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_rewrite_prompt(day_data: dict) -> str:
    """Build a detailed LLM prompt to rewrite a day's script."""
    tony_style = load_config("tony_style.json")
    jarvis_style = load_config("jarvis_style.json")
    story_bible = load_config("story_bible.json")

    day = day_data["day"]
    mission = day_data["mission"]
    act = day_data["act"]
    jarvis_state = day_data["jarvis_state"]

    original_sections = ""
    for i, sec in enumerate(day_data["sections"]):
        original_sections += f"\n--- SECTION {i+1} ({sec['type']}) ---\n{sec['text']}\n"

    prompt = f"""You are rewriting an electronics course script. The original course features "Astrid", an AI companion guiding a student through Arduino/electronics projects in a sci-fi setting.

You must rewrite this as a scene between TONY STARK and J.A.R.V.I.S. from the Marvel Cinematic Universe.

## CONTEXT FOR DAY {day}

**Act**: {act}
**Mission**: {mission.get('mission', 'N/A')}
**Objective**: {mission.get('objective', 'N/A')}
**Narrative**: {mission.get('narrative', 'N/A')}
**JARVIS State**: {jarvis_state}

## SETTING
{story_bible['premise']}

## TONY STARK STYLE GUIDE
- Sarcasm level: {tony_style['style_knobs']['sarcasm']}/10
- Tech jargon: {tony_style['style_knobs']['tech_jargon']}/10
- Warmth: {tony_style['style_knobs']['warmth']}/10
- Humor every {tony_style['style_knobs']['humor_frequency']}
- Sentence starters: {', '.join(tony_style['speech_patterns']['sentence_starters'][:5])}
- Nicknames for student: {', '.join(tony_style['speech_patterns']['nicknames_for_student'])}
- {tony_style['speech_patterns']['technical_analogies']}
- Target audience: 15-year-old recruit (Peter Parker dynamic)

## JARVIS STYLE GUIDE
- Formality: {jarvis_style['style_knobs']['formality']}/10
- Dry humor: {jarvis_style['style_knobs']['dry_humor']}/10
- Address forms: {', '.join(jarvis_style['speech_patterns']['address_forms'])}
- Role: {jarvis_style['role_in_course']['briefings']}

## EPISODE STRUCTURE (must follow this order)
1. JARVIS BRIEFING (15-30 sec): System status, power level, today's priority
2. TONY INTRO (45-90 sec): Video transmission opens, greeting, mission framing
3. TONY TUTORIAL (main body): Technical instruction with JARVIS interjections
4. TONY OUTRO (30-60 sec): Summary, encouragement, tomorrow teaser, sign-off

## RULES
- ALL technical content must be preserved accurately — same Arduino concepts, same code, same components
- Tony explains things HIS way but the information must be correct
- JARVIS adds precision where Tony is casual, caution where Tony is bold
- The student (recruit) never speaks — Tony and JARVIS address them directly
- Include natural Tony/JARVIS banter during technical sections
- Reference the Marvel narrative naturally (outpost, systems, mission)

## ORIGINAL SCRIPT (ASTRID VERSION)
{original_sections}

## OUTPUT FORMAT
Return a JSON array of segments. Each segment MUST have ALL of these fields:
- "speaker": "TONY" or "JARVIS"
- "type": one of "briefing", "intro", "tutorial", "code_explanation", "practical", "banter", "alert", "confirmation", "outro"
- "text": the rewritten dialogue (natural spoken English, ready for TTS). Write as spoken word — no abbreviations, spell out numbers where natural. Avoid parentheses and brackets. Use commas and periods strategically to control TTS pacing.
- "instruct": a TTS voice direction string (max 500 chars) that describes HOW this specific segment should sound. This controls the AI voice engine's tone, pace, emotion, and delivery. Be specific and vivid. Examples:
  - For Tony tutorial: "Confident teaching voice. Warm, patient, conversational. Medium pace with natural pauses. Like explaining something cool to a smart teenager."
  - For Tony emotional: "Warm, proud, slightly emotional. Slower pace, meaningful pauses. A mentor who's genuinely impressed but trying to stay cool about it."
  - For JARVIS alert: "Calm, precise British male. Urgent but controlled. Slightly faster pace. Formal, measured, clinical."
  - For JARVIS confirmation: "Calm, satisfied British male. Slight warmth in the 'well done'. Measured, precise."
- "stage_direction": a brief note about the character's emotional state and context (used for video direction, not TTS)

## INSTRUCT GUIDELINES
The "instruct" field is THE most important field for voice quality. It goes directly to the TTS engine. Rules:
1. ALWAYS specify gender and accent (e.g., "American male", "British male")
2. Describe emotion, pacing, and energy level
3. Use analogies ("like a teacher", "like a worried parent trying to sound calm")
4. Vary the instruct across segments — Tony starts confident, builds excitement, gets emotional at sign-off
5. JARVIS instruct should always include "British male", "precise", "measured"
6. Keep under 500 characters

IMPORTANT: Return ONLY the JSON array. No markdown, no explanation. Just the raw JSON.
"""
    return prompt


def create_tony_script_template(day: int, day_data: dict) -> dict:
    """Create a template for the Tony script."""
    mission = day_data["mission"]

    return {
        "day": day,
        "title": mission.get("mission", f"Day {day}"),
        "objective": mission.get("objective", ""),
        "narrative": mission.get("narrative", ""),
        "act": day_data["act"],
        "segments": [
            {
                "speaker": "JARVIS",
                "type": "briefing",
                "text": "[JARVIS briefing - system status, today's priority]",
                "stage_direction": "calm, measured"
            },
            {
                "speaker": "TONY",
                "type": "intro",
                "text": "[Tony's opening - greeting, situation update, mission framing]",
                "stage_direction": "confident, warm"
            },
            {
                "speaker": "TONY",
                "type": "tutorial",
                "text": "[Main tutorial content - rewrite from original]",
                "stage_direction": "teaching mode"
            },
            {
                "speaker": "TONY",
                "type": "outro",
                "text": "[Tony's closing - summary, encouragement, tomorrow teaser]",
                "stage_direction": "encouraging, hint of pride"
            }
        ],
        "_original_sections": day_data["sections"],
        "_rewrite_status": "template",
        "_last_updated": datetime.now().isoformat()
    }


def apply_rewrite(day: int, rewrite_file: Path) -> None:
    """Apply a rewrite from an LLM response file."""
    with open(rewrite_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    try:
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
        segments = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"  ERROR: Could not parse rewrite as JSON: {e}")
        return

    # Validate segments have required fields
    required_fields = {"speaker", "type", "text", "instruct"}
    for i, seg in enumerate(segments):
        missing = required_fields - set(seg.keys())
        if missing:
            print(f"  WARNING: Segment {i} missing fields: {missing}")
            if "instruct" not in seg:
                # Auto-generate a basic instruct from speaker
                speaker = seg.get("speaker", "TONY").upper()
                if speaker in ("TONY", "TONY STARK"):
                    seg["instruct"] = "Confident, warm American male. Natural conversational pace."
                else:
                    seg["instruct"] = "Calm, measured British male. Precise, formal delivery."
                print(f"    -> Auto-filled instruct for {speaker}")

    segmented_file = SEGMENTED_DIR / f"day_{day:02d}_segmented.json"
    with open(segmented_file, 'r', encoding='utf-8') as f:
        day_data = json.load(f)

    mission = day_data["mission"]

    tony_script = {
        "day": day,
        "title": mission.get("mission", f"Day {day}"),
        "objective": mission.get("objective", ""),
        "narrative": mission.get("narrative", ""),
        "act": day_data["act"],
        "segments": segments,
        "_rewrite_status": "applied",
        "_source": str(rewrite_file),
        "_last_updated": datetime.now().isoformat()
    }

    output_file = TONY_SCRIPTS_DIR / f"day_{day:02d}_tony.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tony_script, f, indent=2, ensure_ascii=False)

    print(f"  Applied rewrite: {len(segments)} segments -> {output_file.name}")


def main():
    TONY_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

    generate_prompts = "--generate-prompts" in sys.argv
    apply_file = None
    process_day_num = None

    for i, arg in enumerate(sys.argv):
        if arg == "--day" and i + 1 < len(sys.argv):
            process_day_num = int(sys.argv[i + 1])
        if arg == "--apply" and i + 1 < len(sys.argv):
            apply_file = Path(sys.argv[i + 1])

    if apply_file and process_day_num:
        print(f"Applying rewrite for Day {process_day_num} from {apply_file}")
        apply_rewrite(process_day_num, apply_file)
        return

    segmented_files = sorted(SEGMENTED_DIR.glob("day_*_segmented.json"))

    if not segmented_files:
        print(f"No segmented scripts found in {SEGMENTED_DIR}")
        print("Run Step 03 first: python -m src.pipeline.03_segment_script --all")
        sys.exit(1)

    print(f"Found {len(segmented_files)} segmented scripts")
    print("=" * 60)

    for seg_file in segmented_files:
        day = int(seg_file.stem.split('_')[1])

        if process_day_num is not None and day != process_day_num:
            continue

        print(f"\nDay {day}:")

        if generate_prompts:
            with open(seg_file, 'r', encoding='utf-8') as f:
                day_data = json.load(f)
            prompt = build_rewrite_prompt(day_data)

            prompt_file = PROMPTS_DIR / f"day_{day:02d}_prompt.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)

            print(f"  Prompt saved: {prompt_file.name}")
            print(f"  Est. tokens: ~{int(len(prompt.split()) * 1.3)}")
        else:
            with open(seg_file, 'r', encoding='utf-8') as f:
                day_data = json.load(f)

            template = create_tony_script_template(day, day_data)

            output_file = TONY_SCRIPTS_DIR / f"day_{day:02d}_tony.json"
            if not output_file.exists():
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(template, f, indent=2, ensure_ascii=False)
                print(f"  Template created: {output_file.name}")
            else:
                print(f"  Script already exists: {output_file.name} (skipping)")

    print(f"\n{'=' * 60}")
    if generate_prompts:
        print(f"Prompts saved to: {PROMPTS_DIR}")
        print("Send each prompt to an LLM, save the response, then apply with:")
        print("  python -m src.pipeline.04_rewrite_tony --day N --apply response.json")
    else:
        print(f"Templates saved to: {TONY_SCRIPTS_DIR}")
        print("To generate LLM rewrite prompts, run with --generate-prompts")


if __name__ == "__main__":
    main()

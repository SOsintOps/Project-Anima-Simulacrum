# Project Status

**Last updated:** 2026-05-06

## Objective

Transform the "30 Days Lost in Space" electronics course into a fully voiced narrative experience featuring Tony Stark and J.A.R.V.I.S., using VoiceBox for local TTS generation. Additionally, test the Stories pipeline with theatre scripts (Euro Star).

## Project Structure

```
applicazione/
  30_days_lost_in_space/    <- TTS course narrative
    pipeline/               <- all pipeline scripts (02-05, utilities)
    config/                 <- story_bible, voicebox_config, style JSONs
    data/                   <- raw SRT, processed scripts, output audio
    docs/research/          <- voice replication research
  massoneria/               <- documentation archive
  teatro/                   <- theatre scripts + Euro Star pipeline
    pipeline/               <- generate_eurostar_story, split_monologues
    eurostar_act1_*.json    <- parsed/segmented script
    output/eurostar_act1/   <- generated audio output
src/
  voicebox/client.py        <- VoiceBox REST API client (v0.5.0)
```

## Logical State

**What works:**

- VoiceBox client upgraded to v0.5.0 (new engines, personality, cancel, speak, transcribe, compose)
- Pipeline steps 02-05 functional with APP_DIR path structure
- Euro Star Act 1 fully parsed: 83 lines, 3 characters (Arthur, Marilyn, Voice)
- Instruct per line extracted from stage directions
- Generation script with resume capability, state persistence, and ambient mixing
- Train ambient audio available for post-processing mix
- Code review completed: 3 bugs fixed, dead code removed, quality improvements applied

**What does not work / is incomplete:**

- Euro Star generation not yet run (needs VoiceBox running)
- Voice preset mapping not yet configured (interactive selection at runtime)
- 30 Days: Days 3-30 Tony scripts not yet generated
- Research recommendations (enriched prompts, instruct templates, quality gate) not yet implemented

**What is blocked:**

- Story generation requires VoiceBox running on port 17493

## Recent Changes (2026-05-06)

- Fixed bug in `generate_eurostar_story.py`: interactive voice selection returned wrong type
- Fixed bug in `split_monologues.py`: original line count printed incorrectly
- Fixed bug in `text_cleaner.py`: section detection could skip first match
- Improved `voicebox_profiles.py`: unknown characters now raise explicit error
- Removed dead code (`prepare_for_tts`, duplicate `get_generation`)
- Reduced inter-segment sleep from 2s to 0.5s in audio generation

## Next Actions

### 30 Days Lost in Space
1. Implement research recommendations: enrich `tony_style.json` with golden/anti-examples
2. Create per-act instruct templates in `voicebox_config.json`
3. Modify `04_rewrite_tony.py` to inject day-specific emotional context
4. Generate Tony scripts for Days 3-30
5. Start VoiceBox and generate audio for Day 1

### Euro Star
1. Start VoiceBox
2. Run `python applicazione/teatro/pipeline/generate_eurostar_story.py --list-voices`
3. Select voice presets for Arthur, Marilyn, Voice
4. Run full generation

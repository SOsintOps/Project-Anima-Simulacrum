# Project Status

**Last updated:** 2026-05-05

## Objective

Transform the "30 Days Lost in Space" electronics course into a fully voiced narrative experience featuring Tony Stark and J.A.R.V.I.S., using VoiceBox for local TTS generation. Additionally, test the Stories pipeline with theatre scripts.

## Modified Files

| File | Reason |
|------|--------|
| `src/voicebox/client.py` | Upgraded to VoiceBox v0.5.0 API |
| `src/pipeline/02_clean_srt.py` | Path refactor (APP_DIR) |
| `src/pipeline/03_segment_script.py` | Path refactor (APP_DIR) |
| `src/pipeline/04_rewrite_tony.py` | Path refactor (APP_DIR) |
| `src/pipeline/05_generate_audio.py` | Path refactor (APP_DIR) |
| `src/pipeline/test_stories.py` | Stories smoke test (Tony+JARVIS) |
| `src/pipeline/generate_eurostar_story.py` | Euro Star Act 1 full Story generation |
| `applicazione/teatro/eurostar_act1_parsed.json` | 83 parsed dialogue lines with instruct |

## Project Structure

```
applicazione/
  30_days_lost_in_space/    <- TTS course narrative (data, config, docs)
  massoneria/               <- documentation archive
  teatro/                   <- theatre scripts + generated output
    eurostar_act1_parsed.json
    Train Ride Experience/  <- train ambient audio for mixing
    output/eurostar_act1/   <- generated audio output
src/                        <- engine code (pipeline, voicebox client v0.5.0)
config/voicebox_config.json <- engine-level config
```

## Logical State

**What works:**

- VoiceBox client upgraded to v0.5.0 (new engines, personality, cancel, speak, transcribe, compose)
- Pipeline steps 02-05 functional with APP_DIR path structure
- Euro Star Act 1 fully parsed: 83 lines, 3 characters (Arthur, Marilyn, Voice)
- Instruct per line extracted from stage directions
- Generation script with resume capability, state persistence, and ambient mixing
- Train ambient audio available for post-processing mix

**What does not work / is incomplete:**

- Euro Star generation not yet run (needs VoiceBox running)
- Voice preset mapping not yet configured (interactive selection at runtime)
- 30 Days: Days 3-30 Tony scripts not yet generated

**What is blocked:**

- Story generation test requires VoiceBox running on port 17493

## Next Action

1. Start VoiceBox
2. Run `python -m src.pipeline.generate_eurostar_story --list-voices` to see available presets
3. Run `python -m src.pipeline.generate_eurostar_story` to generate full Act 1
4. Review output at `applicazione/teatro/output/eurostar_act1/`

# Project Status

**Last updated:** 2026-05-05

## Objective

Transform the "30 Days Lost in Space" electronics course into a fully voiced narrative experience featuring Tony Stark and J.A.R.V.I.S., using VoiceBox for local TTS generation.

## Modified Files

| File | Reason |
|------|--------|
| `PROJECT_STATUS.md` | Created — Codex Machinae §2.3 compliance |
| `CLAUDE.md` | Created — agent configuration §2.4 |
| `DEPENDENCIES.md` | Created — dependency contracts §2.2 |
| `CHANGELOG.md` | Created — retroactive release history |
| `README.md` | Updated to reflect actual project state |

## Logical State

**What works:**

- Pipeline steps 02–05 functional (clean SRT → segment → rewrite → generate audio)
- VoiceBox client (`src/voicebox/client.py`) wraps local API at port 17493
- 30 days of SRT transcripts cleaned and segmented
- Tony Stark rewrite prompts generated for all 30 days
- Day 1–2 Tony scripts fully rewritten
- Day 1 audio generated (multiple speed/pause iterations)
- Two voice profiles configured: Tony Stark, J.A.R.V.I.S.
- Story Bible defines full 30-day narrative arc

**What does not work / is incomplete:**

- Days 3–30 Tony scripts not yet generated (only rewrite prompts exist)
- No audio generated beyond Day 1
- VoiceBox client targets v0.3.0 API — project uses v0.4.x locally (untested against v0.5)
- No J.A.R.V.I.S. scripts generated yet (only briefing structure defined)
- No tests exist
- Stories editor integration (multi-voice timeline) not yet used in pipeline

**What is blocked:**

- Nothing externally blocked. Next steps are execution work.

## Next Action

Upgrade `src/voicebox/client.py` to support VoiceBox v0.5.0 API changes (new engines: Kokoro, HumeAI TADA, Qwen CustomVoice). Then batch-generate Tony scripts for Days 3–30.

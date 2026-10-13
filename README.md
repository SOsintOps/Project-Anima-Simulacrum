# Project Anima Simulacrum

**AI-powered narrative voice pipeline for educational content.**

---

## What This Is

Project Anima Simulacrum transforms the [30 Days Lost in Space](https://inventr.io/) electronics course into a fully voiced narrative experience. Tony Stark mentors a stranded recruit through 30 days of Arduino projects, with J.A.R.V.I.S. providing local AI support — all generated through local TTS using [VoiceBox](https://voicebox.sh/).

## Current State

**Version:** 0.3.1
**Phase:** Audio generation and narrative refinement

### What Works

- **Full text pipeline:** SRT transcripts → cleaned scripts → segmented by speaker/section → rewritten in character voice
- **VoiceBox integration:** REST API client for local TTS generation with voice cloning
- **Two voice profiles:** Tony Stark (confident mentor) and J.A.R.V.I.S. (British AI assistant)
- **30-day Story Bible:** Complete narrative arc with per-day missions mapped to the real Inventr.io curriculum
- **Day 1 audio generated** with iterative speed/pause tuning

### Pipeline Steps

```
02_clean_srt.py      → Strip timestamps, fix formatting from raw SRT files
03_segment_script.py → Split into jarvis_briefing / tony_intro / tony_tutorial / tony_outro
04_rewrite_tony.py   → Rewrite segments in Tony Stark's voice using LLM
05_generate_audio.py → Generate speech via VoiceBox API (Qwen3-TTS engine)
```

## Setup

**Requirements:**
- Python 3.11+
- [VoiceBox](https://voicebox.sh/) running locally on port 17493
- ffmpeg (for audio processing)

**Quick start:**

```bash
docker build -t anima-simulacrum .
docker run -it --network host anima-simulacrum
```

Or without Docker:

```bash
pip install -r requirements.txt
```

See [docs/install.md](./docs/install.md) for detailed setup.

## Project Structure

```
src/
  pipeline/        — Numbered pipeline steps (02–05)
  utils/           — Shared utilities (SRT parsing, text cleaning)
  voicebox/        — VoiceBox API client, profiles, speed correction
config/
  story_bible.json — 30-day narrative arc and character definitions
  voicebox_config.json — Voice profile IDs and generation defaults
  tony_style.json  — Tony Stark writing style guide
  jarvis_style.json — J.A.R.V.I.S. writing style guide
data/
  raw/             — Source SRT transcripts and reference materials
  processed/       — Pipeline intermediate outputs (clean, segmented, rewritten)
  output/          — Final generated audio files
```

## Governance

This project follows the [Codex Machinae](https://github.com/SOsintOps/codex-machinae) framework (Solo profile, D5 ML/Data Pipeline domain). A vendored copy is kept in [`codex-machinae.md`](./codex-machinae.md); it is an early draft (2.0.0, 15 April 2026), so the GitHub repository is the current reference.

## Related projects

- [Codex Machinae](https://github.com/SOsintOps/codex-machinae): the playbook for building software with LLM collaborators that this project follows.
- [Il Conclave](https://github.com/SOsintOps/il-conclave): another multi-procedure, multi-persona LLM project: a Claude Code skill (in Italian) that runs analytic procedures such as ACH and a premortem, then an anonymous peer review and a synthesis.

More in the [FAQ](./docs/faq.md).

## Licence

MIT — see [LICENSE](./LICENSE).

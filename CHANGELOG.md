# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/) and the project
uses [Conventional Commits](https://www.conventionalcommits.org/).

## [Unreleased]

### Added
- `PROJECT_STATUS.md` — Codex Machinae §2.3 compliance
- `CLAUDE.md` — agent configuration per §2.4
- `DEPENDENCIES.md` — dependency registry per §2.2
- `CHANGELOG.md` — this file
- Updated `README.md` to reflect actual project state
- `docs/research/index.md` — research register per §1.7
- `docs/research/2026-05-05-character-voice-replication.md` — character voice replication research (best practices, pipeline architecture, recommendations)
- `docs/research/2026-05-05-character-voice-replication-report.docx` — full DOCX report covering linguistic profiling, persona-consistent generation, personality duplication (Tony Stark case study), neural voice synthesis, and pipeline architecture

### Fixed
- `generate_eurostar_story.py`: interactive voice selection returned `str` instead of `dict`, causing crash in `generate_all_lines()`
- `split_monologues.py`: "Original: N lines" counter printed post-replacement count instead of original
- `text_cleaner.py`: `segment_by_topic()` inner loop `break` did not exit outer loop, allowing later types to overwrite match
- `voicebox_profiles.py`: unknown character silently fell through to "jarvis" profile; now raises `ValueError`

### Changed
- `05_generate_audio.py`: replaced `__import__('datetime')` hack with proper import; reduced inter-segment sleep from 2s to 0.5s

### Removed
- `text_cleaner.py`: dead `prepare_for_tts()` function (never called, superseded by `speed_fix.py`)
- `client.py`: duplicate `get_generation()` method (identical to `get_generation_info()`)

## [0.3.1] — 2026-10-13

### Docs
- `docs/faq.md` and `docs/install.md` translated into English; the FAQ gains a table of contents and answers on the development framework and related projects; the install guide clones the real repository URL instead of a placeholder.
- `README.md`: Codex Machinae linked to its GitHub repository (the vendored `codex-machinae.md` is an early 2.0.0 draft); new *Related projects* section citing Codex Machinae and Il Conclave.

## [0.3.0] — 2026-03-24

### Added
- Audio generation pipeline step (`05_generate_audio.py`)
- VoiceBox client (`src/voicebox/client.py`) — full REST API wrapper for 86 endpoints
- VoiceBox voice profiles module (`src/voicebox/profiles.py`)
- Speed correction module (`src/voicebox/speed_fix.py`)
- VoiceBox configuration (`config/voicebox_config.json`) with Tony Stark and J.A.R.V.I.S. profiles
- Story Bible (`config/story_bible.json`) — 30-day narrative arc
- Tony Stark style config (`config/tony_style.json`)
- J.A.R.V.I.S. style config (`config/jarvis_style.json`)
- Day 1 audio output with multiple speed/pause variations
- Tony scripts generated for Days 1–2

## [0.2.0] — 2026-03-23

### Added
- Script rewrite pipeline step (`04_rewrite_tony.py`) — rewrites clean scripts in Tony Stark's voice
- Rewrite prompts generated for all 30 days
- Segmented scripts for all 30 days (`data/processed/segmented_scripts/`)

## [0.1.0] — 2026-03-23

### Added
- Initial project setup
- SRT transcript cleaning pipeline (`02_clean_srt.py`)
- Script segmentation pipeline (`03_segment_script.py`)
- SRT parser utility (`src/utils/srt_parser.py`)
- Text cleaner utility (`src/utils/text_cleaner.py`)
- Clean scripts for all 30 days (`data/processed/clean_scripts/`)
- Raw data: SRT transcripts, MCU movie scripts, Astrid AI assistant reference docs
- Dockerfile for containerized environment
- README, FAQ, installation docs

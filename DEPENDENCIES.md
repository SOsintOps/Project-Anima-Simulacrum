# Dependencies

**Last reviewed:** 2026-05-06

## Runtime Dependencies

| Dependency | Version | Purpose | Licence | Justification |
|-----------|---------|---------|---------|---------------|
| `requests` | >= 2.31.0 | HTTP client for VoiceBox API | Apache 2.0 | Standard HTTP library, no lighter alternative needed for sync calls |
| `pydub` | >= 0.25.1 | Audio file manipulation (concatenation, crossfade, normalization) | MIT | Simplest API for audio segment operations; alternative (librosa) is heavier |
| `PyPDF2` | >= 3.0.0 | PDF text extraction (movie scripts) | BSD | Legacy use for MCU script ingestion; may be removed if not needed further |

## External Services

| Service | Version | Interface | Role | Local/Remote |
|---------|---------|-----------|------|--------------|
| **VoiceBox** | 0.5.0 | REST API at `127.0.0.1:17493` | TTS generation, voice cloning, story assembly | Local |

### VoiceBox API Contract

- The project depends on VoiceBox's REST API (86 endpoints documented in `src/voicebox/client.py`)
- Key endpoints: `/generate`, `/profiles`, `/stories`, `/audio/{id}`, `/models/status`
- TTS engine contract: uses `qwen` engine with `1.7B` model size (max TTS quality)
- Refinement/Personality LLM: Qwen3 0.6B / 1.7B / 4B — the 4B (2.5 GB) provides full-quality text refinement when `personality: true` is set
- Available engines: qwen, qwen_custom_voice, luxtts, chatterbox, chatterbox_turbo, tada, kokoro

## Development Dependencies

| Dependency | Purpose | Notes |
|-----------|---------|-------|
| Docker | Containerized environment | Defined in `Dockerfile` |
| Python 3.11+ | Runtime | Specified in Dockerfile |
| ffmpeg | Required by pydub for audio format conversion | System-level dependency |

## Dependency Health

| Dependency | Status | Last Check | Notes |
|-----------|--------|------------|-------|
| requests | healthy | 2026-05-05 | Stable, actively maintained |
| pydub | healthy | 2026-05-05 | Stable, low churn |
| PyPDF2 | watch | 2026-05-05 | Consider `pymupdf` if more PDF work needed |
| VoiceBox | healthy | 2026-05-06 | v0.5.0 — client upgraded, all new engines available |

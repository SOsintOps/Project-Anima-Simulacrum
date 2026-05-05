# Dependencies

**Last reviewed:** 2026-05-05

## Runtime Dependencies

| Dependency | Version | Purpose | Licence | Justification |
|-----------|---------|---------|---------|---------------|
| `requests` | >= 2.31.0 | HTTP client for VoiceBox API | Apache 2.0 | Standard HTTP library, no lighter alternative needed for sync calls |
| `pydub` | >= 0.25.1 | Audio file manipulation (concatenation, crossfade, normalization) | MIT | Simplest API for audio segment operations; alternative (librosa) is heavier |
| `PyPDF2` | >= 3.0.0 | PDF text extraction (movie scripts) | BSD | Legacy use for MCU script ingestion; may be removed if not needed further |

## External Services

| Service | Version | Interface | Role | Local/Remote |
|---------|---------|-----------|------|--------------|
| **VoiceBox** | 0.4.x (target: 0.5.0) | REST API at `127.0.0.1:17493` | TTS generation, voice cloning, story assembly | Local |

### VoiceBox API Contract

- The project depends on VoiceBox's REST API (86 endpoints documented in `src/voicebox/client.py`)
- Key endpoints: `/generate`, `/profiles`, `/stories`, `/audio/{id}`, `/models/status`
- Engine contract: currently uses `qwen` engine with `1.7B` model size
- Breaking change risk: VoiceBox v0.5.0 adds new engines (Kokoro, TADA, Qwen CustomVoice) and may modify existing endpoint signatures

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
| VoiceBox | evaluate | 2026-05-05 | v0.5.0 released 2026-04-25; client needs upgrade |

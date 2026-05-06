# Agent Configuration — Claude

**Project:** Project Anima Simulacrum
**Codex version:** 2.0.0
**Profile:** Solo
**Domain appendix:** D5 ML/Data Pipeline
**Cross-cutting modules:** None active yet

---

## Language and Style

- All documentation, comments, commit messages, and code identifiers in **English**.
- Conversational interaction with the developer may be in Italian (the developer's native language).
- Prose style: active voice, short sentences, concrete over abstract.
- No filler phrases ("it should be noted that…", "in order to…").

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| File | snake_case | `srt_parser.py`, `voicebox_config.json` |
| Class | PascalCase | `VoiceBoxClient`, `SrtParser` |
| Function/method | snake_case | `generate_audio()`, `clean_transcript()` |
| Constant | SCREAMING_SNAKE_CASE | `MAX_CHUNK_CHARS`, `API_BASE_URL` |
| Branch | `<type>/<short-description>` | `feat/voicebox-v05-upgrade` |
| Commit | Conventional Commits | `feat(voicebox): add kokoro engine support` |

## Permitted Modifications (Autonomy Levels)

| Level | Scope | Approval |
|-------|-------|----------|
| **L0** | Fix typos, formatting, comments | No approval needed |
| **L1** | Implement within an agreed plan, add tests, update docs | Proceed after confirming the plan |
| **L2** | Architectural changes, new dependencies, delete files | Explicit human approval required |

Default operating level: **L1** — the agent proposes a plan, the human confirms, then the agent executes.

## Protected Paths

These files/directories MUST NOT be modified without explicit human confirmation:

- `applicazione/30_days_lost_in_space/config/story_bible.json` — narrative source of truth
- `applicazione/30_days_lost_in_space/config/voicebox_config.json` — production voice profile IDs
- `applicazione/*/output/` — generated audio artifacts
- `codex-machinae.md` — project governance framework

## Project Size Profile: Solo

- Single developer (sandro)
- Codebase < 5000 lines
- Checklist items tagged `[Solo: optional]` in Appendix A may be skipped
- Focus on working software over ceremony

## Domain: D5 ML/Data Pipeline

Key implications:

- Data flows through discrete, numbered pipeline steps (`01_`, `02_`, …)
- Each step reads from a known input path and writes to a known output path
- Intermediate data is versioned by directory structure, not by filename timestamps
- Pipeline steps must be idempotent: running them twice produces the same output
- Config is separated from code (JSON files in `config/`)

## Conventions

- Each application lives in `applicazione/<name>/` with its own `pipeline/`, `config/`, `data/`
- Shared code (VoiceBox client) stays in `src/`
- Pipeline scripts are numbered: `NN_verb_noun.py` (e.g., `02_clean_srt.py`)
- Config files: one per concern in each app's `config/`
- Git: commit after each logical unit of work, not after each file save

## State-of-the-Art Research Triggers

The agent MUST suggest research when:

- A new TTS engine is being considered for integration
- VoiceBox releases a major version (API changes)
- A new voice cloning approach emerges that could improve quality
- The pipeline architecture needs significant changes

## Agent Behavior Rules

1. **Ask, don't assume.** If something is unclear or underspecified, ask before writing a single line. Never make silent assumptions about intent, architecture, or requirements.
2. **Simplest solution first.** Always implement the simplest thing that could work. Do not add abstractions, layers, or flexibility that weren't explicitly requested.
3. **Don't touch unrelated code.** If a file or function is not directly part of the current task, do not modify it, even if you think it could be improved.
4. **Flag uncertainty explicitly.** If you are not confident about an approach, a library's behavior, or a technical detail, say so before proceeding. Confidence without certainty causes more damage than admitting a gap.

## Definition of Done (Solo profile)

- [ ] Code runs without errors
- [ ] Output matches expected format
- [ ] Commit message follows Conventional Commits
- [ ] `PROJECT_STATUS.md` updated
- [ ] No protected paths modified without approval

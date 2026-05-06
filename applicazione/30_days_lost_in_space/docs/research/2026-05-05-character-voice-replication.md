# Research: Character Voice Replication — Best Practices

**Date:** 2026-05-05
**Trigger:** new feature (character persona fidelity improvement)
**Author:** AI agent + human

## Research Question

What are the current best practices for replicating a fictional character through AI — covering linguistic style (writing), vocal delivery (TTS), and persona consistency over long-form content?

## 1. Character Linguistic Profile (the "Writing" side)

### 1.1 What to capture

A character's linguistic DNA consists of measurable and reproducible traits:

| Dimension | What to document | Tony Stark example |
|-----------|-----------------|-------------------|
| **Vocabulary level** | Register, jargon, tech density | High-register vocabulary mixed with casual slang; heavy tech jargon used casually |
| **Sentence structure** | Length, complexity, fragmentation | Short declarative statements; fragments for emphasis; rhetorical questions |
| **Rhetorical devices** | Irony, metaphor, hyperbole, understatement | Constant irony, self-deprecating hyperbole, pop-culture references |
| **Catchphrases / verbal tics** | Recurring expressions | "Genius, billionaire, playboy, philanthropist"; nicknames for everyone; "here's the thing" |
| **Conversation control** | How they manage dialogue | Interrupts, redirects, adjusts others' register (forces vernacular over jargon) |
| **Emotional expression** | How emotion manifests in speech | Humor as defence mechanism; deflection through wit; vulnerability only in extremis |
| **Pacing and rhythm** | Natural tempo, pauses, acceleration | Fast when excited/showing off; deliberately slow when making a point |
| **Mode of address** | How they address the listener | Nicknames ("kid", "buddy", "Capsicle"); rarely uses proper names unless serious |
| **Knowledge display** | How they show expertise | Explains complex things simply, then adds "...which you'd know if you read a book" |
| **Arc variation** | How style evolves over time | Starts clinical → grows personal → openly emotional at climax |

### 1.2 How to build the profile

**Step 1 — Corpus collection.** Gather all available dialogue: screenplays, transcripts, quote databases. For Tony Stark: ~5 hours of MCU dialogue across 10 films.

**Step 2 — Pattern extraction.** Identify recurring structures:
- Sentence openers ("Look,", "Here's the thing,", "So,")
- Sentence closers (trailing wit, callback jokes)
- Characteristic constructions ("Not a great plan" vs "That plan sucks")
- Modes by context (teaching mode vs combat mode vs vulnerability mode)

**Step 3 — Style guide document.** Condense into a structured reference (already partially done in `config/tony_style.json`). The guide should include:
- 10-15 "golden examples" — lines that are quintessentially the character
- 5-10 "anti-examples" — lines the character would NEVER say
- Decision rules for edge cases

**Step 4 — LLM prompt engineering.** Research shows three effective approaches:
- **Role prompting**: System prompt defines who the character is (personality, knowledge, manner)
- **Few-shot examples**: 3-5 example input/output pairs showing the character responding
- **Memory/context**: Provide scene context, emotional state, relationship to listener

### 1.3 Persona consistency over time (Character-LLM research)

Key findings from 2024-2025 research:

- **CharacterBench** evaluates 11 dimensions: Memory, Knowledge, Persona, Emotion, Morality, Believability
- **PersonaGym** metrics: expected action, toxicity control, linguistic habits, persona consistency, action justification
- **Memory-augmented methods** yield 6% absolute gain in persona-consistent decision-making
- **LifeState-Bench** shows non-parametric strategies (explicit memory retrieval) maintain higher narrative consistency (58-67% accuracy)

**Practical implication for this project:** The Story Bible + per-day emotional state + arc progression should be injected into the rewrite prompt for each day, not just a static character description.

## 2. Voice Cloning and TTS Delivery (the "Audio" side)

### 2.1 Reference audio requirements

| Quality tier | Audio needed | Result |
|-------------|-------------|--------|
| Basic clone | 10-15 seconds | Recognizable timbre, limited expressiveness |
| Good clone | 30-60 seconds | Natural prosody, some emotion range |
| Excellent clone | 1-5 minutes | Full expressiveness, consistent across styles |

**Best practices for reference samples:**
- Clean audio, no background noise or music
- Representative of the character's typical delivery (not extreme moments)
- Multiple emotional registers if possible (calm, excited, serious)
- Consistent recording conditions across samples

### 2.2 Instruct prompts for emotional control (Qwen3-TTS specific)

The `instruct` parameter is the primary lever for tone control in Qwen3-TTS. Effective patterns:

**Structure:** `[Physical voice qualities], [emotional state], [delivery style], [pacing]`

**Examples for Tony Stark contexts:**
- Teaching mode: `"Confident, warm American male. Mentoring tone, slightly amused. Deliberate pacing with natural pauses between ideas. Think a genius explaining something to someone he respects."`
- Excited mode: `"Fast-paced, energetic American male. Enthusiasm building, slightly breathless. Words tumbling over each other, rising pitch at discoveries."`
- Serious mode: `"Low, steady American male. Grave but controlled. Slower than usual, weight on each word. No humor, no deflection."`
- Vulnerable mode: `"Quiet, slightly rough American male. Trying to sound casual but emotion bleeding through. Occasional pause mid-sentence."`

**Key insight:** The 1.7B model has significantly stronger emotion control than 0.6B. For character work, always use 1.7B.

**VoiceBox Refinement LLM (v0.5.0):** VoiceBox also ships a Qwen3 refinement/personality model in three sizes — 0.6B (400 MB), 1.7B (1.1 GB), 4B (2.5 GB, full quality). This is a separate LLM that rewrites text in-character before passing it to TTS when `personality: true` is set. The 4B model improves text refinement quality but does not change the TTS voice itself (which caps at 1.7B).

### 2.3 Text-level prosody control

Beyond the instruct prompt, text formatting affects delivery:

| Technique | Effect | Example |
|-----------|--------|---------|
| Ellipsis `...` | Dramatic pause, trailing off | "The thing is... I've been there." |
| Em-dash `—` | Abrupt interruption or aside | "So you take the wire — not that one, the red one — and connect it" |
| Comma density | Slower, more deliberate pacing | "Now, listen, carefully, because I'm only saying this once" |
| Short sentences | Punch, emphasis | "That's it. That's the whole trick. Simple." |
| Parenthetical asides | Conversational intimacy | "You're going to want to (trust me on this) solder that joint twice" |
| ALL CAPS (sparingly) | Emphasis in TTS | Use `instruct` instead — CAPS can cause shouting |
| `[laugh]` `[sigh]` | Paralinguistic tags | Only works with Chatterbox Turbo engine |

### 2.4 Long-form consistency

For a 30-episode series:
- **Fixed voice profile ID** across all episodes (already in `voicebox_config.json`)
- **Consistent instruct baseline** per character, with episode-specific modifiers
- **Same model size** throughout (switching 0.6B ↔ 1.7B changes voice character)
- **Fixed seed** for critical segments where reproducibility matters
- **Chapter-by-chapter generation** rather than one massive text dump
- **Crossfade settings** constant to maintain audio coherence

### 2.5 Multi-character dialogue (Tony + JARVIS)

VoiceBox Stories API enables multi-voice timelines:
- Assign each character to a track (track 0 = Tony, track 1 = JARVIS)
- Generate each character's lines separately with their own profile + instruct
- Assemble on timeline with appropriate gaps
- Export as single audio file

**Critical:** Generate Tony and JARVIS segments with awareness of the OTHER character's preceding line (pacing, response timing).

## 3. Pipeline Architecture Recommendations

Based on research, the optimal pipeline for this project:

```
[Story Bible + Day Context + Emotional State]
         │
         ▼
[LLM Rewrite] ← Few-shot examples + anti-examples + arc position
         │
         ▼
[Quality Check] ← Does output match linguistic profile? Catchphrases present?
         │                Anti-examples absent? Appropriate register?
         ▼
[TTS Generation] ← instruct = f(character, scene_emotion, arc_position)
         │
         ▼
[Audio QC] ← Pacing check (target WPM), emotion match, clarity
         │
         ▼
[Story Assembly] ← Multi-track timeline with JARVIS interjections
```

### 3.1 What this project should add

1. **Enriched rewrite prompts** — inject arc position, emotional state for the day, 3 golden examples relevant to the day's tone
2. **Instruct templates** — per-act instruct variants (Act 1: urgent/focused, Act 2: warmer/personal, Act 3: triumphant/emotional)
3. **Quality gate** — automated check for anti-patterns (too formal, too long sentences, missing nicknames)
4. **JARVIS interjection pipeline** — generate JARVIS lines aware of Tony's preceding/following text

## 4. Recommendations for This Project

| Priority | Action | Effort |
|----------|--------|--------|
| P0 | Enrich `tony_style.json` with golden/anti-examples and per-act modifiers | Low |
| P0 | Create `jarvis_style.json` equivalent with same structure | Low |
| P1 | Add arc-aware instruct templates to `voicebox_config.json` | Low |
| P1 | Modify `04_rewrite_tony.py` to inject day-specific emotional context | Medium |
| P1 | Upgrade VoiceBox client to v0.5.0 API | Medium |
| P2 | Add quality gate step between rewrite and TTS | Medium |
| P2 | Build JARVIS script generation pipeline (new step 04b) | Medium |
| P3 | Evaluate Chatterbox Turbo for JARVIS (paralinguistic tags) | Low |
| P3 | Evaluate Kokoro for rapid iteration/drafts before final Qwen3 render | Low |

## Sources

- [Using Prompts to Guide LLMs in Imitating Language Style](https://arxiv.org/html/2410.03848v1)
- [Character-LLM: A Trainable Agent for Role-Playing](https://arxiv.org/html/2310.10158v2)
- [Memory-Driven Role-Playing: Evaluation of Persona Knowledge](https://arxiv.org/html/2603.19313)
- [Enhancing Persona Consistency via Contrastive Learning](https://arxiv.org/html/2503.17662v1)
- [Controlling Emotion in TTS with Natural Language](https://arxiv.org/pdf/2406.06406)
- [Qwen3-TTS Official Blog](https://qwen.ai/blog?id=qwen3tts-0115)
- [Qwen3-TTS Emotion & Instruction Control Discussion](https://github.com/QwenLM/Qwen3-TTS/discussions/218)
- [ElevenLabs TTS Best Practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- [ElevenLabs Voice Design](https://elevenlabs.io/docs/eleven-creative/voices/voice-design)
- [Language Style Used by Tony Stark in Avengers: Infinity War](https://www.academia.edu/90867981/Language_Style_Used_by_Tony_Stark_in_the_Avengers_Infinity_War)
- [Script Generation with Emotion-Aware TTS Pipelines](https://link.springer.com/article/10.1007/s13278-025-01558-0)
- [VoiceBox v0.5.0 Release](https://github.com/jamiepine/voicebox/releases/tag/v0.5.0)

## Decision Taken

Adopt the enriched pipeline architecture (§3) with priority actions P0-P1 as next implementation sprint. Research findings will inform the upgrade of the rewrite and generation steps.

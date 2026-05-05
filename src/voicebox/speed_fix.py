"""Speed correction utilities for Qwen3-TTS output.

Qwen3-TTS ignores speed instructions in the `instruct` field.
The only reliable way to slow down speech is through the text itself:
strategic commas, ellipses, and em-dashes force natural pauses.
"""
import re


# Words that get a comma inserted after them when at sentence start
INTRO_WORDS = {
    'Alright', 'Now', 'So', 'Look', 'Okay', 'Right', 'First',
    'Next', 'Then', 'Also', 'Remember', 'Listen', 'Actually',
    'Basically', 'Honestly', 'Seriously', 'Well', 'Wait',
}

# Patterns that get a `...` pause before a punchline/key word
TONY_PUNCHLINE_PATTERNS = [
    r"(You're welcome\.)",
    r'(Told you\.)',
    r"(I know,? right\?)",
    r'(kid)\s*(:)',           # keep the colon
    r'(genius)\b',
    r'(Rule number \w+)',
]


def _split_sentences(text: str) -> list[str]:
    """Split text into individual sentences, preserving trailing space."""
    return re.split(r'(?<=[.!?])\s+', text.strip())


def _add_sentence_intro_pause(sentence: str) -> str:
    """Add a comma after introductory words at sentence start."""
    for word in INTRO_WORDS:
        pattern = rf'^({re.escape(word)})\b(?!,)'
        sentence = re.sub(pattern, r'\1,', sentence, count=1)
    return sentence


def add_strategic_pauses(text: str, intensity: str = "medium") -> str:
    """Add punctuation-based pauses to slow down TTS output.

    Args:
        text: Input text
        intensity: "light", "medium", or "heavy" pause insertion
    """
    sentences = _split_sentences(text)
    processed = []

    for i, sentence in enumerate(sentences):
        s = sentence

        if intensity in ("medium", "heavy"):
            # Comma after introductory word at sentence start
            s = _add_sentence_intro_pause(s)

            # Comma before coordinating conjunctions (if not already there)
            s = re.sub(r'(?<!,)\s+(and|but|or|so|yet)\s+', r', \1 ', s)

            # Comma after subordinate clause openers ONLY mid-sentence (not at start)
            s = re.sub(
                r'(?<!\A)(?<=\w\s)\b(because|since|although|though|unless|while|whereas)\s+',
                r'\1, ', s, flags=re.IGNORECASE
            )

        if intensity == "heavy":
            # Add ellipsis before emphasis words
            s = re.sub(
                r'\b(important|crucial|critical|key|essential|exactly|always|never)\b',
                r'... \1', s
            )

        processed.append(s)

    # Join sentences — for medium/heavy add a brief pause between them
    if intensity == "medium":
        result = ' '.join(processed)
    elif intensity == "heavy":
        result = ' ... '.join(processed)
    else:
        result = ' '.join(processed)

    # Clean up double punctuation artifacts
    result = re.sub(r',\s*,', ',', result)
    result = re.sub(r'\.\s*\.\.\.\s*\.', '...', result)
    result = re.sub(r'\.\.\.\s*\.\.\.', '...', result)
    result = re.sub(r',\s*\.\.\.', ' ...', result)
    result = re.sub(r'\s+', ' ', result)

    return result.strip()


def chunk_for_tts(text: str, max_chars: int = 500) -> list[str]:
    """Split text into TTS-friendly chunks at sentence boundaries."""
    sentences = _split_sentences(text)

    chunks = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        slen = len(sentence)
        if current_len + slen > max_chars and current:
            chunks.append(' '.join(current))
            current = []
            current_len = 0
        current.append(sentence)
        current_len += slen + 1

    if current:
        chunks.append(' '.join(current))

    return chunks


def prepare_tony_text(text: str) -> str:
    """Prepare text for Tony Stark's speech pattern.

    Adds pauses between sentences and at clause boundaries to
    produce a deliberate mentoring pace, not a rushed delivery.
    """
    result = add_strategic_pauses(text, intensity="medium")

    # Inter-sentence pause: add ... after every sentence-ending period/exclamation
    # so each chunk maintains consistent pacing regardless of where it starts
    result = re.sub(r'([.!])\s+(?=[A-Z])', r'\1 ... ', result)

    # Tony's characteristic pause before key points / punchlines
    for pattern in TONY_PUNCHLINE_PATTERNS:
        if r'(:)' in pattern:
            result = re.sub(pattern, r'... \1\2', result)
        else:
            result = re.sub(pattern, r'... \1', result)

    # Ellipsis after "Alright" at sentence start — strip preceding comma if any
    result = re.sub(r'\b(Alright),?\s+', r'\1... ', result)

    # Clean double ellipsis artifacts
    result = re.sub(r'\.\.\.\s*\.\.\.', '...', result)
    result = re.sub(r'\s+', ' ', result)

    return result.strip()


def prepare_jarvis_text(text: str) -> str:
    """Prepare text for JARVIS's speech pattern.

    JARVIS speaks measured and deliberate, with clear pauses
    between every sentence and formal interjections.
    """
    result = add_strategic_pauses(text, intensity="heavy")

    # JARVIS formal pause patterns
    result = re.sub(r'\b(Sir)\b(?!,)', r'\1,', result)
    result = re.sub(r'\b(if I may)\b', r'... \1,', result)
    result = re.sub(r'\b(I should note)\b', r'... \1,', result)
    result = re.sub(r'\b(I must advise)\b', r'... \1,', result)
    result = re.sub(r'\b(Additionally)\b', r'... \1,', result)

    result = re.sub(r'\.\.\.\s*\.\.\.', '...', result)
    result = re.sub(r'\s+', ' ', result)

    return result.strip()

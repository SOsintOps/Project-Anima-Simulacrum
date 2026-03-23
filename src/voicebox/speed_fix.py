"""Speed correction utilities for Qwen3-TTS output.

Qwen3-TTS tends to generate audio that is slightly too fast.
This module provides text preprocessing to encourage slower,
more natural pacing.
"""
import re


def add_strategic_pauses(text: str, intensity: str = "medium") -> str:
    """Add punctuation-based pauses to slow down TTS output.

    Args:
        text: Input text
        intensity: "light", "medium", or "heavy" pause insertion
    """
    result = text

    if intensity in ("medium", "heavy"):
        # Add commas before coordinating conjunctions
        result = re.sub(r'(?<!\,)\s+(and|but|or|so|yet)\s+', r', \1 ', result)

        # Add pause after introductory phrases
        intro_phrases = [
            r'^(Now)\b', r'^(So)\b', r'^(Look)\b', r'^(Okay)\b',
            r'^(Right)\b', r'^(First)\b', r'^(Next)\b', r'^(Then)\b',
            r'^(Also)\b', r'^(Remember)\b',
        ]
        for phrase in intro_phrases:
            result = re.sub(phrase, r'\1,', result)

    if intensity == "heavy":
        result = re.sub(r'\b(important|crucial|critical|key|essential)\b', r'... \1', result)
        result = re.sub(r'([.!?])\s+', r'\1 ... ', result)

    # Clean up
    result = re.sub(r',\s*,', ',', result)
    result = re.sub(r'\.\.\.\s*\.\.\.', '...', result)
    result = re.sub(r'\s+', ' ', result)

    return result.strip()


def chunk_for_tts(text: str, max_chars: int = 500) -> list[str]:
    """Split text into TTS-friendly chunks at sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)

        if current_len + sentence_len > max_chars and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_len = 0

        current_chunk.append(sentence)
        current_len += sentence_len + 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def prepare_tony_text(text: str) -> str:
    """Prepare text for Tony Stark's speech pattern.

    Tony speaks medium-fast but with deliberate pauses for
    punchlines, technical emphasis, and dramatic reveals.
    """
    result = add_strategic_pauses(text, intensity="medium")

    # Tony's characteristic pause before zingers
    result = re.sub(r"(You're welcome\.)", r'... \1', result)
    result = re.sub(r'(Told you\.)', r'... \1', result)
    result = re.sub(r"(I know,? right\?)", r'... \1', result)

    return result


def prepare_jarvis_text(text: str) -> str:
    """Prepare text for JARVIS's speech pattern.

    JARVIS speaks measured and deliberate. More pauses, slower pace.
    """
    result = add_strategic_pauses(text, intensity="heavy")

    # JARVIS formal pause patterns
    result = re.sub(r'\b(Sir)\b', r'\1,', result)
    result = re.sub(r'\b(if I may)\b', r'... \1,', result)
    result = re.sub(r'\b(I should note)\b', r'... \1,', result)

    return result

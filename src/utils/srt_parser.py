"""SRT Parser and Cleaner for Project Anima Simulacrum."""
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SrtEntry:
    index: int
    start_ms: int
    end_ms: int
    text: str


@dataclass
class CleanSegment:
    start_ms: int
    end_ms: int
    text: str
    segment_type: str = "speech"  # speech, music, silence


def parse_timecode(tc: str) -> int:
    """Convert SRT timecode (HH:MM:SS,mmm) to milliseconds."""
    match = re.match(r'(\d{2}):(\d{2}):(\d{2})[,.](\d{3})', tc.strip())
    if not match:
        raise ValueError(f"Invalid timecode: {tc}")
    h, m, s, ms = match.groups()
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)


def ms_to_timecode(ms: int) -> str:
    """Convert milliseconds to SRT timecode."""
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    remainder = ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{remainder:03d}"


NON_SPEECH_PATTERN = re.compile(
    r'^\[(?:Music|Applause|Laughter|Silence|Sound|Noise|Cheering|Clapping)\]$',
    re.IGNORECASE
)

ASR_CORRECTIONS = {
    r'\bherob\b': 'Hero',
    r'\bherob board\b': 'Hero board',
    r'\bhero board\b': 'HERO board',
    r'\bour doino\b': 'Arduino',
    r'\binventor\.\s*hero\b': 'Inventr.io HERO',
    r'\bblink\.\s*IO\b': 'blink.ino',
    r'\bblink\. IO\b': 'blink.ino',
    r'\bblink\.\s*i n o\b': 'blink.ino',
    r'\bblink\.\s*sketch\b': 'blink sketch',
    r'\bdigital right\b': 'digitalWrite',
    r'\bdigital WR\b': 'digitalWrite',
    r'\bdigital write\b': 'digitalWrite',
    r'\bledore builtin\b': 'LED_BUILTIN',
    r'\bSL asterisk\b': 'slash-asterisk',
    r'\bpin mode\b': 'pinMode',
    r'\bour doino Uno\b': 'Arduino Uno',
    r'\banalog right\b': 'analogWrite',
    r'\banalog read\b': 'analogRead',
    r'\bserial dot\b': 'Serial.',
    r'\bser\. begin\b': 'Serial.begin',
}


def parse_srt(filepath: Path) -> list[SrtEntry]:
    """Parse an SRT file into a list of SrtEntry objects."""
    text = filepath.read_text(encoding='utf-8', errors='replace')
    entries = []

    # Split by blank lines to get blocks
    blocks = re.split(r'\n\s*\n', text.strip())

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue

        # First line should be the index
        try:
            index = int(lines[0].strip())
        except ValueError:
            continue

        # Second line should be the timecode
        tc_match = re.match(
            r'(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})',
            lines[1].strip()
        )
        if not tc_match:
            continue

        start_ms = parse_timecode(tc_match.group(1))
        end_ms = parse_timecode(tc_match.group(2))

        # Remaining lines are the subtitle text
        sub_text = ' '.join(lines[2:]).strip()

        if sub_text:
            entries.append(SrtEntry(
                index=index,
                start_ms=start_ms,
                end_ms=end_ms,
                text=sub_text
            ))

    return entries


def clean_text(text: str) -> str:
    """Apply ASR corrections and clean up text."""
    cleaned = text
    for pattern, replacement in ASR_CORRECTIONS.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    # Fix common ASR artifacts
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Multiple spaces
    cleaned = re.sub(r'\s([.,;:!?])', r'\1', cleaned)  # Space before punctuation

    return cleaned.strip()


def is_non_speech(text: str) -> bool:
    """Check if text is a non-speech annotation."""
    return bool(NON_SPEECH_PATTERN.match(text.strip()))


def reconstruct_sentences(entries: list[SrtEntry]) -> list[CleanSegment]:
    """Reconstruct continuous sentences from fragmented SRT entries.

    ASR subtitles are often split mid-sentence across multiple entries.
    This function merges them back into complete sentences.
    """
    if not entries:
        return []

    segments = []
    current_text = ""
    current_start = entries[0].start_ms
    current_end = entries[0].end_ms

    for entry in entries:
        if is_non_speech(entry.text):
            # Flush current text if any
            if current_text.strip():
                segments.append(CleanSegment(
                    start_ms=current_start,
                    end_ms=current_end,
                    text=clean_text(current_text.strip()),
                    segment_type="speech"
                ))
                current_text = ""
            segments.append(CleanSegment(
                start_ms=entry.start_ms,
                end_ms=entry.end_ms,
                text=entry.text,
                segment_type="music"
            ))
            current_start = entry.end_ms
            continue

        text = entry.text.strip()

        # Check if this starts a new sentence (after sentence-ending punctuation)
        if current_text and re.search(r'[.!?]\s*$', current_text):
            segments.append(CleanSegment(
                start_ms=current_start,
                end_ms=current_end,
                text=clean_text(current_text.strip()),
                segment_type="speech"
            ))
            current_text = text
            current_start = entry.start_ms
        else:
            if current_text:
                current_text += " " + text
            else:
                current_text = text
                current_start = entry.start_ms

        current_end = entry.end_ms

    # Don't forget the last segment
    if current_text.strip():
        segments.append(CleanSegment(
            start_ms=current_start,
            end_ms=current_end,
            text=clean_text(current_text.strip()),
            segment_type="speech"
        ))

    return segments


def extract_full_text(segments: list[CleanSegment], speech_only: bool = True) -> str:
    """Extract the full continuous text from segments."""
    filtered = [s for s in segments if s.segment_type == "speech"] if speech_only else segments
    return " ".join(s.text for s in filtered)

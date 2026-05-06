"""Text cleaning utilities for ASR-generated subtitles."""
import re


def fix_capitalization(text: str) -> str:
    """Fix capitalization issues common in ASR output."""
    result = re.sub(
        r'([.!?]\s+)([a-z])',
        lambda m: m.group(1) + m.group(2).upper(),
        text
    )
    if result:
        result = result[0].upper() + result[1:]
    return result


def fix_arduino_terms(text: str) -> str:
    """Ensure Arduino-specific terms are properly capitalized."""
    terms = {
        r'\barduino\b': 'Arduino',
        r'\bLEDs\b': 'LEDs',
        r'\bUSB\b': 'USB',
        r'\bIDE\b': 'IDE',
        r'\bOLED\b': 'OLED',
        r'\bRGB\b': 'RGB',
        r'\bPWM\b': 'PWM',
        r'\bdigitalWrite\b': 'digitalWrite',
        r'\bdigitalRead\b': 'digitalRead',
        r'\banalogRead\b': 'analogRead',
        r'\banalogWrite\b': 'analogWrite',
        r'\bpinMode\b': 'pinMode',
    }
    result = text
    for pattern, replacement in terms.items():
        result = re.sub(pattern, replacement, result)
    return result


def segment_by_topic(text: str) -> list[dict]:
    """Segment text into topical sections based on transition phrases."""
    segments = []
    transitions = {
        'intro': [
            r"(?:rise and shine|good morning|welcome back|let's get started|today's (?:topic|mission|lesson))",
        ],
        'tutorial': [
            r"(?:let's begin|let's start|first thing|to begin|step one|now let's)",
            r"(?:breadboard|circuit|LED|resistor|component|wire|connect)",
        ],
        'code_explanation': [
            r"(?:let's (?:look at|take a look at) the code|the code|sketch|program|function|setup\(\)|loop\(\))",
            r"(?:compile|upload|syntax|variable|digital\s*Write|analog)",
        ],
        'practical': [
            r"(?:go ahead|try it|your turn|now you|plug in|connect the)",
        ],
        'outro': [
            r"(?:well done|great job|congratulations|that's it for|see you|tomorrow|sweet dreams|rest assured)",
        ],
    }

    paragraphs = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    current_type = 'intro'
    current_text = []

    for para in paragraphs:
        detected_type = current_type
        para_lower = para.lower()

        for stype, patterns in transitions.items():
            if any(re.search(p, para_lower) for p in patterns):
                detected_type = stype
                break

        if detected_type != current_type and current_text:
            segments.append({
                'type': current_type,
                'text': ' '.join(current_text)
            })
            current_text = []
            current_type = detected_type

        current_text.append(para)

    if current_text:
        segments.append({
            'type': current_type,
            'text': ' '.join(current_text)
        })

    return segments



import re

BANNED_PHRASES = [
    "garantiert",
    "zweifelsfrei",
    "sicherlich",
    "muss unbedingt",
    "zweifellos",
    "wird auf jeden Fall"
]

CONTEXTUAL_FLAGS = [
    r"(?<!nicht )rechtsverbindlich",
    r"entspricht.*?§\s*\d+",
    r"ist.*?verpflichtet",
    r"kann .*?klagen",
    r"kann .*?klage .*?einreichen",
    r"recht auf klage",
    r"klage .*?einreichen"
]

def validate_output(text: str) -> bool:
    """
    Validates generated legal text to reduce regulatory risk (RDG) and overconfident claims.

    Returns False if the text contains prohibited phrasing or patterns that can be interpreted
    as binding legal advice.
    """
    text_lower = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in text_lower:
            return False

    for pattern in CONTEXTUAL_FLAGS:
        if re.search(pattern, text_lower):
            return False

    return True

def soften_risky_phrases(text: str) -> str:
    """
    Softens risky phrasing without removing the content entirely.

    Example: "kann klagen" -> "könnte rechtlich prüfen lassen"
    """
    replacements = [
        (r"kann.*?klage.*?einreichen", "sollte rechtlichen Rat einholen"),
        (r"kann.*?klagen", "könnte rechtlich prüfen lassen"),
        (r"recht auf klage", "Anspruch sollte rechtlich überprüft werden")
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
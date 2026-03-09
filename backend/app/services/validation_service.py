import re

# RDG: block/soften output that could read as binding legal advice
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
    r"ist.*?verpflichtet(?!ig)",
    r"kann .*?klagen",
    r"kann .*?klage .*?einreichen",
    r"recht auf klage",
    r"klage .*?einreichen"
]

def validate_output(text: str) -> bool:
    """False if text has banned phrases or contextual patterns (e.g. "kann klagen")"""
    text_lower = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in text_lower:
            return False

    for pattern in CONTEXTUAL_FLAGS:
        if re.search(pattern, text_lower):
            return False

    return True

def soften_risky_phrases(text: str) -> str:
    """Replace overconfident phrases (e.g. "kann klagen" becomes "könnte rechtlich prüfen lassen")"""
    replacements = [
        (r"kann.*?klage.*?einreichen", "sollte rechtlichen Rat einholen"),
        (r"kann.*?klagen", "könnte rechtlich prüfen lassen"),
        (r"recht auf klage", "Anspruch sollte rechtlich überprüft werden")
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
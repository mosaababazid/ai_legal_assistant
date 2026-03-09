# DE to AR via Helsinki opus-mt; anti-repetition params to avoid "هيّا" loops / degeneration.
# Model max length 512 tokens; we chunk long text. Generation "brakes" prevent repetition loops.
from transformers import pipeline
import torch

# Chunk size in chars so token count stays under 512 (~4 chars/token for German)
MAX_CHARS_PER_CHUNK = 1200
# Cap output length so runaway generation stops quickly
MAX_OUTPUT_LENGTH = 256

GEN_OPTS = {
    "max_length": min(512, MAX_OUTPUT_LENGTH),
    "repetition_penalty": 1.2,
    "no_repeat_ngram_size": 3,
}

translator = pipeline(
    "translation",
    model="Helsinki-NLP/opus-mt-de-ar",
    tokenizer="Helsinki-NLP/opus-mt-de-ar",
    framework="pt",
    device=0 if torch.cuda.is_available() else -1,
)


def _translate_chunk(chunk: str) -> str:
    return translator(chunk, **GEN_OPTS)[0]["translation_text"]


def translate_to_arabic(text: str) -> str:
    if not (text or text.strip()):
        return ""
    text = text.strip()
    if len(text) <= MAX_CHARS_PER_CHUNK:
        return _translate_chunk(text)
    # Chunk and translate each part to stay under model limit
    parts = []
    start = 0
    while start < len(text):
        chunk = text[start : start + MAX_CHARS_PER_CHUNK]
        if start + MAX_CHARS_PER_CHUNK < len(text):
            last_period = chunk.rfind(". ")
            if last_period > MAX_CHARS_PER_CHUNK // 2:
                chunk = chunk[: last_period + 1]
                start += last_period + 1
            else:
                start += len(chunk)
        else:
            start = len(text)
        if chunk.strip():
            parts.append(_translate_chunk(chunk.strip()))
    return " ".join(parts)
# Optional DEtoAR; not used in main flow (LLM outputs in target language). Kept for other use.
from transformers import pipeline
import torch

MAX_CHARS_PER_CHUNK = 500  # opus-mt-de-ar max 512 tokens; chunk to avoid overflow
MAX_OUTPUT_LENGTH = 256

GEN_OPTS = {
    "max_length": MAX_OUTPUT_LENGTH,
    "repetition_penalty": 1.2,
    "no_repeat_ngram_size": 3,
    "truncation": True,
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
    parts = []  # long text: split at sentence boundary, translate, rejoin
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
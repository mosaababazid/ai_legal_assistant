import os

from llama_index.llms.groq import Groq

from app.core.config import (
    LLM_MODEL_NAME,
    RAG_REQUEST_TIMEOUT_SECONDS,
)


def _get_llm() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable is required for the LLM.")
    return Groq(
        model=LLM_MODEL_NAME,
        api_key=api_key,
        request_timeout=RAG_REQUEST_TIMEOUT_SECONDS,
    )


def summarize_text(text: str, target_language: str = "Deutsch") -> str:
    llm = _get_llm()
    prompt = (
        "Du bist ein Helfer für Menschen, die deutsche Behördenbriefe (Amtsdeutsch) nicht gut verstehen. "
        "Der folgende Text ist ein Ausschnitt aus einem solchen Brief (z.B. Bescheid, Mahnung, Gerichtsentscheid).\n\n"
        "AUFGABE: Fasse den Inhalt in einfacher, verständlicher Sprache zusammen. "
        "Konkret: Was will der Absender? Welche Beträge und Fristen stehen drin? Was soll der Empfänger tun?\n\n"
        "Antworte AUSSCHLIESSLICH auf "
        + ("Deutsch." if target_language == "Deutsch" else "Arabisch (Hocharabisch).")
        + " Keine andere Sprache.\n\n"
        "Text des Briefs:\n"
    ) + text
    return str(llm.complete(prompt).text)
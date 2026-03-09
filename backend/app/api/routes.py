from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from app.core.config import IS_PRODUCTION
from app.services.ocr_service import extract_text_from_image
from app.services.pdf_service import extract_text_from_pdf
from app.services.summarization_service import summarize_text
from app.services.rag_service import handle_legal_query_with_index, IndexNotFoundError
from app.services.validation_service import validate_output, soften_risky_phrases
from app.utils.text_cleaner import clean_extracted_text
import asyncio
import logging


router = APIRouter()
DISCLAIMER = "Diese Einschätzung ersetzt keine anwaltliche Beratung (§ 1 RDG)."  # RDG compliance

logger = logging.getLogger(__name__)


def _success(payload: dict) -> JSONResponse:
    return JSONResponse(status_code=200, content=payload)


@router.post("/api/extract-summarize")
async def extract_and_summarize(
    file: UploadFile = File(...),
    language: str = Form(...),
    mode: str = Form("summary"),
):
    if not file:
        raise HTTPException(status_code=400, detail="Keine Datei hochgeladen.")

    if language not in ["de", "ar"]:
        raise HTTPException(status_code=400, detail="Sprache muss 'de' oder 'ar' sein.")

    try:
        contents = await file.read()

        if file.filename.lower().endswith(".pdf"):
            extracted_text = extract_text_from_pdf(contents)
        else:
            extracted_text = extract_text_from_image(contents)

        if not extracted_text.strip():
            return _success(
                {
                    "original_text": "",
                    "summary": "Kein Text im Dokument erkannt.",
                    "disclaimer": DISCLAIMER,
                }
            )

        extracted_text = clean_extracted_text(extracted_text)

        if len(extracted_text) < 20:
            return _success(
                {
                    "original_text": extracted_text,
                    "summary": "Extrahierter Text ist zu kurz.",
                    "disclaimer": DISCLAIMER,
                }
            )

        if mode == "summary":
            target_lang = "Deutsch" if language == "de" else "Arabisch"
            summary = summarize_text(extracted_text, target_language=target_lang)

            if len(summary.split()) < 5:
                return _success(
                    {
                        "original_text": extracted_text,
                        "summary": "Zusammenfassung zu kurz oder unklar.",
                        "disclaimer": DISCLAIMER,
                    }
                )

            return _success(
                {
                    "original_text": extracted_text,
                    "summary": summary,
                    "disclaimer": DISCLAIMER,
                }
            )

        if mode == "legal_advice":
            try:
                target_lang = "Deutsch" if language == "de" else "Arabisch"
                result = await asyncio.to_thread(
                    handle_legal_query_with_index, extracted_text, target_lang
                )
            except TimeoutError:
                raise HTTPException(
                    status_code=504,
                    detail="LLM-Zeitüberschreitung – bitte später erneut versuchen.",
                )
            except IndexNotFoundError as exc:
                detail = (
                    "Gesetzesindex nicht gefunden. Bitte zuerst den Index mit "
                    "'scripts/build_index.py' erzeugen."
                )
                if not IS_PRODUCTION:
                    detail = f"{detail} ({exc})"
                raise HTTPException(status_code=404, detail=detail)
            except Exception:
                logger.exception("Juristische Analyse fehlgeschlagen.")
                detail = "Fehler bei juristischer Analyse."
                if not IS_PRODUCTION:
                    detail = (
                        "Fehler bei juristischer Analyse. Details siehe Server-Logs."
                    )
                raise HTTPException(status_code=500, detail=detail)

            recommendation_text = soften_risky_phrases(
                result.get("recommendation") or ""
            )
            if not validate_output(recommendation_text or ""):  # RDG guard
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Antwort enthält riskante Formulierungen und wurde blockiert "
                        "(RDG-Schutz)."
                    ),
                )

            return _success(
                {
                    "original_text": extracted_text,
                    "legal_recommendation": recommendation_text,
                    "used_paragraphs": result.get("used_paragraphs", []),
                    "disclaimer": DISCLAIMER,
                }
            )

        return _success(
            {
                "original_text": extracted_text,
                "disclaimer": DISCLAIMER,
            }
        )

    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise

        logger.exception("Unerwarteter Serverfehler:")
        if IS_PRODUCTION:
            raise HTTPException(status_code=500, detail="Verarbeitung fehlgeschlagen.")
        raise HTTPException(
            status_code=500, detail=f"Verarbeitung fehlgeschlagen: {exc}"
        )
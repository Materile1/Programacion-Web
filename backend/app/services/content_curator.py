import json
import logging

import httpx
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import ReviewSnippet
from ..schemas import CuratedReview
from .news_feeder import fetch_news

logger = logging.getLogger(__name__)

def _prompt(topics: list[str]) -> str:
    return ("Genera exactamente un objeto JSON, sin markdown, con las claves title, language, code, "
            "known_issues y difficulty. Crea un snippet de code review útil para aprender programación "
            f"basado en estas tendencias actuales: {', '.join(topics)}. known_issues debe ser una lista de "
            "problemas concretos que el estudiante pueda detectar leyendo el código.")

def _ask_openai(key: str, prompt: str) -> str:
    response = httpx.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {key}"}, json={"model": "gpt-4o-mini", "temperature": 0.2, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": "Responde solo JSON válido."}, {"role": "user", "content": prompt}]}, timeout=20)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def _ask_gemini(key: str, prompt: str) -> str:
    response = httpx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent", params={"key": key}, json={"generationConfig": {"responseMimeType": "application/json"}, "contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

def curate_review(db: Session) -> tuple[CuratedReview | None, list[str], str]:
    topics = [item.title for item in fetch_news(limit=3)]
    settings = get_settings()
    try:
        if settings.gemini_api_key:
            raw = _ask_gemini(settings.gemini_api_key, _prompt(topics))
        elif settings.openai_api_key:
            raw = _ask_openai(settings.openai_api_key, _prompt(topics))
        else:
            return None, topics, "No hay proveedor de IA configurado."
        return CuratedReview.model_validate(json.loads(raw)), topics, "Contenido validado."
    except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError, ValidationError, ValueError):
        logger.warning("Contenido curado descartado: respuesta de IA inválida")
        return None, topics, "La respuesta del proveedor no superó la validación JSON."

def refresh_content(db: Session) -> tuple[int, int, list[str], str]:
    content, topics, detail = curate_review(db)
    if not content:
        return 0, 1, topics, detail
    db.add(ReviewSnippet(title=content.title, language=content.language, code=content.code, known_issues=json.dumps(content.known_issues, ensure_ascii=False), difficulty=content.difficulty, source="ai-curated"))
    db.commit()
    return 1, 0, topics, detail
from __future__ import annotations
import feedparser
from ..schemas import NewsOut

SOURCES = [
    ("Hacker News", "https://hnrss.org/frontpage"),
    ("Python Blog", "https://blog.python.org/feeds/posts/default"),
]

def fetch_news(limit: int = 6) -> list[NewsOut]:
    items: list[NewsOut] = []
    for source, url in SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                items.append(NewsOut(title=entry.get("title", "Novedad tecnológica"), summary=entry.get("summary", "Actualización del ecosistema de desarrollo")[:240], url=entry.get("link", url), source=source, kind="Reto del día"))
        except Exception:
            continue
    return items[:limit] or [NewsOut(title="Practica una función pura", summary="Un reto local para mantener tu ritmo de aprendizaje.", url="https://dev.to", source="DevCoach", kind="Reto del día")]

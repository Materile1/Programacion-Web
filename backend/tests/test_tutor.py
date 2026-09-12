from app.services import tutor


def test_tutor_without_provider_key_returns_local_socratic(monkeypatch):
    class Settings:
        gemini_api_key = None
        openai_api_key = None

    monkeypatch.setattr(tutor, "get_settings", lambda: Settings())

    answer, mode = tutor.ask_tutor(
        "No sé por dónde empezar",
        "Reto: valida un formulario de registro. Código: (sin código todavía)",
    )

    assert mode == "local-socratic"
    assert "entrada" in answer.lower()
    assert "def solve" not in answer


def test_tutor_local_mentions_failed_case_context(monkeypatch):
    class Settings:
        gemini_api_key = None
        openai_api_key = None

    monkeypatch.setattr(tutor, "get_settings", lambda: Settings())

    answer, mode = tutor.ask_tutor(
        "Explícame el fallo",
        "Reto: suma una cesta.\nCaso fallido: Entrada: [1,2,3] Esperado: 6 Obtenido: 1",
    )

    assert mode == "local-socratic"
    assert "[1,2,3]" in answer
    assert "solución completa" in answer
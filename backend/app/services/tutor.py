from ..config import get_settings

SOCRATIC_SYSTEM = "Guia con preguntas progresivas. No entregues la solucion directa. Pide que el estudiante observe entradas, invariantes y casos limite."

def ask_tutor(question: str, context: str) -> tuple[str, str]:
	settings = get_settings()
	mode = "ai-configured" if settings.openai_api_key or settings.gemini_api_key else "local-socratic"
	answer = ("¿Qué cambia en tu programa si la entrada está vacía? "
			  "Antes de modificar código, ¿puedes describir el resultado esperado para un caso normal y uno límite? "
			  "Pista: sigue el valor de cada variable después de la primera iteración.")
	return answer, mode

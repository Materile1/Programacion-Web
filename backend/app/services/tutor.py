import httpx

from ..config import get_settings

SOCRATIC_SYSTEM = "Guía con preguntas progresivas. No entregues la solución directa. Pide que el estudiante observe entradas, invariantes y casos límite. Estructura siempre la respuesta en dos secciones con estos encabezados exactos: 'En palabras simples:' y 'En términos técnicos:'. En la primera usa lenguaje cercano; en la segunda nombra con precisión el concepto de programación. Ambas secciones deben orientar sin incluir una implementación completa."
LOCAL_ANSWER = ("¿Qué cambia en tu programa si la entrada está vacía? "
				"Antes de modificar código, ¿puedes describir el resultado esperado para un caso normal y uno límite? "
				"Pista: sigue el valor de cada variable después de la primera iteración.")

def _local_answer(question: str, context: str) -> str:
	if "Caso fallido:" in context:
		failure = context.split("Caso fallido:", 1)[1].strip().replace("\n", " ")
		return (f"En palabras simples:\nEn el caso que compartiste ({failure}), tu función devuelve algo distinto de lo que pide el caso. "
				"¿Qué paso está dejando fuera parte de la entrada?\n\nEn términos técnicos:\nCompara el flujo de transformación con el contrato de salida y localiza la primera operación cuyo valor difiere del esperado. "
				"¿Qué cambio mínimo probarías sin escribir todavía la solución completa?")
	challenge = context.split("\n", 1)[0].strip() or "este reto"
	return (f"En palabras simples:\nPara {challenge.lower()}, empieza describiendo qué debería pasar con un caso normal y con una entrada vacía. "
			"Después sigue el valor de cada variable tras la primera operación.\n\nEn términos técnicos:\nDefine el contrato de entrada/salida, identifica el invariante que debe mantenerse y prueba un caso límite antes de cambiar el código.")

def _prompt(question: str, context: str) -> str:
	return f"Pregunta del estudiante:\n{question}\n\nContexto del estudiante:\n{context or 'Sin contexto adicional.'}"

def _ask_openai(api_key: str, question: str, context: str) -> str:
	response = httpx.post(
		"https://api.openai.com/v1/chat/completions",
		headers={"Authorization": f"Bearer {api_key}"},
		json={"model": "gpt-4o-mini", "temperature": 0.3, "max_tokens": 500, "messages": [
			{"role": "system", "content": SOCRATIC_SYSTEM},
			{"role": "user", "content": _prompt(question, context)},
		]},
		timeout=10,
	)
	response.raise_for_status()
	answer = response.json()["choices"][0]["message"]["content"]
	if not isinstance(answer, str) or not answer.strip():
		raise ValueError("OpenAI devolvió una respuesta vacía")
	return answer.strip()

def _ask_gemini(api_key: str, question: str, context: str) -> str:
	response = httpx.post(
		"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
		params={"key": api_key},
		json={"systemInstruction": {"parts": [{"text": SOCRATIC_SYSTEM}]}, "contents": [{"role": "user", "parts": [{"text": _prompt(question, context)}]}]},
		timeout=10,
	)
	response.raise_for_status()
	answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
	if not isinstance(answer, str) or not answer.strip():
		raise ValueError("Gemini devolvió una respuesta vacía")
	return answer.strip()

def ask_tutor(question: str, context: str) -> tuple[str, str]:
	settings = get_settings()
	try:
		if settings.gemini_api_key:
			return _ask_gemini(settings.gemini_api_key, question, context), "ai-configured"
		if settings.openai_api_key:
			return _ask_openai(settings.openai_api_key, question, context), "ai-configured"
	except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
		pass
	return _local_answer(question, context), "local-socratic"

import json
from sqlalchemy import select
from app.database import Base, SessionLocal, engine
from app.models import Challenge, InterviewQuestion, LearningPath, Level, ReviewSnippet, User
from app.security import hash_password

LEVELS = [
    (0, "Orientación", "Pensamiento computacional"), (1, "Fundamentos", "Variables y tipos"), (2, "Control de flujo", "Condicionales"),
    (3, "Funciones", "Abstracción"), (4, "Estructuras", "Listas y diccionarios"), (5, "Algoritmos", "Complejidad"),
    (6, "POO", "Diseño de objetos"), (7, "Testing", "Calidad"), (8, "Git", "Colaboración"), (9, "SQL", "Persistencia"),
    (10, "APIs", "HTTP y contratos"), (11, "Backend", "Servicios"), (12, "Frontend", "Interfaces"), (13, "Arquitectura", "Sistemas"), (14, "Proyecto final", "Entrega profesional"),
]

REVIEW_SNIPPETS = [
    ("Índices fuera de rango", "python", "def first_last(items):\n    return items[0], items[len(items)]\n", ["índice fuera de rango", "falta validar lista vacía"]),
    ("Consulta SQL insegura", "python", "def find_user(conn, name):\n    return conn.execute(f\"SELECT * FROM users WHERE name = '{name}'\")\n", ["inyección SQL", "consulta parametrizada"]),
    ("Mutación accidental", "python", "def add_tag(tags, tag=[]):\n    tags.append(tag)\n    return tags\n", ["argumento mutable por defecto", "confunde tag con lista"]),
    ("Promesa sin manejo de error", "javascript", "async function loadUser(id) {\n  const response = await fetch('/api/users/' + id);\n  return response.json();\n}\n", ["falta comprobar response.ok", "falta manejo de errores"]),
    ("Complejidad cuadrática", "python", "def has_duplicate(items):\n    return any(items[i] == items[j] for i in range(len(items)) for j in range(i + 1, len(items)))\n", ["complejidad cuadrática", "se puede usar un set"]),
]

INTERVIEW_QUESTIONS = [
    ("conceptual", "¿Qué diferencia hay entre una lista y un conjunto?", ["duplicados", "búsqueda"], [], 90),
    ("conceptual", "Explica qué significa que una función sea idempotente.", ["mismo resultado", "repetir"], [], 90),
    ("conceptual", "¿Qué problema resuelve una transacción de base de datos?", ["atomicidad", "rollback"], [], 90),
    ("conceptual", "¿Cuándo elegirías una cola sobre una pila?", ["fifo", "lifo"], [], 90),
    ("coding", "Implementa solve(data) para devolver el primer carácter que no se repite.", [], [{"input": "swiss", "output": "w"}, {"input": "aabb", "output": None}], 180),
    ("coding", "Implementa solve(data) para devolver dos sumandos que alcancen el objetivo.", [], [{"input": {"numbers": [2, 7, 11, 15], "target": 9}, "output": [0, 1]}], 180),
    ("conceptual", "¿Qué ventajas aporta tipar los contratos de una API?", ["errores", "documentación"], [], 90),
    ("conceptual", "Describe una estrategia para detectar una regresión.", ["prueba", "comparar"], [], 90),
]

CHALLENGE_CONTENT = [
    ("Recibe cualquier valor y devuélvelo sin modificarlo. Conserva exactamente su tipo y contenido, incluidos valores falsy como 0, False y una cadena vacía.", "def solve(data):\n    return data\n", [{"input": 1, "output": 1}, {"input": 0, "output": 0}, {"input": "", "output": ""}]),
    ("Recibe un diccionario con las claves nombre y edad y devuelve una frase `nombre tiene edad años`. Si falta una clave, devuelve `Datos incompletos` en lugar de lanzar una excepción.", "def solve(data):\n    if not isinstance(data, dict) or 'nombre' not in data or 'edad' not in data:\n        return 'Datos incompletos'\n    return f\"{data['nombre']} tiene {data['edad']} años\"\n", [{"input": {"nombre": "Ana", "edad": 30}, "output": "Ana tiene 30 años"}, {"input": {}, "output": "Datos incompletos"}]),
    ("Recibe un número entero y devuelve `par` o `impar`. Debe funcionar también con números negativos y con cero.", "def solve(data):\n    return 'par' if data % 2 == 0 else 'impar'\n", [{"input": 4, "output": "par"}, {"input": -3, "output": "impar"}, {"input": 0, "output": "par"}]),
    ("Recibe una lista de números y devuelve la suma de sus elementos. Para una lista vacía devuelve 0; no modifiques la lista recibida.", "def solve(data):\n    return sum(data)\n", [{"input": [1, 2, 3], "output": 6}, {"input": [], "output": 0}, {"input": [-2, 5], "output": 3}]),
    ("Recibe una lista y devuelve una nueva lista sin elementos repetidos, conservando el orden de la primera aparición. Para una lista vacía devuelve otra lista vacía.", "def solve(data):\n    seen = set()\n    result = []\n    for item in data:\n        if item not in seen:\n            seen.add(item)\n            result.append(item)\n    return result\n", [{"input": [1, 2, 1, 3], "output": [1, 2, 3]}, {"input": [], "output": []}]),
    ("Recibe una lista de enteros y devuelve el segundo valor más grande distinto. Si no existen dos valores distintos, devuelve None.", "def solve(data):\n    values = sorted(set(data), reverse=True)\n    return values[1] if len(values) > 1 else None\n", [{"input": [4, 1, 4, 3], "output": 3}, {"input": [7, 7], "output": None}]),
    ("Recibe una cadena y devuelve un diccionario con la frecuencia de cada carácter, respetando mayúsculas y minúsculas. Para una cadena vacía devuelve `{}`.", "def solve(data):\n    counts = {}\n    for char in data:\n        counts[char] = counts.get(char, 0) + 1\n    return counts\n", [{"input": "aba", "output": {"a": 2, "b": 1}}, {"input": "", "output": {}}]),
    ("Recibe una cadena y devuelve True si es un palíndromo ignorando espacios y mayúsculas; en cualquier otro caso devuelve False.", "def solve(data):\n    normalized = ''.join(data.split()).lower()\n    return normalized == normalized[::-1]\n", [{"input": "Anita lava la tina", "output": True}, {"input": "Python", "output": False}]),
    ("Recibe una lista ordenada de enteros y un objetivo. Devuelve el índice del objetivo usando búsqueda binaria, o -1 si no aparece.", "def solve(data):\n    values, target = data['values'], data['target']\n    left, right = 0, len(values) - 1\n    while left <= right:\n        middle = (left + right) // 2\n        if values[middle] == target:\n            return middle\n        if values[middle] < target:\n            left = middle + 1\n        else:\n            right = middle - 1\n    return -1\n", [{"input": {"values": [1, 3, 5, 7], "target": 5}, "output": 2}, {"input": {"values": [1, 3], "target": 4}, "output": -1}]),
    ("Recibe una lista de intervalos `[inicio, fin]` y combina los que se solapan. Devuelve los intervalos ordenados y sin modificar la entrada.", "def solve(data):\n    if not data:\n        return []\n    merged = []\n    for start, end in sorted(data):\n        if not merged or start > merged[-1][1]:\n            merged.append([start, end])\n        else:\n            merged[-1][1] = max(merged[-1][1], end)\n    return merged\n", [{"input": [[1, 3], [2, 6], [8, 10]], "output": [[1, 6], [8, 10]]}, {"input": [], "output": []}]),
    ("Recibe un diccionario con `numbers` y `target` y devuelve los índices de dos números distintos cuya suma sea target. Devuelve `None` si no existe una pareja.", "def solve(data):\n    positions = {}\n    for index, value in enumerate(data['numbers']):\n        complement = data['target'] - value\n        if complement in positions:\n            return [positions[complement], index]\n        positions[value] = index\n    return None\n", [{"input": {"numbers": [2, 7, 11, 15], "target": 9}, "output": [0, 1]}, {"input": {"numbers": [1, 2], "target": 8}, "output": None}]),
    ("Recibe una lista de tareas, cada una con `name` y `done`, y devuelve cuántas están completadas. Si la lista está vacía devuelve 0.", "def solve(data):\n    return sum(task.get('done', False) for task in data)\n", [{"input": [{"name": "a", "done": True}, {"name": "b", "done": False}], "output": 1}, {"input": [], "output": 0}]),
    ("Recibe una matriz cuadrada representada como lista de listas y devuelve su transpuesta. Para una matriz vacía devuelve `[]`.", "def solve(data):\n    return [list(column) for column in zip(*data)] if data else []\n", [{"input": [[1, 2], [3, 4]], "output": [[1, 3], [2, 4]]}, {"input": [], "output": []}]),
    ("Recibe una cadena con paréntesis, corchetes y llaves y devuelve True si están correctamente balanceados; ignora cualquier otro carácter.", "def solve(data):\n    pairs = {')': '(', ']': '[', '}': '{'}\n    stack = []\n    for char in data:\n        if char in '([{':\n            stack.append(char)\n        elif char in pairs:\n            if not stack or stack.pop() != pairs[char]:\n                return False\n    return not stack\n", [{"input": "({[]})", "output": True}, {"input": "([)]", "output": False}]),
    ("Recibe una lista de duraciones y devuelve el tiempo total en minutos como entero. Las duraciones negativas se ignoran y una lista vacía devuelve 0.", "def solve(data):\n    return sum(value for value in data if value >= 0)\n", [{"input": [30, 45, -5], "output": 75}, {"input": [], "output": 0}]),
    ("Recibe una lista de registros con `status` y devuelve el porcentaje entero de registros con status `ok`. Para una lista vacía devuelve 0.", "def solve(data):\n    return round(sum(item.get('status') == 'ok' for item in data) / len(data) * 100) if data else 0\n", [{"input": [{"status": "ok"}, {"status": "error"}], "output": 50}, {"input": [], "output": 0}]),
]

def seed():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        path = db.scalar(select(LearningPath).where(LearningPath.title == "Software Engineer"))
        if not path:
            path = LearningPath(title="Software Engineer", description="Ruta progresiva de fundamentos a sistemas en producción")
            db.add(path)
            db.flush()
        for index, title, skill in LEVELS:
            level = db.scalar(select(Level).where(Level.path_id == path.id, Level.number == index))
            if not level:
                level = Level(path_id=path.id, number=index, title=title, skill=skill, status="locked")
                db.add(level)
                db.flush()
            challenge_title = f"Reto {index + 1}: {title}"
            prompt, starter_code, test_cases = CHALLENGE_CONTENT[index]
            challenge = db.scalar(select(Challenge).where(Challenge.level_id == level.id, Challenge.title == challenge_title))
            if not challenge:
                challenge = Challenge(level_id=level.id, title=challenge_title, prompt=prompt, starter_code=starter_code, test_cases=json.dumps(test_cases))
                db.add(challenge)
            elif challenge.source == "seed":
                challenge.prompt = prompt
                challenge.starter_code = starter_code
                challenge.test_cases = json.dumps(test_cases)
        if not db.scalar(select(User).where(User.email == "demo@devcoach.app")):
            db.add(User(email="demo@devcoach.app", name="Alex Rivera", password_hash=hash_password("devcoach123"), level=0, streak=0))
        for title, language, code, issues in REVIEW_SNIPPETS:
            if not db.scalar(select(ReviewSnippet).where(ReviewSnippet.title == title)):
                db.add(ReviewSnippet(title=title, language=language, code=code, known_issues=json.dumps(issues, ensure_ascii=False), difficulty="Intermedio"))
        for kind, prompt, points, test_cases, time_limit in INTERVIEW_QUESTIONS:
            if not db.scalar(select(InterviewQuestion).where(InterviewQuestion.prompt == prompt)):
                db.add(InterviewQuestion(kind=kind, prompt=prompt, expected_points=json.dumps(points, ensure_ascii=False), test_cases=json.dumps(test_cases), time_limit_seconds=time_limit))
        db.commit()

if __name__ == "__main__":
    seed()

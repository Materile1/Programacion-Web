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
                level = Level(path_id=path.id, number=index, title=title, skill=skill, status="completed" if index < 4 else ("active" if index == 4 else "locked"))
                db.add(level)
                db.flush()
            challenge_title = f"Reto {index + 1}: {title}"
            if not db.scalar(select(Challenge).where(Challenge.level_id == level.id, Challenge.title == challenge_title)):
                db.add(Challenge(level_id=level.id, title=challenge_title, prompt=f"Practica {skill.lower()} con una solución clara y verificable.", starter_code="def solve(data):\n    # escribe tu solución\n    return data\n", test_cases=json.dumps([{"input": 1, "output": 1}, {"input": 0, "output": 0}, {"input": -1, "output": -1}])))
        if not db.scalar(select(User).where(User.email == "demo@devcoach.app")):
            db.add(User(email="demo@devcoach.app", name="Alex Rivera", password_hash=hash_password("devcoach123"), level=7, streak=12))
        for title, language, code, issues in REVIEW_SNIPPETS:
            if not db.scalar(select(ReviewSnippet).where(ReviewSnippet.title == title)):
                db.add(ReviewSnippet(title=title, language=language, code=code, known_issues=json.dumps(issues, ensure_ascii=False), difficulty="Intermedio"))
        for kind, prompt, points, test_cases, time_limit in INTERVIEW_QUESTIONS:
            if not db.scalar(select(InterviewQuestion).where(InterviewQuestion.prompt == prompt)):
                db.add(InterviewQuestion(kind=kind, prompt=prompt, expected_points=json.dumps(points, ensure_ascii=False), test_cases=json.dumps(test_cases), time_limit_seconds=time_limit))
        db.commit()

if __name__ == "__main__":
    seed()

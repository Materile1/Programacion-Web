import json
from sqlalchemy import select
from app.database import Base, SessionLocal, engine
from app.models import Challenge, LearningPath, Level, User
from app.security import hash_password

LEVELS = [
    (0, "Orientación", "Pensamiento computacional"), (1, "Fundamentos", "Variables y tipos"), (2, "Control de flujo", "Condicionales"),
    (3, "Funciones", "Abstracción"), (4, "Estructuras", "Listas y diccionarios"), (5, "Algoritmos", "Complejidad"),
    (6, "POO", "Diseño de objetos"), (7, "Testing", "Calidad"), (8, "Git", "Colaboración"), (9, "SQL", "Persistencia"),
    (10, "APIs", "HTTP y contratos"), (11, "Backend", "Servicios"), (12, "Frontend", "Interfaces"), (13, "Arquitectura", "Sistemas"), (14, "Proyecto final", "Entrega profesional"),
]

def seed():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(LearningPath)):
            return
        path = LearningPath(title="Software Engineer", description="Ruta progresiva de fundamentos a sistemas en producción")
        db.add(path); db.flush()
        for index, title, skill in LEVELS:
            level = Level(path_id=path.id, number=index, title=title, skill=skill, status="completed" if index < 4 else ("active" if index == 4 else "locked"))
            db.add(level); db.flush()
            db.add(Challenge(level_id=level.id, title=f"Reto {index + 1}: {title}", prompt=f"Practica {skill.lower()} con una solución clara y verificable.", starter_code="def solve(data):\n    # escribe tu solución\n    return data\n", test_cases=json.dumps([{"input": 1, "output": 1}, {"input": 0, "output": 0}, {"input": -1, "output": -1}])))
        db.add(User(email="demo@devcoach.app", name="Alex Rivera", password_hash=hash_password("devcoach123"), level=7, streak=12))
        db.commit()

if __name__ == "__main__":
    seed()

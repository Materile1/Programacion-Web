# DevCoach

Plataforma de entrenamiento progresivo para programación, con dashboard React/TypeScript, API FastAPI, PostgreSQL y evaluación de dominio.

## Desarrollo local

```powershell
# API
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload --port 8000

# En otra terminal
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. La demo funciona sin login; para persistencia registra un usuario contra `POST /api/auth/register` y guarda el JWT como `devcoach_token`.

## Docker

`docker compose up --build` levanta PostgreSQL, la API en `http://localhost:8000` y el frontend en `http://localhost:5173`. La documentación OpenAPI queda en `http://localhost:8000/docs`.

## CI/CD

El workflow ejecuta Ruff, Pytest y el build de frontend en cada push/PR a `main`. Para desplegar en Render, añade el secreto `RENDER_DEPLOY_HOOK` con el deploy hook del servicio.

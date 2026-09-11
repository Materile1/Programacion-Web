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

Abre `http://localhost:5173`. Configura `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y `VITE_GOOGLE_CLIENT_ID` en `.env` para iniciar sesión con Google. El frontend guarda el JWT en `localStorage` y el ejecutor usa el daemon Docker del host.

## Docker

`docker compose up --build` levanta PostgreSQL, la API en `http://localhost:8000` y el frontend en `http://localhost:5173`. La documentación OpenAPI queda en `http://localhost:8000/docs`.

Para probar la ejecución, inicia sesión, abre `Práctica guiada`, edita `solve(data)` y pulsa `Ejecutar`. La API compara la salida con los casos del seed y guarda una entrega aprobada en `/api/progress`.

## CI/CD

El workflow ejecuta Ruff, Pytest y el build de frontend en cada push/PR a `main`. Para desplegar en Render, añade el secreto `RENDER_DEPLOY_HOOK` con el deploy hook del servicio.

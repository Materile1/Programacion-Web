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

Abre `http://localhost:5173`. Configura `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y `VITE_GOOGLE_CLIENT_ID` en `.env` para iniciar sesión con Google. El frontend guarda el JWT en `localStorage`. La ejecución de retos usa un subprocess de Python con AST, timeout y límites de CPU/memoria; no necesita un socket Docker.

El sandbox por subprocess es compatible con Render, pero ofrece un aislamiento menor que un contenedor: el proceso hereda el kernel y el usuario del servicio (en Linux intenta bajar a `nobody` cuando el proceso tiene privilegios), y los límites POSIX no existen en Windows. El bloqueo AST reduce imports y llamadas peligrosas, pero no debe considerarse una frontera de seguridad para código hostil de alto riesgo. Para ese nivel se necesitaría un servicio externo especializado o aislamiento de VM.

## Docker

`docker compose up --build` levanta PostgreSQL, la API en `http://localhost:8000` y el frontend en `http://localhost:5173`. La documentación OpenAPI queda en `http://localhost:8000/docs`.

Para probar la ejecución, inicia sesión, abre `Práctica guiada`, edita `solve(data)` y pulsa `Ejecutar`. La API compara la salida con los casos del seed y guarda una entrega aprobada en `/api/progress`.

### Render

El servicio `devcoach-api` es un despliegue monolítico: compila el frontend y FastAPI sirve la aplicación y la API desde el mismo dominio. En el dashboard de Render configura `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y `VITE_GOOGLE_CLIENT_ID` (este último con el mismo valor que `GOOGLE_CLIENT_ID`). `DATABASE_URL` se genera desde `devcoach-db`, `JWT_SECRET` se autogenera, `VITE_API_URL` queda en `/api` y `CORS_ORIGINS` debe coincidir con la URL pública del servicio, normalmente `https://devcoach-api.onrender.com`.

El workflow de GitHub Actions usa el secreto `RENDER_DEPLOY_HOOK`. Para habilitarlo, copia el deploy hook de Render en GitHub: `Settings` > `Secrets and variables` > `Actions` > `New repository secret`, usa exactamente ese nombre y pega la URL sin modificarla. El workflow no expone el valor; solo verifica que exista antes de hacer el POST.

La curaduría de contenido usa los RSS de Hacker News y Python Blog como contexto actual y reutiliza `OPENAI_API_KEY` o `GEMINI_API_KEY`; no requiere una variable adicional de búsqueda. Puede programarse con un cron externo o APScheduler llamando periódicamente a `POST /api/admin/content/refresh` con un usuario administrador.

## CI/CD

El workflow ejecuta Ruff, Pytest y el build de frontend en cada push/PR a `main`. Para desplegar en Render, añade el secreto `RENDER_DEPLOY_HOOK` con el deploy hook del servicio.

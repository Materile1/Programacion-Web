from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .database import Base, engine
from .routers import admin, auth, dashboard, interview, review, training

settings = get_settings()
Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(training.router, prefix="/api")
app.include_router(training.execution_router, prefix="/api")
app.include_router(dashboard.progress_router, prefix="/api")
app.include_router(training.progress_router, prefix="/api")
app.include_router(review.router, prefix="/api")
app.include_router(interview.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok", "service": "devcoach-api"}

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def frontend_routes(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        return FileResponse(FRONTEND_DIST / "index.html")

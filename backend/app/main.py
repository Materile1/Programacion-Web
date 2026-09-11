from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import Base, engine
from .routers import auth, dashboard, training

settings = get_settings()
Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(training.router, prefix="/api")
app.include_router(dashboard.progress_router, prefix="/api")
app.include_router(training.progress_router, prefix="/api")

@app.post("/api/execute", response_model=training.ExecuteOut, include_in_schema=False)
def execute_root(payload: training.ExecuteRequest, db=Depends(training.get_db), user=Depends(training.current_user)):
    return training.execute(payload, db, user)

@app.get("/health")
def health():
    return {"status": "ok", "service": "devcoach-api"}

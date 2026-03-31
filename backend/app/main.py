from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routers import auth, dashboard, exercises, professionals, profiles, workouts
from app.core.config import settings

app = FastAPI(title=settings.app_name)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
# Qualquer porta em localhost / 127.0.0.1 (evita CORS em dev quando a porta do Quasar muda)
_cors_local_regex = r"https?://(localhost|127\.0\.0\.1)(:\d+)?$"
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=_cors_local_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_path = Path(settings.upload_dir)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(upload_path)), name="media")

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(profiles.router, prefix=settings.api_prefix)
app.include_router(exercises.router, prefix=settings.api_prefix)
app.include_router(workouts.router, prefix=settings.api_prefix)
app.include_router(professionals.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

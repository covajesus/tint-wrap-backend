import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import (
    Base,
    SessionLocal,
    engine,
    ensure_blogs_date_columns,
    ensure_service_gallery_title_column,
    ensure_services_subtitle_column,
    ensure_sliders_schema,
    ensure_users_password_column,
    ensure_users_table,
)
from models import sliders, users  # noqa: F401 — registra modelos en metadata
from routers import (
    auth,
    blogs,
    configurations,
    service_galleries,
    services,
    sliders,
    tiktok,
    youtube,
)
from utils.cors_origins import get_cors_origins
from utils.media_storage import UPLOADS_ROOT, ensure_uploads_root
from utils.seed_admin import seed_default_admin
from utils.tiktok_sync_scheduler import run_tiktok_sync_scheduler
from utils.youtube_sync_scheduler import run_youtube_sync_scheduler


@asynccontextmanager
async def lifespan(_app: FastAPI):
    tiktok_task = asyncio.create_task(run_tiktok_sync_scheduler())
    youtube_task = asyncio.create_task(run_youtube_sync_scheduler())
    try:
        yield
    finally:
        for task in (tiktok_task, youtube_task):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


app = FastAPI(
    title="TintWrap API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

Base.metadata.create_all(bind=engine)
ensure_service_gallery_title_column()
ensure_services_subtitle_column()
ensure_blogs_date_columns()
ensure_sliders_schema()
ensure_users_table()
ensure_users_password_column()
ensure_uploads_root()

db = SessionLocal()
try:
    seed_default_admin(db)
finally:
    db.close()

app.include_router(auth.router)
app.include_router(blogs.router)
app.include_router(configurations.router)
app.include_router(service_galleries.router)
app.include_router(services.router)
app.include_router(sliders.router)
app.include_router(tiktok.router)
app.include_router(youtube.router)

app.mount(
    "/api/uploads",
    StaticFiles(directory=str(UPLOADS_ROOT)),
    name="uploads",
)


@app.get("/api/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "TintWrap API", "api": "/api", "docs": "/api/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

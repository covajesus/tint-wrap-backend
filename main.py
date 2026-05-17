import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import (
    Base,
    engine,
    ensure_service_gallery_title_column,
    ensure_services_subtitle_column,
    ensure_sliders_active_column,
)
from routers import (
    blogs,
    configurations,
    service_galleries,
    services,
    sliders,
    sliders_items,
    tiktok,
    youtube,
)
from utils.media_storage import UPLOADS_ROOT, ensure_uploads_root
from utils.tiktok_sync_scheduler import run_tiktok_sync_scheduler
from utils.youtube_sync_scheduler import run_youtube_sync_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    tiktok_task = asyncio.create_task(run_tiktok_sync_scheduler())
    youtube_task = asyncio.create_task(run_youtube_sync_scheduler())
    yield
    for task in (tiktok_task, youtube_task):
        task.cancel()
    for task in (tiktok_task, youtube_task):
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
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
ensure_service_gallery_title_column()
ensure_services_subtitle_column()
ensure_sliders_active_column()
ensure_uploads_root()

app.include_router(blogs.router)
app.include_router(configurations.router)
app.include_router(service_galleries.router)
app.include_router(services.router)
app.include_router(sliders_items.router)
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
    import os

    import uvicorn

    port = int(os.getenv("PORT", "8030"))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import (
    Base,
    SessionLocal,
    engine,
    ensure_service_gallery_title_column,
    ensure_services_subtitle_column,
    ensure_sliders_active_column,
    ensure_users_password_column,
    ensure_users_table,
)
from dependencies.auth import get_current_user
from models import users  # noqa: F401 — registra el modelo en metadata
from routers import (
    auth,
    blogs,
    configurations,
    service_galleries,
    services,
    sliders,
    sliders_items,
)
from utils.cors_origins import get_cors_origins
from utils.media_storage import UPLOADS_ROOT, ensure_uploads_root
from utils.seed_admin import seed_default_admin


app = FastAPI(
    title="TintWrap API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
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
ensure_sliders_active_column()
ensure_users_table()
ensure_users_password_column()
ensure_uploads_root()

db = SessionLocal()
try:
    seed_default_admin(db)
finally:
    db.close()

protected = [Depends(get_current_user)]

app.include_router(auth.router)
app.include_router(blogs.router, dependencies=protected)
app.include_router(configurations.router, dependencies=protected)
app.include_router(service_galleries.router, dependencies=protected)
app.include_router(services.router, dependencies=protected)
app.include_router(sliders_items.router, dependencies=protected)
app.include_router(sliders.router, dependencies=protected)

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

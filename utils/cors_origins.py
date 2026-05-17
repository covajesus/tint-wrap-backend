import os

_DEFAULT_ORIGINS = (
    # Vite dev / preview
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5174",
    "http://localhost:5174",
    "http://127.0.0.1:4173",
    "http://localhost:4173",
    # Firebase Hosting — sitio público
    "https://tintwrap-722e4.web.app",
    "https://tintwrap-722e4.firebaseapp.com",
    # Sitio público — https://tint-wrap.com/
    "https://tint-wrap.com",
    "https://www.tint-wrap.com",
    # Panel admin (producción)
    "https://admin.tint-wrap.com",
    "https://www.admin.tint-wrap.com",
    "https://admin-tint-wrap.web.app",
    "https://admin-tint-wrap.firebaseapp.com",
)


def get_cors_origins() -> list[str]:
    """
    Orígenes permitidos para CORS.
    Añade más en `.env`: CORS_ORIGINS=https://otro-dominio.com,https://app.ejemplo.com
    """
    extra = os.getenv("CORS_ORIGINS", "")
    from_env = [o.strip().rstrip("/") for o in extra.split(",") if o.strip()]

    seen: set[str] = set()
    result: list[str] = []
    for raw in (*_DEFAULT_ORIGINS, *from_env):
        origin = raw.strip().rstrip("/")
        if not origin or origin in seen:
            continue
        seen.add(origin)
        result.append(origin)
    return result

import os

_DEFAULT_ORIGINS = (
    # Vite dev / preview
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5174",
    "http://localhost:5174",
    "http://127.0.0.1:4173",
    "http://localhost:4173",
    # Firebase Hosting
    "https://tintwrap-722e4.web.app",
    "https://tintwrap-722e4.firebaseapp.com",
    # Dominio público
    "https://tint-wrap.com",
    "https://www.tint-wrap.com",
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
    for origin in (*_DEFAULT_ORIGINS, *from_env):
        if origin not in seen:
            seen.add(origin)
            result.append(origin)
    return result


def get_cors_origin_regex() -> str:
    """Firebase Hosting, dominio propio y localhost."""
    return (
        r"^https://([a-z0-9-]+\.)*(web\.app|firebaseapp\.com)$"
        r"|^https://(www\.)?tint-wrap\.com$"
        r"|^http://(localhost|127\.0\.0\.1)(:\d+)?$"
    )

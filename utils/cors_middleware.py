"""CORS explícito para OPTIONS (preflight) y respuestas con Authorization."""

from __future__ import annotations

import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from utils.cors_origins import get_cors_origin_regex, get_cors_origins


def _is_allowed_origin(origin: str | None) -> bool:
    if not origin:
        return False
    if origin in get_cors_origins():
        return True
    return re.fullmatch(get_cors_origin_regex(), origin) is not None


def _cors_headers(origin: str, request: Request) -> dict[str, str]:
    requested = request.headers.get("access-control-request-headers")
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": requested or "Authorization, Content-Type",
        "Access-Control-Max-Age": "86400",
        "Vary": "Origin",
    }


class ExplicitCorsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")

        if request.method == "OPTIONS" and _is_allowed_origin(origin):
            return Response(status_code=204, headers=_cors_headers(origin, request))

        response = await call_next(request)

        if _is_allowed_origin(origin):
            for key, value in _cors_headers(origin, request).items():
                if key not in ("Access-Control-Allow-Methods", "Access-Control-Max-Age"):
                    response.headers[key] = value
            response.headers.setdefault("Access-Control-Allow-Origin", origin)
            response.headers.setdefault("Access-Control-Allow-Credentials", "true")

        return response

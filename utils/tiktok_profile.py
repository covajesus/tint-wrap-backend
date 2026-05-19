from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from database import SessionLocal
from models.configurations import Configuration

logger = logging.getLogger(__name__)

_PROFILE_RE = re.compile(
    r"(?:https?://)?(?:www\.)?tiktok\.com/@([^/?#\s]+)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class TikTokProfile:
    username: str
    profile_url: str


def parse_tiktok_profile_url(url: str | None) -> TikTokProfile | None:
    raw = str(url or "").strip()
    if not raw:
        return None

    match = _PROFILE_RE.search(raw)
    if not match:
        return None

    username = match.group(1).strip().lstrip("@")
    if not username:
        return None

    return TikTokProfile(
        username=username,
        profile_url=f"https://www.tiktok.com/@{username}",
    )


def get_configured_tiktok_profile() -> TikTokProfile | None:
    try:
        db = SessionLocal()
        try:
            row = (
                db.query(Configuration)
                .filter(Configuration.id == 1)
                .first()
            )
            if row and row.tiktok_url:
                parsed = parse_tiktok_profile_url(row.tiktok_url)
                if parsed is not None:
                    return parsed
        finally:
            db.close()
    except Exception:
        logger.exception("No se pudo leer tiktok_url de configuración.")

    return None

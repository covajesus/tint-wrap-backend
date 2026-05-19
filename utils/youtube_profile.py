from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from database import SessionLocal
from models.configurations import Configuration

logger = logging.getLogger(__name__)

_HANDLE_RE = re.compile(
    r"(?:https?://)?(?:www\.)?youtube\.com/@([^/?#\s]+)",
    re.IGNORECASE,
)
_CHANNEL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?youtube\.com/channel/([^/?#\s]+)",
    re.IGNORECASE,
)
_C_USER_RE = re.compile(
    r"(?:https?://)?(?:www\.)?youtube\.com/(?:c|user)/([^/?#\s]+)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class YouTubeProfile:
    """handle: @nombre visible o ID de canal."""

    handle: str
    shorts_feed_url: str
    profile_url: str


def _display_handle(raw: str) -> str:
    handle = raw.strip().lstrip("@")
    return f"@{handle}" if handle else ""


def parse_youtube_profile_url(url: str | None) -> YouTubeProfile | None:
    raw = str(url or "").strip()
    if not raw:
        return None

    if not re.search(r"youtube\.com", raw, re.IGNORECASE):
        return None

    if re.search(r"/shorts/?(\?|#|$)", raw, re.IGNORECASE):
        base = raw.split("?")[0].rstrip("/")
        if not base.endswith("/shorts"):
            base = f"{base}/shorts"
        handle_match = _HANDLE_RE.search(raw) or _CHANNEL_RE.search(raw)
        handle = handle_match.group(1) if handle_match else ""
        profile_url = base.replace("/shorts", "") or raw
        return YouTubeProfile(
            handle=_display_handle(handle) if handle else "YouTube",
            shorts_feed_url=base,
            profile_url=profile_url,
        )

    match = _HANDLE_RE.search(raw)
    if match:
        handle = match.group(1).strip().rstrip("/")
        if handle.lower() == "shorts":
            return None
        return YouTubeProfile(
            handle=_display_handle(handle),
            shorts_feed_url=f"https://www.youtube.com/@{handle}/shorts",
            profile_url=f"https://www.youtube.com/@{handle}",
        )

    match = _CHANNEL_RE.search(raw)
    if match:
        channel_id = match.group(1).strip()
        return YouTubeProfile(
            handle=channel_id,
            shorts_feed_url=f"https://www.youtube.com/channel/{channel_id}/shorts",
            profile_url=f"https://www.youtube.com/channel/{channel_id}",
        )

    match = _C_USER_RE.search(raw)
    if match:
        name = match.group(1).strip()
        return YouTubeProfile(
            handle=_display_handle(name),
            shorts_feed_url=f"https://www.youtube.com/c/{name}/shorts",
            profile_url=f"https://www.youtube.com/c/{name}",
        )

    return None


def get_configured_youtube_profile() -> YouTubeProfile | None:
    try:
        db = SessionLocal()
        try:
            row = (
                db.query(Configuration)
                .filter(Configuration.id == 1)
                .first()
            )
            if row and row.youtube_url:
                parsed = parse_youtube_profile_url(row.youtube_url)
                if parsed is not None:
                    return parsed
        finally:
            db.close()
    except Exception:
        logger.exception("No se pudo leer youtube_url de configuración.")

    return None

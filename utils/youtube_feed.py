from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from utils.media_storage import UPLOADS_ROOT, ensure_uploads_root

logger = logging.getLogger(__name__)

YOUTUBE_SHORTS_URL = "https://www.youtube.com/@polarizadoyvinil/shorts"
YOUTUBE_CHANNEL_HANDLE = "polarizadoyvinil"
DEFAULT_LIMIT = 6
CACHE_TTL = timedelta(hours=1)
AUTO_SYNC_INTERVAL_HOURS = 6
AUTO_SYNC_INTERVAL_SECONDS = int(AUTO_SYNC_INTERVAL_HOURS * 3600)

YOUTUBE_UPLOAD_DIR = UPLOADS_ROOT / "youtube"
YOUTUBE_PUBLIC_PREFIX = "/api/uploads/youtube"

_VIDEO_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{6,32}$")

# Un solo archivo MP4 (sin ffmpeg para merge)
_YTDLP_FORMAT = "b[ext=mp4][height<=720]/b[ext=mp4]/b"


@dataclass(frozen=True)
class YouTubeShort:
    id: str
    title: str
    caption: str
    youtube_url: str
    thumbnail_path: str | None
    playback_path: str | None = None


_cache_at: datetime | None = None
_cache_videos: list[YouTubeShort] = []


def _ytdlp_executable() -> str:
    path = shutil.which("yt-dlp")
    if not path:
        raise RuntimeError(
            "yt-dlp no está instalado. Ejecuta: pip install yt-dlp"
        )
    return path


def _run_ytdlp_json(channel_url: str, limit: int) -> list[dict]:
    cmd = [
        _ytdlp_executable(),
        "--dump-json",
        "--playlist-end",
        str(limit),
        "--no-warnings",
        "--no-download",
        channel_url,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(stderr or "yt-dlp falló al leer los Shorts de YouTube.")

    entries: list[dict] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def _pick_thumbnail_url(entry: dict) -> str:
    thumb = entry.get("thumbnail")
    if isinstance(thumb, str) and thumb.strip():
        return thumb.strip()
    thumbs = entry.get("thumbnails")
    if isinstance(thumbs, list):
        for item in reversed(thumbs):
            if isinstance(item, dict):
                url = item.get("url")
                if isinstance(url, str) and url.strip():
                    return url.strip()
    return ""


def _download_thumbnail(video_id: str, remote_url: str) -> str | None:
    if not remote_url:
        return None
    ensure_uploads_root()
    YOUTUBE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = YOUTUBE_UPLOAD_DIR / f"{video_id}.jpg"
    try:
        request = Request(
            remote_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.youtube.com/",
            },
        )
        with urlopen(request, timeout=30) as response:
            data = response.read()
        dest.write_bytes(data)
        return f"{YOUTUBE_PUBLIC_PREFIX}/{video_id}.jpg"
    except Exception:
        logger.exception("No se pudo guardar miniatura YouTube %s", video_id)
        return remote_url


def _local_video_file(video_id: str) -> Path:
    return YOUTUBE_UPLOAD_DIR / f"{video_id}.mp4"


def _download_video_file(video_id: str, webpage_url: str) -> str | None:
    dest = _local_video_file(video_id)
    if dest.exists() and dest.stat().st_size > 50_000:
        return f"{YOUTUBE_PUBLIC_PREFIX}/{video_id}.mp4"

    ensure_uploads_root()
    YOUTUBE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    output_template = str(YOUTUBE_UPLOAD_DIR / f"{video_id}.%(ext)s")
    cmd = [
        _ytdlp_executable(),
        "-f",
        _YTDLP_FORMAT,
        "-o",
        output_template,
        "--no-warnings",
        "--no-playlist",
        webpage_url,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        check=False,
    )
    if result.returncode != 0:
        logger.error(
            "yt-dlp no pudo descargar Short %s: %s",
            video_id,
            (result.stderr or "").strip(),
        )
        return None

    if dest.exists() and dest.stat().st_size > 0:
        return f"{YOUTUBE_PUBLIC_PREFIX}/{video_id}.mp4"

    for candidate in YOUTUBE_UPLOAD_DIR.glob(f"{video_id}.*"):
        if candidate.suffix.lower() in {".mp4", ".webm", ".mkv"} and candidate.stat().st_size > 0:
            if candidate.suffix.lower() != ".mp4":
                try:
                    candidate.replace(dest)
                except OSError:
                    return f"{YOUTUBE_PUBLIC_PREFIX}/{candidate.name}"
            return f"{YOUTUBE_PUBLIC_PREFIX}/{video_id}.mp4"

    return None


def _entry_to_short(entry: dict) -> YouTubeShort | None:
    video_id = str(entry.get("id") or "").strip()
    if not video_id or not _VIDEO_ID_RE.match(video_id):
        return None

    title = str(entry.get("title") or entry.get("description") or "").strip()
    caption = str(entry.get("description") or title or "").strip()
    webpage = str(entry.get("webpage_url") or "").strip()
    if not webpage:
        webpage = f"https://www.youtube.com/shorts/{video_id}"

    remote_thumb = _pick_thumbnail_url(entry)
    thumbnail_path = _download_thumbnail(video_id, remote_thumb)
    playback_path = _download_video_file(video_id, webpage)

    return YouTubeShort(
        id=video_id,
        title=title or f"Short {video_id}",
        caption=caption,
        youtube_url=webpage,
        thumbnail_path=thumbnail_path,
        playback_path=playback_path,
    )


def fetch_latest_shorts(limit: int = DEFAULT_LIMIT, *, force: bool = False) -> list[YouTubeShort]:
    global _cache_at, _cache_videos

    now = datetime.now(timezone.utc)
    if (
        not force
        and _cache_at is not None
        and _cache_videos
        and now - _cache_at < CACHE_TTL
    ):
        return _cache_videos[:limit]

    entries = _run_ytdlp_json(YOUTUBE_SHORTS_URL, limit)
    videos: list[YouTubeShort] = []
    for entry in entries:
        short = _entry_to_short(entry)
        if short is not None:
            videos.append(short)

    if not videos:
        raise RuntimeError("No se encontraron Shorts en el canal de YouTube.")

    _prune_stale_media({video.id for video in videos})

    _cache_at = now
    _cache_videos = videos
    return videos[:limit]


def _prune_stale_media(active_ids: set[str]) -> None:
    if not YOUTUBE_UPLOAD_DIR.exists():
        return
    for path in YOUTUBE_UPLOAD_DIR.iterdir():
        if not path.is_file():
            continue
        if path.stem not in active_ids:
            try:
                path.unlink()
            except OSError:
                logger.exception("No se pudo borrar archivo YouTube obsoleto: %s", path)


def get_sync_metadata() -> dict[str, object]:
    return {
        "synced_at": _cache_at.isoformat() if _cache_at else None,
        "cache_ttl_hours": int(CACHE_TTL.total_seconds() // 3600),
        "auto_sync_interval_hours": AUTO_SYNC_INTERVAL_HOURS,
    }

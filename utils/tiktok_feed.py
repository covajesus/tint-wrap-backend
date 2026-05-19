from __future__ import annotations

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from utils.media_storage import UPLOADS_ROOT, ensure_uploads_root
from utils.tiktok_profile import TikTokProfile, get_configured_tiktok_profile

logger = logging.getLogger(__name__)

DEFAULT_LIMIT = 6
CACHE_TTL = timedelta(hours=1)
AUTO_SYNC_INTERVAL_HOURS = 6
AUTO_SYNC_INTERVAL_SECONDS = int(AUTO_SYNC_INTERVAL_HOURS * 3600)

TIKTOK_UPLOAD_DIR = UPLOADS_ROOT / "tiktok"
TIKTOK_PUBLIC_PREFIX = "/api/uploads/tiktok"


@dataclass(frozen=True)
class TikTokVideo:
    id: str
    title: str
    caption: str
    tiktok_url: str
    thumbnail_path: str | None
    playback_path: str | None = None
    stream_url: str | None = None


_cache_at: datetime | None = None
_cache_videos: list[TikTokVideo] = []
_cache_profile: TikTokProfile | None = None
_stream_cache: dict[str, tuple[datetime, str]] = {}
STREAM_CACHE_TTL = timedelta(minutes=30)


def invalidate_tiktok_cache() -> None:
    """Llamar cuando cambia tiktok_url en configuración."""
    global _cache_at, _cache_videos, _cache_profile, _stream_cache
    _cache_at = None
    _cache_videos = []
    _cache_profile = None
    _stream_cache.clear()


def _ytdlp_executable() -> str:
    path = shutil.which("yt-dlp")
    if not path:
        raise RuntimeError(
            "yt-dlp no está instalado. Ejecuta: pip install yt-dlp"
        )
    return path


def _run_ytdlp_json(profile_url: str, limit: int) -> list[dict]:
    cmd = [
        _ytdlp_executable(),
        "--dump-json",
        "--playlist-end",
        str(limit),
        "--no-warnings",
        "--no-download",
        profile_url,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(stderr or "yt-dlp falló al leer el perfil de TikTok.")

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
    TIKTOK_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = TIKTOK_UPLOAD_DIR / f"{video_id}.jpg"
    try:
        request = Request(
            remote_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.tiktok.com/",
            },
        )
        with urlopen(request, timeout=30) as response:
            data = response.read()
        dest.write_bytes(data)
        return f"{TIKTOK_PUBLIC_PREFIX}/{video_id}.jpg"
    except Exception:
        logger.exception("No se pudo guardar miniatura TikTok %s", video_id)
        return remote_url


def _local_video_file(video_id: str) -> Path:
    return TIKTOK_UPLOAD_DIR / f"{video_id}.mp4"


def _download_video_file(video_id: str, webpage_url: str) -> str | None:
    """Descarga el MP4 al servidor (TikTok bloquea proxy directo con 403)."""
    dest = _local_video_file(video_id)
    if dest.exists() and dest.stat().st_size > 50_000:
        return f"{TIKTOK_PUBLIC_PREFIX}/{video_id}.mp4"

    ensure_uploads_root()
    TIKTOK_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    output_template = str(TIKTOK_UPLOAD_DIR / f"{video_id}.%(ext)s")
    cmd = [
        _ytdlp_executable(),
        "-f",
        "bv*[height<=720]+ba/b[height<=720]/bv*+ba/b",
        "--merge-output-format",
        "mp4",
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
            "yt-dlp no pudo descargar %s: %s",
            video_id,
            (result.stderr or "").strip(),
        )
        return None

    if dest.exists() and dest.stat().st_size > 0:
        return f"{TIKTOK_PUBLIC_PREFIX}/{video_id}.mp4"

    for candidate in TIKTOK_UPLOAD_DIR.glob(f"{video_id}.*"):
        if candidate.suffix.lower() in {".mp4", ".webm", ".mkv"} and candidate.stat().st_size > 0:
            if candidate != dest:
                candidate.replace(dest)
            return f"{TIKTOK_PUBLIC_PREFIX}/{video_id}.mp4"

    return None


def _entry_to_video(entry: dict, *, username: str) -> TikTokVideo | None:
    video_id = str(entry.get("id") or "").strip()
    if not video_id:
        return None

    title = str(entry.get("title") or entry.get("description") or "").strip()
    caption = str(entry.get("description") or title or "").strip()
    webpage = str(entry.get("webpage_url") or "").strip()
    if not webpage:
        webpage = f"https://www.tiktok.com/@{username}/video/{video_id}"

    remote_thumb = _pick_thumbnail_url(entry)
    thumbnail_path = _download_thumbnail(video_id, remote_thumb)

    stream = str(entry.get("url") or "").strip() or None
    playback_path = _download_video_file(video_id, webpage)

    return TikTokVideo(
        id=video_id,
        title=title or f"Video {video_id}",
        caption=caption,
        tiktok_url=webpage,
        thumbnail_path=thumbnail_path,
        playback_path=playback_path,
        stream_url=stream,
    )


_CONFIG_MSG = (
    "Configura la URL de TikTok en Administración → Configuración "
    "(ej. https://www.tiktok.com/@tu_usuario)."
)


def fetch_latest_videos(limit: int = DEFAULT_LIMIT, *, force: bool = False) -> list[TikTokVideo]:
    global _cache_at, _cache_videos, _cache_profile

    profile = get_configured_tiktok_profile()
    if profile is None:
        raise RuntimeError(_CONFIG_MSG)

    now = datetime.now(timezone.utc)
    if (
        not force
        and _cache_at is not None
        and _cache_videos
        and _cache_profile is not None
        and _cache_profile.username == profile.username
        and now - _cache_at < CACHE_TTL
    ):
        return _cache_videos[:limit]

    try:
        entries = _run_ytdlp_json(profile.profile_url, limit)
    except RuntimeError as exc:
        if _cache_videos and _cache_profile and _cache_profile.username == profile.username:
            logger.warning("TikTok: usando caché tras fallo de yt-dlp: %s", exc)
            return _cache_videos[:limit]
        raise RuntimeError(
            "No se pudieron cargar los vídeos de TikTok. "
            "Comprueba la URL del perfil en Configuración y actualiza yt-dlp en el servidor."
        ) from exc

    videos: list[TikTokVideo] = []
    for entry in entries:
        video = _entry_to_video(entry, username=profile.username)
        if video is not None:
            videos.append(video)

    if not videos:
        if _cache_videos and _cache_profile and _cache_profile.username == profile.username:
            return _cache_videos[:limit]
        raise RuntimeError("No se encontraron vídeos en el perfil de TikTok.")

    _prune_stale_media({video.id for video in videos})

    _cache_at = now
    _cache_videos = videos
    _cache_profile = profile
    return videos[:limit]


def get_tiktok_profile_url() -> str:
    profile = get_configured_tiktok_profile()
    return profile.profile_url if profile is not None else ""


def _prune_stale_media(active_ids: set[str]) -> None:
    """Quita del disco videos/miniaturas que ya no están en el top actual."""
    if not TIKTOK_UPLOAD_DIR.exists():
        return
    for path in TIKTOK_UPLOAD_DIR.iterdir():
        if not path.is_file():
            continue
        if path.stem not in active_ids:
            try:
                path.unlink()
            except OSError:
                logger.exception("No se pudo borrar archivo TikTok obsoleto: %s", path)


def get_sync_metadata() -> dict[str, object]:
    return {
        "synced_at": _cache_at.isoformat() if _cache_at else None,
        "cache_ttl_hours": int(CACHE_TTL.total_seconds() // 3600),
        "auto_sync_interval_hours": AUTO_SYNC_INTERVAL_HOURS,
    }


def resolve_stream_url(video_id: str) -> str:
    video_id = str(video_id).strip()
    if not video_id.isdigit():
        raise ValueError("ID de video inválido.")

    profile = get_configured_tiktok_profile()
    if profile is None:
        raise RuntimeError(_CONFIG_MSG)

    now = datetime.now(timezone.utc)
    cached = _stream_cache.get(video_id)
    if cached and now - cached[0] < STREAM_CACHE_TTL:
        return cached[1]

    for video in _cache_videos:
        if video.id == video_id and video.stream_url:
            _stream_cache[video_id] = (now, video.stream_url)
            return video.stream_url

    url = f"https://www.tiktok.com/@{profile.username}/video/{video_id}"
    cmd = [
        _ytdlp_executable(),
        "-g",
        "-f",
        "bv*[height<=720]+ba/b[height<=720]/bv*+ba/b",
        "--no-warnings",
        url,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(stderr or "No se pudo obtener el video.")

    stream_url = (result.stdout or "").strip().splitlines()[0].strip()
    if not stream_url:
        raise RuntimeError("URL de reproducción vacía.")
    _stream_cache[video_id] = (now, stream_url)
    return stream_url

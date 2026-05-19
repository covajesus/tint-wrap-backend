from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, StreamingResponse

from utils.tiktok_feed import (
    DEFAULT_LIMIT,
    TIKTOK_PUBLIC_PREFIX,
    fetch_latest_videos,
    get_sync_metadata,
    get_tiktok_profile_url,
    resolve_stream_url,
)

router = APIRouter(prefix="/api/tiktok", tags=["TikTok"])


@router.get("/videos")
def list_videos(
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=10),
    refresh: bool = Query(default=False),
) -> dict:
    try:
        videos = fetch_latest_videos(limit=limit, force=refresh)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "profile_url": get_tiktok_profile_url(),
        **get_sync_metadata(),
        "videos": [
            {
                "id": video.id,
                "title": video.title,
                "caption": video.caption,
                "tiktok_url": video.tiktok_url,
                "thumbnail_url": (
                    video.thumbnail_path
                    if video.thumbnail_path
                    and video.thumbnail_path.startswith(TIKTOK_PUBLIC_PREFIX)
                    else video.thumbnail_path
                ),
                "playback_url": video.playback_path,
                "stream_url": f"/api/tiktok/videos/{video.id}/stream",
            }
            for video in videos
        ],
    }


@router.get("/videos/{video_id}/stream")
def stream_video(video_id: str) -> RedirectResponse:
    try:
        stream_url = resolve_stream_url(video_id)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return RedirectResponse(url=stream_url, status_code=302)


@router.get("/videos/{video_id}/proxy")
def proxy_video(video_id: str) -> StreamingResponse:
    """Proxy de respaldo si el CDN de TikTok bloquea redirecciones en <video>."""
    try:
        stream_url = resolve_stream_url(video_id)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        request = Request(
            stream_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.tiktok.com/",
            },
        )

        remote = urlopen(request, timeout=60)

        def iter_bytes():
            try:
                while True:
                    chunk = remote.read(1024 * 64)
                    if not chunk:
                        break
                    yield chunk
            finally:
                remote.close()

        content_type = remote.headers.get("Content-Type", "video/mp4")
        return StreamingResponse(
            iter_bytes(),
            media_type=content_type,
            headers={"Accept-Ranges": "bytes"},
        )
    except URLError as exc:
        raise HTTPException(status_code=502, detail="No se pudo reproducir el video.") from exc

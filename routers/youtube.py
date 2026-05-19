from fastapi import APIRouter, HTTPException, Query

from utils.youtube_feed import (
    DEFAULT_LIMIT,
    YOUTUBE_PUBLIC_PREFIX,
    fetch_latest_shorts,
    get_sync_metadata,
    get_youtube_profile_url,
)

router = APIRouter(prefix="/api/youtube", tags=["YouTube"])


@router.get("/shorts")
def list_shorts(
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=10),
    refresh: bool = Query(default=False),
) -> dict:
    try:
        videos = fetch_latest_shorts(limit=limit, force=refresh)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "profile_url": get_youtube_profile_url(),
        **get_sync_metadata(),
        "videos": [
            {
                "id": video.id,
                "title": video.title,
                "caption": video.caption,
                "youtube_url": video.youtube_url,
                "thumbnail_url": (
                    video.thumbnail_path
                    if video.thumbnail_path
                    and video.thumbnail_path.startswith(YOUTUBE_PUBLIC_PREFIX)
                    else video.thumbnail_path
                ),
                "playback_url": video.playback_path,
            }
            for video in videos
        ],
    }

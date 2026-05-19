from __future__ import annotations

import asyncio
import logging

from utils.tiktok_feed import (
    AUTO_SYNC_INTERVAL_SECONDS,
    DEFAULT_LIMIT,
    fetch_latest_videos,
)

logger = logging.getLogger(__name__)

_STARTUP_DELAY_SECONDS = 8


async def run_tiktok_sync_scheduler() -> None:
    """Sincroniza el perfil TikTok de configuración en segundo plano."""
    await asyncio.sleep(_STARTUP_DELAY_SECONDS)

    while True:
        try:
            await asyncio.to_thread(fetch_latest_videos, DEFAULT_LIMIT, force=True)
            logger.info("TikTok: feed sincronizado (%s videos).", DEFAULT_LIMIT)
        except Exception:
            logger.exception("TikTok: falló la sincronización automática.")

        await asyncio.sleep(AUTO_SYNC_INTERVAL_SECONDS)

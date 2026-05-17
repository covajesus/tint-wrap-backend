from __future__ import annotations

import asyncio
import logging

from utils.youtube_feed import (
    AUTO_SYNC_INTERVAL_SECONDS,
    DEFAULT_LIMIT,
    fetch_latest_shorts,
)

logger = logging.getLogger(__name__)

_STARTUP_DELAY_SECONDS = 20


async def run_youtube_sync_scheduler() -> None:
    """Sincroniza Shorts de YouTube en segundo plano."""
    await asyncio.sleep(_STARTUP_DELAY_SECONDS)

    while True:
        try:
            await asyncio.to_thread(fetch_latest_shorts, DEFAULT_LIMIT, force=True)
            logger.info("YouTube: Shorts sincronizados (%s).", DEFAULT_LIMIT)
        except Exception:
            logger.exception("YouTube: falló la sincronización automática.")

        await asyncio.sleep(AUTO_SYNC_INTERVAL_SECONDS)

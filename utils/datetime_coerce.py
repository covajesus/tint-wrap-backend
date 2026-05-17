"""Convierte fechas guardadas como texto en MySQL (ej. '2026-5-17 17:17:50')."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

_LOOSE = re.compile(
    r"^(\d{4})-(\d{1,2})-(\d{1,2})"
    r"(?:[ T](\d{1,2}):(\d{1,2}):(\d{1,2})(?:\.(\d+))?)?$"
)


def parse_db_datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return value

    text = value.strip()
    if not text:
        return None

    match = _LOOSE.match(text)
    if match:
        micro_raw = match.group(7) or "0"
        return datetime(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            int(match.group(4) or 0),
            int(match.group(5) or 0),
            int(match.group(6) or 0),
            int(micro_raw[:6].ljust(6, "0")[:6]),
        )

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    return None

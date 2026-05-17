import base64
import re
import shutil
import uuid
from pathlib import Path

UPLOADS_ROOT = Path(__file__).resolve().parent.parent / "uploads"
PUBLIC_PREFIX = "/api/uploads"

_DATA_URL_RE = re.compile(r"^data:([^;]+);base64,(.+)$", re.DOTALL | re.IGNORECASE)

_MIME_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/ogg": ".ogv",
    "video/quicktime": ".mov",
}


UPLOAD_SUBDIRS = (
    "services",
    "service-galleries",
    "blogs",
    "sliders",
)


def ensure_uploads_root() -> None:
    UPLOADS_ROOT.mkdir(parents=True, exist_ok=True)
    for name in UPLOAD_SUBDIRS:
        (UPLOADS_ROOT / name).mkdir(parents=True, exist_ok=True)


def ensure_service_upload_dir(service_id: int) -> Path:
    folder = UPLOADS_ROOT / "services" / str(service_id)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def ensure_slider_upload_dir(slider_id: int) -> Path:
    folder = UPLOADS_ROOT / "sliders" / str(slider_id)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _public_url(relative_posix: str) -> str:
    return f"{PUBLIC_PREFIX}/{relative_posix.replace(chr(92), '/')}"


def normalize_media_path(value: str | None) -> str | None:
    """Convierte URL absoluta del API a ruta /api/uploads/... para BD y disco."""
    if value is None:
        return None

    raw = str(value).strip()
    if not raw:
        return None

    if raw.startswith(PUBLIC_PREFIX + "/"):
        return raw

    marker = PUBLIC_PREFIX + "/"
    idx = raw.find(marker)
    if idx >= 0:
        return raw[idx:]

    return raw


def _local_path_from_public_url(public_url: str | None) -> Path | None:
    path = normalize_media_path(public_url)
    if not path or not path.startswith(PUBLIC_PREFIX + "/"):
        return None
    rel = path[len(PUBLIC_PREFIX) + 1 :]
    return UPLOADS_ROOT / Path(rel)


def delete_local_media(public_url: str | None) -> None:
    path = _local_path_from_public_url(public_url or "")
    if path and path.is_file():
        path.unlink(missing_ok=True)


def persist_media(value: str | None, *, folder: str) -> str | None:
    """Guarda base64 en disco o conserva URL/ruta ya persistida."""
    if value is None:
        return None

    raw = str(value).strip()
    if not raw:
        return None

    normalized = normalize_media_path(raw)
    if normalized and normalized.startswith(PUBLIC_PREFIX + "/"):
        local = _local_path_from_public_url(normalized)
        if local and local.is_file():
            return normalized

    if raw.startswith("http://") or raw.startswith("https://"):
        if normalized and normalized.startswith(PUBLIC_PREFIX + "/"):
            return normalized
        return raw

    match = _DATA_URL_RE.match(raw)
    if not match:
        return raw

    mime = match.group(1).strip().lower()
    payload = match.group(2)
    ext = _MIME_TO_EXT.get(mime, ".bin")
    filename = f"{uuid.uuid4().hex}{ext}"
    relative = f"{folder.strip('/')}/{filename}"

    dest_dir = UPLOADS_ROOT / folder.strip("/")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / filename
    dest_file.write_bytes(base64.b64decode(payload))

    return _public_url(relative)


def _persist_uploaded_file(
    value: str | None,
    *,
    folder: str,
    previous: str | None = None,
) -> str | None:
    prev_path = normalize_media_path(previous)
    new_value = persist_media(value, folder=folder)
    new_path = normalize_media_path(new_value)

    if prev_path and new_path and prev_path == new_path:
        return prev_path

    if (
        prev_path
        and new_path
        and prev_path != new_path
        and prev_path.startswith(PUBLIC_PREFIX + "/")
    ):
        delete_local_media(prev_path)

    return new_path if new_path is not None else new_value


def persist_service_gallery_file(
    value: str | None,
    *,
    service_id: int,
    field: str,
    previous: str | None = None,
) -> str | None:
    ensure_service_upload_dir(service_id)
    folder = f"services/{service_id}"
    return _persist_uploaded_file(value, folder=folder, previous=previous)


def persist_slider_media(
    value: str | None,
    *,
    slider_id: int,
    previous: str | None = None,
) -> str | None:
    ensure_slider_upload_dir(slider_id)
    folder = f"sliders/{slider_id}"
    return _persist_uploaded_file(value, folder=folder, previous=previous)


def delete_service_upload_folder(service_id: int) -> None:
    folder = UPLOADS_ROOT / "services" / str(service_id)
    if folder.is_dir():
        shutil.rmtree(folder, ignore_errors=True)


def delete_slider_upload_folder(slider_id: int) -> None:
    folder = UPLOADS_ROOT / "sliders" / str(slider_id)
    if folder.is_dir():
        shutil.rmtree(folder, ignore_errors=True)

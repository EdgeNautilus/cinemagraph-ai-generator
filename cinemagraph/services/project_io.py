"""Read/write .cmgx project archives (zip with metadata + masks)."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

_MAX_UNCOMPRESSED = 2 * 1024 * 1024 * 1024


def load_project(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        total = sum(info.file_size for info in zf.infolist())
        if total > _MAX_UNCOMPRESSED:
            raise ValueError(f"project exceeds size cap: {total} bytes")
        for name in zf.namelist():
            if name.startswith("/") or ".." in Path(name).parts:
                raise ValueError(f"unsafe entry in project: {name}")
        meta = json.loads(zf.read("metadata.json").decode("utf-8"))
    return meta


def save_project(path: Path, meta: dict, masks: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("metadata.json", json.dumps(meta, indent=2))
        for name, blob in masks.items():
            zf.writestr(f"masks/{name}", blob)
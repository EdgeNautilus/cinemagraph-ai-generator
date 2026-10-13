"""Disk cache for flow fields and rendered frames keyed by content hash."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np


class FrameCache:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def _key(self, *parts: bytes) -> str:
        h = hashlib.blake2b(digest_size=16)
        for part in parts:
            h.update(part)
        return h.hexdigest()

    def path_for(self, still: np.ndarray, params: str) -> Path:
        key = self._key(still.tobytes(), params.encode("utf-8"))
        return self._root / f"{key}.npz"

    def get(self, still: np.ndarray, params: str) -> np.ndarray | None:
        p = self.path_for(still, params)
        if not p.is_file():
            return None
        return np.load(p)["flow"]

    def put(self, still: np.ndarray, params: str, flow: np.ndarray) -> None:
        np.savez_compressed(self.path_for(still, params), flow=flow)
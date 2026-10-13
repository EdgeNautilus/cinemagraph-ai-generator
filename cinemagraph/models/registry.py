"""Model weight registry with SHA-256 verification."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

_MANIFEST: dict[str, dict[str, str]] = {
    "raft-small": {"file": "raft-small.onnx", "sha256": "
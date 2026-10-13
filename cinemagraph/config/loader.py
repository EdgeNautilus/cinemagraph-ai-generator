"""Load cinemagraph.toml from cwd, then %APPDATA%, then defaults."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from cinemagraph.config.schema import AppConfig

_CANDIDATES = (
    Path("cinemagraph.toml"),
    Path(os.environ.get("APPDATA", "")) / "cinemagraph-ai-generator" / "cinemagraph.toml",
)


def load_config() -> AppConfig:
    for candidate in _CANDIDATES:
        if candidate.is_file():
            with candidate.open("rb") as fh:
                return AppConfig.model_validate(tomllib.load(fh))
    return AppConfig()
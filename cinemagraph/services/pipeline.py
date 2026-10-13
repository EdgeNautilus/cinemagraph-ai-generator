"""End-to-end pipeline: still + mask -> cinemagraph frames."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from cinemagraph.config.schema import AppConfig
from cinemagraph.motion.flow import estimate_flow
from cinemagraph.motion.mask import MaskSpec
from cinemagraph.synthesis.loop import CinemagraphResult, synthesize_loop
from cinemagraph.utils.image_io import read_image


def render_cinemagraph(
    still: Path | np.ndarray,
    spec: MaskSpec,
    cfg: AppConfig,
) -> CinemagraphResult:
    img = still if isinstance(still, np.ndarray) else read_image(still)
    mask = spec.rasterize(img.shape[:2])

    # Seed flow from a slight synthetic translation so RAFT has a pair.
    from cinemagraph.utils.image_io import shift
    seed_b = shift(img, dx=3, dy=0)
    flow = estimate_flow(img, seed_b, cfg.motion.flow_model, cfg.models.device)

    return synthesize_loop(
        img, mask, flow,
        fps=cfg.render.fps,
        duration_s=cfg.render.duration_s,
        passes=cfg.render.loop_passes,
        seam=cfg.render.seam_blend,
    )
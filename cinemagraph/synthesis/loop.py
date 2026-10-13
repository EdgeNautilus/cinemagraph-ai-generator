"""Seamless loop synthesis from a still + motion mask + flow field."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from cinemagraph.motion.flow import FlowField
from cinemagraph.synthesis.warp import remap_frame


@dataclass(slots=True)
class CinemagraphResult:
    frames: list[np.ndarray]
    fps: int

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def duration_s(self) -> float:
        return self.frame_count / self.fps


def synthesize_loop(
    still: np.ndarray,
    mask: np.ndarray,
    flow: FlowField,
    fps: int = 24,
    duration_s: float = 3.0,
    passes: int = 3,
    seam: str = "cosine",
) -> CinemagraphResult:
    """Generate a ping-pong loop that returns to the still at the seam.

    `passes` controls how many eased forward/back cycles are packed into
    the duration. Higher passes = faster perceived motion.
    """
    n_frames = max(int(fps * duration_s), 8)
    mask_f = mask.astype(np.float32) / 255.0
    flow_v = flow.vector

    frames: list[np.ndarray] = []
    for i in range(n_frames):
        phase = _phase(i, n_frames, passes)
        warped = remap_frame(still, flow_v * phase, mask_f)
        frames.append(warped)

    frames = _apply_seam(frames, seam)
    return CinemagraphResult(frames=frames, fps=fps)


def _phase(i: int, n: int, passes: int) -> float:
    # Ping-pong ease: 0 -> 1 -> 0 over each pass.
    t = (i / n) * passes
    tri = abs((t % 1.0) * 2.0 - 1.0)
    return float(np.sin(tri * np.pi) * 0.5)


def _apply_seam(frames: list[np.ndarray], seam: str) -> list[np.ndarray]:
    if seam == "linear" or len(frames) < 3:
        return frames
    head, tail = frames[0], frames[-1]
    if seam == "cosine":
        blend = cv2.addWeighted(head, 0.5, tail, 0.5, 0.0)
        frames[0] = blend
        frames[-1] = blend.copy()
    elif seam == "poisson":
        # Cheap Poisson-ish: match mean in overlapping band.
        band = 8
        h = head.shape[0]
        head[-band:] = tail[-band:]
        frames[0] = head
    return frames
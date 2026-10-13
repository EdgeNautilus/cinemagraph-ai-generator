"""Optical flow estimation via ONNX RAFT or OpenCV Farneback fallback."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from cinemagraph.models.registry import load_model


@dataclass(frozen=True, slots=True)
class FlowField:
    """Dense optical flow between two frames.

    Shape: (H, W, 2) float32, channel 0 = dx, channel 1 = dy (pixels).
    """
    vector: np.ndarray

    @property
    def magnitude(self) -> np.ndarray:
        return np.linalg.norm(self.vector, axis=-1).astype(np.float32)


def estimate_flow(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
    model_name: str = "raft-small",
    device: str = "cuda",
) -> FlowField:
    """Estimate dense flow A->B.

    Falls back to Farneback if the ONNX session is unavailable.
    """
    if model_name == "farneback":
        return _farneback(frame_a, frame_b)
    try:
        session = load_model(model_name, device)
        return _raft_infer(session, frame_a, frame_b)
    except FileNotFoundError:
        return _farneback(frame_a, frame_b)


def _farneback(a: np.ndarray, b: np.ndarray) -> FlowField:
    ga = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    gb = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(
        ga, gb, None, pyr_scale=0.5, levels=4, winsize=21,
        iterations=3, poly_n=7, poly_sigma=1.5, flags=0,
    )
    return FlowField(vector=flow.astype(np.float32))


def _raft_infer(session, a: np.ndarray, b: np.ndarray) -> FlowField:  # type: ignore[no-untyped-def]
    # RAFT expects normalized float32 CHW in [0,1].
    import onnxruntime as ort

    def _prep(img: np.ndarray) -> np.ndarray:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        return np.transpose(rgb, (2, 0, 1))[None, ...]

    inp = {session.get_inputs()[0].name: _prep(a), session.get_inputs()[1].name: _prep(b)}
    out = session.run(None, inp)[0][0]
    flow = np.transpose(out, (1, 2, 0)).astype(np.float32)
    return FlowField(vector=flow)
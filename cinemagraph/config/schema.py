"""Pydantic schema for cinemagraph.toml."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RenderConfig(BaseModel):
    fps: int = Field(24, ge=8, le=60)
    duration_s: float = Field(3.0, gt=0.5, le=30.0)
    loop_passes: int = Field(3, ge=1, le=16)
    seam_blend: Literal["linear", "cosine", "poisson"] = "cosine"


class MotionConfig(BaseModel):
    flow_model: Literal["raft-small", "raft-base", "farneback"] = "raft-small"
    mask_feather_px: int = Field(6, ge=0, le=64)
    flow_scale: float = Field(1.0, gt=0.1, le=4.0)


class ModelConfig(BaseModel):
    weights_dir: str = "models/weights"
    device: Literal["cuda", "cpu"] = "cuda"
    onnx_providers: list[str] = Field(default_factory=lambda: ["CUDAExecutionProvider"])


class AppConfig(BaseModel):
    render: RenderConfig = Field(default_factory=RenderConfig)
    motion: MotionConfig = Field(default_factory=MotionConfig)
    models: ModelConfig = Field(default_factory=ModelConfig)
    theme: Literal["dark", "light"] = "dark"
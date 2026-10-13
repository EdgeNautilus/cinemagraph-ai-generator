"""Export cinemagraph frames to video or animated image formats."""

from __future__ import annotations

import enum
import subprocess
from pathlib import Path

from cinemagraph.synthesis.loop import CinemagraphResult


class ExportFormat(str, enum.Enum):
    WEBM = "webm"
    MP4 = "mp4"
    GIF = "gif"
    APNG = "apng"


_FFMPEG_ARGS = {
    ExportFormat.WEBM: ["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "28"],
    ExportFormat.MP4: ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20"],
}


def export_loop(result: CinemagraphResult, out: Path, fmt: ExportFormat) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if fmt in (ExportFormat.GIF, ExportFormat.APNG):
        _export_animated(result, out, fmt)
        return
    _export_ffmpeg(result, out, fmt)


def _export_ffmpeg(result: CinemagraphResult, out: Path, fmt: ExportFormat) -> None:
    import numpy as np
    h, w = result.frames[0].shape[:2]
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24",
        "-s", f"{w}x{h}", "-r", str(result.fps),
        "-i", "-",
        *_FFMPEG_ARGS[fmt],
        str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    for frame in result.frames:
        proc.stdin.write(np.ascontiguousarray(frame).tobytes())
    proc.stdin.close()
    proc.wait()


def _export_animated(result: CinemagraphResult, out: Path, fmt: ExportFormat) -> None:
    from PIL import Image
    pil_frames = [Image.fromarray(f[..., ::-1]) for f in result.frames]
    save_kwargs = {"save_all": True, "append_images": pil_frames[1:], "duration": int(1000 / result.fps)}
    if fmt is ExportFormat.GIF:
        pil_frames[0].save(out, format="GIF", loop=0, **save_kwargs)
    else:
        pil_frames[0].save(out, format="PNG", **save_kwargs)
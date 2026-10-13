"""Headless CLI entrypoint.

Usage:
    cinemagraph render input.png --motion motion.json --out loop.webm
    cinemagraph batch ./stills --preset portrait-soft --out ./exports
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from cinemagraph.config.loader import load_config
from cinemagraph.motion.mask import MaskSpec
from cinemagraph.services.export import ExportFormat, export_loop
from cinemagraph.services.pipeline import render_cinemagraph

app = typer.Typer(add_completion=False, help="cinemagraph-ai-generator CLI")
console = Console()


@app.command()
def render(
    image: Path = typer.Argument(..., exists=True, dir_okay=False),
    motion: Path = typer.Option(None, "--motion", help="Motion mask JSON"),
    preset: str = typer.Option("portrait-soft", "--preset"),
    out: Path = typer.Option(Path("loop.webm"), "--out"),
    fmt: ExportFormat = typer.Option(ExportFormat.WEBM, "--format"),
) -> None:
    """Render a single still into a seamless looping cinemagraph."""
    cfg = load_config()
    spec = MaskSpec.from_json(motion) if motion else MaskSpec.auto(preset)
    result = render_cinemagraph(image, spec, cfg)
    export_loop(result, out, fmt)
    console.print(f"[green]wrote[/] {out} — {result.frame_count} frames, {result.duration_s:.2f}s")


@app.command()
def batch(
    folder: Path = typer.Argument(..., exists=True, file_okay=False),
    preset: str = typer.Option("portrait-soft", "--preset"),
    out: Path = typer.Option(Path("exports"), "--out"),
) -> None:
    """Batch-render every still in a folder."""
    cfg = load_config()
    out.mkdir(parents=True, exist_ok=True)
    for still in sorted(folder.glob("*.png")) + sorted(folder.glob("*.jpg")):
        spec = MaskSpec.auto(preset)
        result = render_cinemagraph(still, spec, cfg)
        target = out / f"{still.stem}.webm"
        export_loop(result, target, ExportFormat.WEBM)
        console.print(f"[cyan]ok[/] {still.name} -> {target.name}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
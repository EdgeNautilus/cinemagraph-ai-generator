# Contributing to cinemagraph-ai-generator

Thanks for wanting to push cinemagraph synthesis forward. This repo is a
Windows-first desktop tool that turns a still image (or short clip) into a
seamless looping cinemagraph using motion masking, optical-flow warp, and a
loop-seam synthesizer.

## Ground rules

- One feature per PR. If it touches `cinemagraph/motion/` and
  `cinemagraph/synthesis/`, split it.
- Every new mask or loop strategy needs a fixture under `tests/fixtures/`.
- No model weights in-tree. Runtime pulls via `cinemagraph/models/registry.py`.
- Type hints required on all public functions. `mypy --strict` on `cinemagraph/`.
- Ruff for lint/format. Config lives in `pyproject.toml`.

## Dev setup

```
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev,cuda]"
pytest -q
```

## Architecture map

- `cinemagraph/app/` — Qt bootstrap, window wiring, CLI entry
- `cinemagraph/motion/` — optical flow, motion vector estimation, mask painting
- `cinemagraph/synthesis/` — loop-seam synthesis, temporal diffusion, frame blend
- `cinemagraph/handlers/` — event/command handlers between UI and pipeline
- `cinemagraph/services/` — export, cache, telemetry (opt-in), project IO
- `cinemagraph/models/` — tensor models, weight registry, ONNX runtime wrapper
- `cinemagraph/config/` — schema + loader for `cinemagraph.toml`
- `cinemagraph/utils/` — image io, ffmpeg bridge, color, logging

## Commit style

`motion(mask): feather edge radius on brush stroke`
`synth(loop): fix seam drift when period > 48 frames`
`app(ui): dock the mask timeline under the canvas`

## Reporting bugs

Open an issue with: Windows build, GPU + driver, sample image, and the
`cinemagraph.toml` you used. Attach the `.cmgx` project file if you can.
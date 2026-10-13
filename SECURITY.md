# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | ✅        |
| 0.5.x   | ✅ (security only) |
| < 0.5   | ❌        |

## Reporting a vulnerability

Email `security@cinemagraph-ai-generator.dev` with a PoC, affected version,
and impact. We aim to triage within 72 hours.

Do **not** open public issues for:

- Arbitrary code execution via a crafted `.cmgx` project file
- Path traversal in `cinemagraph/services/project_io.py`
- Unsafe deserialization in model weight loading
- ffmpeg argument injection through the export pipeline

## Threat model notes

Cinemagraph projects (`.cmgx`) are zip archives containing metadata, mask
PNGs, and a config blob. They are **untrusted input**. The loader must:

- Reject absolute paths and `..` segments
- Cap decompressed size (zip bomb guard, 2 GiB default)
- Never `eval` any field from the config blob

Runtime model downloads verify SHA-256 against the registry manifest before
loading. If the hash mismatches, the model is quarantined and the run aborts.

## Out of scope

- DoS from deliberately huge images (user-configurable, documented)
- GPU driver crashes (report to vendor)
- Anything requiring an already-compromised host
# Testing

Install development tools with `python -m pip install -e ".[dev]"`. Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, `python -m build` and `python -m pip_audit .`.

The tests cover nested overlaps, source order, non-positive durations, reading speed, malformed timestamps, WebVTT settings and metadata blocks, inline timestamp shifts, BOM/CRLF preservation, source and plan tampering, explicit review, and refusal to overwrite existing outputs.

## Verified environments

On 2026-10-15, the Linux suite passed 24 tests with 96.93% branch-aware coverage. Formatting, lint, strict typing, dependency audit and package builds passed. GitHub CI also passed on Python 3.11 across Windows, macOS and Linux. CodeQL analysis and result upload passed.

A native Windows CLI check shifted a synthetic WebVTT cue from 1–3 seconds to 11–13 seconds and its inline timestamp from 2 to 12 seconds. The source file's SHA-256 was unchanged. All fixtures are synthetic.

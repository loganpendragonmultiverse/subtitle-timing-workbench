# Changelog

## 0.1.0-rc.1 — 2026-10-15

- Added uTF-8 SRT and WebVTT timing validation, all overlapping cue pairs (including nested cues), source-order evidence, non-positive durations, configurable reading-speed evidence and reviewed global millisecond offsets. Timings are preserved as integer milliseconds; original BOM, line endings, cue text, identifiers, settings and metadata blocks are preserved during export.
- Added original implementation, synthetic fixtures, safety regression tests, usage documentation and MIT licensing.
- Candidate only: no public release or catalog deployment is claimed.

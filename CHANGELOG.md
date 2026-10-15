# Changelog

## 0.1.0 — 2026-10-15

- Added UTF-8 SRT and WebVTT timing validation, all overlapping cue pairs (including nested cues), source-order evidence, non-positive durations, configurable reading-speed evidence and reviewed global millisecond offsets. Timings are preserved as integer milliseconds; original BOM, line endings, identifiers, settings, metadata blocks and visible cue text are preserved during export. Supported WebVTT inline timestamp tags shift by the same offset as cue boundaries and appear in before/after review evidence.
- Shift WebVTT inline timestamp tags with cue boundaries and show their before/after values in review evidence; accept later cue identifiers beginning WEBVTT.
- Added synthetic examples, regression tests, usage documentation and MIT licensing.
- Added version-checked release packaging with SHA-256 checksums.

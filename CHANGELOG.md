# Changelog

## 0.1.0 — 2026-10-15

- Added UTF-8 SRT and WebVTT timing validation, all overlapping cue pairs (including nested cues), source-order evidence, non-positive durations, configurable reading-speed evidence and reviewed global millisecond offsets. Timings are preserved as integer milliseconds; original BOM, line endings, identifiers, settings, metadata blocks and visible cue text are preserved during export. Supported WebVTT inline timestamp tags shift by the same offset as cue boundaries and appear in before/after review evidence.
- Shift WebVTT inline timestamp tags with cue boundaries and show their before/after values in review evidence; accept later cue identifiers beginning WEBVTT.
- Added original implementation, synthetic fixtures, safety regression tests, usage documentation and MIT licensing.
- Release preparation includes corrected privacy/support wording and tag-build checksum packaging. Publication remains gated; this changelog alone does not establish a public release.

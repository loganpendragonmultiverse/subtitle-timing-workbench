# Changelog

## 0.1.1 — 2026-10-20

- Ship all four authority documents and the synthetic subtitle example in installed wheels.

- Bound actual subtitle and review-plan reads instead of relying on a prior file-size check.
- Reject non-object, duplicate-key, deeply nested and type-altered review plans before creating output. Reject oversized generated plans before export.
- Identify WebVTT inline timestamps outside cue boundaries or in non-increasing order while retaining before/after review evidence and source preservation.
- Add malformed-plan, read-budget and inline-timing regression coverage.

## 0.1.0 — 2026-10-15

- Added UTF-8 SRT and WebVTT timing validation, all overlapping cue pairs (including nested cues), source-order evidence, non-positive durations, configurable reading-speed evidence and reviewed global millisecond offsets. Timings are preserved as integer milliseconds; original BOM, line endings, identifiers, settings, metadata blocks and visible cue text are preserved during export. Supported WebVTT inline timestamp tags shift by the same offset as cue boundaries and appear in before/after review evidence.
- Shift WebVTT inline timestamp tags with cue boundaries and show their before/after values in review evidence; accept later cue identifiers beginning WEBVTT.
- Added synthetic examples, regression tests, usage documentation and MIT licensing.
- Added version-checked release packaging with SHA-256 checksums.

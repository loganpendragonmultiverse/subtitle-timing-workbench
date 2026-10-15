# Subtitle Timing Workbench

Validate local SRT/WebVTT timing and review source-preserving offsets.

Version: **0.1.0**. [GitHub Releases](https://github.com/loganpendragonmultiverse/subtitle-timing-workbench/releases) identifies published downloads and release status. Original implementation for Logan Pendragon Forge. MIT licensed. No paid services, account or credentials are needed.

## Three-minute start

```sh
python -m pip install .
subtitle-timing-workbench inspect examples/sample.srt --output audit.json
subtitle-timing-workbench plan examples/sample.srt --offset-ms 500 --output plan.json
# Review the before/after evidence and hashes in plan.json.
subtitle-timing-workbench apply examples/sample.srt --plan plan.json --reviewed --output shifted.srt
```

## What this candidate does

UTF-8 SRT and WebVTT timing validation, all overlapping cue pairs (including nested cues), source-order evidence, non-positive durations, configurable reading-speed evidence and reviewed global millisecond offsets. Timings are preserved as integer milliseconds; original BOM, line endings, identifiers, settings, metadata blocks and visible cue text are preserved during export. Supported WebVTT inline timestamp tags shift by the same offset as cue boundaries and appear in before/after review evidence.

## Privacy and safe operation

No network, telemetry, account, persistent cache or media access. Only explicitly selected subtitle and plan files are read. Reports contain timing evidence; review plans bind source bytes and output bytes using SHA-256. All output paths use exclusive creation, so original and existing files cannot be overwritten.

## Boundaries

This is a timing workbench, not a full WebVTT specification validator or subtitle editor. WebVTT NOTE/STYLE/REGION blocks are preserved without semantic validation. No media playback, translation, per-cue editing, automatic correction, or alignment to audio. Character speed excludes whitespace and markup and counts Unicode code points, not visual graphemes; it is review evidence, not a universal readability rule. Inputs are limited to 5 MB, 20,000 cues and 100,000 overlap pairs; timestamps after shifts must remain within 00..99 hours.

## Development and support

Requires Python 3.11+; the runtime has no third-party dependencies. Windows and Linux acceptance results are recorded in TESTING.md; the Windows, macOS and Linux CI matrices also passed for the prepared source. See [DEVELOPMENT.md](DEVELOPMENT.md), [TESTING.md](TESTING.md), [SECURITY.md](SECURITY.md), and [CHANGELOG.md](CHANGELOG.md). Pull requests receive maintainer review; no contribution or release merges automatically. Maintenance is on demand, with no service-level commitment.

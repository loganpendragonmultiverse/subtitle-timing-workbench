# Development handoff

Approved scope: UTF-8 SRT and WebVTT timing validation, all overlapping cue pairs (including nested cues), source-order evidence, non-positive durations, configurable reading-speed evidence and reviewed global millisecond offsets. Timings are preserved as integer milliseconds; original BOM, line endings, cue text, identifiers, settings and metadata blocks are preserved during export.

No network, telemetry, account, persistent cache or media access. Only explicitly selected subtitle and plan files are read. Reports contain timing evidence; review plans bind source bytes and output bytes using SHA-256. All output paths use exclusive creation, so original and existing files cannot be overwritten.

This is a timing workbench, not a full WebVTT specification validator or subtitle editor. WebVTT NOTE/STYLE/REGION blocks are preserved without semantic validation. No media playback, translation, per-cue editing, automatic correction, or alignment to audio. Character speed excludes whitespace and markup and counts Unicode code points, not visual graphemes; it is review evidence, not a universal readability rule. Inputs are limited to 5 MB, 20,000 cues and 100,000 overlap pairs; timestamps after shifts must remain within 00..99 hours.

Repository target: `loganpendragonmultiverse/subtitle-timing-workbench`. Candidate version: `v0.1.0` (PEP 440: 0.1.0). Source must remain independent of all existing portfolio implementations. Shared community files and pinned CI conventions follow the canonical portfolio.

Install editable development dependencies with `python -m pip install -e ".[dev]"`. Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, `python -m build` and `python -m pip_audit .`. Runtime dependencies are empty.

## Publication gate

This candidate does not authorize bypassing protected branches, failed checks or security review. Before a public release: review scope and source; run CI and CodeQL; configure protected main and required checks, squash-only merges, resolved conversations, read-only workflow permissions, security reporting, scanning and dependency alerts; obtain maintainer release review; build from the reviewed annotated tag; verify downloadable SHA-256 values; publish exact approved source/artifacts. Enable Pages for the keyboard app after browser acceptance. Parent task owns catalog coordination: update release register, catalog, generated information pages and sitemap only after verified GitHub release evidence, then render/deploy/live-verify and reconcile the Open Source Engine. Reconcile/audit organization all-activity watches. Do not advertise candidate versions as released.

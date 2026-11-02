# Development

Scope: UTF-8 SRT and WebVTT timing validation, all overlapping cue pairs (including nested cues), source-order evidence, non-positive durations, configurable reading-speed evidence and reviewed global millisecond offsets. Timings are preserved as integer milliseconds; original BOM, line endings, identifiers, settings, metadata blocks and visible cue text are preserved during export. Supported WebVTT inline timestamp tags shift by the same offset as cue boundaries and appear in before/after review evidence.

No network, telemetry, account, persistent cache or media access. Only explicitly selected subtitle and plan files are read. Reports contain timing evidence; review plans bind source bytes and output bytes using SHA-256. All output paths use exclusive creation, so original and existing files cannot be overwritten.

This is a timing workbench, not a full WebVTT specification validator or subtitle editor. WebVTT NOTE/STYLE/REGION blocks are preserved without semantic validation. No media playback, translation, per-cue editing, automatic correction, or alignment to audio. Character speed excludes whitespace and markup and counts Unicode code points, not visual graphemes; it is review evidence, not a universal readability rule. Inputs are limited to 5 MB, 20,000 cues and 100,000 overlap pairs; timestamps after shifts must remain within 00..99 hours.

Install editable development dependencies with `python -m pip install -e ".[dev]"`. Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, `python -m build` and `python -m pip_audit .`. Runtime dependencies are empty.

## Release process

Use a branch and pull request for changes. Run the test matrix and CodeQL, resolve review conversations, and let the maintainer make the final merge decision. CI workflows use read-only permissions and pinned actions.

For a release, keep the package version and changelog in agreement, create an annotated semantic-version tag, and use that tag's successful release build. Verify the downloadable files against SHA256SUMS before publishing a GitHub release. Never bypass repository protections or publish artifacts from a different commit.

## 0.1.1 completion review

Read at most the configured limit plus one byte from subtitle and plan inputs;
never treat stat metadata as a read budget. Reject generated plans over 30 MB before
creating a destination. Parse plans as unique-key objects and compare canonical JSON
with preserved types so a boolean or float cannot substitute for integer evidence.
Nesting over 100 levels fails with an actionable error. Inline timestamp ordering and
cue-boundary violations are findings, preserved by a global shift, rather than a
claim of complete WebVTT semantic validation. Tests cover malformed plan roots,
duplicate keys, deep nesting, altered numeric types, actual read limits and
source/output preservation. Repeat all documented checks and installed wheel/sdist
CLI acceptance from exact tag-built artifacts.

Installed wheels include the four authority documents and synthetic SRT sample at
`share/doc/subtitle-timing-workbench` under Python's data prefix. Locate it with
`python -c "import sysconfig; print(sysconfig.get_path('data'))"`. Run inspect, plan
and reviewed apply against that installed sample, writing only new disposable outputs.
Release acceptance installs exact tag wheel/sdist distributions in fresh environments,
checks installed documentation/example hashes and repeats those CLI flows outside source.

# Testing

Install development tools with `python -m pip install -e ".[dev]"`. Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, `python -m build` and `python -m pip_audit .`.

The tests cover nested overlaps, source order, non-positive durations, reading speed, malformed timestamps, WebVTT settings and metadata blocks, inline timestamp shifts, BOM/CRLF preservation, source and plan tampering, explicit review, and refusal to overwrite existing outputs.

## Verified environments

On 2026-10-15, the Linux suite passed 24 tests with 96.93% branch-aware coverage. Formatting, lint, strict typing, dependency audit and package builds passed. GitHub CI also passed on Python 3.11 across Windows, macOS and Linux. CodeQL analysis and result upload passed.

A native Windows CLI check shifted a synthetic WebVTT cue from 1–3 seconds to 11–13 seconds and its inline timestamp from 2 to 12 seconds. The source file's SHA-256 was unchanged. All fixtures are synthetic.

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

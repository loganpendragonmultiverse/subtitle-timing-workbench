# Testing

Tests exercise nested overlaps, exact boundaries, out-of-order and invalid durations, reading speed, malformed timestamps, WebVTT settings and NOTE blocks, BOM/CRLF preservation, source tampering, plan tampering, explicit review and existing-output refusal.

`python -m pip install -e ".[dev]"`; `ruff format --check .`; `ruff check .`; `mypy src`; `pytest`; `python -m build`.

Exact execution results and environment evidence are supplied with the RC bundle. CI definitions are not proof of completed remote CI. Public release remains gated on successful remote checks and maintainer security review.

## Candidate evidence — 2026-10-15

Windows Python 3.14.3: 19 tests passed; branch-aware coverage 96.80%; Ruff format/lint and strict mypy passed; wheel and source distribution built.

Linux container and remote CI results are recorded in the release-candidate evidence packet. macOS and Firefox remain unverified unless the remote checks explicitly establish them. No real backup or private browsing was used.

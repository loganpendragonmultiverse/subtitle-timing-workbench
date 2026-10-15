"""Command-line interface; output paths must be new."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import MAX_BYTES, apply, exclusive, inspect, plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "plan", "apply"):
        item = sub.add_parser(name)
        item.add_argument("source", type=Path)
        item.add_argument("--output", type=Path, required=True)
        if name == "plan":
            item.add_argument("--offset-ms", type=int, required=True)
        if name == "inspect":
            item.add_argument("--cps", type=float, default=20)
        if name == "apply":
            item.add_argument("--plan", type=Path, required=True)
            item.add_argument("--reviewed", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "apply":
            apply(args.source, args.plan, args.output, args.reviewed)
        else:
            if args.source.stat().st_size > MAX_BYTES:
                raise ValueError("Subtitle exceeds 5 MB limit")
            data = args.source.read_bytes()
            report = (
                inspect(data, args.cps) if args.command == "inspect" else plan(data, args.offset_ms)
            )
            exclusive(
                args.output, (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode()
            )
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"subtitle-timing-workbench: {error}\n")
    return 0

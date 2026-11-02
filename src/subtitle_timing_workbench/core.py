"""Bounded UTF-8 SRT/WebVTT parsing; originals are never edited."""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any

MAX_BYTES = 5_000_000
MAX_PLAN_BYTES = 30_000_000
STAMP = r"(?:\d{2,}:)?\d{2}:\d{2}[.,]\d{3}"
INLINE_TIMESTAMP = re.compile(rf"<({STAMP})>")
TIMING = re.compile(rf"^(?P<a>{STAMP}) --> (?P<b>{STAMP})(?P<settings>[ \t].*)?$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def milliseconds(stamp: str, vtt: bool) -> int:
    if ("," in stamp) == vtt:
        raise ValueError("Wrong timestamp separator for format")
    bits = stamp.replace(",", ".").split(":")
    if len(bits) == 2 and not vtt:
        raise ValueError("SRT requires hours")
    seconds, fraction = bits[-1].split(".")
    minutes = int(bits[-2])
    if minutes > 59 or int(seconds) > 59:
        raise ValueError("Minutes and seconds must be 00..59")
    hours = int(bits[0]) if len(bits) == 3 else 0
    return ((hours * 60 + minutes) * 60 + int(seconds)) * 1000 + int(fraction)


def stamp(value: int, vtt: bool) -> str:
    if value < 0 or value > 359_999_999:
        raise ValueError("Offset would leave supported 00..99 hour range")
    seconds, ms = divmod(value, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}{'.' if vtt else ','}{ms:03}"


def parse(data: bytes) -> dict[str, Any]:
    if len(data) > MAX_BYTES:
        raise ValueError("Subtitle exceeds 5 MB limit")
    text = data.decode("utf-8-sig")
    if "\x00" in text:
        raise ValueError("NUL bytes are unsupported")
    lines = text.splitlines(keepends=True)
    vtt = bool(lines and re.fullmatch(r"WEBVTT(?:[ \t].*)?", lines[0].rstrip("\r\n")))
    blocks: list[list[tuple[int, str]]] = []
    block: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        if not line.strip():
            if block:
                blocks.append(block)
                block = []
        else:
            block.append((index, line.rstrip("\r\n")))
    if block:
        blocks.append(block)
    cues: list[dict[str, Any]] = []
    for block_index, block in enumerate(blocks):
        if vtt:
            first = block[0][1]
            if block_index == 0:
                if any("-->" in line for _, line in block):
                    raise ValueError("WebVTT header needs a blank separator")
                continue
            if first in ("NOTE", "STYLE", "REGION") or first.startswith(("NOTE ", "NOTE\t")):
                continue
        position = 0 if "-->" in block[0][1] else 1
        if position >= len(block):
            raise ValueError(f"Missing timing near line {block[0][0] + 1}")
        line_index, timing = block[position]
        match = TIMING.fullmatch(timing)
        if not match:
            raise ValueError(f"Invalid timing at line {line_index + 1}")
        if not vtt and (position != 1 or not block[0][1].isdigit() or match["settings"]):
            raise ValueError("SRT needs a numeric identifier and no cue settings")
        start = milliseconds(match["a"], vtt)
        end = milliseconds(match["b"], vtt)
        body = "\n".join(line for _, line in block[position + 1 :])
        visible = html.unescape(re.sub(r"<[^>]*>", "", body))
        cues.append(
            dict(
                number=len(cues) + 1,
                line=line_index,
                start=start,
                end=end,
                text=body,
                body_lines=[index for index, _ in block[position + 1 :]],
                characters=len("".join(visible.split())),
                settings=match["settings"] or "",
            )
        )
    if not cues or len(cues) > 20_000:
        raise ValueError("Expected 1..20000 cues")
    return dict(
        format="vtt" if vtt else "srt", cues=cues, lines=lines, bom=data.startswith(b"\xef\xbb\xbf")
    )


def inspect(data: bytes, cps_limit: float = 20) -> dict[str, Any]:
    if not 1 <= cps_limit <= 100:
        raise ValueError("Reading-speed limit must be 1..100 characters/second")
    parsed = parse(data)
    evidence = []
    active: list[dict[str, Any]] = []
    prior = -1
    for cue in parsed["cues"]:
        duration = cue["end"] - cue["start"]
        cps = round(cue["characters"] * 1000 / duration, 2) if duration > 0 else None
        inline_timestamps = (
            [milliseconds(match[1], True) for match in INLINE_TIMESTAMP.finditer(cue["text"])]
            if parsed["format"] == "vtt"
            else []
        )
        findings = []
        if any(value <= cue["start"] or value >= cue["end"] for value in inline_timestamps):
            findings.append("inline-timestamp-outside-cue")
        if any(
            current <= previous
            for previous, current in zip(inline_timestamps, inline_timestamps[1:])
        ):
            findings.append("inline-timestamp-out-of-order")
        if duration <= 0:
            findings.append("non-positive-duration")
        if cue["start"] < prior:
            findings.append("out-of-order")
        if not cue["text"].strip():
            findings.append("empty-text")
        if cps is not None and cps > cps_limit:
            findings.append("reading-speed")
        evidence.append(
            dict(
                cue=cue["number"],
                start_ms=cue["start"],
                end_ms=cue["end"],
                duration_ms=duration,
                characters=cue["characters"],
                cps=cps,
                findings=findings,
                inline_timestamps_ms=inline_timestamps,
            )
        )
        prior = cue["start"]
    # Sort independently from source order to expose nested and non-adjacent overlaps.
    overlaps = []
    for cue in sorted(parsed["cues"], key=lambda item: item["start"]):
        active = [other for other in active if other["end"] > cue["start"]]
        for other in active:
            if cue["end"] > cue["start"]:
                overlaps.append(
                    dict(
                        cues=[other["number"], cue["number"]],
                        overlap_ms=min(other["end"], cue["end"]) - cue["start"],
                    )
                )
                if len(overlaps) > 100_000:
                    raise ValueError("Too many overlaps; split this subtitle")
        if cue["end"] > cue["start"]:
            active.append(cue)
    return dict(
        format=parsed["format"],
        sha256=digest(data),
        cps_limit=cps_limit,
        cues=evidence,
        overlaps=overlaps,
    )


def shifted(data: bytes, offset_ms: int) -> bytes:
    if isinstance(offset_ms, bool) or not isinstance(offset_ms, int):
        raise ValueError("Offset must be integer milliseconds")
    parsed = parse(data)
    vtt = parsed["format"] == "vtt"
    lines = parsed["lines"][:]

    def shift_inline(match: re.Match[str]) -> str:
        return "<" + stamp(milliseconds(match[1], True) + offset_ms, True) + ">"

    for cue in parsed["cues"]:
        old = lines[cue["line"]]
        ending = old[len(old.rstrip("\r\n")) :]
        lines[cue["line"]] = (
            f"{stamp(cue['start'] + offset_ms, vtt)} --> "
            f"{stamp(cue['end'] + offset_ms, vtt)}{cue['settings']}{ending}"
        )
        if vtt:
            for index in cue["body_lines"]:
                lines[index] = INLINE_TIMESTAMP.sub(shift_inline, lines[index])
    return (b"\xef\xbb\xbf" if parsed["bom"] else b"") + "".join(lines).encode("utf-8")


def plan(data: bytes, offset_ms: int) -> dict[str, Any]:
    result = shifted(data, offset_ms)
    return dict(
        schema=1,
        source_sha256=digest(data),
        offset_ms=offset_ms,
        output_sha256=digest(result),
        before=inspect(data),
        after=inspect(result),
    )


def exclusive(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Output already exists: {path}")
    with path.open("xb") as handle:
        handle.write(data)


def read_bounded(path: Path, limit: int) -> bytes:
    with path.open("rb") as handle:
        data = handle.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Input exceeds limit")
    return data


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Plan contains duplicate JSON keys")
        result[key] = value
    return result


def _plan_json(data: bytes) -> Any:
    text = data.decode("utf-8")
    depth = 0
    quoted = False
    escaped = False
    for character in text:
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
        elif character == '"':
            quoted = True
        elif character in "{[":
            depth += 1
            if depth > 100:
                raise ValueError("Plan nesting exceeds 100 levels")
        elif character in "}]":
            depth -= 1
    return json.loads(text, object_pairs_hook=_unique_object)


def _canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def apply(source: Path, plan_path: Path, output: Path, reviewed: bool) -> None:
    if not reviewed:
        raise ValueError("Review the plan before --reviewed export")
    data = read_bounded(source, MAX_BYTES)
    try:
        candidate = _plan_json(read_bounded(plan_path, MAX_PLAN_BYTES))
    except RecursionError as exc:
        raise ValueError("Plan nesting exceeds supported JSON depth") from exc
    if not isinstance(candidate, dict):
        raise ValueError("Plan must be a JSON object")
    offset = candidate.get("offset_ms")
    if isinstance(offset, bool) or not isinstance(offset, int):
        raise ValueError("Plan offset must be integer milliseconds")
    expected = plan(data, offset)
    if _canonical(candidate) != _canonical(expected):
        raise ValueError("Plan changed or source differs; generate and review again")
    exclusive(output, shifted(data, expected["offset_ms"]))

import json
from pathlib import Path

import pytest

from subtitle_timing_workbench.core import apply, inspect, parse, plan, shifted

SRT = b"1\r\n00:00:01,000 --> 00:00:05,000\r\nHello world\r\n\r\n2\r\n00:00:02,000 --> 00:00:03,000\r\nNested cue\r\n\r\n3\r\n00:00:03,000 --> 00:00:04,000\r\nThird cue\r\n"


def test_nested_and_adjacent_overlap_evidence():
    report = inspect(SRT)
    assert report["overlaps"] == [
        {"cues": [1, 2], "overlap_ms": 1000},
        {"cues": [1, 3], "overlap_ms": 1000},
    ]
    assert report["cues"][0]["characters"] == 10


def test_speed_duration_and_order():
    data = b"1\n00:00:02,000 --> 00:00:02,001\nLong text\n\n2\n00:00:01,000 --> 00:00:00,000\nx\n"
    assert inspect(data)["cues"][0]["findings"] == ["reading-speed"]
    assert inspect(data)["cues"][1]["findings"] == ["non-positive-duration", "out-of-order"]


def test_vtt_settings_notes_bom_and_newlines():
    data = b"\xef\xbb\xbfWEBVTT\r\n\r\nNOTE keep me\r\narbitrary\r\n\r\nid\r\n00:01.000 --> 00:02.000 align:start\r\n<b>A &amp; B</b>\r\n"
    output = shifted(data, 500)
    assert b"00:00:01.500 --> 00:00:02.500 align:start\r\n" in output
    assert output.startswith(b"\xef\xbb\xbfWEBVTT\r\n")
    assert inspect(data)["cues"][0]["characters"] == 3
    assert b"NOTE keep me\r\narbitrary" in output


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"bad",
        b"1\n00:61:00,000 --> 00:62:00,000\nx",
        b"1\n00:00:01.000 --> 00:00:02.000\nx",
        b"\x00",
    ],
)
def test_reject_invalid(data):
    with pytest.raises(ValueError):
        parse(data)


def test_negative_offset_refused():
    with pytest.raises(ValueError):
        shifted(SRT, -1001)


def test_review_source_integrity_and_no_overwrite(tmp_path: Path):
    source = tmp_path / "source.srt"
    proposal = tmp_path / "plan.json"
    output = tmp_path / "copy.srt"
    source.write_bytes(SRT)
    proposal.write_text(json.dumps(plan(SRT, 100)))
    with pytest.raises(ValueError):
        apply(source, proposal, output, False)
    apply(source, proposal, output, True)
    assert source.read_bytes() == SRT
    assert inspect(output.read_bytes())["cues"][0]["start_ms"] == 1100
    with pytest.raises(FileExistsError):
        apply(source, proposal, output, True)
    with pytest.raises(FileExistsError):
        apply(source, proposal, source, True)
    source.write_bytes(SRT + b"\n")
    with pytest.raises(ValueError):
        apply(source, proposal, tmp_path / "other.srt", True)


def test_tampered_plan_rejected(tmp_path):
    source = tmp_path / "a.srt"
    source.write_bytes(SRT)
    p = plan(SRT, 100)
    p["after"]["cues"][0]["start_ms"] = 8
    proposal = tmp_path / "plan.json"
    proposal.write_text(json.dumps(p))
    with pytest.raises(ValueError):
        apply(source, proposal, tmp_path / "b.srt", True)

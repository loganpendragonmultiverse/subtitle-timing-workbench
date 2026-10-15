import json
import sys

import pytest

from subtitle_timing_workbench.cli import main

SRT = "1\n00:00:01,000 --> 00:00:03,000\nSynthetic text\n"


def run(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["subtitle-timing-workbench", *map(str, args)])
    return main()


def test_documented_inspect_plan_apply(monkeypatch, tmp_path):
    source = tmp_path / "a.srt"
    source.write_text(SRT)
    audit, proposal, output = [tmp_path / name for name in ("audit.json", "plan.json", "shift.srt")]
    assert run(monkeypatch, "inspect", source, "--output", audit, "--cps", "8") == 0
    assert json.loads(audit.read_text())["cps_limit"] == 8
    assert run(monkeypatch, "plan", source, "--offset-ms", "500", "--output", proposal) == 0
    assert (
        run(monkeypatch, "apply", source, "--plan", proposal, "--output", output, "--reviewed") == 0
    )
    assert "00:00:01,500" in output.read_text()
    assert source.read_text() == SRT
    with pytest.raises(SystemExit) as error:
        run(monkeypatch, "inspect", source, "--output", audit)
    assert error.value.code == 2


@pytest.mark.parametrize(
    "args",
    [
        ["inspect", "missing", "--output", "other"],
        ["inspect", "source", "--output", "other", "--cps", "0"],
        ["plan", "source", "--output", "other", "--offset-ms", "-999999"],
        ["apply", "source", "--output", "other", "--plan", "plan"],
    ],
)
def test_actionable_cli_failures(monkeypatch, tmp_path, args):
    (tmp_path / "source").write_text(SRT)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as error:
        run(monkeypatch, *args)
    assert error.value.code == 2


def test_vtt_identifiers_are_not_comments():
    from subtitle_timing_workbench.core import parse

    data = (
        b"WEBVTT\n\nNOTEworthy\n00:01.000 --> 00:02.000\nx\n\nSTYLEid\n00:03.000 --> 00:04.000\ny\n"
    )
    assert len(parse(data)["cues"]) == 2


def test_header_requires_blank_separator():
    from subtitle_timing_workbench.core import parse

    with pytest.raises(ValueError):
        parse(b"WEBVTT\n00:01.000 --> 00:02.000\nx\n\n00:03.000 --> 00:04.000\ny\n")


def test_bounds_and_empty_evidence(monkeypatch):
    import subtitle_timing_workbench.core as core

    with pytest.raises(ValueError):
        core.shifted(SRT.encode(), True)
    with pytest.raises(ValueError):
        core.parse(b"1\n")
    with pytest.raises(ValueError):
        core.parse(b"1\n00:00:01,000 --> 00:00:02,000 setting\nx")
    assert (
        "empty-text" in core.inspect(b"1\n00:00:01,000 --> 00:00:02,000\n")["cues"][0]["findings"]
    )
    with pytest.raises(ValueError):
        core.parse(b"1\nbad --> timing\nx")
    with pytest.raises(ValueError):
        core.parse(b"1\n00:01,000 --> 00:02,000\nx")
    monkeypatch.setattr(core, "MAX_BYTES", 2)
    with pytest.raises(ValueError):
        core.parse(SRT.encode())

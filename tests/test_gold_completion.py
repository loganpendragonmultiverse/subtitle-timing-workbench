import io
import json
import sys
from pathlib import Path

import pytest

import subtitle_timing_workbench.cli as cli
from subtitle_timing_workbench.core import apply, inspect, plan, read_bounded

SRT = b"1\n00:00:01,000 --> 00:00:03,000\nSynthetic text\n"


@pytest.mark.parametrize("root", [[], None, 1, "plan", True])
def test_nonobject_plans_are_clean_errors(tmp_path, root):
    source, proposal, output = [tmp_path / name for name in ["a.srt", "plan.json", "out.srt"]]
    source.write_bytes(SRT)
    proposal.write_text(json.dumps(root))
    with pytest.raises(ValueError, match="JSON object"):
        apply(source, proposal, output, True)
    assert not output.exists()
    assert source.read_bytes() == SRT


@pytest.mark.parametrize(
    "mutate", [lambda value: value.update(schema=True), lambda value: value.update(schema=1.0)]
)
def test_type_changed_review_evidence_is_rejected(tmp_path, mutate):
    source, proposal, output = [tmp_path / name for name in ["a.srt", "plan.json", "out.srt"]]
    source.write_bytes(SRT)
    candidate = plan(SRT, 500)
    mutate(candidate)
    proposal.write_text(json.dumps(candidate))
    with pytest.raises(ValueError, match="Plan changed"):
        apply(source, proposal, output, True)
    assert not output.exists()


def test_duplicate_keys_and_excessive_nesting_rejected(tmp_path):
    source, proposal, output = [tmp_path / name for name in ["a.srt", "plan.json", "out.srt"]]
    source.write_bytes(SRT)
    proposal.write_text('{"schema":1,"schema":1,"offset_ms":500}')
    with pytest.raises(ValueError, match="duplicate"):
        apply(source, proposal, output, True)
    proposal.write_text("[" * 2000 + "0" + "]" * 2000)
    with pytest.raises(ValueError, match="nesting"):
        apply(source, proposal, output, True)
    assert not output.exists()


def test_bounded_reader_limits_actual_read_without_relying_on_stat(monkeypatch):
    reads = []

    class Tracked(io.BytesIO):
        def read(self, size=-1):
            reads.append(size)
            return super().read(size)

    monkeypatch.setattr(Path, "open", lambda *args, **kwargs: Tracked(b"123456789"))
    with pytest.raises(ValueError, match="limit"):
        read_bounded(Path("synthetic"), 5)
    assert reads == [6]


def test_plan_export_limit_fails_before_creating_output(tmp_path, monkeypatch):
    source, output = tmp_path / "a.srt", tmp_path / "plan.json"
    source.write_bytes(SRT)
    monkeypatch.setattr(cli, "MAX_PLAN_BYTES", 10)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "subtitle-timing-workbench",
            "plan",
            str(source),
            "--offset-ms",
            "500",
            "--output",
            str(output),
        ],
    )
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2
    assert not output.exists()


def test_inline_time_relationship_findings_are_review_evidence():
    value = b"WEBVTT\n\n00:01.000 --> 00:03.000\n<00:01.000>one <00:02.000>two <00:01.500>three <00:03.000>end\n"
    report = inspect(value)
    assert report["cues"][0]["findings"] == [
        "inline-timestamp-outside-cue",
        "inline-timestamp-out-of-order",
    ]
    proposal = plan(value, 500)
    assert proposal["after"]["cues"][0]["findings"] == report["cues"][0]["findings"]
    assert proposal["after"]["cues"][0]["inline_timestamps_ms"] == [1500, 2500, 2000, 3500]


@pytest.mark.parametrize("offset", [None, True, "1", 1.0])
def test_plan_offset_has_strict_integer_type(tmp_path, offset):
    source, proposal, output = [tmp_path / name for name in ["a.srt", "plan.json", "out.srt"]]
    source.write_bytes(SRT)
    proposal.write_text(json.dumps({"offset_ms": offset}))
    with pytest.raises(ValueError, match="integer milliseconds"):
        apply(source, proposal, output, True)
    assert not output.exists()


def test_quoted_json_brackets_do_not_count_as_nesting(tmp_path):
    source, proposal, output = [tmp_path / name for name in ["a.srt", "plan.json", "out.srt"]]
    source.write_bytes(SRT)
    candidate = plan(SRT, 500)
    candidate["note"] = "[" * 200 + '\\"' + "]" * 200
    proposal.write_text(json.dumps(candidate))
    with pytest.raises(ValueError, match="Plan changed"):
        apply(source, proposal, output, True)
    assert not output.exists()


def test_existing_dangling_symlink_cannot_create_target(tmp_path):
    from subtitle_timing_workbench.core import exclusive

    target, link = tmp_path / "absent", tmp_path / "output"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks unavailable")
    with pytest.raises(FileExistsError):
        exclusive(link, b"report")
    assert not target.exists()


def test_exclusive_creation_rejects_raced_regular_file(tmp_path, monkeypatch):
    from subtitle_timing_workbench.core import exclusive

    output = tmp_path / "output"
    original = Path.open

    def raced(path, mode="r", *args, **kwargs):
        if path == output and mode == "xb":
            with original(output, "wb") as writer:
                writer.write(b"preserve")
        return original(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", raced)
    with pytest.raises(FileExistsError):
        exclusive(output, b"report")
    assert output.read_bytes() == b"preserve"

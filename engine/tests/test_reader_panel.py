"""Reader Panel / Adversarial Revision Lab MVP: deterministic branch review."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import get_reader_panel


SLOPPY_CHAPTER = """# 第八章 听雨轩

他解释道，原因是退魂铃的余响仍在墙角盘旋。也就是说，所有人都明白了这件事。这是因为线索已经很清楚了。

首先，墨青烟看见了退魂铃。然后，赵轩记录了退魂铃。最后，众人决定明日继续观察。

“我知道。”赵轩说。
“我知道。”墨青烟说。
“我知道。”林晚舟说。

风平浪静，屋内的灯慢慢暗下去，众人安静地等待。归于沉默。

他们又看了看彼此，没有新的阻碍，也没有新的代价。归于沉默。
"""


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _prepare_branch(
    outputs_dir: Path,
    *,
    run_id: str = "run_reader",
    branch_id: str = "branch_a",
) -> None:
    run_dir = outputs_dir / run_id
    branch = run_dir / branch_id
    branch.mkdir(parents=True, exist_ok=True)
    _write_json(run_dir / "intervention.json", {"story_slug": "reader-story"})
    (branch / "chapter.md").write_text(SLOPPY_CHAPTER, encoding="utf-8")
    _write_json(branch / "events.json", {"accepted_events": []})
    _write_json(
        branch / "narrative_diagnostics.json",
        {
            "warnings": ["张力曲线偏低，冲突或危险信号不足。"],
            "suggestions": ["让角色面对一个必须选择的代价。"],
        },
    )
    _write_json(
        branch / "worldline_judgement.json",
        {
            "scores": {"anti_slop": 0.35, "tension": 0.25},
            "warnings": ["套话、重复和空转风险。"],
        },
    )


@pytest.fixture
def iso_env(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LNE_MOCK", "1")
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    _prepare_branch(outputs)
    return outputs


def test_reader_panel_detects_revision_issues_without_external_calls(iso_env):
    report = get_reader_panel("run_reader", "branch_a")
    issues = {item["id"]: item for item in report["issues"]}
    personas = {item["id"]: item for item in report["personas"]}

    assert report["version"] == "reader-panel-mvp"
    assert report["mode"] == "deterministic_reader_panel"
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["llm_required"] is False
    assert {
        "over_explanation",
        "three_part_stack",
        "repeated_ending",
        "same_voice_dialogue",
        "flat_pacing",
    }.issubset(issues)
    assert issues["over_explanation"]["severity"] in {"medium", "high"}
    assert issues["same_voice_dialogue"]["evidence"]
    assert {"impatient_reader", "line_editor", "continuity_reader", "pacing_reader"}.issubset(
        personas
    )
    assert any("删" in item["revision_brief"] for item in report["revision_briefs"])


def test_reader_panel_damaged_optional_artifacts_degrade_to_warning(iso_env):
    branch = iso_env / "run_reader" / "branch_a"
    (branch / "narrative_diagnostics.json").write_text("{bad-json}", encoding="utf-8")
    (branch / "worldline_judgement.json").write_text("{bad-json}", encoding="utf-8")

    report = get_reader_panel("run_reader", "branch_a")

    assert report["status"] == "attention"
    assert any("narrative_diagnostics.json 损坏" in item for item in report["warnings"])
    assert any("worldline_judgement.json 损坏" in item for item in report["warnings"])
    assert report["issues"]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


@pytest.fixture
def running_server(iso_env):
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_reader_panel_http_statuses(running_server):
    status, body = _get(
        running_server,
        "/api/runs/run_reader/branches/branch_a/reader-panel",
    )
    assert status == 200
    assert body["version"] == "reader-panel-mvp"
    assert body["summary"]["issue_count"] >= 5

    bad_status, bad = _get(
        running_server,
        "/api/runs/..%2Fbad/branches/branch_a/reader-panel",
    )
    assert bad_status == 400
    assert "invalid" in bad["error"]

    missing_status, missing = _get(
        running_server,
        "/api/runs/run_missing/branches/branch_a/reader-panel",
    )
    assert missing_status == 404
    assert "运行不存在" in missing["error"]

"""Chapter Commit / Projection Health MVP: read-only branch projection report."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import get_projection_health


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def _write_project(projects_dir: Path, slug: str) -> None:
    project = projects_dir / slug
    project.mkdir(parents=True, exist_ok=True)
    (project / "world.yaml").write_text("title: 投影健康样例\n", encoding="utf-8")
    (project / "characters.yaml").write_text(
        "- id: mo_qingyan\n  name: 墨青烟\n",
        encoding="utf-8",
    )
    (project / "open_threads.yaml").write_text("threads: []\n", encoding="utf-8")
    (project / "story_contract.yaml").write_text(
        "protagonists: [mo_qingyan]\n",
        encoding="utf-8",
    )
    _write_jsonl(
        project / "memory" / "canon_ledger.jsonl",
        [
            {
                "id": "canon-001",
                "summary": "墨青烟持有退魂铃。",
                "source_ref": "chapter_001.md",
            }
        ],
    )
    _write_jsonl(
        project / "memory" / "project_audit_log.jsonl",
        [
            {
                "id": "audit-001",
                "action": "chapter_projection_review",
                "artifact": "outputs/run_projection/branch_a/chapter.md",
                "created_at": "2026-06-01T00:00:00Z",
            }
        ],
    )


def _write_branch(
    outputs_dir: Path,
    *,
    slug: str,
    run_id: str = "run_projection",
    branch_id: str = "branch_a",
) -> None:
    run_dir = outputs_dir / run_id
    branch = run_dir / branch_id
    branch.mkdir(parents=True, exist_ok=True)
    _write_json(
        run_dir / "intervention.json",
        {"story_slug": slug, "source_kind": "imported", "target": "plot"},
    )
    (branch / "chapter.md").write_text(
        "# 第七章 退魂铃\n\n墨青烟在听雨轩复核退魂铃线索。",
        encoding="utf-8",
    )
    _write_json(
        branch / "events.json",
        {
            "theme": "退魂铃复核",
            "accepted_events": [
                {"id": "evt-001", "summary": "墨青烟复核退魂铃。"}
            ],
        },
    )
    _write_json(
        branch / "state_snapshot.json",
        {
            "characters": {"mo_qingyan": {"location": "听雨轩"}},
            "open_threads": ["退魂铃"],
        },
    )
    _write_json(
        branch / "causal_diff.json",
        {"blocks": [{"id": "cause-001", "summary": "退魂铃余响推进调查。"}]},
    )
    _write_json(
        branch / "multi_agent_trace.json",
        {"turn_plans": [{"agent": "narrator", "intent": "保持节奏"}]},
    )
    _write_json(
        branch / "runtime_memory_context.json",
        {"consumed_layers": [{"layer": "canon", "item_count": 1}]},
    )
    _write_json(
        branch / "narrative_diagnostics.json",
        {"warnings": [], "scores": {"rhythm": 0.8}},
    )
    _write_json(
        branch / "worldline_judgement.json",
        {"status": "pass", "score": 0.9},
    )


@pytest.fixture
def iso_env(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LNE_MOCK", "1")
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    _write_project(projects, "projection-story")
    _write_branch(outputs, slug="projection-story")
    return {"projects": projects, "outputs": outputs}


def test_projection_health_reports_branch_projection_without_writes(iso_env):
    report = get_projection_health("run_projection", "branch_a")
    checks = {item["id"]: item for item in report["checks"]}

    assert report["version"] == "projection-health-mvp"
    assert report["mode"] == "read_only_projection_health"
    assert report["status"] == "ready"
    assert report["story_slug"] == "projection-story"
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["mutates_state_snapshot"] is False
    assert {
        "chapter",
        "events",
        "state_snapshot",
        "causal_diff",
        "multi_agent_trace",
        "runtime_memory",
        "narrative_diagnostics",
        "worldline_judgement",
        "canon_ledger",
        "audit_log",
    }.issubset(checks)
    assert checks["chapter"]["status"] == "ready"
    assert checks["events"]["detail"]["event_count"] == 1
    assert checks["canon_ledger"]["detail"]["entry_count"] == 1
    assert checks["audit_log"]["detail"]["entry_count"] >= 1


def test_projection_health_degrades_damaged_artifacts(iso_env):
    outputs = iso_env["outputs"]
    projects = iso_env["projects"]
    branch = outputs / "run_projection" / "branch_a"
    (branch / "events.json").write_text("{bad-json}", encoding="utf-8")
    (branch / "state_snapshot.json").write_text("{bad-json}", encoding="utf-8")
    (projects / "projection-story" / "memory" / "canon_ledger.jsonl").write_text(
        "{bad-json}\n",
        encoding="utf-8",
    )

    report = get_projection_health("run_projection", "branch_a")
    checks = {item["id"]: item for item in report["checks"]}

    assert report["status"] == "blocked"
    assert report["summary"]["blocked_count"] >= 3
    assert checks["events"]["status"] == "blocked"
    assert checks["state_snapshot"]["status"] == "blocked"
    assert checks["canon_ledger"]["status"] == "blocked"
    assert any("损坏" in warning for warning in report["warnings"])


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


def test_projection_health_http_statuses(running_server):
    port = running_server

    status, body = _get(
        port,
        "/api/runs/run_projection/branches/branch_a/projection-health",
    )
    assert status == 200
    assert body["version"] == "projection-health-mvp"
    assert body["summary"]["check_count"] >= 10

    bad_status, bad = _get(
        port,
        "/api/runs/..%2Fbad/branches/branch_a/projection-health",
    )
    assert bad_status == 400
    assert "invalid" in bad["error"]

    missing_status, missing = _get(
        port,
        "/api/runs/run_missing/branches/branch_a/projection-health",
    )
    assert missing_status == 404
    assert "运行不存在" in missing["error"]

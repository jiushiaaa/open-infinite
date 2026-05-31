"""v1.0-beta Commercial Audit Log Schema-B：本地项目审计日志只读聚合。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest
import yaml

from living_novel_engine.browser import server
from living_novel_engine.service import get_project_audit_log


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _make_project(projects: Path, slug: str = "audit-story") -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": "审计测试世界"})
    _write_yaml(project / "characters.yaml", {"characters": []})
    return project


def _seed_audit_artifacts(project: Path) -> None:
    _write_json(
        project / "import_report.json",
        {
            "version": "v0.8.6",
            "status": "ready",
            "created_at": "2026-06-01T09:00:00",
            "total_chapters": 3,
        },
    )
    _write_json(
        project / "selected_worldline.json",
        {
            "version": "v0.9.0-alpha",
            "status": "ready",
            "run_id": "run_demo",
            "branch_id": "branch_a",
            "selected_at": "2026-06-01T10:00:00",
        },
    )
    _write_json(
        project / "memory" / "master_setting_update_report.json",
        {
            "version": "v0.9.2",
            "status": "saved",
            "changed": ["display_name", "world_rules"],
        },
    )
    _write_json(
        project / "creation_loop_alpha_closeout.json",
        {"version": "v0.9.0-alpha", "status": "ready", "created_at": "2026-06-01T11:00:00"},
    )
    audit_path = project / "memory" / "project_audit_log.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        json.dumps(
            {
                "event_id": "manual-1",
                "action": "manual_note",
                "label": "人工备注",
                "created_at": "2026-06-01T12:00:00",
                "summary": "已人工确认版权来源。",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def test_project_audit_log_schema_aggregates_existing_artifacts(tmp_path):
    projects = tmp_path / "projects"
    project = _make_project(projects)
    _seed_audit_artifacts(project)

    report = get_project_audit_log("audit-story", projects_dir=projects)
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "v1.0-beta-commercial-audit-log-schema-b"
    assert report["status"] == "ready"
    assert report["schema"]["storage"] == "memory/project_audit_log.jsonl"
    assert "event_id" in report["schema"]["required_fields"]
    actions = {event["action"] for event in report["events"]}
    assert {
        "import_review_generated",
        "worldline_selected",
        "master_setting_updated",
        "creation_loop_closed",
        "manual_note",
    }.issubset(actions)
    assert report["summary"]["event_count"] == 5
    assert report["summary"]["source_count"] >= 4
    assert str(tmp_path) not in text


def test_project_audit_log_damaged_jsonl_degrades_to_warning(tmp_path):
    projects = tmp_path / "projects"
    project = _make_project(projects)
    audit_path = project / "memory" / "project_audit_log.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text("{bad json\n", encoding="utf-8")

    report = get_project_audit_log("audit-story", projects_dir=projects)

    assert report["status"] == "empty"
    assert report["events"] == []
    assert any(w["code"] == "damaged_project_audit_log" for w in report["warnings"])


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    project = _make_project(projects)
    _seed_audit_artifacts(project)
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_MOCK", "1")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_project_audit_log_http_ok(running_server):
    status, body = _get(running_server, "/api/stories/audit-story/audit-log")

    assert status == 200
    assert body["version"] == "v1.0-beta-commercial-audit-log-schema-b"
    assert body["summary"]["event_count"] == 5


def test_project_audit_log_http_bad_slug_400(running_server):
    status, body = _get(running_server, "/api/stories/..%2Fbad/audit-log")

    assert status == 400
    assert body["error"] == "invalid slug"


def test_project_audit_log_http_missing_story_404(running_server):
    status, body = _get(running_server, "/api/stories/missing-story/audit-log")

    assert status == 404
    assert "error" in body

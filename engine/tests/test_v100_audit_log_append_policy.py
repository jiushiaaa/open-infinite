"""v1.0-beta Audit Log Append Policy-I：本地审计日志追加策略。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from living_novel_engine.browser import server
from living_novel_engine.service import (
    ProjectAuditLogConflictError,
    ProjectAuditLogRequestError,
    append_project_audit_log_event,
    get_project_audit_log,
)


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _make_project(projects: Path, slug: str = "audit-append-story") -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": "审计追加测试"})
    _write_yaml(project / "characters.yaml", {"characters": []})
    return project


def test_append_project_audit_event_writes_jsonl_without_secret_metadata(
    tmp_path, monkeypatch
):
    projects = tmp_path / "projects"
    _make_project(projects)
    monkeypatch.setenv("LLM_API_KEY", "sk-audit-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-audit-secret-8899")

    report = append_project_audit_log_event(
        "audit-append-story",
        {
            "action": "manual_note",
            "label": "人工复核",
            "summary": "确认项目保留策略。",
            "actor_type": "user",
            "severity": "info",
            "metadata": {
                "screen": "project_workspace",
                "api_key": "sk-audit-secret-7788",
            },
        },
        projects_dir=projects,
        now=datetime(2026, 6, 1, 12, 0, 0),
    )
    log_path = projects / "audit-append-story" / "memory" / "project_audit_log.jsonl"
    raw_line = log_path.read_text(encoding="utf-8").strip()
    event = json.loads(raw_line)
    text = json.dumps(report, ensure_ascii=False) + raw_line

    assert report["version"] == "v1.0-beta-audit-log-append-policy-i"
    assert report["status"] == "appended"
    assert event["action"] == "manual_note"
    assert event["label"] == "人工复核"
    assert event["created_at"] == "2026-06-01T12:00:00"
    assert event["metadata"] == {"screen": "project_workspace"}
    assert any(w["code"] == "metadata_key_dropped" for w in report["warnings"])
    assert "audit-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text

    timeline = get_project_audit_log("audit-append-story", projects_dir=projects)
    assert timeline["summary"]["event_count"] == 1
    assert timeline["events"][0]["summary"] == "确认项目保留策略。"


def test_append_project_audit_event_rejects_unknown_action(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects)

    with pytest.raises(ProjectAuditLogRequestError):
        append_project_audit_log_event(
            "audit-append-story",
            {"action": "delete_everything", "summary": "危险动作"},
            projects_dir=projects,
        )


def test_append_project_audit_event_rejects_builtin_sample(tmp_path):
    with pytest.raises(ProjectAuditLogConflictError):
        append_project_audit_log_event(
            "tianhuang-night",
            {"action": "manual_note", "summary": "内置样例不写日志"},
            projects_dir=tmp_path / "projects",
        )


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    _make_project(projects)
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "outputs"))
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


def _post(port: int, path: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_audit_log_append_http_ok(running_server):
    status, body = _post(
        running_server,
        "/api/stories/audit-append-story/audit-log/events",
        {
            "action": "project_space_reviewed",
            "label": "项目空间复核",
            "summary": "已确认项目空间仍为本地单用户。",
        },
    )

    assert status == 200
    assert body["status"] == "appended"
    assert body["event"]["action"] == "project_space_reviewed"
    assert body["audit_log"]["summary"]["event_count"] == 1


def test_audit_log_append_http_bad_payload_400(running_server):
    status, body = _post(
        running_server,
        "/api/stories/audit-append-story/audit-log/events",
        {"action": "bad_action", "summary": "bad"},
    )

    assert status == 400
    assert "error" in body


def test_audit_log_append_http_missing_story_404(running_server):
    status, body = _post(
        running_server,
        "/api/stories/missing-story/audit-log/events",
        {"action": "manual_note", "summary": "缺项目"},
    )

    assert status == 404
    assert "error" in body

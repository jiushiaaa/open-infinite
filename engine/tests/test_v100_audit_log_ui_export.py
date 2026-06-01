"""v1.0-beta Audit Log UI & Export-P：项目审计时间线导出。"""

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
from living_novel_engine.service import export_project_audit_log


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _make_project(projects: Path, slug: str = "audit-export-story") -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": "审计导出世界"})
    _write_yaml(project / "characters.yaml", {"characters": []})
    return project


def _seed_audit_artifacts(project: Path) -> None:
    _write_json(
        project / "import_report.json",
        {
            "version": "v0.8.6",
            "status": "ready",
            "created_at": "2026-06-01T09:00:00",
            "total_chapters": 5,
        },
    )
    audit_path = project / "memory" / "project_audit_log.jsonl"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        json.dumps(
            {
                "event_id": "manual-1",
                "action": "manual_note",
                "label": "人工备注",
                "created_at": "2026-06-01T10:00:00",
                "summary": "已人工核对审计链路。",
                "metadata": {"api_key": "sk-secret-should-not-export"},
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def test_project_audit_log_export_markdown_omits_paths_and_secret_metadata(tmp_path):
    projects = tmp_path / "projects"
    project = _make_project(projects)
    _seed_audit_artifacts(project)

    report = export_project_audit_log("audit-export-story", projects_dir=projects)
    content = report["content_md"]

    assert report["version"] == "v1.0-beta-audit-log-ui-export-p"
    assert report["kind"] == "project_audit_log_export"
    assert report["filename"] == "audit-export-story-audit-log.md"
    assert report["content_type"] == "text/markdown; charset=utf-8"
    assert report["metadata"]["event_count"] == 2
    assert report["share_guard"]["public_share_allowed"] is False
    assert "# 项目审计日志：审计导出世界" in content
    assert "生成导入检查报告" in content
    assert "人工备注" in content
    assert "sk-secret-should-not-export" not in content
    assert "api_key" not in content
    assert str(tmp_path) not in content


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


def test_project_audit_log_export_http_ok(running_server):
    status, body = _get(
        running_server,
        "/api/stories/audit-export-story/audit-log/export",
    )

    assert status == 200
    assert body["version"] == "v1.0-beta-audit-log-ui-export-p"
    assert body["metadata"]["event_count"] == 2


def test_project_audit_log_export_http_bad_slug_400(running_server):
    status, body = _get(running_server, "/api/stories/..%2Fbad/audit-log/export")

    assert status == 400
    assert body["error"] == "invalid slug"

"""v1.0-beta Rights Approval Checklist-S：项目版权审批只读清单。"""

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
from living_novel_engine.service import (
    get_rights_approval_checklist,
    write_project_copyright_statement,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _make_project(projects: Path, slug: str = "rights-approval-story") -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": "版权审批测试世界"})
    _write_yaml(project / "characters.yaml", {"characters": []})
    _write_json(
        project / "import_report.json",
        {
            "version": "v0.8.6",
            "source": {"type": "txt", "name": "approval-demo.txt", "file_count": 1},
            "total_chapters": 2,
        },
    )
    return project


def test_rights_approval_missing_statement_requires_attention(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    _make_project(projects)
    monkeypatch.setenv("LLM_API_KEY", "sk-rights-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-rights-secret-8899")

    report = get_rights_approval_checklist(
        "rights-approval-story",
        projects_dir=projects,
    )
    checkpoints = {item["id"]: item for item in report["checkpoints"]}
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "v1.0-beta-rights-approval-checklist-s"
    assert report["mode"] == "read_only_rights_approval_checklist"
    assert report["status"] == "attention"
    assert report["summary"]["public_publish_enabled"] is False
    assert checkpoints["project_rights_statement"]["status"] == "attention"
    assert checkpoints["rights_audit_event"]["status"] == "attention"
    assert any("公开分享" in step for step in report["next_steps"])
    assert "rights-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text


def test_rights_approval_declared_statement_is_locally_ready(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects)

    write_project_copyright_statement(
        "rights-approval-story",
        {
            "source_title": "审批测试原作",
            "license_status": "authorized",
            "permitted_uses": ["private_research", "local_export"],
            "attestation": "我确认已获得本地评估与导出授权。",
        },
        projects_dir=projects,
    )

    report = get_rights_approval_checklist(
        "rights-approval-story",
        projects_dir=projects,
    )
    checkpoints = {item["id"]: item for item in report["checkpoints"]}

    assert report["status"] == "ready"
    assert checkpoints["project_rights_statement"]["status"] == "ready"
    assert checkpoints["rights_attestation"]["status"] == "ready"
    assert checkpoints["local_export_scope"]["status"] == "ready"
    assert checkpoints["rights_audit_event"]["status"] == "ready"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    _make_project(projects)
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
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


def test_rights_approval_http_ok(running_server):
    status, body = _get(
        running_server,
        "/api/stories/rights-approval-story/rights-approval-checklist",
    )

    assert status == 200
    assert body["version"] == "v1.0-beta-rights-approval-checklist-s"
    assert body["summary"]["public_publish_enabled"] is False


def test_rights_approval_http_bad_slug_400(running_server):
    status, body = _get(
        running_server,
        "/api/stories/..%2Fbad/rights-approval-checklist",
    )

    assert status == 400
    assert body["error"] == "invalid slug"

"""v1.0-beta Project Copyright Statement-D：项目级版权/来源声明。"""

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
    build_chapter_export,
    get_project_copyright_statement,
    write_project_copyright_statement,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _make_project(projects: Path, slug: str = "rights-story") -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": "版权测试世界"})
    _write_yaml(project / "characters.yaml", {"characters": []})
    _write_json(
        project / "import_report.json",
        {
            "version": "v0.8.6",
            "source": {
                "type": "zip",
                "name": "rights-demo.zip",
                "file_count": 2,
                "filenames": ["chapter_001.md", "chapter_002.md"],
            },
            "total_chapters": 2,
        },
    )
    return project


def _make_run(outputs: Path, story_slug: str = "rights-story") -> tuple[str, str]:
    run_id = "run_rights"
    branch_id = "branch_a"
    run_dir = outputs / run_id
    branch_dir = run_dir / branch_id
    _write_json(
        run_dir / "intervention.json",
        {"story_slug": story_slug, "source_kind": "imported"},
    )
    _write_json(run_dir / "meta.json", {"story_slug": story_slug})
    _write_json(branch_dir / "events.json", {"theme": "顺势续写"})
    _write_json(branch_dir / "worldline_judgement.json", {"recommendation": "可读"})
    branch_dir.mkdir(parents=True, exist_ok=True)
    (branch_dir / "chapter.md").write_text("这一章是测试生成内容。", encoding="utf-8")
    return run_id, branch_id


def test_copyright_statement_missing_infers_import_source(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects)

    report = get_project_copyright_statement("rights-story", projects_dir=projects)
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "v1.0-beta-project-copyright-statement-d"
    assert report["status"] == "missing"
    assert report["artifact_path"] == "memory/project_copyright_statement.json"
    assert report["source"]["source_kind"] == "imported"
    assert report["source"]["import_source"]["name"] == "rights-demo.zip"
    assert report["statement"]["license_status"] == "unknown"
    assert report["share_policy"]["public_publish_enabled"] is False
    assert "补充" in " ".join(report["next_steps"])
    assert str(tmp_path) not in text


def test_write_copyright_statement_persists_sanitized_artifact(tmp_path):
    projects = tmp_path / "projects"
    project = _make_project(projects)

    report = write_project_copyright_statement(
        "rights-story",
        {
            "source_title": "测试原作",
            "source_author": "原作者",
            "rights_holder": "授权方",
            "license_status": "authorized",
            "permitted_uses": ["private_research", "local_export"],
            "attestation": "已确认仅用于本地个人评估。",
            "notes": "公开发布前需另行确认授权。",
        },
        projects_dir=projects,
    )
    reread = get_project_copyright_statement("rights-story", projects_dir=projects)
    text = json.dumps(reread, ensure_ascii=False)

    assert report["status"] == "declared"
    assert reread["status"] == "declared"
    assert reread["statement"]["source_title"] == "测试原作"
    assert reread["statement"]["license_status"] == "authorized"
    assert reread["statement"]["permitted_uses"] == [
        "private_research",
        "local_export",
    ]
    assert (project / "memory" / "project_copyright_statement.json").exists()
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_damaged_copyright_statement_degrades_to_warning(tmp_path):
    projects = tmp_path / "projects"
    project = _make_project(projects)
    damaged = project / "memory" / "project_copyright_statement.json"
    damaged.parent.mkdir(parents=True, exist_ok=True)
    damaged.write_text("{bad json", encoding="utf-8")

    report = get_project_copyright_statement("rights-story", projects_dir=projects)

    assert report["status"] == "damaged"
    assert any(w["code"] == "damaged_copyright_statement" for w in report["warnings"])


def test_chapter_export_share_guard_includes_statement_basis(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    _make_project(projects)
    run_id, branch_id = _make_run(outputs)
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))

    write_project_copyright_statement(
        "rights-story",
        {
            "source_title": "测试原作",
            "license_status": "authorized",
            "permitted_uses": ["private_research", "local_export"],
            "attestation": "已确认授权边界。",
        },
        projects_dir=projects,
    )

    export = build_chapter_export(
        run_id=run_id,
        branch_id=branch_id,
        outputs_dir=outputs,
    )

    assert export["share_guard"]["rights_basis"]["status"] == "declared"
    assert export["share_guard"]["rights_basis"]["license_status"] == "authorized"
    assert export["share_guard"]["public_share_allowed"] is False
    assert "测试原作" in export["content_md"]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    _make_project(projects)
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


def _request(port: int, method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_copyright_statement_http_get_and_write(running_server):
    status, body = _request(
        running_server,
        "GET",
        "/api/stories/rights-story/copyright-statement",
    )
    assert status == 200
    assert body["status"] == "missing"

    status, body = _request(
        running_server,
        "POST",
        "/api/stories/rights-story/copyright-statement",
        {
            "source_title": "HTTP 原作",
            "license_status": "owned_by_user",
            "permitted_uses": ["private_research"],
            "attestation": "我确认仅用于本地评估。",
        },
    )

    assert status == 200
    assert body["status"] == "declared"
    assert body["statement"]["source_title"] == "HTTP 原作"


def test_copyright_statement_http_bad_slug_400(running_server):
    status, body = _request(
        running_server,
        "GET",
        "/api/stories/..%2Fbad/copyright-statement",
    )

    assert status == 400
    assert body["error"] == "invalid slug"


def test_copyright_statement_http_missing_story_404(running_server):
    status, body = _request(
        running_server,
        "GET",
        "/api/stories/missing-story/copyright-statement",
    )

    assert status == 404
    assert "error" in body

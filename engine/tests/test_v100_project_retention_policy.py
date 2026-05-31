"""v1.0-beta Project Retention Policy-J：项目删除/保留策略。"""

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
    ProjectRetentionPolicyConflictError,
    ProjectRetentionPolicyRequestError,
    get_project_audit_log,
    get_project_retention_policy,
    write_project_retention_policy,
)


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _make_project(projects: Path, slug: str = "retention-story") -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": "保留策略测试"})
    _write_yaml(project / "characters.yaml", {"characters": []})
    return project


def test_retention_policy_missing_returns_default_without_paths(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects)

    report = get_project_retention_policy("retention-story", projects_dir=projects)
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "v1.0-beta-project-retention-policy-j"
    assert report["status"] == "missing"
    assert report["artifact_path"] == "memory/project_retention_policy.json"
    assert report["policy"]["project_retention"] == "keep_until_manual_delete"
    assert report["policy"]["deletion_confirmation_required"] is True
    assert "补充" in " ".join(report["next_steps"])
    assert str(tmp_path) not in text


def test_write_retention_policy_persists_policy_and_audit_event(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    project = _make_project(projects)
    monkeypatch.setenv("LLM_API_KEY", "sk-retention-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-retention-secret-8899")

    report = write_project_retention_policy(
        "retention-story",
        {
            "project_retention": "delete_on_request",
            "uploaded_source_retention": "delete_on_project_delete",
            "generated_artifact_retention": "keep_with_project",
            "holdout_retention": "evaluator_private_until_delete",
            "audit_log_retention": "append_only_until_project_delete",
            "ingest_chunk_retention": "expire_after_import",
            "deletion_confirmation_required": True,
            "notes": "删除项目前需二次确认。",
        },
        projects_dir=projects,
        now=datetime(2026, 6, 1, 13, 0, 0),
    )
    reread = get_project_retention_policy("retention-story", projects_dir=projects)
    audit = get_project_audit_log("retention-story", projects_dir=projects)
    text = json.dumps(report, ensure_ascii=False) + json.dumps(audit, ensure_ascii=False)

    assert report["status"] == "declared"
    assert reread["policy"]["project_retention"] == "delete_on_request"
    assert reread["updated_at"] == "2026-06-01T13:00:00"
    assert (project / "memory" / "project_retention_policy.json").exists()
    assert any(event["action"] == "retention_policy_reviewed" for event in audit["events"])
    assert "retention-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_write_retention_policy_rejects_secret_notes(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects)

    with pytest.raises(ProjectRetentionPolicyRequestError):
        write_project_retention_policy(
            "retention-story",
            {"notes": "sk-retention-secret-7788"},
            projects_dir=projects,
        )


def test_write_retention_policy_rejects_builtin_sample(tmp_path):
    with pytest.raises(ProjectRetentionPolicyConflictError):
        write_project_retention_policy(
            "tianhuang-night",
            {"project_retention": "keep_until_manual_delete"},
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


def test_retention_policy_http_get_and_write(running_server):
    status, body = _request(
        running_server,
        "GET",
        "/api/stories/retention-story/retention-policy",
    )
    assert status == 200
    assert body["status"] == "missing"

    status, body = _request(
        running_server,
        "POST",
        "/api/stories/retention-story/retention-policy",
        {
            "project_retention": "archive_only",
            "uploaded_source_retention": "owner_private",
            "notes": "暂不删除，仅归档。",
        },
    )

    assert status == 200
    assert body["status"] == "declared"
    assert body["policy"]["project_retention"] == "archive_only"


def test_retention_policy_http_bad_slug_400(running_server):
    status, body = _request(
        running_server,
        "GET",
        "/api/stories/..%2Fbad/retention-policy",
    )

    assert status == 400
    assert body["error"] == "invalid slug"


def test_retention_policy_http_missing_story_404(running_server):
    status, body = _request(
        running_server,
        "GET",
        "/api/stories/missing-story/retention-policy",
    )

    assert status == 404
    assert "error" in body

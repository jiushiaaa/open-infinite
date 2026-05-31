"""v1.0-beta Cloud Persistence Boundary-G：云端持久化迁移边界。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

from living_novel_engine.browser import server
from living_novel_engine.service import get_cloud_persistence_boundary


def _write(path: Path, payload: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def test_cloud_persistence_boundary_maps_artifacts_without_cloud_side_effects(
    tmp_path, monkeypatch
):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    sessions = tmp_path / "_ingest_sessions"
    _write(projects / "story-a" / "world.yaml", "name: story-a")
    _write(projects / "story-a" / "source_raw" / "chapter_001.txt", "raw")
    _write(projects / "story-a" / "source" / "chapter_001.md", "chapter")
    _write(projects / "story-a" / "memory" / "canon_ledger.jsonl", "{}\n")
    _write(projects / "story-a" / "canon" / "holdout_private" / "chapter_002.md", "h")
    _write(outputs / "run_001" / "branch_a" / "chapter.md", "chapter")
    _write(outputs / "story_selections" / "story-a" / "selected_worldline.json")
    _write(sessions / "abc123" / "manifest.json", "{}")
    monkeypatch.setenv("LLM_API_KEY", "sk-cloud-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-cloud-secret-8899")

    report = get_cloud_persistence_boundary(
        projects_root=projects,
        outputs_root=outputs,
        ingest_sessions_root=sessions,
    )
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "v1.0-beta-cloud-persistence-boundary-g"
    assert report["status"] == "boundary_defined"
    assert report["migration"]["mode"] == "not_started"
    assert report["migration"]["external_services_required"] is False
    assert report["local_inventory"]["project_count"] == 1
    assert report["local_inventory"]["run_count"] == 1
    assert report["local_inventory"]["ingest_session_count"] == 1
    resource_ids = {item["id"] for item in report["resource_map"]}
    assert {
        "uploaded_source_private",
        "runtime_visible_source",
        "project_memory",
        "canon_holdout_private",
        "run_artifacts",
        "ingest_upload_parts",
        "selected_worldlines",
    }.issubset(resource_ids)
    holdout = next(
        item for item in report["resource_map"] if item["id"] == "canon_holdout_private"
    )
    assert holdout["visibility"] == "evaluator_private"
    assert holdout["platform_candidate"] == "private_object_storage"
    retention_ids = {item["id"] for item in report["retention_policy"]}
    assert {"project_delete", "ingest_chunk_expiry", "audit_append_only"}.issubset(
        retention_ids
    )
    assert "cloud-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text


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


def test_cloud_persistence_boundary_http(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_MOCK", "1")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "outputs"))
    monkeypatch.setenv("LNE_INGEST_SESSIONS_DIR", str(tmp_path / "_ingest_sessions"))
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _get(port, "/api/settings/cloud-persistence-boundary")
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "boundary_defined"
    assert body["migration"]["source_of_truth"] == "local_file_artifacts"
    assert body["next_steps"][0].startswith("先把")

"""v0.8.8 Long Project Workspace: project-level review surface."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import indexer, server
from living_novel_engine.service import import_novel_from_payload


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i:03d}.md",
            "content": (
                f"第{i}章 长篇工作台\n"
                f"赵轩在归云斋核对第 {i} 章线索，沈冰月记录风鸣铃的回响。"
            ),
        }
        for i in range(1, n + 1)
    ]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port, tmp_path
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_project_workspace_collects_long_project_assets(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "projects_dir", lambda: tmp_path)
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path / "_outputs")
    import_novel_from_payload(
        name="workspace-story",
        chapters=_chapters(6),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )

    workspace = indexer.get_project_workspace("workspace-story")

    assert workspace["slug"] == "workspace-story"
    assert workspace["source_kind"] == "imported"
    assert workspace["chapter_overview"]["total_chapters"] == 6
    assert workspace["chapter_overview"]["previews"][0]["preview"]
    assert workspace["import_review"]["status"] == "ready"
    assert workspace["memory"]["status"] == "ready"
    assert workspace["memory"]["layer_count"] >= 5
    assert workspace["canon_ledger"]["status"] == "ready"
    assert workspace["canon_ledger"]["entry_count"] >= 6
    assert workspace["entity_aliases"]["status"] == "ready"
    assert workspace["audit"]["status"] == "ready"
    assert "repair_suggestions" in workspace["audit"]
    assert workspace["retrieval"]["status"] == "missing"
    assert workspace["actions"]["anchor_hash"] == "#/anchor/workspace-story"
    assert workspace["actions"]["can_start_baseline"] is True
    assert workspace["actions"]["can_start_intervention"] is True


def test_project_workspace_degrades_damaged_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "projects_dir", lambda: tmp_path)
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path / "_outputs")
    import_novel_from_payload(
        name="workspace-damaged",
        chapters=_chapters(6),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    memory_dir = tmp_path / "workspace-damaged" / "memory"
    (memory_dir / "canon_ledger.jsonl").write_text("{not-json}\n", encoding="utf-8")
    (memory_dir / "consistency_report.json").write_text("{not-json}", encoding="utf-8")

    workspace = indexer.get_project_workspace("workspace-damaged")

    assert workspace["canon_ledger"]["status"] == "damaged"
    assert workspace["canon_ledger"]["entry_count"] == 0
    assert workspace["canon_ledger"]["warnings"]
    assert workspace["audit"]["status"] == "damaged"
    assert workspace["audit"]["summary"]["issue_count"] == 0
    assert workspace["audit"]["warnings"]


def test_project_workspace_http_statuses(running_server):
    port, tmp_path = running_server
    import_novel_from_payload(
        name="workspace-http",
        chapters=_chapters(6),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )

    status, body = _get(port, "/api/stories/workspace-http/project-workspace")
    assert status == 200
    assert body["chapter_overview"]["total_chapters"] == 6
    assert body["memory"]["status"] == "ready"
    assert body["creation_loop"]["version"] == "v0.9.0-alpha"
    assert body["creation_loop"]["status"] == "empty"

    bad_status, bad = _get(port, "/api/stories/..%2Fsecret/project-workspace")
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    missing_status, missing = _get(port, "/api/stories/missing-story/project-workspace")
    assert missing_status == 404
    assert "故事不存在" in missing["error"]

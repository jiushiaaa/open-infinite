"""v0.9.3 Graph Memory Evaluation: trigger conditions only."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import (
    evaluate_graph_memory_trigger,
    import_novel_from_payload,
)


def _chapters(n: int) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i:03d}.md",
            "content": (
                f"第{i}章 图记忆评估\n"
                f"赵轩在归云斋核对第 {i} 章正史账本，沈冰月记录风鸣铃线索。"
            ),
        }
        for i in range(1, n + 1)
    ]


def _make_project(tmp_path, slug: str, chapters: int = 6):
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(chapters),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    return tmp_path / slug


def test_graph_memory_trigger_small_project_not_triggered(tmp_path):
    _make_project(tmp_path, "graph-small", chapters=6)

    report = evaluate_graph_memory_trigger("graph-small", projects_dir=tmp_path)

    assert report["version"] == "v0.9.3"
    assert report["status"] == "not_triggered"
    assert report["trigger"]["should_evaluate"] is False
    assert report["metrics"]["chapter_count"] == 6
    assert report["metrics"]["canon_ledger_count"] > 0
    assert "当前项目规模尚未达到图记忆评估门槛" in report["summary"]


def test_graph_memory_trigger_large_project_with_missing_ledger_triggers(tmp_path):
    project_dir = _make_project(tmp_path, "graph-large", chapters=55)
    (project_dir / "memory" / "canon_ledger.jsonl").write_text("", encoding="utf-8")
    (project_dir / "memory" / "entity_aliases.yaml").unlink()

    report = evaluate_graph_memory_trigger("graph-large", projects_dir=tmp_path)

    assert report["status"] == "triggered"
    assert report["trigger"]["should_evaluate"] is True
    assert "large_project" in report["trigger"]["reasons"]
    assert "empty_canon_ledger" in report["trigger"]["reasons"]
    assert "missing_entity_aliases" in report["trigger"]["reasons"]
    assert report["metrics"]["chapter_count"] == 55
    assert report["metrics"]["canon_ledger_count"] == 0
    assert any("Zep" in step for step in report["next_steps"])


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "graph-http", chapters=6)
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
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def test_graph_memory_trigger_http_statuses(running_server):
    port = running_server

    status, body = _get(port, "/api/stories/graph-http/graph-memory-evaluation")
    assert status == 200
    assert body["status"] == "not_triggered"

    bad_status, bad = _get(port, "/api/stories/..%2Fx/graph-memory-evaluation")
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    missing_status, _missing = _get(port, "/api/stories/ghost/graph-memory-evaluation")
    assert missing_status == 404

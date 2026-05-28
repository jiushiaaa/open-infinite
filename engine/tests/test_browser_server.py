"""Server-level tests for v0.4 worldline browser: routing, validation, port-handling."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from living_novel_engine.browser import indexer, server


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)

    run_dir = tmp_path / "run_demo_001"
    run_dir.mkdir()
    (run_dir / "intervention.json").write_text(
        json.dumps(
            {"target": "hero", "content": "干预", "story_slug": "demo", "source_kind": "imported"},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    bdir = run_dir / "branch_a"
    bdir.mkdir()
    (bdir / "chapter.md").write_text("# 章节", encoding="utf-8")
    (bdir / "events.json").write_text(json.dumps({"theme": "相信"}), encoding="utf-8")

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
    url = f"http://127.0.0.1:{port}{path}"
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def test_runs_endpoint_returns_demo_run(running_server):
    status, body = _get(running_server, "/api/runs")
    assert status == 200
    ids = [r["run_id"] for r in body["runs"]]
    assert "run_demo_001" in ids


def test_branch_endpoint_returns_chapter(running_server):
    status, body = _get(running_server, "/api/runs/run_demo_001/branches/branch_a")
    assert status == 200
    assert "章节" in body["chapter_md"]


def test_run_id_path_traversal_rejected(running_server):
    status, body = _get(running_server, "/api/runs/..%2F..%2Fetc")
    assert status == 400
    assert "invalid" in body["error"].lower()


def test_branch_id_path_traversal_rejected(running_server):
    status, body = _get(running_server, "/api/runs/run_demo_001/branches/..")
    assert status == 400
    assert "invalid" in body["error"].lower()


def test_story_slug_path_traversal_rejected(running_server):
    status, body = _get(running_server, "/api/stories/..%2Fsamples")
    assert status == 400
    assert "invalid" in body["error"].lower()


def test_unknown_run_returns_404(running_server):
    status, body = _get(running_server, "/api/runs/run_nope")
    assert status == 404
    assert "error" in body


def test_port_in_use_raises_clean_error():
    """端口被外部 socket 占用时应抛 BrowserServerStartError 而非裸 OSError。"""
    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE if hasattr(socket, "SO_EXCLUSIVEADDRUSE") else socket.SO_REUSEADDR, 1)
    blocker.bind(("127.0.0.1", 0))
    blocker.listen(1)
    port = blocker.getsockname()[1]
    try:
        with pytest.raises(server.BrowserServerStartError):
            server.start_browser_server("127.0.0.1", port, open_browser=False)
    finally:
        blocker.close()

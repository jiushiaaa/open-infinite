"""v0.8+ Emergence Mining-A：从 run artifact 沉淀涌现节点。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.emergence_mining import mine_emergence_nodes
from living_novel_engine.service import get_emergence_nodes, mine_run_emergence, run_intervention


def test_run_intervention_writes_emergence_nodes(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")

    result = run_intervention(
        story_slug="tianhuang-night",
        target="lin_wan_zhou",
        content="告诉林晚舟竹林里有埋伏，让她改走城内密道",
        mock=True,
        rounds=1,
    )

    path = outputs / result.run_id / "emergence_nodes.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["kind"] == "emergence_nodes"
    assert data["story_slug"] == "tianhuang-night"
    assert data["nodes"]
    assert data["summary"]["node_count"] == len(data["nodes"])
    assert result.extra["emergence_nodes"]["nodes"]


def test_mine_emergence_nodes_uses_diff_registry_and_diagnostics(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
    result = run_intervention(
        story_slug="tianhuang-night",
        target="lin_wan_zhou",
        content="把退魂铃的代价提前告诉林晚舟",
        mock=True,
        rounds=1,
    )

    report = mine_emergence_nodes(outputs / result.run_id)

    assert report.version == "v0.8-emergence-mining-a"
    assert any(node.source_artifacts for node in report.nodes)
    assert any("dynamic_action_registry.yaml" in node.source_artifacts for node in report.nodes)
    assert report.summary["high_value_count"] >= 0


def test_emergence_service_rebuilds_and_reads_report(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
    result = run_intervention(
        story_slug="tianhuang-night",
        target="lin_wan_zhou",
        content="告诉林晚舟竹林里有埋伏",
        mock=True,
        rounds=1,
    )
    (outputs / result.run_id / "emergence_nodes.json").unlink()

    rebuilt = mine_run_emergence(result.run_id, outputs_dir=outputs)
    loaded = get_emergence_nodes(result.run_id, outputs_dir=outputs)

    assert rebuilt["kind"] == "emergence_nodes"
    assert loaded["summary"]["node_count"] == rebuilt["summary"]["node_count"]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    projects.mkdir()
    outputs.mkdir()
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
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
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_emergence_nodes_http_get_and_rebuild(running_server):
    port = running_server
    status, body = _post(
        port,
        "/api/interventions",
        {
            "story_slug": "tianhuang-night",
            "target": "lin_wan_zhou",
            "content": "告诉林晚舟竹林里有埋伏",
            "mock": True,
            "rounds": 1,
        },
    )
    assert status == 200
    assert body["emergence_nodes"]["kind"] == "emergence_nodes"

    run_id = body["run_id"]
    status, fetched = _get(port, f"/api/runs/{run_id}/emergence-nodes")
    assert status == 200
    assert fetched["run_id"] == run_id

    status, rebuilt = _post(port, f"/api/runs/{run_id}/emergence-nodes", {})
    assert status == 200
    assert rebuilt["summary"]["node_count"] == fetched["summary"]["node_count"]

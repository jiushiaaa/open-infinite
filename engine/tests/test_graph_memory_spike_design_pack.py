"""Graph Memory Spike Design Pack MVP：只读 spike 设计包。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from datetime import datetime

from click.testing import CliRunner

from living_novel_engine.browser import server
from living_novel_engine.cli import main
from living_novel_engine.service import get_graph_memory_spike_design_pack

from test_cross_project_retrieval_samples_index import _make_project as _make_sample_project
from test_v093_graph_memory_trigger import _make_project as _make_graph_project


def _make_trigger_project(tmp_path):
    project_dir = _make_graph_project(tmp_path, "graph-design-large", chapters=55)
    (project_dir / "memory" / "canon_ledger.jsonl").write_text("", encoding="utf-8")
    (project_dir / "memory" / "entity_aliases.yaml").unlink()
    _make_sample_project(tmp_path, "graph-design-samples", with_sample=True)
    return project_dir


def test_graph_memory_spike_design_pack_turns_trigger_evidence_into_design(tmp_path, monkeypatch):
    _make_trigger_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = get_graph_memory_spike_design_pack(
        "graph-design-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 3, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    layers = {layer["id"]: layer for layer in report["layer_plans"]}
    gates = {gate["id"]: gate for gate in report["acceptance_gates"]}

    assert report["version"] == "graph-memory-spike-design-pack-mvp"
    assert report["mode"] == "read_only_graph_memory_spike_design_pack"
    assert report["status"] == "ready_for_spike"
    assert report["design_gate"]["passed"] is True
    assert report["design_gate"]["status"] == "design_pack_ready"
    assert report["summary"]["evidence_status"] == "triggered"
    assert report["summary"]["candidate_layer_count"] >= 2
    assert report["summary"]["experiment_input_count"] >= 4
    assert report["summary"]["acceptance_gate_count"] >= 4
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert layers["graphrag"]["status"] == "candidate"
    assert layers["zep"]["status"] == "candidate"
    assert gates["contract_safety"]["status"] == "required"
    assert any(item["id"] == "retrieval_eval_records" for item in report["experiment_inputs"])
    assert any("run_scene" in item for item in report["no_go_conditions"])
    assert "graph-design-samples-retrieval-eval-001" in report["content_json"]
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_spike_design_pack_small_project_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-design-small", chapters=3)

    report = get_graph_memory_spike_design_pack("graph-design-small", projects_dir=tmp_path)

    assert report["status"] == "deferred"
    assert report["design_gate"]["passed"] is False
    assert report["design_gate"]["status"] == "deferred"
    assert report["summary"]["candidate_layer_count"] == 0
    assert all(layer["status"] == "deferred" for layer in report["layer_plans"])


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


def test_graph_memory_spike_design_pack_http_statuses(tmp_path, monkeypatch):
    _make_graph_project(tmp_path, "graph-design-http", chapters=3)
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_MOCK", "1")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _get(port, "/api/stories/graph-design-http/graph-memory-spike-design-pack")
        bad_status, bad = _get(port, "/api/stories/..%2Fx/graph-memory-spike-design-pack")
        missing_status, _missing = _get(port, "/api/stories/ghost/graph-memory-spike-design-pack")
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_design_pack_json(tmp_path):
    _make_graph_project(tmp_path, "graph-design-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-design", "graph-design-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["design_gate"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-design-cli"

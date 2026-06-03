"""GraphRAG / Zep Trigger Evidence MVP：只读触发证据。"""

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
from living_novel_engine.service import get_graph_memory_trigger_evidence

from test_cross_project_retrieval_samples_index import _make_project as _make_sample_project
from test_v093_graph_memory_trigger import _make_project as _make_graph_project


def test_graph_memory_trigger_evidence_combines_graph_trigger_and_sample_trend(
    tmp_path, monkeypatch
):
    project_dir = _make_graph_project(tmp_path, "graph-evidence-large", chapters=55)
    (project_dir / "memory" / "canon_ledger.jsonl").write_text("", encoding="utf-8")
    (project_dir / "memory" / "entity_aliases.yaml").unlink()
    _make_sample_project(tmp_path, "graph-evidence-samples", with_sample=True)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = get_graph_memory_trigger_evidence(
        "graph-evidence-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 2, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    signals = {signal["id"]: signal for signal in report["signals"]}
    candidates = {item["id"]: item for item in report["candidate_layers"]}

    assert report["version"] == "graph-memory-trigger-evidence-mvp"
    assert report["mode"] == "read_only_graph_memory_trigger_evidence"
    assert report["status"] == "triggered"
    assert report["trigger_gate"]["passed"] is True
    assert report["trigger_gate"]["status"] == "ready_for_spike_design"
    assert report["summary"]["graph_memory_status"] == "triggered"
    assert report["summary"]["trend_record_count"] == 1
    assert report["summary"]["trend_lexical_gap_count"] == 1
    assert signals["graph_memory_trigger"]["status"] == "triggered"
    assert signals["retrieval_trend_pressure"]["status"] == "attention"
    assert signals["external_service_boundary"]["status"] == "deferred"
    assert candidates["graphrag"]["status"] == "candidate"
    assert candidates["zep"]["status"] == "candidate"
    assert "graph-evidence-samples-retrieval-eval-001" in report["content_json"]
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_trigger_evidence_small_project_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-evidence-small", chapters=3)

    report = get_graph_memory_trigger_evidence("graph-evidence-small", projects_dir=tmp_path)

    assert report["status"] == "not_triggered"
    assert report["trigger_gate"]["passed"] is False
    assert report["trigger_gate"]["status"] == "deferred"
    assert report["summary"]["external_services_required"] is False
    assert report["candidate_layers"][0]["status"] == "deferred"


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


def test_graph_memory_trigger_evidence_http_statuses(tmp_path, monkeypatch):
    _make_graph_project(tmp_path, "graph-evidence-http", chapters=3)
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
        status, body = _get(
            port,
            "/api/stories/graph-evidence-http/graph-memory-trigger-evidence",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/graph-memory-trigger-evidence",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/graph-memory-trigger-evidence",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "not_triggered"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_trigger_json(tmp_path):
    _make_graph_project(tmp_path, "graph-evidence-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-trigger", "graph-evidence-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["trigger_gate"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-evidence-cli"

"""Graph Memory Provider Spike Review Gate MVP tests."""

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
import living_novel_engine.service as service

from test_graph_memory_provider_spike_fixture_pack import _make_fixture_project
from test_v093_graph_memory_trigger import _make_project as _make_graph_project


def test_graph_memory_provider_spike_review_gate_from_mock_result(tmp_path, monkeypatch):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-review-gate-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-review-gate-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_review_gate",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 15, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    review = report["provider_reviews"][0]

    assert report["version"] == "graph-memory-provider-spike-review-gate-mvp"
    assert report["mode"] == "read_only_graph_memory_provider_spike_review_gate"
    assert report["status"] == "ready_for_manual_review_gate"
    assert report["summary"]["source_mock_result_status"] == "ready_for_manual_review"
    assert report["summary"]["mock_record_count"] >= 2
    assert report["summary"]["candidate_gain_count"] >= 2
    assert report["summary"]["manual_review_required_count"] >= 2
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["result_write_allowed"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["real_provider_config_allowed"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["review_gate"]["passed"] is True
    assert report["review_gate"]["status"] == "manual_review_gate_ready"
    assert report["review_gate"]["approval_required"] is True
    assert report["review_gate"]["real_provider_config_allowed"] is False
    assert review["status"] == "manual_review_required"
    assert review["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert review["source_record_id"].startswith("mock-result-")
    assert review["manual_decision"] in {
        "collect_more_evidence",
        "upgrade_manual_opt_in_spike",
    }
    assert review["gate_decision"] == "collect_more_evidence"
    assert review["review_item_count"] >= 4
    assert review["candidate_gain"] is True
    assert review["risk_summary"]
    assert review["gain_summary"]
    assert review["evidence_refs"]
    assert report["decision"]["status"] == "review_required_no_real_provider_config"
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert any("真实付费 Key" in item for item in report["no_go_conditions"])
    assert "review-gate-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_review_gate_small_project_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-review-gate-small", chapters=3)

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_review_gate",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-review-gate-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["review_gate"]["passed"] is False
    assert report["summary"]["mock_record_count"] == 0
    assert report["provider_reviews"] == []


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


def test_graph_memory_provider_spike_review_gate_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-review-gate-http", chapters=3)
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
            "/api/stories/graph-review-gate-http/"
            "graph-memory-provider-spike-review-gate",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/graph-memory-provider-spike-review-gate",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/graph-memory-provider-spike-review-gate",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_review_gate_json(tmp_path):
    _make_graph_project(tmp_path, "graph-review-gate-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-review-gate", "graph-review-gate-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["review_gate"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-review-gate-cli"

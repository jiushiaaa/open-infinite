"""Graph Memory Provider Spike Mock Result Report MVP tests."""

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


def test_graph_memory_provider_spike_mock_result_report_from_template(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-mock-result-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-mock-result-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_mock_result_report",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 13, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    record = report["mock_result_records"][0]
    value_ids = {item["field_id"] for item in record["field_values"]}

    assert report["version"] == "graph-memory-provider-spike-mock-result-report-mvp"
    assert report["mode"] == "read_only_graph_memory_provider_spike_mock_result_report"
    assert report["status"] == "ready_for_manual_review"
    assert report["summary"]["source_result_template_status"] == (
        "ready_for_manual_result_recording"
    )
    assert report["summary"]["provider_result_count"] >= 2
    assert report["summary"]["filled_record_count"] >= 2
    assert report["summary"]["candidate_gain_count"] >= 2
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["result_write_allowed"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["report_gate"]["passed"] is True
    assert report["report_gate"]["status"] == "mock_result_report_ready"
    assert record["status"] == "mock_filled_result_ready"
    assert record["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert record["fixture_id"].startswith("single-project-fixture-")
    assert record["template_field_count"] >= 11
    assert {
        "baseline_retrieval_summary",
        "provider_candidate_summary",
        "manual_decision",
        "evidence_refs",
    }.issubset(value_ids)
    assert record["manual_decision"] in {
        "collect_more_evidence",
        "upgrade_manual_opt_in_spike",
    }
    assert record["review_summary"]
    assert record["gain_summary"]
    assert record["risk_summary"]
    assert report["decision"]["status"] == "mock_result_review_required_no_real_config"
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert any("真实付费 Key" in item for item in report["no_go_conditions"])
    assert "mock-result-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_mock_result_report_small_project_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-mock-result-small", chapters=3)

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_mock_result_report",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-mock-result-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["report_gate"]["passed"] is False
    assert report["summary"]["filled_record_count"] == 0
    assert report["mock_result_records"] == []


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


def test_graph_memory_provider_spike_mock_result_report_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-mock-result-http", chapters=3)
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
            "/api/stories/graph-mock-result-http/"
            "graph-memory-provider-spike-mock-result-report",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/graph-memory-provider-spike-mock-result-report",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/graph-memory-provider-spike-mock-result-report",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_mock_result_json(tmp_path):
    _make_graph_project(tmp_path, "graph-mock-result-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-mock-result", "graph-mock-result-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["report_gate"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-mock-result-cli"

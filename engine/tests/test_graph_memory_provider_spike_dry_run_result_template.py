"""Graph Memory Provider Spike Dry-run Result Template MVP tests."""

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


def test_graph_memory_provider_spike_dry_run_result_template_from_runbook(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-result-template-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-result-template-secret-8899")

    get_template = getattr(
        service,
        "get_graph_memory_provider_spike_dry_run_result_template",
        None,
    )
    assert callable(get_template)
    report = get_template(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 12, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    provider = report["provider_result_templates"][0]
    field_ids = {field["id"] for field in provider["result_fields"]}
    decision_ids = {item["id"] for item in provider["pause_or_upgrade_decisions"]}

    assert report["version"] == (
        "graph-memory-provider-spike-dry-run-result-template-mvp"
    )
    assert report["mode"] == (
        "read_only_graph_memory_provider_spike_dry_run_result_template"
    )
    assert report["status"] == "ready_for_manual_result_recording"
    assert report["summary"]["source_runbook_status"] == "ready_for_manual_dry_run"
    assert report["summary"]["provider_template_count"] >= 2
    assert report["summary"]["ready_provider_count"] >= 2
    assert report["summary"]["blocked_provider_count"] == 0
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["template"]["manual_only"] is True
    assert report["template"]["result_write_allowed"] is False
    assert report["template"]["real_provider_config_allowed"] is False
    assert provider["status"] == "manual_result_template_ready"
    assert provider["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert provider["fixture_id"].startswith("single-project-fixture-")
    assert provider["source_step_count"] >= 6
    assert {
        "baseline_retrieval_summary",
        "provider_candidate_summary",
        "relationship_gain",
        "causal_chain_gain",
        "state_tracking_gain",
        "false_positive_risk",
        "privacy_scope_confirmed",
        "cost_guardrail_confirmed",
        "rollback_verified",
        "manual_decision",
        "evidence_refs",
    }.issubset(field_ids)
    assert {"pause_no_go_hit", "pause_no_stable_gain", "upgrade_manual_opt_in_spike"}.issubset(
        decision_ids
    )
    assert provider["comparison_axes"]
    assert provider["acceptance_record"]
    assert provider["evidence_refs"]
    assert any("真实付费 Key" in item for item in report["no_go_conditions"])
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert report["decision"]["status"] == "result_template_ready_no_real_config"
    assert "result-template-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_dry_run_result_template_small_project_deferred(
    tmp_path,
):
    _make_graph_project(tmp_path, "graph-result-template-small", chapters=3)

    get_template = getattr(
        service,
        "get_graph_memory_provider_spike_dry_run_result_template",
        None,
    )
    assert callable(get_template)
    report = get_template(
        "graph-result-template-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["template"]["status"] == "deferred"
    assert report["template"]["manual_only"] is True
    assert report["template"]["result_write_allowed"] is False
    assert report["summary"]["provider_template_count"] == 0
    assert report["provider_result_templates"] == []


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


def test_graph_memory_provider_spike_dry_run_result_template_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-result-template-http", chapters=3)
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
            "/api/stories/graph-result-template-http/"
            "graph-memory-provider-spike-dry-run-result-template",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/graph-memory-provider-spike-dry-run-result-template",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/graph-memory-provider-spike-dry-run-result-template",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_result_template_json(tmp_path):
    _make_graph_project(tmp_path, "graph-result-template-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-result-template", "graph-result-template-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["template"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-result-template-cli"

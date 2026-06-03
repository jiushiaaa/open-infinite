"""Graph Memory Provider Spike Runbook MVP：只读人工 opt-in SOP。"""

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


def test_graph_memory_provider_spike_runbook_from_readiness_gate(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-runbook-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-runbook-secret-8899")

    get_runbook = getattr(service, "get_graph_memory_provider_spike_runbook", None)
    assert callable(get_runbook)
    report = get_runbook(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 11, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    provider = report["provider_runbooks"][0]
    step_phases = {step["phase"] for step in provider["steps"]}

    assert report["version"] == "graph-memory-provider-spike-runbook-mvp"
    assert report["mode"] == "read_only_graph_memory_provider_spike_runbook"
    assert report["status"] == "ready_for_manual_dry_run"
    assert report["summary"]["source_readiness_gate_status"] == (
        "ready_for_manual_opt_in_review"
    )
    assert report["summary"]["provider_runbook_count"] >= 2
    assert report["summary"]["ready_provider_count"] >= 2
    assert report["summary"]["blocked_provider_count"] == 0
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["runbook"]["status"] == "ready_for_manual_dry_run"
    assert report["runbook"]["manual_only"] is True
    assert report["runbook"]["real_provider_config_allowed"] is False
    assert provider["status"] == "manual_dry_run_ready"
    assert provider["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert provider["fixture_id"].startswith("single-project-fixture-")
    assert {"prepare", "dry_run", "compare", "review", "rollback", "stop"}.issubset(
        step_phases
    )
    assert provider["acceptance_checks"]
    assert provider["rollback_steps"]
    assert provider["pause_conditions"]
    assert provider["evidence_refs"]
    assert any("真实付费 Key" in item for item in report["no_go_conditions"])
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert report["decision"]["status"] == "manual_runbook_ready_no_real_config"
    assert "runbook-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_runbook_small_project_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-runbook-small", chapters=3)

    get_runbook = getattr(service, "get_graph_memory_provider_spike_runbook", None)
    assert callable(get_runbook)
    report = get_runbook(
        "graph-runbook-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["runbook"]["status"] == "deferred"
    assert report["runbook"]["manual_only"] is True
    assert report["runbook"]["real_provider_config_allowed"] is False
    assert report["summary"]["provider_runbook_count"] == 0
    assert report["provider_runbooks"] == []


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


def test_graph_memory_provider_spike_runbook_http_statuses(tmp_path, monkeypatch):
    _make_graph_project(tmp_path, "graph-runbook-http", chapters=3)
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
            "/api/stories/graph-runbook-http/graph-memory-provider-spike-runbook",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/graph-memory-provider-spike-runbook",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/graph-memory-provider-spike-runbook",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_runbook_json(tmp_path):
    _make_graph_project(tmp_path, "graph-runbook-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-runbook", "graph-runbook-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["runbook"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-runbook-cli"

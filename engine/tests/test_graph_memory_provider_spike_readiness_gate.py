"""Graph Memory Provider Spike Readiness Gate MVP：只读 provider spike 门禁。"""

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


def test_graph_memory_provider_spike_readiness_gate_from_fixture_pack(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    get_readiness_gate = getattr(
        service, "get_graph_memory_provider_spike_readiness_gate", None
    )
    assert callable(get_readiness_gate)
    report = get_readiness_gate(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 10, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    provider = report["provider_readiness"][0]
    check_ids = {item["id"] for item in provider["readiness_checks"]}

    assert report["version"] == "graph-memory-provider-spike-readiness-gate-mvp"
    assert report["mode"] == "read_only_graph_memory_provider_spike_readiness_gate"
    assert report["status"] == "ready_for_manual_opt_in_review"
    assert report["readiness_gate"]["passed"] is True
    assert report["readiness_gate"]["status"] == "ready_for_manual_opt_in_review"
    assert report["readiness_gate"]["real_provider_config_allowed"] is False
    assert report["summary"]["source_fixture_pack_status"] == "ready_for_fixture_pack"
    assert report["summary"]["provider_fixture_count"] >= 2
    assert report["summary"]["ready_for_manual_review_count"] >= 2
    assert report["summary"]["blocked_provider_count"] == 0
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert provider["status"] == "manual_review_ready"
    assert provider["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert provider["fixture_id"].startswith("single-project-fixture-")
    assert provider["blockers"] == []
    assert provider["manual_review_items"]
    assert {"fixture_scope", "cost_guardrails", "privacy_guardrails"}.issubset(check_ids)
    assert {"rollback_plan", "manual_acceptance", "no_go_review"}.issubset(check_ids)
    assert any("真实付费 Key" in item for item in report["no_go_conditions"])
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert report["decision"]["status"] == "manual_review_ready_no_real_config"
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_readiness_gate_small_project_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-readiness-gate-small", chapters=3)

    get_readiness_gate = getattr(
        service, "get_graph_memory_provider_spike_readiness_gate", None
    )
    assert callable(get_readiness_gate)
    report = get_readiness_gate(
        "graph-readiness-gate-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["readiness_gate"]["passed"] is False
    assert report["readiness_gate"]["status"] == "deferred"
    assert report["readiness_gate"]["real_provider_config_allowed"] is False
    assert report["summary"]["provider_fixture_count"] == 0
    assert report["provider_readiness"] == []


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


def test_graph_memory_provider_spike_readiness_gate_http_statuses(tmp_path, monkeypatch):
    _make_graph_project(tmp_path, "graph-readiness-gate-http", chapters=3)
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
            "/api/stories/graph-readiness-gate-http/graph-memory-provider-spike-readiness-gate",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/graph-memory-provider-spike-readiness-gate",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/graph-memory-provider-spike-readiness-gate",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_readiness_gate_json(tmp_path):
    _make_graph_project(tmp_path, "graph-readiness-gate-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-readiness-gate", "graph-readiness-gate-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["readiness_gate"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-readiness-gate-cli"

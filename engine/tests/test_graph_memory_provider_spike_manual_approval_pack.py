"""Graph Memory Provider Spike Manual Approval Pack MVP tests."""

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


def test_graph_memory_provider_spike_manual_approval_pack_from_review_gate(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-manual-approval-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-manual-approval-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_manual_approval_pack",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 16, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    approval = report["approval_items"][0]

    assert report["version"] == "graph-memory-provider-spike-manual-approval-pack-mvp"
    assert report["mode"] == "read_only_graph_memory_provider_spike_manual_approval_pack"
    assert report["status"] == "ready_for_manual_approval_pack"
    assert report["summary"]["source_review_gate_status"] == "ready_for_manual_review_gate"
    assert report["summary"]["provider_review_count"] >= 2
    assert report["summary"]["approval_item_count"] >= 2
    assert report["summary"]["risk_signoff_count"] >= 2
    assert report["summary"]["rollback_confirmation_count"] >= 2
    assert report["summary"]["opt_in_material_count"] >= 2
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["approval_write_allowed"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["real_provider_config_allowed"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["approval_pack"]["status"] == "manual_approval_pack_ready"
    assert report["approval_pack"]["approval_required"] is True
    assert report["approval_pack"]["manual_signature_required"] is True
    assert report["approval_pack"]["automatic_upgrade_allowed"] is False
    assert report["approval_pack"]["real_provider_config_allowed"] is False
    assert approval["status"] == "manual_approval_required"
    assert approval["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert approval["source_review_id"].startswith("review-gate-")
    assert approval["gate_decision"] in {
        "collect_more_evidence",
        "manual_approval_required",
    }
    assert approval["risk_signoff_count"] >= 4
    assert approval["rollback_confirmation_count"] >= 3
    assert approval["opt_in_material_count"] >= 4
    assert approval["risk_signoffs"]
    assert approval["rollback_confirmations"]
    assert approval["opt_in_materials"]
    assert report["decision"]["status"] == "approval_pack_ready_no_real_provider_config"
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert any("真实 provider 配置" in item for item in report["no_go_conditions"])
    assert "manual-approval-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_manual_approval_pack_small_project_deferred(
    tmp_path,
):
    _make_graph_project(tmp_path, "graph-manual-approval-small", chapters=3)

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_manual_approval_pack",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-manual-approval-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["approval_pack"]["status"] == "deferred"
    assert report["summary"]["provider_review_count"] == 0
    assert report["approval_items"] == []


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


def test_graph_memory_provider_spike_manual_approval_pack_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-manual-approval-http", chapters=3)
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
            "/api/stories/graph-manual-approval-http/"
            "graph-memory-provider-spike-manual-approval-pack",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/graph-memory-provider-spike-manual-approval-pack",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/graph-memory-provider-spike-manual-approval-pack",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_manual_approval_pack_json(tmp_path):
    _make_graph_project(tmp_path, "graph-manual-approval-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-manual-approval-pack", "graph-manual-approval-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["approval_pack"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-manual-approval-cli"

"""Graph Memory Provider Spike Manual Approval Evidence Checklist MVP tests."""

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


def test_graph_memory_provider_spike_manual_approval_evidence_checklist_ready(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-approval-evidence-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-approval-evidence-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_manual_approval_evidence_checklist",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 17, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    item = report["checklist_items"][0]

    assert (
        report["version"]
        == "graph-memory-provider-spike-manual-approval-evidence-checklist-mvp"
    )
    assert (
        report["mode"]
        == "read_only_graph_memory_provider_spike_manual_approval_evidence_checklist"
    )
    assert report["status"] == "ready_for_manual_approval_evidence_checklist"
    assert report["summary"]["source_approval_pack_status"] == (
        "ready_for_manual_approval_pack"
    )
    assert report["summary"]["approval_item_count"] >= 2
    assert report["summary"]["checklist_item_count"] >= 2
    assert report["summary"]["pending_signoff_count"] >= 2
    assert report["summary"]["material_gap_count"] == 0
    assert report["summary"]["rollback_material_gap_count"] == 0
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["approval_write_allowed"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["real_provider_config_allowed"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["evidence_checklist"]["status"] == "evidence_checklist_ready"
    assert report["evidence_checklist"]["manual_signoff_required"] is True
    assert report["evidence_checklist"]["real_provider_config_allowed"] is False
    assert item["status"] == "manual_signoff_required"
    assert item["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert item["source_approval_id"].startswith("manual-approval-")
    assert item["evidence_status"] == "materials_ready_signoff_pending"
    assert item["pending_signoff_count"] >= 4
    assert item["material_gap_count"] == 0
    assert item["rollback_material_gap_count"] == 0
    assert item["pending_signoffs"]
    assert item["material_gaps"] == []
    assert item["rollback_material_gaps"] == []
    assert report["decision"]["status"] == "checklist_ready_no_real_provider_config"
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert any("真实 provider 配置" in item for item in report["no_go_conditions"])
    assert "approval-evidence-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_manual_approval_evidence_checklist_deferred(
    tmp_path,
):
    _make_graph_project(tmp_path, "graph-approval-evidence-small", chapters=3)

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_manual_approval_evidence_checklist",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-approval-evidence-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["evidence_checklist"]["status"] == "deferred"
    assert report["summary"]["approval_item_count"] == 0
    assert report["checklist_items"] == []


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


def test_graph_memory_provider_spike_manual_approval_evidence_checklist_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-approval-evidence-http", chapters=3)
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
            "/api/stories/graph-approval-evidence-http/"
            "graph-memory-provider-spike-manual-approval-evidence-checklist",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/"
            "graph-memory-provider-spike-manual-approval-evidence-checklist",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/"
            "graph-memory-provider-spike-manual-approval-evidence-checklist",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_approval_evidence_checklist_json(tmp_path):
    _make_graph_project(tmp_path, "graph-approval-evidence-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        [
            "memory",
            "graph-approval-evidence-checklist",
            "graph-approval-evidence-cli",
            "--json",
        ],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["evidence_checklist"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-approval-evidence-cli"

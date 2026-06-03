"""Graph Memory Provider Spike Opt-in Decision Ledger Preview MVP tests."""

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


def test_graph_memory_provider_spike_opt_in_decision_ledger_preview_ready(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-decision-ledger-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-decision-ledger-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_decision_ledger_preview",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 3, 0, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    row = report["ledger_rows"][0]
    field = row["pending_signoff_fields"][0]

    assert report["version"] == (
        "graph-memory-provider-spike-opt-in-decision-ledger-preview-mvp"
    )
    assert report["mode"] == (
        "read_only_graph_memory_provider_spike_opt_in_decision_ledger_preview"
    )
    assert report["status"] == "ready_for_opt_in_decision_ledger_preview"
    assert report["summary"]["source_review_packet_status"] == (
        "ready_for_opt_in_review_packet"
    )
    assert report["summary"]["provider_count"] >= 2
    assert report["summary"]["ledger_row_count"] >= 2
    assert report["summary"]["pending_signoff_field_count"] >= 4
    assert report["summary"]["blocked_row_count"] >= 2
    assert report["summary"]["pause_material_count"] >= 2
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["ledger_write_allowed"] is False
    assert report["summary"]["approval_saved"] is False
    assert report["summary"]["real_provider_config_allowed"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["decision_ledger_preview"]["status"] == (
        "decision_ledger_preview_ready"
    )
    assert report["decision_ledger_preview"]["ledger_write_allowed"] is False
    assert report["decision_ledger_preview"]["real_provider_config_allowed"] is False
    assert row["status"] == "blocked"
    assert row["approved"] is False
    assert row["ledger_write_allowed"] is False
    assert row["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert row["source_review_packet_section_id"].startswith("review-packet-")
    assert row["decision_fields"]
    assert field["value"] is None
    assert field["required"] is True
    assert field["saved"] is False
    assert report["decision"]["status"] == (
        "decision_ledger_preview_ready_real_provider_still_blocked"
    )
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert any("签收" in item for item in report["ledger_preview_materials"])
    assert "decision-ledger-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_opt_in_decision_ledger_preview_deferred(
    tmp_path,
):
    _make_graph_project(tmp_path, "graph-decision-ledger-small", chapters=3)

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_decision_ledger_preview",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-decision-ledger-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["decision_ledger_preview"]["status"] == "deferred"
    assert report["summary"]["ledger_row_count"] == 0
    assert report["ledger_rows"] == []


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


def test_graph_memory_provider_spike_opt_in_decision_ledger_preview_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-decision-ledger-http", chapters=3)
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
            "/api/stories/graph-decision-ledger-http/"
            "graph-memory-provider-spike-opt-in-decision-ledger-preview",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/"
            "graph-memory-provider-spike-opt-in-decision-ledger-preview",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/"
            "graph-memory-provider-spike-opt-in-decision-ledger-preview",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_opt_in_decision_ledger_preview_json(tmp_path):
    _make_graph_project(tmp_path, "graph-decision-ledger-cli", chapters=3)
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
            "graph-opt-in-decision-ledger-preview",
            "graph-decision-ledger-cli",
            "--json",
        ],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["decision_ledger_preview"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-decision-ledger-cli"

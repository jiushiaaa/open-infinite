"""Graph Memory Provider Spike Opt-in Final Readiness Summary MVP tests."""

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


def test_graph_memory_provider_spike_opt_in_final_readiness_summary_ready(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-final-readiness-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-final-readiness-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_final_readiness_summary",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 3, 1, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    row = report["readiness_rows"][0]
    signoff = report["unresolved_signoff_fields"][0]

    assert report["version"] == (
        "graph-memory-provider-spike-opt-in-final-readiness-summary-mvp"
    )
    assert report["mode"] == (
        "read_only_graph_memory_provider_spike_opt_in_final_readiness_summary"
    )
    assert report["status"] == "ready_for_opt_in_final_readiness_summary"
    assert report["summary"]["source_decision_ledger_status"] == (
        "ready_for_opt_in_decision_ledger_preview"
    )
    assert report["summary"]["provider_count"] >= 2
    assert report["summary"]["readiness_row_count"] >= 2
    assert report["summary"]["unresolved_signoff_field_count"] >= 4
    assert report["summary"]["blocked_row_count"] >= 2
    assert report["summary"]["unresolved_blocker_count"] >= 2
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["final_decision_saved"] is False
    assert report["summary"]["real_provider_config_allowed"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["final_readiness_summary"]["status"] == (
        "final_readiness_summary_ready"
    )
    assert report["final_readiness_summary"]["real_provider_ready"] is False
    assert report["final_readiness_summary"]["real_provider_config_allowed"] is False
    assert row["gate_status"] == "not_ready_for_real_provider"
    assert row["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert row["source_decision_ledger_row_id"].startswith(
        "decision-ledger-preview-"
    )
    assert row["unresolved_signoff_fields"]
    assert row["unresolved_blockers"]
    assert signoff["saved"] is False
    assert signoff["required"] is True
    assert report["decision"]["status"] == (
        "final_readiness_summary_ready_real_provider_still_blocked"
    )
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert any("最终就绪摘要" in item for item in report["final_readiness_materials"])
    assert "final-readiness-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_opt_in_final_readiness_summary_deferred(
    tmp_path,
):
    _make_graph_project(tmp_path, "graph-final-readiness-small", chapters=3)

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_final_readiness_summary",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-final-readiness-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["final_readiness_summary"]["status"] == "deferred"
    assert report["summary"]["readiness_row_count"] == 0
    assert report["readiness_rows"] == []


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


def test_graph_memory_provider_spike_opt_in_final_readiness_summary_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-final-readiness-http", chapters=3)
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
            "/api/stories/graph-final-readiness-http/"
            "graph-memory-provider-spike-opt-in-final-readiness-summary",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/"
            "graph-memory-provider-spike-opt-in-final-readiness-summary",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/"
            "graph-memory-provider-spike-opt-in-final-readiness-summary",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_opt_in_final_readiness_summary_json(tmp_path):
    _make_graph_project(tmp_path, "graph-final-readiness-cli", chapters=3)
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
            "graph-opt-in-final-readiness-summary",
            "graph-final-readiness-cli",
            "--json",
        ],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["final_readiness_summary"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-final-readiness-cli"

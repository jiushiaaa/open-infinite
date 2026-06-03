"""Graph Memory Provider Spike Opt-in No-go Matrix MVP tests."""

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


def test_graph_memory_provider_spike_opt_in_no_go_matrix_ready(tmp_path, monkeypatch):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-no-go-matrix-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-no-go-matrix-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_no_go_matrix",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 20, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    row = report["matrix_rows"][0]
    cells = row["cells"]

    assert report["version"] == "graph-memory-provider-spike-opt-in-no-go-matrix-mvp"
    assert report["mode"] == "read_only_graph_memory_provider_spike_opt_in_no_go_matrix"
    assert report["status"] == "ready_for_opt_in_no_go_matrix"
    assert report["summary"]["source_opt_in_snapshot_status"] == (
        "ready_for_opt_in_evidence_snapshot"
    )
    assert report["summary"]["provider_count"] >= 2
    assert report["summary"]["matrix_row_count"] >= 2
    assert report["summary"]["matrix_cell_count"] >= 10
    assert report["summary"]["blocked_cell_count"] >= 2
    assert report["summary"]["signoff_blocker_count"] >= 2
    assert report["summary"]["material_blocker_count"] == 0
    assert report["summary"]["rollback_blocker_count"] == 0
    assert report["summary"]["real_config_blocker_count"] >= 2
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["matrix_write_allowed"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["real_provider_config_allowed"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["no_go_matrix"]["status"] == "no_go_matrix_ready"
    assert report["no_go_matrix"]["opt_in_blocked"] is True
    assert report["no_go_matrix"]["real_provider_config_allowed"] is False
    assert row["status"] == "blocked"
    assert row["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert row["source_snapshot_id"].startswith("opt-in-evidence-")
    assert row["no_go_reasons"]
    assert any(
        cell["category"] == "manual_signoff" and cell["status"] == "blocked"
        for cell in cells
    )
    assert any(
        cell["category"] == "real_provider_config" and cell["status"] == "blocked"
        for cell in cells
    )
    assert report["decision"]["status"] == (
        "no_go_matrix_ready_real_provider_still_blocked"
    )
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert any("真实 provider 配置" in item for item in report["no_go_conditions"])
    assert "no-go-matrix-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_opt_in_no_go_matrix_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-no-go-matrix-small", chapters=3)

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_no_go_matrix",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-no-go-matrix-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["no_go_matrix"]["status"] == "deferred"
    assert report["summary"]["matrix_row_count"] == 0
    assert report["matrix_rows"] == []


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


def test_graph_memory_provider_spike_opt_in_no_go_matrix_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-no-go-matrix-http", chapters=3)
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
            "/api/stories/graph-no-go-matrix-http/"
            "graph-memory-provider-spike-opt-in-no-go-matrix",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/"
            "graph-memory-provider-spike-opt-in-no-go-matrix",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/"
            "graph-memory-provider-spike-opt-in-no-go-matrix",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_opt_in_no_go_matrix_json(tmp_path):
    _make_graph_project(tmp_path, "graph-no-go-matrix-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-opt-in-no-go-matrix", "graph-no-go-matrix-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["no_go_matrix"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-no-go-matrix-cli"

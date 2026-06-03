"""Graph Memory Provider Spike Opt-in Operator Checklist MVP tests."""

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


def test_graph_memory_provider_spike_opt_in_operator_checklist_ready(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-operator-checklist-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-operator-checklist-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_operator_checklist",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 22, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    section = report["checklist_sections"][0]
    step = section["steps"][0]

    assert report["version"] == "graph-memory-provider-spike-opt-in-operator-checklist-mvp"
    assert report["mode"] == "read_only_graph_memory_provider_spike_opt_in_operator_checklist"
    assert report["status"] == "ready_for_opt_in_operator_checklist"
    assert report["summary"]["source_no_go_matrix_status"] == (
        "ready_for_opt_in_no_go_matrix"
    )
    assert report["summary"]["provider_count"] >= 2
    assert report["summary"]["checklist_section_count"] >= 2
    assert report["summary"]["operator_step_count"] >= 10
    assert report["summary"]["blocked_step_count"] >= 2
    assert report["summary"]["manual_signoff_step_count"] >= 2
    assert report["summary"]["real_config_step_count"] >= 2
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["checklist_write_allowed"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["real_provider_config_allowed"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["operator_checklist"]["status"] == "operator_checklist_ready"
    assert report["operator_checklist"]["opt_in_blocked"] is True
    assert report["operator_checklist"]["real_provider_config_allowed"] is False
    assert section["status"] == "blocked"
    assert section["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert section["source_matrix_row_id"].startswith("no-go-matrix-")
    assert section["steps"]
    assert step["category"] in {
        "manual_signoff",
        "opt_in_materials",
        "rollback_materials",
        "real_provider_config",
        "external_account_or_key",
    }
    assert step["status"] in {"blocked", "review"}
    assert step["action"]
    assert report["decision"]["status"] == (
        "operator_checklist_ready_real_provider_still_blocked"
    )
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert any("真实 provider 配置" in item for item in report["no_go_conditions"])
    assert "operator-checklist-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_opt_in_operator_checklist_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-operator-checklist-small", chapters=3)

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_operator_checklist",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-operator-checklist-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["operator_checklist"]["status"] == "deferred"
    assert report["summary"]["checklist_section_count"] == 0
    assert report["checklist_sections"] == []


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


def test_graph_memory_provider_spike_opt_in_operator_checklist_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-operator-checklist-http", chapters=3)
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
            "/api/stories/graph-operator-checklist-http/"
            "graph-memory-provider-spike-opt-in-operator-checklist",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/"
            "graph-memory-provider-spike-opt-in-operator-checklist",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/"
            "graph-memory-provider-spike-opt-in-operator-checklist",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_opt_in_operator_checklist_json(tmp_path):
    _make_graph_project(tmp_path, "graph-operator-checklist-cli", chapters=3)
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
            "graph-opt-in-operator-checklist",
            "graph-operator-checklist-cli",
            "--json",
        ],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["operator_checklist"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-operator-checklist-cli"

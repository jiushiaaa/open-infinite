"""Graph Memory Provider Spike Opt-in Human Signoff Schema Draft MVP tests."""

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


def test_graph_memory_provider_spike_opt_in_human_signoff_schema_draft_ready(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-human-signoff-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-human-signoff-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_human_signoff_schema_draft",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 3, 2, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    field = report["schema_fields"][0]

    assert report["version"] == (
        "graph-memory-provider-spike-opt-in-human-signoff-schema-draft-mvp"
    )
    assert report["mode"] == (
        "read_only_graph_memory_provider_spike_opt_in_human_signoff_schema_draft"
    )
    assert report["status"] == "ready_for_human_signoff_schema_draft"
    assert report["summary"]["source_final_readiness_status"] == (
        "ready_for_opt_in_final_readiness_summary"
    )
    assert report["summary"]["provider_count"] >= 2
    assert report["summary"]["schema_field_count"] >= 4
    assert report["summary"]["required_field_count"] >= 4
    assert report["summary"]["unresolved_signoff_field_count"] >= 4
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["signoff_saved"] is False
    assert report["summary"]["real_provider_config_allowed"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["schema_draft"]["status"] == "human_signoff_schema_draft_ready"
    assert report["schema_draft"]["save_allowed"] is False
    assert report["schema_draft"]["real_provider_config_allowed"] is False
    assert field["required"] is True
    assert field["saved"] is False
    assert field["input_storage"] == "not_saved"
    assert field["source_final_readiness_field_id"]
    assert field["validation_rule"]["type"] == "required_non_empty_text"
    assert report["decision"]["status"] == (
        "human_signoff_schema_draft_ready_real_provider_still_blocked"
    )
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert any("签收 schema 草案" in item for item in report["schema_materials"])
    assert "human-signoff-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_opt_in_human_signoff_schema_draft_deferred(
    tmp_path,
):
    _make_graph_project(tmp_path, "graph-human-signoff-small", chapters=3)

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_human_signoff_schema_draft",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-human-signoff-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["schema_draft"]["status"] == "deferred"
    assert report["summary"]["schema_field_count"] == 0
    assert report["schema_fields"] == []


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


def test_graph_memory_provider_spike_opt_in_human_signoff_schema_draft_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-human-signoff-http", chapters=3)
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
            "/api/stories/graph-human-signoff-http/"
            "graph-memory-provider-spike-opt-in-human-signoff-schema-draft",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/"
            "graph-memory-provider-spike-opt-in-human-signoff-schema-draft",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/"
            "graph-memory-provider-spike-opt-in-human-signoff-schema-draft",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_opt_in_human_signoff_schema_draft_json(tmp_path):
    _make_graph_project(tmp_path, "graph-human-signoff-cli", chapters=3)
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
            "graph-opt-in-human-signoff-schema",
            "graph-human-signoff-cli",
            "--json",
        ],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["schema_draft"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-human-signoff-cli"

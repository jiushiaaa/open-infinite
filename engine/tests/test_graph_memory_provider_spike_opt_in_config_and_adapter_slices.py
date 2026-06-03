"""Graph Memory Provider Spike opt-in config and adapter boundary slice tests."""

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


def test_graph_memory_provider_spike_opt_in_config_draft_ready_and_secret_safe(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-opt-in-config-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-opt-in-config-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_config_draft",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 3, 3, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "graph-memory-provider-spike-opt-in-config-draft-mvp"
    assert report["mode"] == "read_only_graph_memory_provider_spike_opt_in_config_draft"
    assert report["status"] == "ready_for_opt_in_config_draft"
    assert report["summary"]["source_human_signoff_schema_status"] == (
        "ready_for_human_signoff_schema_draft"
    )
    assert report["summary"]["provider_count"] >= 2
    assert report["summary"]["config_entry_count"] >= 2
    assert report["summary"]["field_mapping_count"] >= 4
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["config_saved"] is False
    assert report["summary"]["real_provider_config_allowed"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["config_draft"]["status"] == "opt_in_config_draft_ready"
    assert report["config_draft"]["save_allowed"] is False
    assert report["config_draft"]["mock_compatible"] is True
    assert report["config_entries"][0]["storage_policy"] == "not_saved"
    assert report["config_entries"][0]["plaintext_key_required"] is False
    assert report["config_entries"][0]["real_provider_config_allowed"] is False
    assert report["field_mappings"][0]["source_schema_field_id"]
    assert report["adapter_boundary"]["real_provider_adapter_allowed"] is False
    assert "Graph Memory Provider Spike Local Provider Contract" in (
        report["decision"]["next_slice"]
    )
    assert "opt-in-config-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_local_contract_harness_and_mock_adapter_ready(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-adapter-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-adapter-secret-8899")

    get_contract = getattr(
        service,
        "get_graph_memory_provider_spike_local_provider_contract",
        None,
    )
    get_harness = getattr(
        service,
        "get_graph_memory_provider_spike_single_fixture_dry_run_harness",
        None,
    )
    get_adapter = getattr(
        service,
        "get_graph_memory_provider_spike_mock_compatible_adapter",
        None,
    )
    assert callable(get_contract)
    assert callable(get_harness)
    assert callable(get_adapter)

    contract = get_contract(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 3, 3, 10, 0),
    )
    harness = get_harness(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 3, 3, 20, 0),
    )
    adapter = get_adapter(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 3, 3, 30, 0),
    )
    text = json.dumps(
        {"contract": contract, "harness": harness, "adapter": adapter},
        ensure_ascii=False,
    )

    assert contract["status"] == "ready_for_local_provider_contract"
    assert contract["summary"]["provider_contract_count"] >= 2
    assert contract["summary"]["adapter_boundary_count"] >= 2
    assert contract["summary"]["external_services_required"] is False
    assert contract["local_provider_contract"]["status"] == (
        "local_provider_contract_ready"
    )
    assert {"prepare_fixture_payload", "run_mock_fixture", "validate_mock_result"}.issubset(
        {method["name"] for method in contract["contract_methods"]}
    )
    assert contract["adapter_boundaries"][0]["plaintext_key_allowed"] is False

    assert harness["status"] == "ready_for_single_fixture_dry_run_harness"
    assert harness["summary"]["fixture_harness_count"] >= 2
    assert harness["summary"]["mock_execution_allowed"] is True
    assert harness["summary"]["real_provider_execution_allowed"] is False
    assert harness["dry_run_harness"]["status"] == "single_fixture_harness_ready"
    assert harness["fixture_harnesses"][0]["execution_mode"] == "local_mock_only"
    assert harness["fixture_harnesses"][0]["writes_artifacts"] is False

    assert adapter["status"] == "ready_for_mock_compatible_adapter"
    assert adapter["summary"]["adapter_count"] >= 2
    assert adapter["summary"]["mock_adapter_ready"] is True
    assert adapter["summary"]["real_provider_adapter_allowed"] is False
    assert adapter["mock_compatible_adapter"]["status"] == "mock_adapter_ready"
    assert adapter["adapter_specs"][0]["implements_contract_methods"]
    assert adapter["adapter_specs"][0]["real_provider_calls_allowed"] is False
    assert "adapter-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_opt_in_config_draft_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-opt-in-config-small", chapters=3)

    report = service.get_graph_memory_provider_spike_opt_in_config_draft(
        "graph-opt-in-config-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["config_draft"]["status"] == "deferred"
    assert report["config_entries"] == []


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


def test_graph_memory_provider_spike_opt_in_config_and_adapter_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-adapter-http", chapters=3)
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
        for endpoint in (
            "graph-memory-provider-spike-opt-in-config-draft",
            "graph-memory-provider-spike-local-provider-contract",
            "graph-memory-provider-spike-single-fixture-dry-run-harness",
            "graph-memory-provider-spike-mock-compatible-adapter",
        ):
            status, body = _get(port, f"/api/stories/graph-adapter-http/{endpoint}")
            bad_status, bad = _get(port, f"/api/stories/..%2Fx/{endpoint}")
            missing_status, _missing = _get(port, f"/api/stories/ghost/{endpoint}")

            assert status == 200
            assert body["story_slug"] == "graph-adapter-http"
            assert bad_status == 400
            assert bad["error"] == "invalid slug"
            assert missing_status == 404
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_memory_cli_graph_opt_in_config_and_adapter_json(tmp_path):
    _make_graph_project(tmp_path, "graph-adapter-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    for command, expected_key in (
        ("graph-opt-in-config-draft", "config_draft"),
        ("graph-local-provider-contract", "local_provider_contract"),
        ("graph-single-fixture-dry-run-harness", "dry_run_harness"),
        ("graph-mock-compatible-adapter", "mock_compatible_adapter"),
    ):
        result = CliRunner().invoke(
            main,
            ["memory", command, "graph-adapter-cli", "--json"],
            env=env,
        )
        assert result.exit_code == 0, result.output
        body = json.loads(result.output)
        assert body["story_slug"] == "graph-adapter-cli"
        assert expected_key in body

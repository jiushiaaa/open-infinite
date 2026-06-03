"""Graph Memory Provider Spike Manual Mock Adapter Review MVP tests."""

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


def test_graph_memory_provider_spike_manual_mock_adapter_review_ready_and_secret_safe(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-manual-mock-review-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-manual-mock-review-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_manual_mock_adapter_review",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 3, 4, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    first_row = report["review_rows"][0]
    first_check = report["compliance_checks"][0]

    assert report["version"] == "graph-memory-provider-spike-manual-mock-adapter-review-mvp"
    assert report["mode"] == "read_only_graph_memory_provider_spike_manual_mock_adapter_review"
    assert report["status"] == "ready_for_manual_mock_adapter_review"
    assert report["summary"]["source_mock_adapter_status"] == (
        "ready_for_mock_compatible_adapter"
    )
    assert report["summary"]["review_row_count"] >= 2
    assert report["summary"]["compliance_check_count"] >= 4
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["real_provider_adapter_allowed"] is False
    assert report["summary"]["pause_after_this_slice"] is True
    assert report["manual_mock_adapter_review"]["status"] == (
        "manual_mock_adapter_review_ready"
    )
    assert report["manual_mock_adapter_review"]["save_allowed"] is False
    assert report["manual_mock_adapter_review"]["pause_after_this_slice"] is True
    assert first_row["review_status"] == "requires_manual_review"
    assert first_row["real_provider_calls_allowed"] is False
    assert first_row["plaintext_key_allowed"] is False
    assert first_row["writes_artifacts"] is False
    assert first_check["status"] == "pass"
    assert first_check["external_services_required"] is False
    assert report["decision"]["status"] == (
        "manual_mock_adapter_review_ready_pause_after_this_slice"
    )
    assert report["decision"]["next_slice"] == "Pause Development"
    assert "manual-mock-review-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_manual_mock_adapter_review_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-manual-mock-review-small", chapters=3)

    report = service.get_graph_memory_provider_spike_manual_mock_adapter_review(
        "graph-manual-mock-review-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["manual_mock_adapter_review"]["status"] == "deferred"
    assert report["review_rows"] == []
    assert report["compliance_checks"] == []


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


def test_graph_memory_provider_spike_manual_mock_adapter_review_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-manual-mock-review-http", chapters=3)
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
            "/api/stories/graph-manual-mock-review-http/"
            "graph-memory-provider-spike-manual-mock-adapter-review",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/"
            "graph-memory-provider-spike-manual-mock-adapter-review",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/"
            "graph-memory-provider-spike-manual-mock-adapter-review",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["story_slug"] == "graph-manual-mock-review-http"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_manual_mock_adapter_review_json(tmp_path):
    _make_graph_project(tmp_path, "graph-manual-mock-review-cli", chapters=3)
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
            "graph-manual-mock-adapter-review",
            "graph-manual-mock-review-cli",
            "--json",
        ],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["story_slug"] == "graph-manual-mock-review-cli"
    assert "manual_mock_adapter_review" in body

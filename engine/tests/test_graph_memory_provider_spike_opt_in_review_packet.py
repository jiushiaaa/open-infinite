"""Graph Memory Provider Spike Opt-in Review Packet MVP tests."""

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


def test_graph_memory_provider_spike_opt_in_review_packet_ready(
    tmp_path, monkeypatch
):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-review-packet-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-review-packet-secret-8899")

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_review_packet",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 23, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    section = report["packet_sections"][0]
    evidence = section["evidence_sequence"][0]

    assert report["version"] == "graph-memory-provider-spike-opt-in-review-packet-mvp"
    assert report["mode"] == "read_only_graph_memory_provider_spike_opt_in_review_packet"
    assert report["status"] == "ready_for_opt_in_review_packet"
    assert report["summary"]["source_operator_checklist_status"] == (
        "ready_for_opt_in_operator_checklist"
    )
    assert report["summary"]["provider_count"] >= 2
    assert report["summary"]["packet_section_count"] >= 2
    assert report["summary"]["evidence_item_count"] >= 10
    assert report["summary"]["blocked_step_count"] >= 2
    assert report["summary"]["pause_material_count"] >= 2
    assert report["summary"]["escalation_material_count"] >= 2
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["review_packet_write_allowed"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["real_provider_config_allowed"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["review_packet"]["status"] == "review_packet_ready"
    assert report["review_packet"]["real_provider_config_allowed"] is False
    assert report["review_packet"]["opt_in_blocked"] is True
    assert section["status"] == "blocked"
    assert section["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert section["source_checklist_section_id"].startswith("operator-checklist-")
    assert section["pause_required"] is True
    assert section["pause_materials"]
    assert section["escalation_materials"]
    assert evidence["source_step_id"]
    assert evidence["category"] in {
        "manual_signoff",
        "opt_in_materials",
        "rollback_materials",
        "real_provider_config",
        "external_account_or_key",
    }
    assert evidence["review_note"]
    assert report["decision"]["status"] == (
        "review_packet_ready_real_provider_still_blocked"
    )
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert any("暂停" in item for item in report["review_packet_materials"])
    assert "review-packet-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_opt_in_review_packet_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-review-packet-small", chapters=3)

    get_report = getattr(
        service,
        "get_graph_memory_provider_spike_opt_in_review_packet",
        None,
    )
    assert callable(get_report)
    report = get_report(
        "graph-review-packet-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["review_packet"]["status"] == "deferred"
    assert report["summary"]["packet_section_count"] == 0
    assert report["packet_sections"] == []


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


def test_graph_memory_provider_spike_opt_in_review_packet_http_statuses(
    tmp_path, monkeypatch
):
    _make_graph_project(tmp_path, "graph-review-packet-http", chapters=3)
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
            "/api/stories/graph-review-packet-http/"
            "graph-memory-provider-spike-opt-in-review-packet",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/"
            "graph-memory-provider-spike-opt-in-review-packet",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/"
            "graph-memory-provider-spike-opt-in-review-packet",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_opt_in_review_packet_json(tmp_path):
    _make_graph_project(tmp_path, "graph-review-packet-cli", chapters=3)
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
            "graph-opt-in-review-packet",
            "graph-review-packet-cli",
            "--json",
        ],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["review_packet"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-review-packet-cli"

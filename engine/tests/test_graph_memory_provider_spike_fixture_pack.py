"""Graph Memory Provider Spike Fixture Pack MVP：只读 provider spike 前置包。"""

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
from living_novel_engine.service import get_graph_memory_provider_spike_fixture_pack

from test_cross_project_retrieval_samples_index import _make_project as _make_sample_project
from test_v093_graph_memory_trigger import _make_project as _make_graph_project


def _make_fixture_project(tmp_path):
    project_dir = _make_graph_project(tmp_path, "graph-fixture-pack-large", chapters=55)
    (project_dir / "memory" / "canon_ledger.jsonl").write_text("", encoding="utf-8")
    (project_dir / "memory" / "entity_aliases.yaml").unlink()
    _make_sample_project(tmp_path, "graph-fixture-pack-samples", with_sample=True)
    return project_dir


def test_graph_memory_provider_spike_fixture_pack_from_replay_report(tmp_path, monkeypatch):
    _make_fixture_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = get_graph_memory_provider_spike_fixture_pack(
        "graph-fixture-pack-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 9, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    pack = report["provider_fixture_packs"][0]
    fixture = pack["fixture"]

    assert report["version"] == "graph-memory-provider-spike-fixture-pack-mvp"
    assert report["mode"] == "read_only_graph_memory_provider_spike_fixture_pack"
    assert report["status"] == "ready_for_fixture_pack"
    assert report["fixture_gate"]["passed"] is True
    assert report["fixture_gate"]["status"] == "fixture_pack_ready"
    assert report["summary"]["source_replay_report_status"] == "ready_for_review"
    assert report["summary"]["provider_fixture_count"] >= 2
    assert report["summary"]["selected_fixture_count"] >= 2
    assert report["summary"]["manual_review_required_count"] >= 2
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert pack["status"] == "dry_run_fixture_ready"
    assert pack["opt_in_required"] is True
    assert pack["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert fixture["dry_run_only"] is True
    assert fixture["scope"] == "single_provider_single_project_single_fixture"
    assert fixture["source_report_status"] == "ready_for_review"
    assert fixture["sample_case_count"] >= 1
    assert fixture["project_slug"] == "graph-fixture-pack-large"
    assert pack["manual_acceptance_checklist"]
    assert pack["cost_guardrails"]
    assert pack["privacy_guardrails"]
    assert pack["rollback_checklist"]
    assert any("真实付费 Key" in item for item in report["no_go_conditions"])
    assert "graph-fixture-pack-samples-retrieval-eval-001" in report["content_json"]
    assert report["decision"]["status"] == "manual_review_before_real_provider_config"
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_provider_spike_fixture_pack_small_project_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-fixture-pack-small", chapters=3)

    report = get_graph_memory_provider_spike_fixture_pack(
        "graph-fixture-pack-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["fixture_gate"]["passed"] is False
    assert report["fixture_gate"]["status"] == "deferred"
    assert report["summary"]["provider_fixture_count"] == 0
    assert report["provider_fixture_packs"] == []


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


def test_graph_memory_provider_spike_fixture_pack_http_statuses(tmp_path, monkeypatch):
    _make_graph_project(tmp_path, "graph-fixture-pack-http", chapters=3)
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
            "/api/stories/graph-fixture-pack-http/graph-memory-provider-spike-fixture-pack",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/graph-memory-provider-spike-fixture-pack",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/graph-memory-provider-spike-fixture-pack",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_fixture_pack_json(tmp_path):
    _make_graph_project(tmp_path, "graph-fixture-pack-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-fixture-pack", "graph-fixture-pack-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["fixture_gate"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-fixture-pack-cli"

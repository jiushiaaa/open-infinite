"""Graph Memory Offline Shadow Replay Report MVP：只读离线 replay 结果报告。"""

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
from living_novel_engine.service import get_graph_memory_offline_shadow_replay_report

from test_cross_project_retrieval_samples_index import _make_project as _make_sample_project
from test_v093_graph_memory_trigger import _make_project as _make_graph_project


def _make_replay_project(tmp_path):
    project_dir = _make_graph_project(tmp_path, "graph-replay-report-large", chapters=55)
    (project_dir / "memory" / "canon_ledger.jsonl").write_text("", encoding="utf-8")
    (project_dir / "memory" / "entity_aliases.yaml").unlink()
    _make_sample_project(tmp_path, "graph-replay-report-samples", with_sample=True)
    return project_dir


def test_graph_memory_offline_shadow_replay_report_from_plan(tmp_path, monkeypatch):
    _make_replay_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = get_graph_memory_offline_shadow_replay_report(
        "graph-replay-report-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 8, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    result = report["case_results"][0]
    providers = {item["provider_id"]: item for item in report["provider_results"]}

    assert report["version"] == "graph-memory-offline-shadow-replay-report-mvp"
    assert report["mode"] == "read_only_graph_memory_offline_shadow_replay_report"
    assert report["status"] == "ready_for_review"
    assert report["report_gate"]["passed"] is True
    assert report["report_gate"]["status"] == "offline_replay_report_ready"
    assert report["summary"]["source_replay_plan_status"] == "ready_for_offline_replay"
    assert report["summary"]["provider_result_count"] >= 2
    assert report["summary"]["case_result_count"] >= 2
    assert report["summary"]["manual_review_required_count"] == report["summary"]["case_result_count"]
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["uses_graphrag"] is False
    assert report["summary"]["uses_zep"] is False
    assert report["summary"]["uses_vector_store"] is False
    assert report["summary"]["uses_reranker"] is False
    assert report["summary"]["uses_embedding_provider"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert result["status"] == "mock_candidate_gain"
    assert result["fixture_kind"] == "local_shadow_fixture"
    assert result["mock_delta"]["dry_run_only"] is True
    assert "BM25" in result["baseline_chain"]
    assert "人工复核" in result["manual_review_result"]["status_label"]
    assert result["failure_mode"]["fallback"] == "keep_local_baseline"
    assert providers["graphrag"]["recommendation"] in {
        "manual_review_before_opt_in_spike",
        "collect_more_evidence",
    }
    assert report["decision"]["status"] == "manual_review_required"
    assert any("真实付费 Key" in item for item in report["no_go_conditions"])
    assert "graph-replay-report-samples-retrieval-eval-001" in report["content_json"]
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_offline_shadow_replay_report_small_project_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-replay-report-small", chapters=3)

    report = get_graph_memory_offline_shadow_replay_report(
        "graph-replay-report-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["report_gate"]["passed"] is False
    assert report["report_gate"]["status"] == "deferred"
    assert report["summary"]["case_result_count"] == 0
    assert report["case_results"] == []


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


def test_graph_memory_offline_shadow_replay_report_http_statuses(tmp_path, monkeypatch):
    _make_graph_project(tmp_path, "graph-replay-report-http", chapters=3)
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
            "/api/stories/graph-replay-report-http/graph-memory-offline-shadow-replay-report",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/graph-memory-offline-shadow-replay-report",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/graph-memory-offline-shadow-replay-report",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_replay_report_json(tmp_path):
    _make_graph_project(tmp_path, "graph-replay-report-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-replay-report", "graph-replay-report-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["report_gate"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-replay-report-cli"

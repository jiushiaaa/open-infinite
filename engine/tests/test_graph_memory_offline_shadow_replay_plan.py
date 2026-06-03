"""Graph Memory Offline Shadow Replay Plan MVP：只读离线 shadow replay 计划。"""

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
from living_novel_engine.service import get_graph_memory_offline_shadow_replay_plan

from test_cross_project_retrieval_samples_index import _make_project as _make_sample_project
from test_v093_graph_memory_trigger import _make_project as _make_graph_project


def _make_replay_project(tmp_path):
    project_dir = _make_graph_project(tmp_path, "graph-replay-large", chapters=55)
    (project_dir / "memory" / "canon_ledger.jsonl").write_text("", encoding="utf-8")
    (project_dir / "memory" / "entity_aliases.yaml").unlink()
    _make_sample_project(tmp_path, "graph-replay-samples", with_sample=True)
    return project_dir


def test_graph_memory_offline_shadow_replay_plan_from_provider_boundaries(
    tmp_path, monkeypatch
):
    _make_replay_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = get_graph_memory_offline_shadow_replay_plan(
        "graph-replay-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 7, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    case = report["replay_cases"][0]

    assert report["version"] == "graph-memory-offline-shadow-replay-plan-mvp"
    assert report["mode"] == "read_only_graph_memory_offline_shadow_replay_plan"
    assert report["status"] == "ready_for_offline_replay"
    assert report["replay_gate"]["passed"] is True
    assert report["replay_gate"]["status"] == "offline_replay_ready"
    assert report["summary"]["source_provider_boundary_status"] == "ready_for_boundary_review"
    assert report["summary"]["candidate_provider_count"] >= 2
    assert report["summary"]["replay_case_count"] >= 2
    assert report["summary"]["manual_review_required_count"] == report["summary"]["replay_case_count"]
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["provider_calls"] is False
    assert report["summary"]["uses_graphrag"] is False
    assert report["summary"]["uses_zep"] is False
    assert report["summary"]["uses_vector_store"] is False
    assert report["summary"]["uses_reranker"] is False
    assert report["summary"]["uses_embedding_provider"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert case["status"] == "planned"
    assert case["fixture_kind"] == "local_shadow_fixture"
    assert case["provider_id"] in {"graphrag", "zep", "temporal_memory"}
    assert "BM25" in case["baseline_chain"]
    assert case["replay_input"]["query"]
    assert any("验收" in item for item in case["acceptance_criteria"])
    assert any("回退" in item for item in case["rollback_checklist"])
    assert any("人工" in item for item in case["manual_review_checklist"])
    assert any("真实付费 Key" in item for item in report["no_go_conditions"])
    assert "graph-replay-samples-retrieval-eval-001" in report["content_json"]
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_offline_shadow_replay_plan_small_project_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-replay-small", chapters=3)

    report = get_graph_memory_offline_shadow_replay_plan(
        "graph-replay-small",
        projects_dir=tmp_path,
    )

    assert report["status"] == "deferred"
    assert report["replay_gate"]["passed"] is False
    assert report["replay_gate"]["status"] == "deferred"
    assert report["summary"]["replay_case_count"] == 0
    assert report["replay_cases"] == []


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


def test_graph_memory_offline_shadow_replay_plan_http_statuses(tmp_path, monkeypatch):
    _make_graph_project(tmp_path, "graph-replay-http", chapters=3)
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
            "/api/stories/graph-replay-http/graph-memory-offline-shadow-replay-plan",
        )
        bad_status, bad = _get(
            port,
            "/api/stories/..%2Fx/graph-memory-offline-shadow-replay-plan",
        )
        missing_status, _missing = _get(
            port,
            "/api/stories/ghost/graph-memory-offline-shadow-replay-plan",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_replay_plan_json(tmp_path):
    _make_graph_project(tmp_path, "graph-replay-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-replay-plan", "graph-replay-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["replay_gate"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-replay-cli"

"""v0.9.4 Advanced Runner Evaluation: trigger conditions only."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import evaluate_advanced_runner_trigger


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_run(outputs, run_id: str, *, complex_case: bool = False):
    run_dir = outputs / run_id
    run_dir.mkdir(parents=True)
    if complex_case:
        summary = {
            "candidate_count": 9,
            "executable_count": 1,
            "review_required_count": 5,
            "blocked_count": 3,
            "high_risk_count": 2,
        }
        trace = {
            "turn_plans": [
                {"round_num": 1, "actor_id": f"char_{i}", "intents": []}
                for i in range(6)
            ],
            "private_knowledge": [{"fact_id": f"pk_{i}"} for i in range(4)],
            "misunderstandings": [{"holder_id": f"char_{i}"} for i in range(3)],
            "generation_meta": {
                "validation_status": "repaired",
                "validator_warnings": [
                    "在场角色 lin_fan 缺少 turn_plan",
                    "干预内容未进入目标角色 private_knowledge",
                ],
            },
        }
        emergence = {
            "nodes": [
                {"node_id": "n1", "status": "high_value", "score": 0.88},
                {"node_id": "n2", "status": "candidate", "score": 0.5},
            ]
        }
    else:
        summary = {
            "candidate_count": 2,
            "executable_count": 2,
            "review_required_count": 0,
            "blocked_count": 0,
            "high_risk_count": 0,
        }
        trace = {
            "turn_plans": [{"round_num": 1, "actor_id": "lin_fan", "intents": []}],
            "private_knowledge": [],
            "misunderstandings": [],
            "generation_meta": {
                "validation_status": "ok",
                "validator_warnings": [],
            },
        }
        emergence = {"nodes": []}

    _write_json(
        run_dir / "runner_state_execution_report.json",
        {
            "kind": "runner_state_execution_spike",
            "summary": summary,
            "safety": {"default_run_scene_unchanged": True},
        },
    )
    _write_json(run_dir / "branch_a" / "multi_agent_trace.json", trace)
    _write_json(run_dir / "emergence_nodes.json", emergence)
    return run_dir


def test_advanced_runner_trigger_simple_run_not_triggered(tmp_path):
    outputs = tmp_path / "outputs"
    _make_run(outputs, "run_simple")

    report = evaluate_advanced_runner_trigger("run_simple", outputs_dir=outputs)

    assert report["version"] == "v0.9.4"
    assert report["status"] == "not_triggered"
    assert report["trigger"]["should_evaluate"] is False
    assert report["metrics"]["state_execution_candidate_count"] == 2
    assert "继续使用当前" in report["summary"]


def test_advanced_runner_trigger_complex_run_triggers(tmp_path):
    outputs = tmp_path / "outputs"
    _make_run(outputs, "run_complex", complex_case=True)

    report = evaluate_advanced_runner_trigger("run_complex", outputs_dir=outputs)

    assert report["status"] == "triggered"
    assert report["trigger"]["should_evaluate"] is True
    assert "state_execution_backlog" in report["trigger"]["reasons"]
    assert "high_risk_actions" in report["trigger"]["reasons"]
    assert "trace_repair_warnings" in report["trigger"]["reasons"]
    assert "high_value_emergence" in report["trigger"]["reasons"]
    assert report["metrics"]["trace_warning_count"] == 2
    assert any("LangGraph" in step for step in report["next_steps"])


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    _make_run(outputs, "run_http")
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def test_advanced_runner_trigger_http_statuses(running_server):
    port = running_server

    status, body = _get(port, "/api/runs/run_http/advanced-runner-evaluation")
    assert status == 200
    assert body["status"] == "not_triggered"

    bad_status, bad = _get(port, "/api/runs/bad..id/advanced-runner-evaluation")
    assert bad_status == 400
    assert bad["error"] == "invalid run_id"

    missing_status, _missing = _get(port, "/api/runs/missing/advanced-runner-evaluation")
    assert missing_status == 404

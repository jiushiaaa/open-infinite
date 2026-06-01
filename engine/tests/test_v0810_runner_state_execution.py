"""v0.8.10-A Runner State Execution Spike.

第一刀只做 opt-in dry-run 评估：把动作计划 / 注册表 / 涌现节点转成
候选状态变化报告，不改 run_scene 默认行为，不写回 state_snapshot.json。
"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

from living_novel_engine.browser import indexer, server
from living_novel_engine.service import (
    apply_runner_state_execution,
    evaluate_runner_state_execution,
    get_project_audit_log,
    get_runner_state_execution_report,
    import_novel_from_payload,
    rollback_runner_state_execution,
    run_intervention,
)


def _run_basic_intervention(tmp_path, monkeypatch, content: str):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    result = run_intervention(
        story_slug="tianhuang-night",
        target="lin_wan_zhou",
        content=content,
        mock=True,
        rounds=1,
    )
    return outputs, result


def _run_imported_intervention(tmp_path, monkeypatch, content: str):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    projects.mkdir()
    outputs.mkdir()
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    import_novel_from_payload(
        name="state-audit",
        chapters=[
            {
                "filename": f"chapter_{i:03d}.md",
                "content": f"第{i}章 风鸣铃疑云\n赵轩在归云斋追查风鸣铃线索，第 {i} 次记录角色动机。",
            }
            for i in range(1, 7)
        ],
        mock=True,
        long_mode=True,
        projects_dir=projects,
    )
    result = run_intervention(
        story_slug="state-audit",
        target="zhao_xuan",
        content=content,
        mock=True,
        rounds=1,
    )
    return projects, outputs, result


def test_state_execution_spike_writes_dry_run_report_without_mutating_snapshots(
    tmp_path, monkeypatch
):
    outputs, result = _run_basic_intervention(
        tmp_path,
        monkeypatch,
        "告诉林晚舟竹林里有埋伏，让她先查证退魂铃",
    )
    before = json.loads(
        (outputs / result.run_id / "branch_a" / "state_snapshot.json").read_text(
            encoding="utf-8"
        )
    )

    report = evaluate_runner_state_execution(result.run_id, outputs_dir=outputs)
    after = json.loads(
        (outputs / result.run_id / "branch_a" / "state_snapshot.json").read_text(
            encoding="utf-8"
        )
    )
    loaded = get_runner_state_execution_report(result.run_id, outputs_dir=outputs)

    assert report["kind"] == "runner_state_execution_spike"
    assert report["mode"] == "dry_run"
    assert report["safety"]["default_run_scene_unchanged"] is True
    assert report["safety"]["writes_state_snapshot"] is False
    assert report["summary"]["candidate_count"] >= 1
    assert report["summary"]["applied_count"] == 0
    assert any(c["state_deltas"] for c in report["candidates"])
    assert before == after
    assert loaded["summary"] == report["summary"]
    assert (outputs / result.run_id / "runner_state_execution_report.json").exists()


def test_state_execution_blocks_high_risk_alternate_actions(tmp_path, monkeypatch):
    outputs, result = _run_basic_intervention(
        tmp_path,
        monkeypatch,
        "让林晚舟获得现代系统和无限子弹手枪",
    )

    report = evaluate_runner_state_execution(result.run_id, outputs_dir=outputs)

    assert report["summary"]["blocked_count"] >= 1
    assert report["summary"]["applied_count"] == 0
    assert any(
        candidate["gate_status"] == "blocked"
        and "故事合约" in " ".join(candidate["blockers"])
        for candidate in report["candidates"]
    )


def test_branch_detail_exposes_state_execution_report_and_damaged_degrades(
    tmp_path, monkeypatch
):
    outputs, result = _run_basic_intervention(
        tmp_path,
        monkeypatch,
        "把退魂铃代价提前告诉林晚舟",
    )
    evaluate_runner_state_execution(result.run_id, outputs_dir=outputs)
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))

    detail = indexer.get_branch(result.run_id, "branch_a")
    assert detail["runner_state_execution_report"]["kind"] == (
        "runner_state_execution_spike"
    )

    (outputs / result.run_id / "runner_state_execution_report.json").write_text(
        "{broken",
        encoding="utf-8",
    )
    damaged = indexer.get_branch(result.run_id, "branch_a")
    assert damaged["runner_state_execution_report"] == {}


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _post(port: int, path: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}{path}", timeout=10
        ) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_state_execution_http_evaluate_get_and_status_codes(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    projects.mkdir()
    outputs.mkdir()
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")

    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _post(
            port,
            "/api/interventions",
            {
                "story_slug": "tianhuang-night",
                "target": "lin_wan_zhou",
                "content": "告诉林晚舟竹林里有埋伏",
                "mock": True,
                "rounds": 1,
            },
        )
        assert status == 200
        run_id = body["run_id"]

        status, report = _post(
            port,
            f"/api/runs/{run_id}/state-execution-evaluate",
            {},
        )
        assert status == 200
        assert report["kind"] == "runner_state_execution_spike"

        status, fetched = _get(
            port,
            f"/api/runs/{run_id}/state-execution-report",
        )
        assert status == 200
        assert fetched["summary"] == report["summary"]

        status, bad = _post(port, "/api/runs/bad..id/state-execution-evaluate", {})
        assert status == 400
        assert "invalid" in bad["error"]

        status, missing = _get(port, "/api/runs/missing_run/state-execution-report")
        assert status == 404
        assert "不存在" in missing["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_state_execution_mvp_applies_low_risk_overlay_and_preserves_snapshot(
    tmp_path, monkeypatch
):
    outputs, result = _run_basic_intervention(
        tmp_path,
        monkeypatch,
        "告诉林晚舟竹林里有埋伏，让她先查证退魂铃",
    )
    evaluate_runner_state_execution(result.run_id, outputs_dir=outputs)
    branch_snapshot_path = outputs / result.run_id / "branch_a" / "state_snapshot.json"
    before = json.loads(branch_snapshot_path.read_text(encoding="utf-8"))

    apply_report = apply_runner_state_execution(
        result.run_id,
        confirm=True,
        outputs_dir=outputs,
    )
    after = json.loads(branch_snapshot_path.read_text(encoding="utf-8"))
    overlay_path = outputs / result.run_id / "branch_a" / "state_execution_overlay.json"
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))

    assert apply_report["kind"] == "runner_state_execution_apply"
    assert apply_report["mode"] == "overlay"
    assert apply_report["summary"]["applied_count"] >= 1
    assert apply_report["safety"]["default_run_scene_unchanged"] is True
    assert apply_report["safety"]["mutates_state_snapshot"] is False
    assert apply_report["safety"]["rollback_available"] is True
    assert before == after
    assert overlay["kind"] == "state_execution_overlay"
    assert overlay["branch_id"] == "branch_a"
    assert overlay["state_overlay"] != before
    assert any(delta["field"] == "characters.emotion" for delta in overlay["state_deltas"])

    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    detail = indexer.get_branch(result.run_id, "branch_a")
    assert detail["state_execution_overlay"]["kind"] == "state_execution_overlay"
    assert detail["runner_state_execution_apply_report"]["summary"]["applied_count"] >= 1


def test_state_execution_mvp_requires_confirm_and_blocks_unsafe_candidates(
    tmp_path, monkeypatch
):
    outputs, result = _run_basic_intervention(
        tmp_path,
        monkeypatch,
        "让林晚舟获得现代系统和无限子弹手枪",
    )
    evaluate_runner_state_execution(result.run_id, outputs_dir=outputs)

    try:
        apply_runner_state_execution(result.run_id, outputs_dir=outputs)
    except Exception as exc:
        assert "confirm" in str(exc) or "确认" in str(exc)
    else:  # pragma: no cover - defensive, test must fail if implicit apply works
        raise AssertionError("apply must require explicit confirm=True")

    try:
        apply_runner_state_execution(result.run_id, confirm=True, outputs_dir=outputs)
    except Exception as exc:
        assert "可应用" in str(exc) or "eligible" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("unsafe alternate candidates must not be applied")

    assert not (outputs / result.run_id / "branch_a" / "state_execution_overlay.json").exists()


def test_state_execution_mvp_rollback_removes_overlay_without_mutating_snapshot(
    tmp_path, monkeypatch
):
    outputs, result = _run_basic_intervention(
        tmp_path,
        monkeypatch,
        "告诉林晚舟竹林里有埋伏，让她先查证退魂铃",
    )
    evaluate_runner_state_execution(result.run_id, outputs_dir=outputs)
    branch_snapshot_path = outputs / result.run_id / "branch_a" / "state_snapshot.json"
    before = json.loads(branch_snapshot_path.read_text(encoding="utf-8"))
    apply_runner_state_execution(result.run_id, confirm=True, outputs_dir=outputs)

    rollback = rollback_runner_state_execution(
        result.run_id,
        confirm=True,
        outputs_dir=outputs,
    )
    after = json.loads(branch_snapshot_path.read_text(encoding="utf-8"))

    assert rollback["kind"] == "runner_state_execution_rollback"
    assert rollback["summary"]["removed_overlay_count"] >= 1
    assert before == after
    assert not (outputs / result.run_id / "branch_a" / "state_execution_overlay.json").exists()
    assert (outputs / result.run_id / "runner_state_execution_rollback_report.json").exists()


def test_state_execution_mvp_appends_project_audit_events(tmp_path, monkeypatch):
    projects, outputs, result = _run_imported_intervention(
        tmp_path,
        monkeypatch,
        "让赵轩提前核对风鸣铃线索，并把可疑地点记入册页",
    )
    evaluate_runner_state_execution(result.run_id, outputs_dir=outputs)

    apply_runner_state_execution(result.run_id, confirm=True, outputs_dir=outputs)
    audit = get_project_audit_log("state-audit", projects_dir=projects)
    applied = next(
        event
        for event in audit["events"]
        if event["action"] == "state_execution_applied"
        and event["artifact"] == "memory/project_audit_log.jsonl"
    )
    assert applied["metadata"]["run_id"] == result.run_id
    assert applied["metadata"]["applied_count"] >= 1

    rollback_runner_state_execution(result.run_id, confirm=True, outputs_dir=outputs)
    audit = get_project_audit_log("state-audit", projects_dir=projects)
    rolled_back = next(
        event
        for event in audit["events"]
        if event["action"] == "state_execution_rolled_back"
        and event["artifact"] == "memory/project_audit_log.jsonl"
    )
    assert rolled_back["metadata"]["run_id"] == result.run_id
    assert rolled_back["metadata"]["removed_overlay_count"] >= 1


def test_state_execution_mvp_http_apply_rollback_and_status_codes(
    tmp_path, monkeypatch
):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    projects.mkdir()
    outputs.mkdir()
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")

    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _post(
            port,
            "/api/interventions",
            {
                "story_slug": "tianhuang-night",
                "target": "lin_wan_zhou",
                "content": "告诉林晚舟竹林里有埋伏",
                "mock": True,
                "rounds": 1,
            },
        )
        assert status == 200
        run_id = body["run_id"]

        status, missing = _post(
            port,
            f"/api/runs/{run_id}/state-execution-apply",
            {"confirm": True},
        )
        assert status == 404
        assert "评估报告" in missing["error"]

        _post(port, f"/api/runs/{run_id}/state-execution-evaluate", {})

        status, unconfirmed = _post(
            port,
            f"/api/runs/{run_id}/state-execution-apply",
            {},
        )
        assert status == 400
        assert "确认" in unconfirmed["error"]

        status, apply_report = _post(
            port,
            f"/api/runs/{run_id}/state-execution-apply",
            {"confirm": True},
        )
        assert status == 200
        assert apply_report["kind"] == "runner_state_execution_apply"
        assert apply_report["summary"]["applied_count"] >= 1

        status, detail = _get(port, f"/api/runs/{run_id}/branches/branch_a")
        assert status == 200
        assert detail["state_execution_overlay"]["kind"] == "state_execution_overlay"

        status, bad = _post(
            port,
            "/api/runs/bad..id/state-execution-rollback",
            {"confirm": True},
        )
        assert status == 400
        assert "invalid" in bad["error"]

        status, rollback = _post(
            port,
            f"/api/runs/{run_id}/state-execution-rollback",
            {"confirm": True},
        )
        assert status == 200
        assert rollback["summary"]["removed_overlay_count"] >= 1
    finally:
        httpd.shutdown()
        httpd.server_close()

"""World Sandbox Loop v6: world autopilot report and checkpoints."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

from living_novel_engine.browser import server
from living_novel_engine.service import import_novel_from_payload
from living_novel_engine.service.tianming import (
    confirm_tianming_book,
    generate_tianming_book,
)
from living_novel_engine.service import world_autopilot
from living_novel_engine.service.world_autopilot import run_world_autopilot


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 世界自演\n"
                "赵轩追查风鸣铃，沈冰月守住苍澜派规矩，韩无归逼问旧案。"
            ),
        }
        for idx in range(1, n + 1)
    ]


def _make_project(tmp_path, slug: str = "autopilot-story"):
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    generate_tianming_book(slug, projects_dir=tmp_path)
    confirm_tianming_book(slug, confirm=True, projects_dir=tmp_path)


def test_world_autopilot_writes_report_checkpoints_and_rounds(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    report = run_world_autopilot(
        "autopilot-story",
        seed_event="老皇帝驾崩，边境军报传来。",
        objective_type="rounds",
        round_limit=3,
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    run_dir = outputs_dir / report["run_id"]

    assert report["version"] == "world-autopilot-v1"
    assert report["artifact"] == "autopilot_report.json"
    assert (run_dir / "autopilot_report.json").exists()
    assert (run_dir / "checkpoints" / "checkpoint_003.json").exists()
    assert report["rounds_completed"] == 3
    assert len(report["sandbox_runs"]) == 3
    assert len(report["checkpoints"]) == 3
    assert all(row["sandbox_run_id"] for row in report["checkpoints"])
    assert report["checkpoints"][0]["consequence_state"]["status"] == "active"
    assert report["checkpoints"][0]["consequence_state"]["domains"]["location"]["current"]
    assert report["final_world_stage"]["stage"] != "未启动"


def test_world_autopilot_stops_on_anchor_change_objective(tmp_path):
    _make_project(tmp_path)

    report = run_world_autopilot(
        "autopilot-story",
        seed_event="赵轩死亡，云城失去主锚点。",
        objective_type="anchor_change",
        round_limit=5,
        projects_dir=tmp_path,
        outputs_dir=tmp_path / "_outputs",
    )

    assert report["objective"]["type"] == "anchor_change"
    assert report["stop_reason"] == "anchor_change_detected"
    assert report["rounds_completed"] <= 2


def test_world_autopilot_supports_event_and_time_objectives(tmp_path):
    _make_project(tmp_path)

    event_report = run_world_autopilot(
        "autopilot-story",
        seed_event="暗线密探抵达归云斋，请求等待风鸣铃。",
        objective_type="event",
        stop_event="风鸣铃",
        round_limit=5,
        projects_dir=tmp_path,
        outputs_dir=tmp_path / "_outputs",
    )

    assert event_report["objective"]["type"] == "event"
    assert event_report["objective"]["stop_event"] == "风鸣铃"
    assert event_report["stop_reason"] == "target_event_reached"
    assert event_report["rounds_completed"] == 1

    time_report = run_world_autopilot(
        "autopilot-story",
        seed_event="沈冰月宣布闭山三日，诸峰各自试探。",
        objective_type="time",
        time_limit="三日后",
        round_limit=5,
        projects_dir=tmp_path,
        outputs_dir=tmp_path / "_outputs",
    )

    assert time_report["objective"]["type"] == "time"
    assert time_report["objective"]["time_limit"] == "三日后"
    assert time_report["stop_reason"] == "time_limit_reached"
    assert time_report["rounds_completed"] == 2


def test_world_autopilot_stops_on_causal_debt_and_writes_readable_timeline(tmp_path):
    _make_project(tmp_path)

    report = run_world_autopilot(
        "autopilot-story",
        seed_event="归云斋因果债爆发，封山令压向所有弟子。",
        objective_type="causal_debt",
        round_limit=5,
        projects_dir=tmp_path,
        outputs_dir=tmp_path / "_outputs",
    )

    assert report["objective"]["type"] == "causal_debt"
    assert report["stop_reason"] == "causal_debt_burst_detected"
    assert report["rounds_completed"] == 1
    assert report["stop_condition"]["matched"] is True
    assert "因果债" in report["stop_condition"]["evidence"]
    assert report["overnight_report"]["timeline"]
    assert report["overnight_report"]["checkpoint_recovery"]["resume_from_checkpoint"]


def test_world_autopilot_failure_can_resume_from_latest_checkpoint(
    tmp_path, monkeypatch
):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    real_run_sandbox_round = world_autopilot.run_sandbox_round
    calls = {"count": 0}

    def fail_after_first_checkpoint(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 2:
            raise RuntimeError("模拟本地长时自演中断")
        return real_run_sandbox_round(*args, **kwargs)

    monkeypatch.setattr(
        world_autopilot,
        "run_sandbox_round",
        fail_after_first_checkpoint,
    )

    failed = run_world_autopilot(
        "autopilot-story",
        seed_event="沈冰月夜巡归云斋，风鸣铃忽然倒响。",
        objective_type="rounds",
        round_limit=3,
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )

    assert failed["status"] == "failed"
    assert failed["task"]["status"] == "failed"
    assert failed["rounds_completed"] == 1
    assert failed["failure"]["latest_checkpoint"] == "checkpoint_001"
    assert failed["recovery"]["can_resume"] is True
    assert failed["overnight_report"]["checkpoint_recovery"]["resume_from_checkpoint"] == (
        "checkpoint_001"
    )

    task = world_autopilot.get_world_autopilot_task(
        "autopilot-story",
        failed["task"]["task_id"],
        projects_dir=tmp_path,
        worldline_id="main",
    )
    assert task["status"] == "failed"
    assert task["failure"]["latest_checkpoint"] == "checkpoint_001"

    monkeypatch.setattr(world_autopilot, "run_sandbox_round", real_run_sandbox_round)
    resumed = world_autopilot.resume_world_autopilot_task(
        "autopilot-story",
        failed["task"]["task_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="main",
    )

    assert resumed["status"] == "completed"
    assert resumed["latest_report_run_id"] != failed["run_id"]
    assert resumed["recovered_from"]["checkpoint_id"] == "checkpoint_001"


def test_world_autopilot_records_task_progress_pause_resume_and_checkpoint_replay(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    report = run_world_autopilot(
        "autopilot-story",
        seed_event="赵轩拒绝主线召唤，沈冰月把风鸣铃藏入旧祠。",
        objective_type="awakening",
        round_limit=3,
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="awake_branch",
    )
    task = report["task"]

    assert task["task_id"]
    assert task["status"] == "completed"
    assert report["progress"]["current_round"] == report["rounds_completed"]
    assert report["progress"]["percent"] == 100
    assert report["overnight_report"]["what_happened"]
    assert report["overnight_report"]["who_remembered_what"]
    assert report["overnight_report"]["where_to_continue"]
    assert report["stop_reason"] in {"character_awareness_detected", "round_limit_reached"}

    loaded = world_autopilot.get_world_autopilot_task(
        "autopilot-story",
        task["task_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="awake_branch",
    )
    assert loaded["task_id"] == task["task_id"]
    assert loaded["latest_report_run_id"] == report["run_id"]

    paused = world_autopilot.pause_world_autopilot_task(
        "autopilot-story",
        task["task_id"],
        projects_dir=tmp_path,
        worldline_id="awake_branch",
    )
    assert paused["status"] == "paused"
    resumed = world_autopilot.resume_world_autopilot_task(
        "autopilot-story",
        task["task_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="awake_branch",
    )
    assert resumed["status"] in {"completed", "running"}

    replay = world_autopilot.replay_world_autopilot_checkpoint(
        report["run_id"],
        checkpoint_id="checkpoint_002",
        outputs_dir=outputs_dir,
    )
    assert replay["checkpoint"]["round_index"] == 2
    assert replay["replay"]["sandbox_run_id"]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _post(port: int, path: str, body: dict) -> tuple[int, dict]:
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_world_autopilot_http_statuses(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "autopilot-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _post(
            port,
            "/api/stories/autopilot-http/world-autopilot/run",
            {"seed_event": "老皇帝驾崩。", "round_limit": 2},
        )
        assert status == 200
        assert body["rounds_completed"] == 2
        assert body["artifact"] == "autopilot_report.json"
        task_id = body["task"]["task_id"]

        task_status, task = _get(
            port,
            f"/api/stories/autopilot-http/worldlines/main/world-autopilot/tasks/{task_id}",
        )
        assert task_status == 200
        assert task["latest_report_run_id"] == body["run_id"]

        pause_status, pause = _post(
            port,
            f"/api/stories/autopilot-http/worldlines/main/world-autopilot/tasks/{task_id}/pause",
            {},
        )
        assert pause_status == 200
        assert pause["status"] == "paused"

        resume_status, resume = _post(
            port,
            f"/api/stories/autopilot-http/worldlines/main/world-autopilot/tasks/{task_id}/resume",
            {},
        )
        assert resume_status == 200
        assert resume["status"] in {"running", "completed"}

        replay_status, replay = _get(
            port,
            f"/api/world-autopilot-runs/{body['run_id']}/checkpoints/checkpoint_001",
        )
        assert replay_status == 200
        assert replay["checkpoint"]["round_index"] == 1

        bad_status, bad = _post(
            port,
            "/api/stories/..%2Fbad/world-autopilot/run",
            {"seed_event": "老皇帝驾崩。"},
        )
        assert bad_status == 400
        assert bad["error"] == "invalid slug"

        empty_status, empty = _post(
            port,
            "/api/stories/autopilot-http/world-autopilot/run",
            {"seed_event": ""},
        )
        assert empty_status == 400
        assert "seed_event" in empty["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()

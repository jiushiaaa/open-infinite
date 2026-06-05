"""Worldline dossier API for independent worldline and checkpoint pages."""

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
from living_novel_engine.service.world_autopilot import run_world_autopilot
from living_novel_engine.service.worldline_dossier import get_worldline_dossier


def _chapters() -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 世界线档案\n"
                "赵轩追查风鸣铃，沈冰月守住苍澜派规矩，韩无归逼问旧案。"
            ),
        }
        for idx in range(1, 7)
    ]


def _make_project(tmp_path, slug: str = "dossier-story") -> None:
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    generate_tianming_book(slug, projects_dir=tmp_path)
    confirm_tianming_book(slug, confirm=True, projects_dir=tmp_path)


def test_worldline_dossier_collects_state_tasks_checkpoints_and_next_actions(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    report = run_world_autopilot(
        "dossier-story",
        seed_event="读者强行让赵轩放弃主线，沈冰月听见高维低语。",
        objective_type="awakening",
        round_limit=2,
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="awake_branch",
    )

    dossier = get_worldline_dossier(
        "dossier-story",
        worldline_id="awake_branch",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )

    assert dossier["version"] == "worldline-dossier-v1"
    assert dossier["story_slug"] == "dossier-story"
    assert dossier["worldline_id"] == "awake_branch"
    assert dossier["worldline_state"]["current_worldline"] == "awake_branch"
    assert dossier["tianming_audit"]["root_tianming_mutated"] is False
    assert dossier["tianming_audit"]["audit_status"]
    assert dossier["worldline_state"]["consequence_state"]["status"] == "active"
    assert dossier["task_count"] == 1
    assert dossier["tasks"][0]["latest_report_run_id"] == report["run_id"]
    assert dossier["checkpoint_count"] == 2
    assert dossier["checkpoints"][0]["run_id"] == report["run_id"]
    assert dossier["checkpoints"][0]["checkpoint_id"] == "checkpoint_002"
    assert {row["checkpoint_id"] for row in dossier["checkpoints"]} == {
        "checkpoint_001",
        "checkpoint_002",
    }
    assert dossier["checkpoints"][0]["consequence_state"]["domains"]["location"]["current"]
    assert dossier["next_actions"][0]["action"] == "continue_sandbox"
    assert any(item["action"] == "replay_checkpoint" for item in dossier["next_actions"])


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


def test_worldline_dossier_http_statuses(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "dossier-http")
    run_world_autopilot(
        "dossier-http",
        seed_event="归云斋分支进入世界自演。",
        round_limit=1,
        projects_dir=tmp_path,
        outputs_dir=tmp_path / "_outputs",
        worldline_id="branch_http",
    )
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _get(
            port,
            "/api/stories/dossier-http/worldlines/branch_http/dossier",
        )
        assert status == 200
        assert body["worldline_id"] == "branch_http"
        assert body["checkpoint_count"] == 1

        bad_status, bad = _get(
            port,
            "/api/stories/dossier-http/worldlines/..%2Fbad/dossier",
        )
        assert bad_status == 400
        assert bad["error"] == "invalid slug or worldline id"

        missing_status, missing = _get(
            port,
            "/api/stories/no-such-story/worldlines/main/dossier",
        )
        assert missing_status == 404
        assert "不存在" in missing["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()

"""World Sandbox Loop v1: deterministic sandbox round artifact and API."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import import_novel_from_payload
from living_novel_engine.service.world_sandbox import (
    WorldSandboxRequestError,
    get_character_subjective_memory,
    get_sandbox_run,
    run_sandbox_round,
)


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 世界沙盘\n"
                f"赵轩在归云斋听见第 {idx} 次边境急报，沈冰月记录朝堂风向，"
                "林晚舟暗中追查失踪的钥匙。"
            ),
        }
        for idx in range(1, n + 1)
    ]


def _make_project(tmp_path, slug: str = "sandbox-story"):
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    return tmp_path / slug


def test_run_sandbox_round_writes_round_artifact_and_world_delta(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    report = run_sandbox_round(
        "sandbox-story",
        major_event="老皇帝驾崩，边境军报同时传入归云斋。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )

    run_dir = outputs_dir / report["run_id"]
    rounds_path = run_dir / "sandbox_rounds.jsonl"
    rows = [
        json.loads(line)
        for line in rounds_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert report["version"] == "world-sandbox-round-v1"
    assert report["story_slug"] == "sandbox-story"
    assert report["round_count"] == 1
    assert report["summary"]["character_action_count"] >= 3
    assert report["summary"]["writes_artifacts"] is True
    assert report["artifacts"]["sandbox_rounds"] == "sandbox_rounds.jsonl"
    assert rounds_path.exists()
    assert len(rows) == 1
    assert rows[0]["major_event"] == "老皇帝驾崩，边境军报同时传入归云斋。"
    assert len(rows[0]["character_actions"]) >= 3
    assert all(action["intent"] for action in rows[0]["character_actions"])
    assert all(action["action"] for action in rows[0]["character_actions"])
    assert all(action["reason"] for action in rows[0]["character_actions"])
    assert rows[0]["conflicts"]
    assert rows[0]["information_flow"]
    assert rows[0]["world_state_delta"]["status"] == "changed"

    loaded = get_sandbox_run(report["run_id"], outputs_dir=outputs_dir)
    assert loaded["run_id"] == report["run_id"]
    assert loaded["rounds"][0]["round_index"] == 1


def test_sandbox_round_writes_and_reuses_subjective_memory(tmp_path):
    project_dir = _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    first = run_sandbox_round(
        "sandbox-story",
        major_event="老皇帝驾崩，边境军报同时传入归云斋。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    first_action = first["rounds"][0]["character_actions"][0]
    character_id = first_action["character_id"]
    memory_path = (
        project_dir
        / "worldlines"
        / "main"
        / "characters"
        / character_id
        / "subjective_memory.jsonl"
    )
    rows = [
        json.loads(line)
        for line in memory_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert first["summary"]["subjective_memory_entries_written"] >= 3
    assert first["artifacts"]["subjective_memory_delta"] == "subjective_memory_delta.json"
    assert rows[0]["character_id"] == character_id
    assert rows[0]["saw"]
    assert rows[0]["did"]
    assert rows[0]["new_belief"]
    assert rows[0]["emotion_delta"]
    assert rows[0]["trust_delta"]
    assert rows[0]["anomaly_delta"]

    second = run_sandbox_round(
        "sandbox-story",
        major_event="归云斋外突然出现一封匿名密信。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    second_action = next(
        action
        for action in second["rounds"][0]["character_actions"]
        if action["character_id"] == character_id
    )

    assert second_action["previous_subjective_memory"]
    assert rows[0]["new_belief"] in second_action["previous_subjective_memory"]

    memory_report = get_character_subjective_memory(
        "sandbox-story",
        character_id,
        projects_dir=tmp_path,
    )
    assert memory_report["character_id"] == character_id
    assert memory_report["entry_count"] == 2
    assert memory_report["entries"][0]["source_run_id"] == first["run_id"]


def test_run_sandbox_round_validates_inputs(tmp_path):
    _make_project(tmp_path)

    with pytest.raises(WorldSandboxRequestError):
        run_sandbox_round(
            "sandbox-story",
            major_event="",
            projects_dir=tmp_path,
            outputs_dir=tmp_path / "_outputs",
        )

    with pytest.raises(FileNotFoundError):
        run_sandbox_round(
            "missing-story",
            major_event="老皇帝驾崩。",
            projects_dir=tmp_path,
            outputs_dir=tmp_path / "_outputs",
        )


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "sandbox-http")
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
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


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


def test_world_sandbox_http_run_and_read_statuses(running_server):
    port = running_server

    status, body = _post(
        port,
        "/api/stories/sandbox-http/sandbox/run",
        {"major_event": "老皇帝驾崩，三方势力同时试探。"},
    )
    assert status == 200
    assert body["version"] == "world-sandbox-round-v1"
    assert body["summary"]["character_action_count"] >= 3

    detail_status, detail = _get(port, f"/api/sandbox-runs/{body['run_id']}")
    assert detail_status == 200
    assert detail["run_id"] == body["run_id"]
    assert len(detail["rounds"][0]["character_actions"]) >= 3
    character_id = detail["rounds"][0]["character_actions"][0]["character_id"]

    memory_status, memory = _get(
        port,
        f"/api/stories/sandbox-http/worldlines/main/characters/{character_id}/subjective-memory",
    )
    assert memory_status == 200
    assert memory["character_id"] == character_id
    assert memory["entry_count"] == 1
    assert memory["entries"][0]["saw"]

    bad_status, bad = _post(
        port,
        "/api/stories/..%2Fbad/sandbox/run",
        {"major_event": "老皇帝驾崩。"},
    )
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    missing_status, _missing = _post(
        port,
        "/api/stories/ghost/sandbox/run",
        {"major_event": "老皇帝驾崩。"},
    )
    assert missing_status == 404

    bad_run_status, bad_run = _get(port, "/api/sandbox-runs/..%2Fbad")
    assert bad_run_status == 400
    assert bad_run["error"] == "invalid run_id"

    bad_memory_status, bad_memory = _get(
        port,
        "/api/stories/sandbox-http/worldlines/main/characters/..%2Fbad/subjective-memory",
    )
    assert bad_memory_status == 400
    assert bad_memory["error"] == "invalid slug, worldline, or character id"

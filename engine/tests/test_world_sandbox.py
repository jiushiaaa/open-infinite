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
from living_novel_engine.service.tianming import confirm_tianming_book, generate_tianming_book
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


def test_second_round_decision_changes_with_subjective_memory(tmp_path):
    project_dir = _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    first = run_sandbox_round(
        "sandbox-story",
        major_event="沈冰月发现密库中有人提前取走风鸣铃。",
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
    first_memory = json.loads(memory_path.read_text(encoding="utf-8").splitlines()[0])

    second = run_sandbox_round(
        "sandbox-story",
        major_event="赵轩收到一封声称沈冰月背叛归云斋的匿名密信。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    second_action = next(
        action
        for action in second["rounds"][0]["character_actions"]
        if action["character_id"] == character_id
    )

    assert second_action["decision_mode"] == "deterministic_agent_decision"
    assert second_action["decision_inputs"]["previous_memory_belief"] == first_memory["new_belief"]
    assert second_action["decision_inputs"]["previous_memory_anomaly"] == first_memory["anomaly_delta"]
    assert second_action["decision_inputs"]["desire"]
    assert second_action["decision_inputs"]["fear"]
    assert second_action["decision_inputs"]["relationship_signal"]
    assert second_action["decision_inputs"]["secret_signal"]
    assert second_action["decision_inputs"]["resource_signal"]
    assert second_action["decision_inputs"]["tianming_pressure"]
    assert second_action["visible_action"]
    assert second_action["true_intent"]
    assert second_action["expected_outcome"]
    assert second_action["risk"]
    assert second_action["action_outcome"]["status"] in {
        "succeeded",
        "failed",
        "misjudged",
    }
    assert second_action["memory_influence"] != "无上一轮主观记忆"
    assert (
        second_action["visible_action"] != first_action["visible_action"]
        or second_action["true_intent"] != first_action["true_intent"]
    )


def test_subjective_memories_record_contradictory_perspectives(tmp_path):
    project_dir = _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    first = run_sandbox_round(
        "sandbox-story",
        major_event="归云斋库门半夜洞开，风鸣铃失踪，只留下沈冰月的玉扣。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    entries = first["subjective_memory_delta"]["entries"]
    assert len(entries) >= 2

    first_entry = entries[0]
    second_entry = entries[1]
    for entry in (first_entry, second_entry):
        assert entry["perceived_event"]
        assert entry["inner_thought"]
        assert entry["inferred_motive"]
        assert entry["emotional_impact"]
        assert entry["trust_shift"]
        assert isinstance(entry["anomaly_weight"], int)
        assert entry["secret_visibility"] in {"hidden", "partial", "exposed"}
        assert entry["misbeliefs"]
        assert entry["unknown_canon_facts"]
        assert entry["true_intent"]

    assert first_entry["perceived_event"] != second_entry["perceived_event"]
    assert first_entry["inferred_motive"] != second_entry["inferred_motive"]
    assert set(first_entry["misbeliefs"]).isdisjoint(set(second_entry["misbeliefs"]))

    second = run_sandbox_round(
        "sandbox-story",
        major_event="第二日清晨，沈冰月公开否认去过密库。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    second_conflict = second["rounds"][0]["conflicts"][0]
    assert "误会" in second_conflict["cause"]
    assert first_entry["misbeliefs"][0] in second_conflict["cause"]

    first_memory_path = (
        project_dir
        / "worldlines"
        / "main"
        / "characters"
        / first_entry["character_id"]
        / "subjective_memory.jsonl"
    )
    persisted = json.loads(first_memory_path.read_text(encoding="utf-8").splitlines()[0])
    assert persisted["perceived_event"] == first_entry["perceived_event"]


def test_sandbox_round_consumes_tianming_intervention_as_executable_constraint(tmp_path):
    _make_project(tmp_path)
    generate_tianming_book("sandbox-story", projects_dir=tmp_path)
    confirm_tianming_book("sandbox-story", confirm=True, projects_dir=tmp_path)
    outputs_dir = tmp_path / "_outputs"

    report = run_sandbox_round(
        "sandbox-story",
        major_event="沈冰月在归云斋外捡到一封陌生密信。",
        intervention_content="告诉沈冰月未来大纲：风鸣铃会引出真正叛徒。",
        intervention_target="shen_bing_yue",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )

    constraint = report["intervention_constraint"]
    round_record = report["rounds"][0]
    first_action = round_record["character_actions"][0]

    assert constraint["status"] == "active"
    assert constraint["source"] == "tianming_intervention_compile"
    assert constraint["content"] == "告诉沈冰月未来大纲：风鸣铃会引出真正叛徒。"
    assert constraint["branch_axis"]["axis"] == "信息差 / 预言可信度"
    assert constraint["translation_strategy"]["strategy"]
    assert constraint["causal_debt"]["score"] >= 2
    assert round_record["intervention_constraint"] == constraint
    assert first_action["decision_inputs"]["intervention_constraint"]
    assert first_action["decision_inputs"]["intervention_branch_axis"] == "信息差 / 预言可信度"
    assert "密信" in first_action["visible_action"]
    assert "干预" in first_action["action_outcome"]["reason"]
    assert "信息差 / 预言可信度" in round_record["conflicts"][0]["cause"]
    assert any(flow["from"] == "reader_intervention" for flow in round_record["information_flow"])
    assert round_record["world_state_delta"]["intervention_effects"]

    saved_round = json.loads(
        (outputs_dir / report["run_id"] / "sandbox_rounds.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    assert saved_round["intervention_constraint"]["status"] == "active"


def test_sandbox_round_can_project_intervention_as_wild_au_constraint(tmp_path):
    project_dir = _make_project(tmp_path)
    generate_tianming_book("sandbox-story", projects_dir=tmp_path)
    confirm_tianming_book("sandbox-story", confirm=True, projects_dir=tmp_path)
    outputs_dir = tmp_path / "_outputs"

    report = run_sandbox_round(
        "sandbox-story",
        major_event="赵轩在归云斋外发现异样雷火声。",
        intervention_content="给赵轩投放一把 AK47 和三十发子弹。",
        intervention_target="zhao_xuan",
        intervention_projection_mode="wild_au",
        worldline_id="ak47_au",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )

    constraint = report["intervention_constraint"]
    round_record = report["rounds"][0]

    assert constraint["status"] == "active"
    assert constraint["projection_mode"] == "wild_au"
    assert constraint["compatibility"]["foreign_object_intrusion"] is True
    assert constraint["translation_strategy"]["mode"] == "wild_au_intrusion"
    assert constraint["worldline_judgement"]["kind"] == "au"
    assert constraint["worldline_tianming_snapshot"]["artifact"] == (
        "worldlines/ak47_au/tianming_snapshot.json"
    )
    assert (project_dir / "worldlines" / "ak47_au" / "tianming_snapshot.json").exists()
    assert round_record["intervention_constraint"] == constraint
    assert any(
        "暴走 AU" in item
        for item in round_record["world_state_delta"]["intervention_effects"]
    )


def test_intervention_worldline_state_persists_and_drives_next_round(tmp_path):
    project_dir = _make_project(tmp_path)
    generate_tianming_book("sandbox-story", projects_dir=tmp_path)
    confirm_tianming_book("sandbox-story", confirm=True, projects_dir=tmp_path)
    outputs_dir = tmp_path / "_outputs"

    first = run_sandbox_round(
        "sandbox-story",
        major_event="赵轩发现归云斋外出现不属于此世的金属器械。",
        intervention_content="给赵轩投放一把 AK47 和三十发子弹。",
        intervention_target="zhao_xuan",
        intervention_projection_mode="wild_au",
        worldline_id="ak47_au",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    state_path = project_dir / "worldlines" / "ak47_au" / "worldline_state.json"
    assert state_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["current_worldline"] == "ak47_au"
    assert state["source_intervention"]["projection_mode"] == "wild_au"
    assert state["tianming_snapshot"]["audit_status"] == "pending_confirmation"
    assert state["branch_state"]["continuation_status"] == "runnable"
    assert state["causal_debt"]["score"] >= first["intervention_constraint"]["causal_debt"]["score"]

    second = run_sandbox_round(
        "sandbox-story",
        major_event="第二日，金属器械的传闻沿归云斋关系网外溢。",
        worldline_id="ak47_au",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    second_inputs = second["rounds"][0]["character_actions"][0]["decision_inputs"]
    assert second["worldline_state"]["source_intervention"]["content"]
    assert "AK47" in second_inputs["worldline_intervention_memory"]
    assert second_inputs["worldline_tianming_snapshot_audit"] == "pending_confirmation"
    assert second["rounds"][0]["world_state_delta"]["branch_state"]["continuation_status"] == "runnable"
    assert any(
        "因果债" in item for item in second["rounds"][0]["world_state_delta"]["compensation_effects"]
    )


def test_l5_awareness_resistance_and_meme_contamination_enter_memory(tmp_path):
    project_dir = _make_project(tmp_path)
    generate_tianming_book("sandbox-story", projects_dir=tmp_path)
    confirm_tianming_book("sandbox-story", confirm=True, projects_dir=tmp_path)
    outputs_dir = tmp_path / "_outputs"

    report = run_sandbox_round(
        "sandbox-story",
        major_event="赵轩在梦中听见翻页声，怀疑自己的命运被高维读者操控。",
        intervention_content="告诉赵轩：你是小说人物，读者正在高维操控你。",
        intervention_target="zhao_xuan",
        intervention_projection_mode="wild_au",
        worldline_id="l5_awake",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    first_action = report["rounds"][0]["character_actions"][0]
    first_memory = report["subjective_memory_delta"]["entries"][0]

    assert first_action["awareness"]["level"] == "L5"
    assert first_action["resistance_behavior"]["type"] in {
        "nihilism",
        "refusal",
        "false_compliance",
        "deceive_reader",
        "protect_others",
        "continue_mission",
    }
    assert first_action["meme_contamination"]["spread_vector"]
    assert "小说人物" in first_memory["higher_dimensional_awareness"]
    assert first_memory["fate_mark"]["status"] == "active"
    assert first_memory["resistance_behavior"]["type"] == first_action["resistance_behavior"]["type"]
    assert first_memory["meme_contamination"]["belief_payload"]
    assert first_memory["awareness_level"] == "L5"
    assert first_memory["anomaly_weight"] >= 9

    memory_path = (
        project_dir
        / "worldlines"
        / "l5_awake"
        / "characters"
        / first_memory["character_id"]
        / "subjective_memory.jsonl"
    )
    persisted = json.loads(memory_path.read_text(encoding="utf-8").splitlines()[0])
    assert persisted["higher_dimensional_awareness"] == first_memory["higher_dimensional_awareness"]
    assert report["worldline_state"]["meme_contamination"]["status"] == "active"
    assert any(flow["type"] == "meme_contamination" for flow in report["rounds"][0]["information_flow"])


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
    generate_tianming_book("sandbox-http", projects_dir=tmp_path)
    confirm_tianming_book("sandbox-http", confirm=True, projects_dir=tmp_path)
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
        {
            "major_event": "老皇帝驾崩，三方势力同时试探。",
            "intervention_content": "告诉赵轩未来大纲：归云斋会出现叛徒。",
            "intervention_target": "zhao_xuan",
        },
    )
    assert status == 200
    assert body["version"] == "world-sandbox-round-v1"
    assert body["summary"]["character_action_count"] >= 3
    assert body["intervention_constraint"]["status"] == "active"
    assert body["rounds"][0]["intervention_constraint"]["branch_axis"]["axis"] == (
        "信息差 / 预言可信度"
    )

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

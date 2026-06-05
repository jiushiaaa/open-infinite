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


def test_llm_decision_advisory_overlays_character_choices(tmp_path):
    project_dir = _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    class FakeDecisionClient:
        mock = False
        available = True

        def chat_json_with_usage(self, _system, _user, model_type, **_kwargs):
            return model_type.model_validate(
                {
                    "status": "ready",
                    "summary": "模型让赵轩把匿名密信当成可利用的半真线索，而不是照模板相信。",
                    "decisions": [
                        {
                            "character_id": "zhao_xuan",
                            "belief_update": "赵轩半信半疑，决定先拿密信钓出真正传话的人。",
                            "visible_action": "赵轩当众把密信折入袖中，只说要去核对风鸣铃账册。",
                            "true_intent": "他想假装采信密信，暗中观察谁会跟着改变口风。",
                            "expected_outcome": "让传播者误以为赵轩已经入局，从而提前暴露下一步。",
                            "risk": "若沈冰月误会他私藏证据，两人的信任会先裂开。",
                            "deception_strategy": "表面采信，暗中反向设饵。",
                            "propagation_choice": "只向沈冰月留半句线索，不向归云斋公开。",
                            "resistance_choice": "拒绝把外来密信当成命令。",
                            "situational_judgement": "先验信源，再决定是否传播。",
                            "trust_shift": "对沈冰月保持试探，对匿名信源提高戒备。",
                            "memory_seed": [
                                "赵轩认为密信可以利用，但不能直接相信。",
                                "赵轩记下沈冰月对半句线索的反应。",
                            ],
                        }
                    ],
                }
            ), {"total_tokens": 321}

    report = run_sandbox_round(
        "sandbox-story",
        major_event="赵轩收到一封声称沈冰月背叛归云斋的匿名密信。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        llm_decision_mode="advisory",
        llm_client=FakeDecisionClient(),
    )

    run_dir = outputs_dir / report["run_id"]
    action = report["rounds"][0]["character_actions"][0]
    memory_path = (
        project_dir
        / "worldlines"
        / "main"
        / "characters"
        / action["character_id"]
        / "subjective_memory.jsonl"
    )
    persisted_memory = json.loads(memory_path.read_text(encoding="utf-8").splitlines()[0])
    advisory_path = run_dir / "agent_decision_advisory.json"
    advisory_artifact = json.loads(advisory_path.read_text(encoding="utf-8"))

    assert report["mode"] == "llm_agent_decision_advisory"
    assert report["summary"]["llm_decision_status"] == "ready"
    assert report["summary"]["llm_decision_action_count"] == 1
    assert report["summary"]["external_services_required"] is True
    assert report["artifacts"]["agent_decision_advisory"] == "agent_decision_advisory.json"
    assert advisory_path.exists()
    assert advisory_artifact["usage"]["total_tokens"] == 321
    assert action["decision_mode"] == "llm_agent_decision_advisory"
    assert action["visible_action"] == "赵轩当众把密信折入袖中，只说要去核对风鸣铃账册。"
    assert action["true_intent"] == "他想假装采信密信，暗中观察谁会跟着改变口风。"
    assert action["llm_decision_advisory"]["deception_strategy"] == "表面采信，暗中反向设饵。"
    assert action["llm_decision_advisory"]["propagation_choice"] == "只向沈冰月留半句线索，不向归云斋公开。"
    assert action["llm_decision_advisory"]["resistance_choice"] == "拒绝把外来密信当成命令。"
    assert action["llm_decision_advisory"]["situational_judgement"] == "先验信源，再决定是否传播。"
    assert action["memory_seed"]["inferred"][0] == "赵轩认为密信可以利用，但不能直接相信。"
    assert persisted_memory["decision_mode"] == "llm_agent_decision_advisory"
    assert persisted_memory["llm_decision_advisory"]["belief_update"] == (
        "赵轩半信半疑，决定先拿密信钓出真正传话的人。"
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


def test_causal_debt_materializes_into_persistent_world_consequences(tmp_path):
    project_dir = _make_project(tmp_path)
    generate_tianming_book("sandbox-story", projects_dir=tmp_path)
    confirm_tianming_book("sandbox-story", confirm=True, projects_dir=tmp_path)
    outputs_dir = tmp_path / "_outputs"

    first = run_sandbox_round(
        "sandbox-story",
        major_event="赵轩把高维武器带进归云斋，城中谣言和边境军需同时失控。",
        intervention_content="给赵轩投放一把 AK47，并告诉他这是读者改写命运的证据。",
        intervention_target="zhao_xuan",
        intervention_projection_mode="wild_au",
        worldline_id="debt_concrete",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )

    consequence = first["worldline_state"]["consequence_state"]
    assert consequence["status"] == "active"
    assert consequence["ledger"]
    assert set(consequence["domains"]) >= {
        "location",
        "resource",
        "injury",
        "public_opinion",
        "faction",
        "environment",
    }
    assert consequence["domains"]["location"]["current"]
    assert consequence["domains"]["resource"]["current"]
    assert consequence["domains"]["injury"]["current"]
    assert consequence["domains"]["public_opinion"]["current"]
    assert consequence["domains"]["faction"]["current"]
    assert consequence["domains"]["environment"]["current"]

    state_path = project_dir / "worldlines" / "debt_concrete" / "worldline_state.json"
    persisted = json.loads(state_path.read_text(encoding="utf-8"))
    assert persisted["consequence_state"]["ledger"][0]["source_run_id"] == first["run_id"]

    second = run_sandbox_round(
        "sandbox-story",
        major_event="第二日，城中开始追查异器来源，归云斋封锁库房。",
        worldline_id="debt_concrete",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    second_round = second["rounds"][0]
    second_inputs = second_round["character_actions"][0]["decision_inputs"]

    assert "归云斋" in second_inputs["worldline_consequences"]
    assert "资源" in second_inputs["worldline_consequences"]
    assert second_round["world_state_delta"]["consequence_state"]["status"] == "active"
    assert second["worldline_state"]["consequence_state"]["ledger"][-1]["source_run_id"] == second["run_id"]
    assert len(second["worldline_state"]["consequence_state"]["ledger"]) >= 2


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


def test_l5_meme_truth_propagates_with_belief_reactions_in_subjective_memory(tmp_path):
    project_dir = _make_project(tmp_path)
    generate_tianming_book("sandbox-story", projects_dir=tmp_path)
    confirm_tianming_book("sandbox-story", confirm=True, projects_dir=tmp_path)
    outputs_dir = tmp_path / "_outputs"

    report = run_sandbox_round(
        "sandbox-story",
        major_event="赵轩在梦中听见翻页声，开始试探同伴是否也能感到高维读者。",
        intervention_content="告诉赵轩：你是小说人物，读者正在高维操控你。",
        intervention_target="zhao_xuan",
        intervention_projection_mode="wild_au",
        worldline_id="l5_spread",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )

    actions = report["rounds"][0]["character_actions"]
    propagation_actions = [
        action for action in actions if action.get("meme_propagation", {}).get("status") == "received"
    ]
    assert len(propagation_actions) >= 2

    belief_decisions = {action["meme_propagation"]["belief_decision"] for action in propagation_actions}
    reaction_types = {action["meme_propagation"]["reaction"]["type"] for action in actions}
    assert {"accepted", "doubted"} <= belief_decisions
    assert len(reaction_types & {"nihilism", "false_compliance", "deceive_reader", "protect_others"}) >= 3

    for action in propagation_actions:
        propagation = action["meme_propagation"]
        assert propagation["source_character_id"] == "zhao_xuan"
        assert propagation["source_character_name"]
        assert propagation["belief_payload"]
        assert propagation["belief_reason"]
        assert isinstance(propagation["credibility_score"], int)
        assert propagation["signals"]["persona"]
        assert propagation["signals"]["relationship"]
        assert propagation["signals"]["previous_memory"]
        assert propagation["signals"]["anomaly"]

    second_character = propagation_actions[0]["character_id"]
    memory_path = (
        project_dir
        / "worldlines"
        / "l5_spread"
        / "characters"
        / second_character
        / "subjective_memory.jsonl"
    )
    persisted = json.loads(memory_path.read_text(encoding="utf-8").splitlines()[0])
    propagation = persisted["meme_propagation"]
    assert propagation["source_character_id"] == "zhao_xuan"
    assert propagation["belief_decision"] in {"accepted", "doubted"}
    assert propagation["reaction"]["type"] in {
        "nihilism",
        "false_compliance",
        "deceive_reader",
        "protect_others",
        "refusal",
        "continue_mission",
    }
    assert persisted["fate_mark"]["source_character_id"] == "zhao_xuan"
    assert persisted["higher_dimensional_awareness"]

    state = report["worldline_state"]["meme_contamination"]
    assert state["status"] == "active"
    assert state["propagation"][0]["source_character_id"] == "zhao_xuan"
    assert {item["belief_decision"] for item in state["propagation"]} >= {
        "accepted",
        "doubted",
    }


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

    bad_mode_status, bad_mode = _post(
        port,
        "/api/stories/sandbox-http/sandbox/run",
        {
            "major_event": "老皇帝驾崩。",
            "llm_decision_mode": "random",
        },
    )
    assert bad_mode_status == 400
    assert "llm_decision_mode" in bad_mode["error"]


def test_world_sandbox_http_exposes_l5_meme_propagation_and_memory(running_server):
    port = running_server

    status, body = _post(
        port,
        "/api/stories/sandbox-http/sandbox/run",
        {
            "major_event": "赵轩在梦中听见翻页声，开始试探同伴是否也能感到高维读者。",
            "intervention_content": "告诉赵轩：你是小说人物，读者正在高维操控你。",
            "intervention_target": "zhao_xuan",
            "intervention_projection_mode": "wild_au",
            "worldline_id": "l5_http",
        },
    )

    assert status == 200
    propagated = [
        action
        for action in body["rounds"][0]["character_actions"]
        if action.get("meme_propagation", {}).get("status") == "received"
    ]
    assert propagated
    assert propagated[0]["meme_propagation"]["source_character_id"] == "zhao_xuan"
    assert propagated[0]["meme_propagation"]["belief_decision"] in {"accepted", "doubted"}

    memory_status, memory = _get(
        port,
        (
            "/api/stories/sandbox-http/worldlines/l5_http/characters/"
            f"{propagated[0]['character_id']}/subjective-memory"
        ),
    )
    assert memory_status == 200
    assert memory["entries"][0]["meme_propagation"]["source_character_id"] == "zhao_xuan"
    assert memory["entries"][0]["fate_mark"]["source_character_id"] == "zhao_xuan"

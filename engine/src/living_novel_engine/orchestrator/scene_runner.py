from __future__ import annotations

import copy
import uuid
from typing import Any

from living_novel_engine.agents.character_agent import decide_character_action
from living_novel_engine.agents.narrator import render_chapter, render_summary
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.models import CharacterAgent, Intervention, StoryWorld
from living_novel_engine.models.events import (
    AcceptedEvent,
    SceneRecord,
    SimulationResult,
    StateDelta,
)
from living_novel_engine.orchestrator.state_snapshot import build_state_snapshot
from living_novel_engine.orchestrator.worldline_brancher import BranchSpec


def run_scene(
    world: StoryWorld,
    characters: list[CharacterAgent],
    intervention: Intervention,
    spec: BranchSpec,
    llm: LLMClient,
  *,
    max_rounds: int = 4,
    canon_excerpt: str = "",
) -> SimulationResult:
    chars = copy.deepcopy(characters)
    char_map = {c.id: c for c in chars}
    present = [c for c in chars if c.present_in_scene]

    scene_state: dict[str, Any] = {
        "location": "听雨轩及院外",
        "time": "子时将至",
        "lin_wan_zhou_departed": False,
        "bamboo_grove_triggered": False,
        "conflict_escalated": False,
        "intervention_target": intervention.target,
    }

    all_events: list[AcceptedEvent] = []
    scenes: list[SceneRecord] = []
    termination_reason = "max_rounds"

    branch_intervention = intervention.model_copy(
        update={"worldline_id": spec.branch_id, "branch_seed": spec.branch_seed}
    )

    for round_num in range(1, max_rounds + 1):
        round_actions = []
        for char in present:
            action = decide_character_action(
                char,
                world,
                branch_intervention,
                scene_state,
                round_num,
                spec.branch_seed,
                llm,
                forced_stance=spec.forced_stance if char.id == intervention.target else None,
            )
            round_actions.append(action)
            evt = AcceptedEvent(
                event_id=f"evt_{uuid.uuid4().hex[:10]}",
                chapter=13,
                round_num=round_num,
                event_type=action.action_type,
                subject=char.id,
                payload={
                    "stance": action.stance,
                    "target": action.target,
                    "content": action.content,
                    "thought": action.internal_thought,
                },
                narrative=f"{action.character_name}{action.content}（立场：{action.stance}）",
            )
            all_events.append(evt)

        _apply_actions_to_scene(scene_state, round_actions, char_map)

        scene = SceneRecord(
            round_num=round_num,
            location=str(scene_state.get("location", "")),
            summary=_round_summary(round_actions),
            events=[e for e in all_events if e.round_num == round_num],
        )
        scenes.append(scene)

        if _should_terminate(scene_state, round_num, max_rounds):
            termination_reason = _termination_reason(scene_state)
            break

    result = SimulationResult(
        worldline_id=spec.branch_id,
        branch_seed=spec.branch_seed,
        theme=spec.theme,
        rounds=scenes,
        accepted_events=all_events,
        state_deltas=_collect_state_deltas(char_map, characters),
        scenes=scenes,
        termination_reason=termination_reason,
        final_scene_state=scene_state,
    )
    result.state_snapshot = build_state_snapshot(
        world, characters, char_map, scene_state, spec, result
    )
    result.summary_text = render_summary(world, result, llm)
    result.chapter_text = render_chapter(world, result, canon_excerpt, llm)
    return result


def _apply_actions_to_scene(scene_state: dict, actions, char_map: dict[str, CharacterAgent]) -> None:
    for act in actions:
        char = char_map.get(act.character_id)
        if act.character_id == "lin_wan_zhou":
            if act.stance == "believe" and ("不出" in act.content or "留" in act.content):
                scene_state["lin_wan_zhou_departed"] = False
                if char:
                    char.current_state.emotion = "迟疑后决断"
                    char.current_state.location = "听雨轩廊下"
            elif act.stance == "reject":
                scene_state["lin_wan_zhou_departed"] = True
                scene_state["conflict_escalated"] = True
                if char:
                    char.current_state.emotion = "愠怒"
                    char.current_state.location = "院门外"
            elif act.stance == "doubt":
                scene_state["lin_wan_zhou_departed"] = False
                scene_state["investigating"] = True
                if char:
                    char.current_state.emotion = "警惕"
        if act.character_id == "lin_fan":
            if "玉简" in act.content or "传讯" in act.content:
                scene_state["jade_slip_used"] = True
                if char:
                    char.current_state.emotion = "决绝"
            if "跟" in act.content or "拦" in act.content:
                scene_state["lin_fan_followed"] = True
                scene_state["conflict_escalated"] = True
                if char and char.relationships.get("lin_wan_zhou"):
                    char.relationships["lin_wan_zhou"] = (
                        char.relationships["lin_wan_zhou"] + "（今夜冲突加剧）"
                    )
        if char:
            char.memory.append(f"轮次行动: {act.content[:80]}")


def _round_summary(actions) -> str:
    return "；".join(f"{a.character_name}({a.stance}): {a.content[:40]}" for a in actions)


def _should_terminate(scene_state: dict, round_num: int, max_rounds: int) -> bool:
    if round_num >= max_rounds:
        return True
    if scene_state.get("bamboo_grove_triggered"):
        return True
    if scene_state.get("lin_wan_zhou_departed") and scene_state.get("lin_fan_followed"):
        return True
    if scene_state.get("jade_slip_used") and scene_state.get("investigating"):
        return True
    return False


def _termination_reason(scene_state: dict) -> str:
    if scene_state.get("bamboo_grove_triggered"):
        return "竹林线已触发"
    if scene_state.get("jade_slip_used"):
        return "传讯玉简已使用"
    if scene_state.get("lin_wan_zhou_departed"):
        return "林晚舟仍赴约"
    if scene_state.get("investigating"):
        return "调查拖延成功"
    return "回合耗尽"


def _collect_state_deltas(
    after: dict[str, CharacterAgent],
    before: list[CharacterAgent],
) -> list[StateDelta]:
    deltas: list[StateDelta] = []
    before_map = {c.id: c for c in before}
    for cid, char in after.items():
        prev = before_map.get(cid)
        if prev and len(char.memory) > len(prev.memory):
            deltas.append(
                StateDelta(
                    character_id=cid,
                    field="memory",
                    old_value=len(prev.memory),
                    new_value=len(char.memory),
                )
            )
    return deltas

from __future__ import annotations

import copy
import uuid

from living_novel_engine.agents.character_agent import decide_character_action
from living_novel_engine.agents.narrator import render_chapter
from living_novel_engine.fourth_wall import (
    awareness_narrator_hint,
    mock_fourth_wall_aside,
)
from living_novel_engine.models import CharacterAgent
from living_novel_engine.models.events import (
    AcceptedEvent,
    SceneRecord,
    SimulationResult,
    StateDelta,
)
from living_novel_engine.orchestrator.canon_guard import normalize_canon_text
from living_novel_engine.orchestrator.narrative_constraints import summary_from_snapshot
from living_novel_engine.orchestrator.runners.base import SceneRequest, SceneRunner
from living_novel_engine.orchestrator.scene_rules import (
    apply_character_action_to_scene,
    ensure_bamboo_arrival_event,
    is_fan_warning_action,
    is_jade_slip_action,
    lin_wan_zhou_jade_resource_drift,
    reconcile_linear_flags_from_events,
    rewrite_lwz_jade_resource_drift,
    substitute_fan_warning_exhausted,
    substitute_jade_exhausted_action,
    sync_locations_from_scene_flags,
)
from living_novel_engine.orchestrator.state_snapshot import build_state_snapshot


class LightweightSceneRunner(SceneRunner):
    """单 prompt 多角色轮询（Phase 0 → v0.5 的既有实现）。"""

    name = "lightweight"

    def run(self, request: SceneRequest) -> SimulationResult:
        return run_lightweight(request)


def run_lightweight(request: SceneRequest) -> SimulationResult:
    world = request.world
    characters = request.characters
    intervention = request.intervention
    spec = request.spec
    llm = request.llm
    max_rounds = request.max_rounds
    canon_excerpt = request.canon_excerpt
    prologue = request.prologue
    canon_opening = request.canon_opening
    canon_chapter = request.canon_chapter
    seed_scene_state = request.seed_scene_state
    seed_characters = request.seed_characters
    chapter_number = request.chapter_number
    source_type = request.source_type
    retrieved_context = request.retrieved_context
    ledger = request.ledger

    chars = copy.deepcopy(seed_characters if seed_characters is not None else characters)
    char_map = {c.id: c for c in chars}
    present = [c for c in chars if c.present_in_scene]

    fw_active = ledger is not None and ledger.enabled
    awareness_map = ledger.awareness if (ledger is not None) else {}

    is_builtin = source_type == "builtin_sample"

    intervention_target = intervention.target if intervention else ""
    if seed_scene_state is not None:
        scene_state = {**seed_scene_state, "branch_seed": spec.branch_seed}
        if intervention:
            scene_state["intervention_target"] = intervention_target
    else:
        scene_state = {
            "location": world.scene_description.split("\n")[0][:30] if world.scene_description else "场景",
            "time": "当前",
            "intervention_target": intervention_target,
            "branch_seed": spec.branch_seed,
        }
        if is_builtin:
            scene_state.update({
                "location": "听雨轩及院外",
                "time": "子时将至",
                "lin_wan_zhou_departed": False,
                "bamboo_grove_triggered": False,
                "conflict_escalated": False,
            })

    all_events: list[AcceptedEvent] = []
    scenes: list[SceneRecord] = []
    termination_reason = "max_rounds"

    branch_intervention = (
        intervention.model_copy(
            update={"worldline_id": spec.branch_id, "branch_seed": spec.branch_seed}
        )
        if intervention
        else None
    )

    for round_num in range(1, max_rounds + 1):
        round_actions = []
        for char in present:
            forced = None
            if intervention and spec.forced_stance and char.id == intervention.target:
                forced = spec.forced_stance
            action = decide_character_action(
                char,
                world,
                branch_intervention,
                scene_state,
                round_num,
                spec.branch_seed,
                llm,
                forced_stance=forced,
                branch_spec=spec,
                source_type=source_type,
                retrieved_context=retrieved_context,
                awareness=awareness_map.get(char.id) if fw_active else None,
            )
            if is_builtin and char.id == "lin_fan":
                if scene_state.get("jade_slip_used") and is_jade_slip_action(action):
                    action = substitute_jade_exhausted_action(action)
                elif scene_state.get("fan_warning_delivered") and is_fan_warning_action(
                    action
                ):
                    action = substitute_fan_warning_exhausted(action)
            if is_builtin and char.id == "lin_wan_zhou" and lin_wan_zhou_jade_resource_drift(
                action, scene_state
            ):
                action = rewrite_lwz_jade_resource_drift(action, scene_state)
            jade_used = bool(scene_state.get("jade_slip_used")) if is_builtin else False
            action = action.model_copy(
                update={
                    "content": normalize_canon_text(
                        action.content, jade_slip_used=jade_used
                    ) if is_builtin else action.content,
                    "internal_thought": normalize_canon_text(
                        action.internal_thought, jade_slip_used=jade_used
                    ) if is_builtin else action.internal_thought,
                }
            )
            round_actions.append(action)
            narrative = normalize_canon_text(
                f"{action.character_name}{action.content}（立场：{action.stance}）",
                jade_slip_used=jade_used,
            )
            evt = AcceptedEvent(
                event_id=f"evt_{uuid.uuid4().hex[:10]}",
                chapter=chapter_number,
                round_num=round_num,
                event_type=action.action_type,
                subject=char.id,
                payload={
                    "stance": action.stance,
                    "target": action.target,
                    "content": action.content,
                    "thought": action.internal_thought,
                },
                narrative=narrative,
            )
            all_events.append(evt)

        for act in round_actions:
            if is_builtin:
                apply_character_action_to_scene(scene_state, act, char_map, spec)
            else:
                if char_map.get(act.character_id):
                    char_map[act.character_id].memory.append(f"轮次行动: {act.content[:80]}")

        scene = SceneRecord(
            round_num=round_num,
            location=str(scene_state.get("location", "")),
            summary=_round_summary(round_actions),
            events=[e for e in all_events if e.round_num == round_num],
        )
        scenes.append(scene)

        if _should_terminate(scene_state, round_num, max_rounds, is_builtin=is_builtin):
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
        runner_name=LightweightSceneRunner.name,
    )
    if is_builtin and spec.branch_seed == "linear":
        reconcile_linear_flags_from_events(scene_state, all_events, char_map)

    if is_builtin:
        ensure_bamboo_arrival_event(
            scene_state,
            all_events,
            char_map,
            chapter_number=chapter_number,
        )
        sync_locations_from_scene_flags(scene_state, char_map)
    result.final_scene_state = scene_state
    result.accepted_events = all_events

    present_ids = [c.id for c in present]
    present_awareness = (
        [awareness_map[cid] for cid in present_ids if cid in awareness_map]
        if fw_active
        else []
    )
    fw_hint = awareness_narrator_hint(present_awareness) if fw_active else ""
    fw_mock_aside = mock_fourth_wall_aside(present_awareness) if fw_active else ""

    result.state_snapshot = build_state_snapshot(
        world, characters, char_map, scene_state, spec, result,
        ledger=ledger if fw_active else None,
    )
    result.summary_text = summary_from_snapshot(
        world.display_name or world.title, result
    )
    context = canon_excerpt or canon_chapter
    result.chapter_text = render_chapter(
        world,
        result,
        context,
        llm,
        prologue=prologue,
        canon_opening=canon_opening,
        canon_chapter=canon_chapter or canon_excerpt,
        state_snapshot=result.state_snapshot,
        chapter_number=chapter_number,
        retrieved_context=retrieved_context,
        fourth_wall_hint=fw_hint,
        fourth_wall_mock_aside=fw_mock_aside,
    )
    return result


def _round_summary(actions) -> str:
    return "；".join(f"{a.character_name}({a.stance}): {a.content[:40]}" for a in actions)


def _should_terminate(scene_state: dict, round_num: int, max_rounds: int, *, is_builtin: bool = True) -> bool:
    if round_num >= max_rounds:
        return True
    if not is_builtin:
        return False
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

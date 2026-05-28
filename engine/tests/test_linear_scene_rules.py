from __future__ import annotations

from living_novel_engine.models.events import CharacterAction
from living_novel_engine.models.events import AcceptedEvent
from living_novel_engine.orchestrator.narrative_constraints import (
    strip_debug_variable_leak,
    validate_debug_variable_leak,
)
from living_novel_engine.orchestrator.scene_rules import (
    action_implies_physical_departure,
    action_implies_stay_or_investigate,
    apply_character_action_to_scene,
    content_implies_departure,
    reconcile_linear_flags_from_events,
)
from living_novel_engine.orchestrator.worldline_brancher import build_continuation_spec


def test_mention_bamboo_direction_does_not_imply_departure():
    content = "她望向城外竹林的方向，收回迈出的脚步，转身回到听雨轩。"
    assert content_implies_departure(content)
    act = CharacterAction(
        character_id="lin_wan_zhou",
        character_name="林晚舟",
        stance="doubt",
        action_type="investigate",
        target="听雨轩",
        content=content,
        internal_thought="",
        intervention_response="doubt",
    )
    assert action_implies_stay_or_investigate(act)
    assert not action_implies_physical_departure(act)


def test_linear_investigate_clears_false_departure_flags():
    spec = build_continuation_spec("doubt", "branch_a")
    scene_state = {
        "branch_seed": "linear",
        "lin_wan_zhou_departed": True,
        "bamboo_grove_triggered": True,
        "investigating": False,
    }
    act = CharacterAction(
        character_id="lin_wan_zhou",
        character_name="林晚舟",
        stance="doubt",
        action_type="investigate",
        target="听雨轩",
        content="收回迈出的脚步，转身回到听雨轩，墨色竹简被她重新收回袖中。",
        internal_thought="望向城外竹林的方向",
        intervention_response="doubt",
    )
    apply_character_action_to_scene(scene_state, act, {}, spec)
    assert scene_state["lin_wan_zhou_departed"] is False
    assert scene_state["bamboo_grove_triggered"] is False
    assert scene_state["investigating"] is True


def test_reconcile_linear_from_last_event():
    spec = build_continuation_spec("doubt", "branch_a")
    scene_state = {
        "branch_seed": "linear",
        "lin_wan_zhou_departed": True,
        "bamboo_grove_triggered": True,
    }
    evt = AcceptedEvent(
        event_id="e1",
        chapter=14,
        round_num=1,
        event_type="investigate",
        subject="lin_wan_zhou",
        payload={
            "stance": "doubt",
            "content": "收回脚步，回屋屏息，感知城主府方向灵力异动。",
            "thought": "",
        },
        narrative="",
    )
    reconcile_linear_flags_from_events(scene_state, [evt], {})
    assert scene_state["lin_wan_zhou_departed"] is False
    assert scene_state["bamboo_grove_triggered"] is False


def test_validate_and_strip_debug_variable_leak():
    bad = "她停下脚步。`lin_wan_zhou_departed = True`。雨幕中。"
    assert validate_debug_variable_leak(bad)
    cleaned = strip_debug_variable_leak(bad)
    assert not validate_debug_variable_leak(cleaned)
    assert "lin_wan_zhou_departed" not in cleaned

"""v0.6.5 trace 质量校验器测试（`trace_quality.validate_and_repair_trace`）。"""

from __future__ import annotations

from types import SimpleNamespace

from living_novel_engine.orchestrator.runners.protocol import (
    AgentIntent,
    AgentTurnPlan,
    DelayedAction,
    Misunderstanding,
    MultiAgentTrace,
    PrivateKnowledge,
)
from living_novel_engine.orchestrator.runners.trace_quality import (
    validate_and_repair_trace,
)


def _char(cid: str, present: bool = True):
    return SimpleNamespace(id=cid, present_in_scene=present)


def _request(*, chars=None, target="lin_wan_zhou", content="今晚不要去城外竹林"):
    chars = chars if chars is not None else [_char("lin_wan_zhou"), _char("lin_fan")]
    intervention = (
        SimpleNamespace(target=target, content=content) if target is not None else None
    )
    return SimpleNamespace(
        spec=SimpleNamespace(branch_id="branch_a", branch_seed="doubt"),
        intervention=intervention,
        characters=chars,
        seed_characters=None,
    )


def _plan(actor: str, **kw) -> AgentTurnPlan:
    return AgentTurnPlan(round_num=kw.pop("round_num", 1), actor_id=actor, **kw)


def test_empty_turn_plans_is_hard_fail():
    trace = MultiAgentTrace()
    vr = validate_and_repair_trace(trace, _request())
    assert vr.status == "hard_fail"


def test_fills_worldline_and_seed():
    trace = MultiAgentTrace(turn_plans=[_plan("lin_wan_zhou")])
    validate_and_repair_trace(trace, _request())
    assert trace.worldline_id == "branch_a"
    assert trace.branch_seed == "doubt"


def test_round_normalization():
    trace = MultiAgentTrace(
        turn_plans=[
            AgentTurnPlan(
                round_num=0,
                actor_id="lin_wan_zhou",
                delayed_actions=[
                    DelayedAction(actor_id="lin_wan_zhou", created_round=0, due_round=0)
                ],
            )
        ]
    )
    vr = validate_and_repair_trace(trace, _request())
    assert trace.turn_plans[0].round_num == 1
    da = trace.turn_plans[0].delayed_actions[0]
    assert da.created_round == 1
    assert da.due_round == 1
    assert vr.status == "repaired"


def test_secret_intent_forced_private():
    trace = MultiAgentTrace(
        turn_plans=[
            _plan(
                "lin_wan_zhou",
                intents=[
                    AgentIntent(actor_id="lin_wan_zhou", intent_type="conceal", visibility="public")
                ],
            )
        ]
    )
    vr = validate_and_repair_trace(trace, _request())
    assert trace.turn_plans[0].intents[0].visibility == "private"
    assert vr.status == "repaired"


def test_unrevealed_knowledge_forced_private():
    trace = MultiAgentTrace(
        turn_plans=[_plan("lin_wan_zhou")],
        private_knowledge=[
            PrivateKnowledge(
                fact_id="pk", owner_id="lin_wan_zhou", content="x",
                visibility="public", revealed=False,
            )
        ],
    )
    validate_and_repair_trace(trace, _request())
    assert trace.private_knowledge[0].visibility == "private"


def test_uncorrected_misunderstanding_forced_private():
    trace = MultiAgentTrace(
        turn_plans=[_plan("lin_wan_zhou")],
        misunderstandings=[
            Misunderstanding(holder_id="lin_wan_zhou", visibility="public", corrected=False)
        ],
    )
    validate_and_repair_trace(trace, _request())
    assert trace.misunderstandings[0].visibility == "private"


def test_missing_present_character_warns():
    trace = MultiAgentTrace(turn_plans=[_plan("lin_wan_zhou")])
    vr = validate_and_repair_trace(trace, _request())
    assert any("lin_fan" in w for w in vr.warnings)


def test_intervention_not_in_private_knowledge_warns():
    trace = MultiAgentTrace(turn_plans=[_plan("lin_wan_zhou")])
    vr = validate_and_repair_trace(trace, _request())
    assert any("private_knowledge" in w for w in vr.warnings)


def test_clean_trace_is_ok():
    trace = MultiAgentTrace(
        worldline_id="branch_a",
        branch_seed="doubt",
        turn_plans=[
            _plan("lin_wan_zhou", intents=[AgentIntent(actor_id="lin_wan_zhou", visibility="public")]),
            _plan("lin_fan", intents=[AgentIntent(actor_id="lin_fan", visibility="public")]),
        ],
        private_knowledge=[
            PrivateKnowledge(
                fact_id="pk", owner_id="lin_wan_zhou",
                content="外部低语：今晚不要去城外竹林", revealed=False,
            )
        ],
    )
    vr = validate_and_repair_trace(trace, _request())
    assert vr.status == "ok"
    assert vr.warnings == []

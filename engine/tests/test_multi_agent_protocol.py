from __future__ import annotations

from living_novel_engine.orchestrator.runners.protocol import (
    AgentIntent,
    AgentTurnPlan,
    DelayedAction,
    Misunderstanding,
    MultiAgentTrace,
    PrivateKnowledge,
    RelationshipSignal,
)


# ── 序列化往返 ─────────────────────────────────────────────────


def test_trace_roundtrip_serialization():
    trace = MultiAgentTrace(
        worldline_id="branch_a",
        branch_seed="believe",
        turn_plans=[
            AgentTurnPlan(
                round_num=1,
                actor_id="lin_fan",
                intents=[
                    AgentIntent(
                        actor_id="lin_fan",
                        intent_type="protect",
                        target="lin_wan_zhou",
                        motivation="不愿师姐赴险",
                        description="设法拦下林晚舟",
                        visibility="private",
                        confidence=0.8,
                    )
                ],
                delayed_actions=[
                    DelayedAction(
                        actor_id="lin_fan",
                        action_type="follow",
                        created_round=1,
                        due_round=3,
                    )
                ],
                relationship_signals=[
                    RelationshipSignal(
                        signal_id="sig1",
                        from_id="lin_wan_zhou",
                        to_id="lin_fan",
                        change="trust+",
                        magnitude=0.3,
                    )
                ],
            )
        ],
        private_knowledge=[
            PrivateKnowledge(
                fact_id="pk1",
                owner_id="lin_fan",
                content="竹林是局",
                source="intervention",
            )
        ],
        misunderstandings=[
            Misunderstanding(
                holder_id="lin_wan_zhou",
                about="墨青烟",
                believed="故友相邀",
                reality="设局者",
            )
        ],
    )
    dumped = trace.model_dump()
    restored = MultiAgentTrace.model_validate(dumped)
    assert restored == trace
    assert abs(restored.turn_plans[0].intents[0].confidence - 0.8) < 1e-9


def test_all_models_json_roundtrip():
    models = [
        AgentIntent(actor_id="a"),
        PrivateKnowledge(fact_id="f", owner_id="a", content="x"),
        Misunderstanding(holder_id="a"),
        DelayedAction(actor_id="a", due_round=2),
        RelationshipSignal(from_id="a", to_id="b"),
        AgentTurnPlan(round_num=1, actor_id="a"),
    ]
    for m in models:
        cls = type(m)
        assert cls.model_validate_json(m.model_dump_json()) == m


# ── 延迟行动 due_round ─────────────────────────────────────────


def test_delayed_action_due_round():
    da = DelayedAction(actor_id="lin_fan", created_round=1, due_round=3)
    assert da.is_due(1) is False
    assert da.is_due(2) is False
    assert da.is_due(3) is True
    assert da.is_due(4) is True
    da.executed = True
    assert da.is_due(3) is False


def test_trace_pending_vs_due_delayed_actions():
    trace = MultiAgentTrace(
        turn_plans=[
            AgentTurnPlan(
                round_num=1,
                actor_id="lin_fan",
                delayed_actions=[
                    DelayedAction(actor_id="lin_fan", created_round=1, due_round=2),
                    DelayedAction(actor_id="lin_fan", created_round=1, due_round=4),
                ],
            )
        ]
    )
    assert len(trace.pending_delayed_actions(1)) == 2
    # round 2：due=2 到期，due=4 仍 pending
    assert len(trace.due_delayed_actions(2)) == 1
    assert len(trace.pending_delayed_actions(2)) == 1


# ── 私有信息 / 误解默认不泄漏 ──────────────────────────────────


def test_private_knowledge_defaults_private_and_hidden():
    pk = PrivateKnowledge(fact_id="f", owner_id="lin_fan", content="竹林是局")
    assert pk.visibility == "private"
    assert pk.revealed is False
    assert pk.knows("lin_fan") is True
    assert pk.knows("lin_wan_zhou") is False


def test_revealable_knowledge_only_returns_revealed():
    trace = MultiAgentTrace(
        private_knowledge=[
            PrivateKnowledge(fact_id="hidden", owner_id="a", content="秘密"),
            PrivateKnowledge(
                fact_id="open", owner_id="a", content="已揭露", revealed=True
            ),
        ]
    )
    revealable = trace.revealable_knowledge()
    assert len(revealable) == 1
    assert revealable[0].fact_id == "open"


def test_misunderstanding_defaults_private_and_uncorrected():
    m = Misunderstanding(holder_id="lin_wan_zhou", about="墨青烟")
    assert m.visibility == "private"
    assert m.corrected is False
    trace = MultiAgentTrace(misunderstandings=[m])
    assert trace.correctable_misunderstandings() == []


def test_public_intents_filter():
    trace = MultiAgentTrace(
        turn_plans=[
            AgentTurnPlan(
                round_num=1,
                actor_id="a",
                intents=[
                    AgentIntent(actor_id="a", visibility="private"),
                    AgentIntent(actor_id="a", visibility="public", description="公开宣告"),
                ],
            )
        ]
    )
    public = trace.public_intents()
    assert len(public) == 1
    assert public[0].description == "公开宣告"


# ── 协议未接入默认 runner ──────────────────────────────────────


def test_protocol_not_wired_into_default_runner():
    from living_novel_engine.orchestrator.runners import DEFAULT_RUNNER, get_runner

    assert DEFAULT_RUNNER == "lightweight"
    assert get_runner().name == "lightweight"

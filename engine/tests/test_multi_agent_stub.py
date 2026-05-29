from __future__ import annotations

import json

from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.models.events import SimulationResult
from living_novel_engine.orchestrator import (
    SceneRequest,
    available_runners,
    build_branch_specs,
    dispatch_scene,
    get_runner,
    run_scene,
)
from living_novel_engine.orchestrator.runners.projection import (
    project_trace,
)
from living_novel_engine.orchestrator.runners.protocol import (
    AgentIntent,
    AgentTurnPlan,
    DelayedAction,
    Misunderstanding,
    MultiAgentTrace,
    PrivateKnowledge,
    RelationshipSignal,
)
from living_novel_engine.output.writer import write_run_output
from living_novel_engine.samples import load_sample

WHISPER = "今晚不要去城外竹林"


def _request(*, believe: bool, max_rounds: int = 3) -> SceneRequest:
    bundle = load_sample("tianhuang-night")
    llm = LLMClient(mock=True)
    inv = audit_intervention(
        build_intervention(
            target="lin_wan_zhou",
            content=WHISPER,
            intervention_type="whisper",
        ),
        bundle.world,
        bundle.character_map(),
    )
    inv.story_slug = "tianhuang-night"
    inv.source_kind = "builtin"
    specs = build_branch_specs(inv, 3)
    spec = next(
        s for s in specs if (s.branch_seed == "believe") == believe
    )
    return SceneRequest(
        world=bundle.world,
        characters=bundle.characters,
        intervention=inv,
        spec=spec,
        llm=llm,
        max_rounds=max_rounds,
        canon_excerpt=bundle.canon_chapter,
        canon_chapter=bundle.canon_chapter,
    )


def _events_json(events) -> str:
    return json.dumps([e.model_dump() for e in events], ensure_ascii=False)


# ── 投影：公开/私有 ────────────────────────────────────────────


def test_project_only_public_intents():
    trace = MultiAgentTrace(
        turn_plans=[
            AgentTurnPlan(
                round_num=1,
                actor_id="a",
                intents=[
                    AgentIntent(actor_id="a", visibility="public", description="公开表态"),
                    AgentIntent(actor_id="a", visibility="private", description="秘密意图XYZ"),
                ],
            )
        ]
    )
    out = project_trace(trace, max_rounds=4)
    intent_events = [e for e in out.accepted_events if e.payload.get("source") == "agent_intent"]
    assert len(intent_events) == 1
    assert "秘密意图XYZ" not in _events_json(out.accepted_events)


def test_project_private_knowledge_not_leaked_unless_revealed():
    secret = PrivateKnowledge(fact_id="s", owner_id="a", content="隐藏机密ABC")
    revealed = PrivateKnowledge(
        fact_id="r", owner_id="a", content="已公开线索DEF", revealed=True
    )
    trace = MultiAgentTrace(private_knowledge=[secret, revealed])
    out = project_trace(trace, max_rounds=4)
    dumped = _events_json(out.accepted_events)
    assert "隐藏机密ABC" not in dumped
    assert "已公开线索DEF" in dumped


def test_project_misunderstanding_only_when_corrected():
    uncorrected = Misunderstanding(
        holder_id="a", about="x", believed="错信GHI", reality="真相JKL"
    )
    trace = MultiAgentTrace(misunderstandings=[uncorrected])
    out = project_trace(trace, max_rounds=4)
    dumped = _events_json(out.accepted_events)
    assert "真相JKL" not in dumped

    corrected = uncorrected.model_copy(update={"corrected": True})
    out2 = project_trace(
        MultiAgentTrace(misunderstandings=[corrected]), max_rounds=4
    )
    assert "真相JKL" in _events_json(out2.accepted_events)


def test_project_delayed_action_due_vs_pending():
    trace = MultiAgentTrace(
        turn_plans=[
            AgentTurnPlan(
                round_num=1,
                actor_id="a",
                delayed_actions=[
                    DelayedAction(actor_id="a", action_type="x", due_round=2, description="到期动作"),
                    DelayedAction(actor_id="a", action_type="y", due_round=99, description="远期动作"),
                ],
            )
        ]
    )
    out = project_trace(trace, max_rounds=4)
    delayed_events = [e for e in out.accepted_events if e.payload.get("source") == "delayed_action"]
    assert len(delayed_events) == 1
    assert delayed_events[0].round_num == 2
    # 远期动作未到期，保留 pending，不投影
    pending = trace.pending_delayed_actions(4)
    assert len(pending) == 1
    assert pending[0].due_round == 99


def test_project_relationship_signal_to_delta():
    trace = MultiAgentTrace(
        turn_plans=[
            AgentTurnPlan(
                round_num=1,
                actor_id="a",
                relationship_signals=[
                    RelationshipSignal(from_id="a", to_id="b", change="trust+")
                ],
            )
        ]
    )
    out = project_trace(trace, max_rounds=4)
    assert any(
        d.character_id == "a" and d.field == "relationship:b" and d.new_value == "trust+"
        for d in out.state_deltas
    )


# ── runner 注册 / 默认不变 ─────────────────────────────────────


def test_stub_runner_registered_but_not_default():
    assert "multi_agent_stub" in available_runners()
    assert get_runner().name == "lightweight"
    assert get_runner("multi_agent_stub").name == "multi_agent_stub"


def test_lightweight_trace_is_none():
    result = run_scene(
        world=_request(believe=True).world,
        characters=_request(believe=True).characters,
        intervention=_request(believe=True).intervention,
        spec=_request(believe=True).spec,
        llm=LLMClient(mock=True),
        max_rounds=2,
        canon_excerpt="",
        canon_chapter="",
    )
    assert result.runner_name == "lightweight"
    assert result.multi_agent_trace is None


# ── stub runner：契约 + 不泄漏 ────────────────────────────────


def test_stub_runner_keeps_contract():
    result = dispatch_scene(_request(believe=True), runner_name="multi_agent_stub")
    assert isinstance(result, SimulationResult)
    assert result.runner_name == "multi_agent_stub"
    assert result.accepted_events
    assert result.state_snapshot.get("branch_seed") == "believe"
    assert result.chapter_text.strip()
    assert result.multi_agent_trace is not None


def test_stub_runner_private_whisper_not_in_public_events():
    result = dispatch_scene(_request(believe=False), runner_name="multi_agent_stub")
    dumped = _events_json(result.accepted_events)
    assert WHISPER not in dumped
    assert WHISPER not in result.chapter_text
    # 但内部 trace 仍保留私下信息
    trace_dump = json.dumps(result.multi_agent_trace, ensure_ascii=False)
    assert WHISPER in trace_dump


def test_stub_runner_reveals_on_believe_seed():
    result = dispatch_scene(_request(believe=True), runner_name="multi_agent_stub")
    dumped = _events_json(result.accepted_events)
    assert any(e.event_type == "revelation" for e in result.accepted_events)
    assert WHISPER in dumped


def test_stub_trace_has_generation_meta():
    # v0.6.5：stub 也写 generation_meta，便于浏览器区分 stub / llm / fallback
    result = dispatch_scene(_request(believe=True), runner_name="multi_agent_stub")
    gm = result.multi_agent_trace["generation_meta"]
    assert gm["source"] == "stub"
    assert gm["validation_status"] == "ok"


# ── artifact 落盘 ──────────────────────────────────────────────


def test_stub_trace_written_artifact(tmp_path, monkeypatch):
    import living_novel_engine.output.writer as writer_mod

    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)

    req = _request(believe=True)
    result = dispatch_scene(req, runner_name="multi_agent_stub")
    out = write_run_output(req.intervention, [result], run_id="test_stub_trace")
    branch_dir = out.run_dir / result.worldline_id
    assert (branch_dir / "multi_agent_trace.json").exists()
    events = json.loads((branch_dir / "events.json").read_text(encoding="utf-8"))
    assert events["runner"] == "multi_agent_stub"


def test_lightweight_writes_no_trace_artifact(tmp_path, monkeypatch):
    import living_novel_engine.output.writer as writer_mod

    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)

    req = _request(believe=True)
    result = dispatch_scene(req)  # 默认 lightweight
    out = write_run_output(req.intervention, [result], run_id="test_lw_no_trace")
    branch_dir = out.run_dir / result.worldline_id
    assert not (branch_dir / "multi_agent_trace.json").exists()

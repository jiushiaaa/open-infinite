"""v0.6.2 多 Agent 协议 → 输出契约的投影层。

把 `MultiAgentTrace`（runner 内部中间产物）映射成既有契约对象
`AcceptedEvent` / `StateDelta`，保证：

- **私下信息 / 误解默认不进公开层**：只有 `revealed=True` 的 `PrivateKnowledge`
  与 `corrected=True` 的 `Misunderstanding` 才会投影成公开事件。
- **延迟行动按 `due_round` 落地**：`due_round <= max_rounds` 的动作在其到期回合
  执行并投影成事件（标记 `executed=True`）；尚未到期的保留为 pending，不投影。
- **关系传播投影成 `StateDelta`**，供 `state_snapshot` 体现关系变化。

本模块不调用 LLM、不接外部服务，纯结构化转换，便于测试与解释。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from living_novel_engine.models.events import AcceptedEvent, StateDelta
from living_novel_engine.orchestrator.runners.protocol import (
    AgentIntent,
    AgentTurnPlan,
    DelayedAction,
    Misunderstanding,
    MultiAgentTrace,
    PrivateKnowledge,
    RelationshipSignal,
)


@dataclass
class ProjectionOutput:
    """投影结果：公开事件流 + 状态增量。"""

    accepted_events: list[AcceptedEvent] = field(default_factory=list)
    state_deltas: list[StateDelta] = field(default_factory=list)


def _intent_event(intent: AgentIntent, round_num: int, chapter_number: int, seq: int) -> AcceptedEvent:
    return AcceptedEvent(
        event_id=f"ma_intent_{intent.actor_id}_{round_num}_{seq}",
        chapter=chapter_number,
        round_num=round_num,
        event_type=intent.intent_type,
        subject=intent.actor_id,
        payload={
            "source": "agent_intent",
            "target": intent.target,
            "description": intent.description,
            "confidence": intent.confidence,
        },
        narrative=intent.description or f"{intent.actor_id} 公开行动",
    )


def _delayed_event(da: DelayedAction, chapter_number: int, seq: int) -> AcceptedEvent:
    return AcceptedEvent(
        event_id=f"ma_delayed_{da.actor_id}_{da.due_round}_{seq}",
        chapter=chapter_number,
        round_num=da.due_round,
        event_type=da.action_type,
        subject=da.actor_id,
        payload={
            "source": "delayed_action",
            "due_round": da.due_round,
            "created_round": da.created_round,
            "description": da.description,
        },
        narrative=da.description or f"{da.actor_id} 延迟行动到期",
    )


def _revealed_event(pk: PrivateKnowledge, chapter_number: int, seq: int) -> AcceptedEvent:
    return AcceptedEvent(
        event_id=f"ma_reveal_{pk.fact_id}_{seq}",
        chapter=chapter_number,
        round_num=0,
        event_type="revelation",
        subject=pk.owner_id,
        payload={
            "source": "revealed_knowledge",
            "fact_id": pk.fact_id,
            "content": pk.content,
        },
        narrative=pk.content,
    )


def _correction_event(m: Misunderstanding, chapter_number: int, seq: int) -> AcceptedEvent:
    return AcceptedEvent(
        event_id=f"ma_correct_{m.holder_id}_{seq}",
        chapter=chapter_number,
        round_num=0,
        event_type="correction",
        subject=m.holder_id,
        payload={
            "source": "corrected_misunderstanding",
            "about": m.about,
            "reality": m.reality,
        },
        narrative=f"{m.holder_id} 认清「{m.about}」：{m.reality}",
    )


def _relationship_delta(sig: RelationshipSignal) -> StateDelta:
    return StateDelta(
        character_id=sig.from_id,
        field=f"relationship:{sig.to_id}",
        old_value=None,
        new_value=sig.change or f"magnitude={sig.magnitude}",
    )


def _project_public_intents(
    trace: MultiAgentTrace, chapter_number: int, seq: int
) -> tuple[list[AcceptedEvent], int]:
    events: list[AcceptedEvent] = []
    for plan in trace.turn_plans:
        for intent in plan.intents:
            if intent.visibility != "public":
                continue
            events.append(_intent_event(intent, plan.round_num, chapter_number, seq))
            seq += 1
    return events, seq


def _project_due_delayed_actions(
    trace: MultiAgentTrace, chapter_number: int, max_rounds: int, seq: int
) -> tuple[list[AcceptedEvent], int]:
    """到期才执行并投影；未到期保留 pending。就地标记 executed。"""
    events: list[AcceptedEvent] = []
    for plan in trace.turn_plans:
        for da in plan.delayed_actions:
            if da.executed or da.due_round > max_rounds:
                continue
            events.append(_delayed_event(da, chapter_number, seq))
            da.executed = True
            if da.visibility == "private":
                da.visibility = "scene"
            seq += 1
    return events, seq


def _project_revealed(
    trace: MultiAgentTrace, chapter_number: int, seq: int
) -> tuple[list[AcceptedEvent], int]:
    events: list[AcceptedEvent] = []
    for pk in trace.revealable_knowledge():
        events.append(_revealed_event(pk, chapter_number, seq))
        seq += 1
    for m in trace.correctable_misunderstandings():
        events.append(_correction_event(m, chapter_number, seq))
        seq += 1
    return events, seq


def _project_relationship_deltas(trace: MultiAgentTrace) -> list[StateDelta]:
    return [
        _relationship_delta(sig)
        for plan in trace.turn_plans
        for sig in plan.relationship_signals
    ]


def project_trace(
    trace: MultiAgentTrace,
    *,
    chapter_number: int = 13,
    max_rounds: int = 4,
) -> ProjectionOutput:
    """把 trace 投影成公开 `AcceptedEvent` / `StateDelta`。

    会就地把已到期的 `DelayedAction.executed` 置为 True（trace 反映执行状态）；
    未到期的延迟行动保持 pending，不投影。私下信息 / 误解默认不投影，
    仅 `revealed=True` / `corrected=True` 才进公开层。
    """
    out = ProjectionOutput()
    seq = 0

    intent_events, seq = _project_public_intents(trace, chapter_number, seq)
    delayed_events, seq = _project_due_delayed_actions(
        trace, chapter_number, max_rounds, seq
    )
    revealed_events, seq = _project_revealed(trace, chapter_number, seq)

    out.accepted_events = intent_events + delayed_events + revealed_events
    out.state_deltas = _project_relationship_deltas(trace)

    out.accepted_events.sort(key=lambda e: (e.round_num, e.event_id))
    return out


def _merge_relationship(existing: str | None, note: str) -> str:
    if existing and note not in existing:
        return f"{existing}｜{note}"
    return note


def apply_relationship_signals(trace: MultiAgentTrace, char_map: dict) -> None:
    """把关系信号写入角色 relationships，使 state_snapshot 体现关系变化。"""
    for plan in trace.turn_plans:
        for sig in plan.relationship_signals:
            actor = char_map.get(sig.from_id)
            if actor is None:
                continue
            note = sig.change or f"magnitude={sig.magnitude}"
            actor.relationships[sig.to_id] = _merge_relationship(
                actor.relationships.get(sig.to_id), note
            )


def _present_plan(char, *, target_id: str, seed: str) -> AgentTurnPlan:
    is_target = char.id == target_id
    intent = AgentIntent(
        actor_id=char.id,
        intent_type="declare",
        target="" if is_target else target_id,
        motivation=f"对「{seed}」种子的立场",
        description=f"{char.name}在场表态（种子：{seed}）",
        visibility="public",
        confidence=0.6,
    )
    plan = AgentTurnPlan(round_num=1, actor_id=char.id, intents=[intent])
    if not is_target and target_id:
        plan.relationship_signals.append(
            RelationshipSignal(
                signal_id=f"sig_{char.id}_to_{target_id}",
                from_id=char.id,
                to_id=target_id,
                change="concern+",
                magnitude=0.2,
            )
        )
    return plan


def _target_plan(target_id: str) -> AgentTurnPlan:
    """干预目标的私下念头 + 延迟行动（一近一远）。"""
    return AgentTurnPlan(
        round_num=1,
        actor_id=target_id,
        intents=[
            AgentIntent(
                actor_id=target_id,
                intent_type="conceal",
                motivation="不愿暴露真实打算",
                description="暗自保留去留的念头",
                visibility="private",
                confidence=0.7,
            )
        ],
        delayed_actions=[
            DelayedAction(
                actor_id=target_id,
                action_type="resolve",
                description="在后续回合落定去留",
                created_round=1,
                due_round=2,
                visibility="private",
            ),
            DelayedAction(
                actor_id=target_id,
                action_type="rendezvous",
                description="远期赴约的预备动作",
                created_round=1,
                due_round=99,
                visibility="private",
            ),
        ],
    )


def build_demo_trace(request) -> MultiAgentTrace:
    """从场景输入确定性地构造一个可解释的演示 trace。

    这是 stub 级实现（非真正多 Agent 推理）：
    - 每个在场角色产生一个 **public** 表态意图（会投影成事件）。
    - 干预目标额外持有 **private** 念头、私下信息（默认不泄漏）、延迟行动与误解。
    - `believe` 种子下，目标公开回应低语：私下信息 reveal、误解 corrected（会投影）。
    """
    spec = request.spec
    intervention = request.intervention
    seed = spec.branch_seed
    reveal = seed == "believe"

    source_chars = (
        request.seed_characters if request.seed_characters is not None else request.characters
    )
    present = [c for c in source_chars if getattr(c, "present_in_scene", True)]
    if not present:
        present = list(source_chars)

    if intervention:
        target_id = intervention.target
    elif present:
        target_id = present[0].id
    else:
        target_id = ""

    turn_plans: list[AgentTurnPlan] = [
        _present_plan(c, target_id=target_id, seed=seed) for c in present
    ]
    private_knowledge: list[PrivateKnowledge] = []
    misunderstandings: list[Misunderstanding] = []

    if target_id:
        turn_plans.append(_target_plan(target_id))
        whisper = (intervention.content if intervention else "").strip()
        if whisper:
            private_knowledge.append(
                PrivateKnowledge(
                    fact_id="pk_whisper",
                    owner_id=target_id,
                    content=f"外部低语：{whisper[:60]}",
                    visibility="private",
                    revealed=reveal,
                    source="intervention",
                )
            )
        misunderstandings.append(
            Misunderstanding(
                holder_id=target_id,
                about="低语来源",
                believed="或许是故友相邀",
                reality="可能是设局",
                corrected=reveal,
            )
        )

    return MultiAgentTrace(
        worldline_id=spec.branch_id,
        branch_seed=seed,
        turn_plans=turn_plans,
        private_knowledge=private_knowledge,
        misunderstandings=misunderstandings,
    )

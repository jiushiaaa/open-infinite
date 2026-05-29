"""v0.6.1 多 Agent runner 内部协议（数据结构骨架）。

本模块仅定义未来 multi-agent runner 的「内部中间产物」结构，**尚未接入运行**：
`lightweight` 仍是默认 runner，本协议不进入 `dispatch_scene` 默认路径。

设计要点（详见 docs/v0.6.1-multi-agent-runner-protocol.md）：
- 不破坏 `SimulationResult` / `accepted_events` / `state_snapshot` 输出契约。
- 私下信息 / 误解默认 private，**只有显式 reveal/corrected 才允许投影成公开事件**。
- 延迟行动用 `due_round` 表达未来回合执行。
- 所有结构可 `model_dump()` / `model_validate()` 往返序列化。
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Visibility = Literal["private", "scene", "public"]


class AgentIntent(BaseModel):
    """角色本回合的一个计划/意图。"""

    actor_id: str
    intent_type: str = "plan"
    target: str = ""
    motivation: str = ""
    description: str = ""
    visibility: Visibility = "private"
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class PrivateKnowledge(BaseModel):
    """只有部分角色掌握的私下信息。

    `revealed=False` 时绝不应投影到公开事件流（由 v0.6.2 投影函数执行）。
    """

    fact_id: str
    owner_id: str
    content: str
    known_by: list[str] = Field(default_factory=list)
    visibility: Visibility = "private"
    revealed: bool = False
    source: str = ""

    def knows(self, character_id: str) -> bool:
        return character_id == self.owner_id or character_id in self.known_by


class Misunderstanding(BaseModel):
    """角色对某对象/事件的错误认知，可被后续证据纠正。"""

    holder_id: str
    about: str = ""
    believed: str = ""
    reality: str = ""
    corrected: bool = False
    visibility: Visibility = "private"


class DelayedAction(BaseModel):
    """计划在未来某回合执行的动作。"""

    actor_id: str
    action_type: str = "act"
    description: str = ""
    created_round: int = 0
    due_round: int = 0
    executed: bool = False
    visibility: Visibility = "private"

    def is_due(self, round_num: int) -> bool:
        """是否在给定回合到期且尚未执行。"""
        return not self.executed and round_num >= self.due_round


class RelationshipSignal(BaseModel):
    """一次互动对关系/态度的改变；可链式传播到第三方。"""

    signal_id: str = ""
    from_id: str
    to_id: str
    change: str = ""
    magnitude: float = Field(default=0.0, ge=-1.0, le=1.0)
    propagated_from: str = ""
    visibility: Visibility = "scene"


class AgentTurnPlan(BaseModel):
    """单角色单回合的完整计划集合。"""

    round_num: int
    actor_id: str
    intents: list[AgentIntent] = Field(default_factory=list)
    delayed_actions: list[DelayedAction] = Field(default_factory=list)
    relationship_signals: list[RelationshipSignal] = Field(default_factory=list)


class MultiAgentTrace(BaseModel):
    """整场多 Agent 推演的结构化轨迹。

    最终由 v0.6.2 投影函数转为 `AcceptedEvent` / `StateDelta` / `state_snapshot`，
    保持现有输出契约不变。
    """

    worldline_id: str = ""
    branch_seed: str = ""
    turn_plans: list[AgentTurnPlan] = Field(default_factory=list)
    private_knowledge: list[PrivateKnowledge] = Field(default_factory=list)
    misunderstandings: list[Misunderstanding] = Field(default_factory=list)

    def public_intents(self) -> list[AgentIntent]:
        """可进入公开层的意图（即可见性为 public 的项）。"""
        return [
            intent
            for plan in self.turn_plans
            for intent in plan.intents
            if intent.visibility == "public"
        ]

    def pending_delayed_actions(self, round_num: int) -> list[DelayedAction]:
        """尚未执行、且 due_round 仍在未来的延迟行动。"""
        return [
            da
            for plan in self.turn_plans
            for da in plan.delayed_actions
            if not da.executed and da.due_round > round_num
        ]

    def due_delayed_actions(self, round_num: int) -> list[DelayedAction]:
        """在给定回合到期、应当执行的延迟行动。"""
        return [
            da
            for plan in self.turn_plans
            for da in plan.delayed_actions
            if da.is_due(round_num)
        ]

    def revealable_knowledge(self) -> list[PrivateKnowledge]:
        """已显式公开、允许投影成公开事件的私下信息。"""
        return [pk for pk in self.private_knowledge if pk.revealed]

    def correctable_misunderstandings(self) -> list[Misunderstanding]:
        """已被纠正、可在公开层体现的误解。"""
        return [m for m in self.misunderstandings if m.corrected]

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AcceptedEvent(BaseModel):
    event_id: str
    chapter: int = 1
    round_num: int = 0
    event_type: str
    subject: str
    payload: dict[str, Any] = Field(default_factory=dict)
    narrative: str = ""


class StateDelta(BaseModel):
    character_id: str
    field: str
    old_value: Any = None
    new_value: Any = None


class EntityDelta(BaseModel):
    entity_id: str
    action: str
    detail: str = ""


class SceneRecord(BaseModel):
    round_num: int
    location: str
    summary: str
    events: list[AcceptedEvent] = Field(default_factory=list)


class CharacterAction(BaseModel):
    character_id: str
    character_name: str
    stance: Literal["believe", "doubt", "reject"] = "doubt"
    action_type: str
    target: str = ""
    content: str
    internal_thought: str = ""
    intervention_response: str = ""
    # v0.7.2 additive：结构化可审计动作字段（STORY2GAME / eastworld 吸收）。
    # 全部带默认值，旧构造调用与旧 artifact 读取完全兼容；
    # 第一版不强制接入 runner 主链路，缺省即空，UI 空态正常。
    action_id: str | None = None
    action_label: str = ""
    preconditions: list[str] = Field(default_factory=list)
    effects: list[str] = Field(default_factory=list)
    failure_reason: str = ""
    repair_suggestions: list[str] = Field(default_factory=list)
    risk: str = ""
    visibility: str = ""


class SimulationResult(BaseModel):
    worldline_id: str
    branch_seed: str
    theme: str
    rounds: list[SceneRecord] = Field(default_factory=list)
    accepted_events: list[AcceptedEvent] = Field(default_factory=list)
    state_deltas: list[StateDelta] = Field(default_factory=list)
    entity_deltas: list[EntityDelta] = Field(default_factory=list)
    scenes: list[SceneRecord] = Field(default_factory=list)
    summary_text: str = ""
    chapter_text: str = ""
    termination_reason: str = ""
    final_scene_state: dict[str, Any] = Field(default_factory=dict)
    state_snapshot: dict[str, Any] = Field(default_factory=dict)
    retrieval_record: dict[str, Any] | None = None
    runner_name: str = "lightweight"
    # v0.6.2 additive：多 Agent runner 的可解释内部轨迹（MultiAgentTrace.model_dump()）。
    # 仅 multi_agent 系 runner 会填充；lightweight 恒为 None，不影响既有契约。
    multi_agent_trace: dict[str, Any] | None = None

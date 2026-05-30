from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ACT_DIRECTOR_VERSION = "v0.8-actdirector-a"


class ActionPlanStep(BaseModel):
    action_id: str
    branch_axis_id: str
    branch_label: str = ""
    character_id: str
    character_name: str = ""
    action_type: str
    action_label: str
    preconditions: list[str] = Field(default_factory=list)
    effects: list[str] = Field(default_factory=list)
    failure_reason: str = ""
    repair_suggestions: list[str] = Field(default_factory=list)
    risk: Literal["low", "medium", "high"] = "low"
    visibility: str = "private"
    rationale: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class CharacterActionPlan(BaseModel):
    version: str = ACT_DIRECTOR_VERSION
    kind: Literal["act_director_plan"] = "act_director_plan"
    story_slug: str = ""
    lineage_type: str = "divergent_worldline"
    source_compiler_version: str = ""
    steps: list[ActionPlanStep] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

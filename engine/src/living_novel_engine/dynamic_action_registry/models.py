from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

DYNAMIC_ACTION_REGISTRY_VERSION = "v0.8-dynamic-action-registry-a"


class ActionRegistryEntry(BaseModel):
    action_type: str
    action_label: str
    aliases: list[str] = Field(default_factory=list)
    preconditions: list[str] = Field(default_factory=list)
    effects: list[str] = Field(default_factory=list)
    failure_reasons: list[str] = Field(default_factory=list)
    repair_suggestions: list[str] = Field(default_factory=list)
    risk: Literal["low", "medium", "high"] = "low"
    visibility: str = "private"
    source_step_ids: list[str] = Field(default_factory=list)
    branch_axis_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DynamicActionRegistry(BaseModel):
    version: str = DYNAMIC_ACTION_REGISTRY_VERSION
    kind: Literal["dynamic_action_registry"] = "dynamic_action_registry"
    story_slug: str = ""
    source_plan_version: str = ""
    actions: list[ActionRegistryEntry] = Field(default_factory=list)
    aliases: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)

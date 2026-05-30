from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

EMERGENCE_MINING_VERSION = "v0.8-emergence-mining-a"


class EmergenceNode(BaseModel):
    node_id: str
    branch_id: str = ""
    node_type: str = "worldline_divergence"
    title: str
    description: str = ""
    score: float = 0.0
    evidence: list[str] = Field(default_factory=list)
    source_artifacts: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    recommendation: str = ""
    status: Literal["candidate", "high_value", "archive"] = "candidate"
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmergenceReport(BaseModel):
    version: str = EMERGENCE_MINING_VERSION
    kind: Literal["emergence_nodes"] = "emergence_nodes"
    story_slug: str = ""
    run_id: str = ""
    nodes: list[EmergenceNode] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)

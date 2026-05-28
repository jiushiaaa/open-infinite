from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from .contract_audit import ContractAuditResult

InterventionType = Literal[
    "whisper",
    "dream_hint",
    "letter",
    "rumor",
    "weather",
    "resource",
    "crisis",
    "new_event",
]
Strength = Literal["soft", "medium", "strong"]
Visibility = Literal["target_only", "scene", "world_wide"]
ContractRisk = Literal["low", "medium", "high"]


class Intervention(BaseModel):
    id: str
    worldline_id: str = "canon"
    target: str
    type: InterventionType = "whisper"
    content: str
    strength: Strength = "soft"
    visibility: Visibility = "target_only"
    contract_risk: ContractRisk = "low"
    contract_audit: ContractAuditResult | None = None
    branch_seed: str = ""
    audit_notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    story_slug: str = ""
    source_kind: str = ""

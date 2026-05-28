from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ContractRisk = Literal["low", "medium", "high"]
ResistanceLevel = Literal["low", "medium", "high"]


class ContractAuditResult(BaseModel):
    """故事合约审计结构化输出。"""

    allowed: bool = True
    risk: ContractRisk = "low"
    violations: list[str] = Field(default_factory=list)
    repair_suggestions: list[str] = Field(default_factory=list)
    expected_character_resistance: ResistanceLevel = "low"

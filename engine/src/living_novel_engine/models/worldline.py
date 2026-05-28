from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from .intervention import Intervention

WorldlineStatus = Literal["active", "archived", "candidate"]


class Worldline(BaseModel):
    id: str
    parent_id: str = "canon"
    divergence_point: str = ""
    theme: str = ""
    branch_seed: str = ""
    interventions: list[Intervention] = Field(default_factory=list)
    chapters: list[str] = Field(default_factory=list)
    state_snapshot: dict[str, Any] = Field(default_factory=dict)
    status: WorldlineStatus = "candidate"
    summary: str = ""
    created_at: datetime = Field(default_factory=datetime.now)

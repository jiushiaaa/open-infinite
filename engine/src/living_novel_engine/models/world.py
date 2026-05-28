from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Location(BaseModel):
    id: str
    name: str
    description: str = ""


class OpenThread(BaseModel):
    id: str
    title: str
    description: str = ""
    status: str = "open"


class StoryWorld(BaseModel):
    id: str
    title: str
    display_name: str = ""
    source_type: str = "builtin_sample"
    rules: list[str] = Field(default_factory=list)
    locations: list[Location] = Field(default_factory=list)
    factions: list[str] = Field(default_factory=list)
    timeline: list[str] = Field(default_factory=list)
    open_threads: list[OpenThread] = Field(default_factory=list)
    worldline_policy: str = "branch_on_major_intervention"
    divergence_point: str = ""
    scene_description: str = ""
    canon_chapter_path: str = ""
    created_at: datetime = Field(default_factory=datetime.now)

    def rules_text(self) -> str:
        return "\n".join(f"- {r}" for r in self.rules)

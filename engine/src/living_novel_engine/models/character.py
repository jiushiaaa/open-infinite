from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CharacterPersona(BaseModel):
    traits: list[str] = Field(default_factory=list)
    desires: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)


class CharacterState(BaseModel):
    location: str = ""
    emotion: str = "平静"
    resources: list[str] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)


class CharacterAgent(BaseModel):
    id: str
    name: str
    narrative_role: str = "supporting"
    persona: CharacterPersona = Field(default_factory=CharacterPersona)
    memory: list[str] = Field(default_factory=list)
    relationships: dict[str, str] = Field(default_factory=dict)
    current_state: CharacterState = Field(default_factory=CharacterState)
    fourth_wall_awareness: float = 0.0
    present_in_scene: bool = True

    def persona_summary(self) -> str:
        p = self.persona
        parts = [
            f"性格: {', '.join(p.traits) or '未设定'}",
            f"欲望: {', '.join(p.desires) or '未设定'}",
            f"恐惧: {', '.join(p.fears) or '未设定'}",
            f"边界: {', '.join(p.boundaries) or '未设定'}",
        ]
        return "\n".join(parts)

"""v0.7.5 Worldline Judge artifact contract.

The report is branch-level and additive:
``outputs/<run_id>/<branch_id>/worldline_judgement.json``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

WORLDLINE_JUDGE_VERSION = "v0.7.5"
Recommendation = Literal["推荐继续", "谨慎继续", "建议归档"]


class WorldlineJudgeScores(BaseModel):
    """0-1 score dimensions. ``contract_risk`` is a risk value: lower is better."""

    persona_consistency: float = 0.0
    contract_risk: float = 0.0
    branch_diversity: float = 0.0
    narrative_momentum: float = 0.0
    emotional_payoff: float = 0.0
    anti_slop: float = 0.0
    continuation_potential: float = 0.0
    emergence_score: float = 0.0
    story_arc: float = 0.0
    turning_points: float = 0.0
    tension: float = 0.0
    overall: float = 0.0


class JudgementDimension(BaseModel):
    key: str
    label: str
    score: float
    evidence: list[str] = Field(default_factory=list)
    comment: str = ""


class StoryArcPoint(BaseModel):
    label: str
    tension: float = 0.0
    momentum: float = 0.0


class WorldlineJudgement(BaseModel):
    """Worldline Judge branch report."""

    version: str = WORLDLINE_JUDGE_VERSION
    kind: Literal["worldline_judgement"] = "worldline_judgement"
    story_slug: str = ""
    source_kind: Literal["builtin", "imported"] = "builtin"
    run_id: str = ""
    branch_id: str = ""
    chapter_number: int | None = None
    recommendation: Recommendation = "谨慎继续"
    scores: WorldlineJudgeScores = Field(default_factory=WorldlineJudgeScores)
    dimensions: list[JudgementDimension] = Field(default_factory=list)
    turning_points: list[str] = Field(default_factory=list)
    story_arc_curve: list[StoryArcPoint] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    interpretation: str = ""
    created_at: str = ""

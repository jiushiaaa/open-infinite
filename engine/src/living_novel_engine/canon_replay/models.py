"""v0.7.4 Canon Replay artifact 契约（holdout manifest + replay report）。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

CANON_REPLAY_VERSION = "v0.7.4"


class HoldoutChapter(BaseModel):
    """单个正史 holdout 章节的元数据（manifest 条目，不含正文）。"""

    chapter: int
    title: str = ""
    path: str = ""  # 相对项目目录的路径，如 canon/holdout/chapter_005.md
    chars: int = 0


class HoldoutManifest(BaseModel):
    """正史 holdout 清单（canon/holdout_manifest.json）。"""

    version: str = CANON_REPLAY_VERSION
    story_slug: str = ""
    chapters: list[HoldoutChapter] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def chapter_numbers(self) -> list[int]:
        return sorted(c.chapter for c in self.chapters)


class ReplayScores(BaseModel):
    """各项 0-1 评分（deterministic、轻量、不打 LLM）。"""

    lexical_overlap: float = 0.0
    entity_overlap: float = 0.0
    thread_overlap: float = 0.0
    length_ratio: float = 0.0
    state_consistency: float = 0.0
    overall: float = 0.0


class CanonReplayReport(BaseModel):
    """正史回放评估报告（canon_replay_report.json）。"""

    version: str = CANON_REPLAY_VERSION
    kind: Literal["canon_replay"] = "canon_replay"
    story_slug: str = ""
    baseline_run_id: str = ""
    baseline_branch_id: str = "baseline"
    holdout_chapter: int = 0
    scores: ReplayScores = Field(default_factory=ReplayScores)
    matched_entities: list[str] = Field(default_factory=list)
    missing_entities: list[str] = Field(default_factory=list)
    matched_threads: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    interpretation: str = ""
    created_at: str = ""

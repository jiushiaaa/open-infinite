"""v0.7.4 Baseline Worldline artifact 契约（additive、不含干预语义）。

baseline_report.json 写在 baseline run 根目录；baseline/baseline_meta.json
是分支级轻量元数据。两者都不含 intervention/contract_audit 字段。
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

BASELINE_VERSION = "v0.7.4"


class CharacterStateChange(BaseModel):
    """基线推进后角色的当前状态快照（用于对照，不含 delta 强约束）。"""

    character_id: str
    name: str = ""
    location: str = ""
    emotion: str = ""


class BaselineReport(BaseModel):
    """无干预基线报告（baseline_report.json）。"""

    version: str = BASELINE_VERSION
    kind: Literal["baseline"] = "baseline"
    story_slug: str = ""
    source_kind: Literal["builtin", "imported"] = "builtin"
    run_id: str = ""
    branch_id: str = "baseline"
    from_run_id: str | None = None
    from_branch_id: str | None = None
    chapter_number: int = 1
    runner: str = "lightweight"
    mock: bool = True
    no_intervention: bool = True
    summary: str = ""
    natural_development_points: list[str] = Field(default_factory=list)
    character_state_changes: list[CharacterStateChange] = Field(default_factory=list)
    open_threads_touched: list[str] = Field(default_factory=list)
    created_at: str = ""

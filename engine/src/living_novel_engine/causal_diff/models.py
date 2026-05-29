"""v0.7.1-C Causal Diff 后端数据模型。

为未来「时空 Diff / 局部采纳 / 回滚干预」准备稳定 artifact。
本版本只生成数据，不改 chapter.md/events.json/state_snapshot.json 契约，
也不实现 accept/reject/revert 命令（仅预留生命周期字段）。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

DiffStatus = Literal["proposed", "accepted", "rejected", "reverted"]
DiffOp = Literal["replace", "insert", "delete"]
# local_divergence：原世界规则内的局部偏离
# broad_rewrite：大范围改写（规则改写型但仍尝试落在原世界）
# alternate_novel_seed：另开 AU 世界线的种子，不是普通局部修改
DiffMode = Literal["local_divergence", "broad_rewrite", "alternate_novel_seed"]


class DiffAnchor(BaseModel):
    """定位一个 diff 块在原/新文本中的位置（段落级）。"""

    chapter: int = 0
    kind: str = "paragraph"  # paragraph | chapter | scene
    old_index: int = -1      # 段落在 old_text 中的序号（-1 表示无）
    new_index: int = -1      # 段落在 new_text 中的序号（-1 表示无）
    ref: str = ""            # 可选锚点引用（地点/事件/角色等）


class CausalDiffBlock(BaseModel):
    """一个因果差异块：被抹去的旧现实 + 新凝聚的世界线。"""

    id: str
    op: DiffOp
    old_text: str = ""
    new_text: str = ""
    anchor: DiffAnchor = Field(default_factory=DiffAnchor)
    note: str = ""
    # v0.7 第三刀 additive：块级采纳状态（None=继承 artifact 级 proposed）。
    status: DiffStatus | None = None


class CausalDiffArtifact(BaseModel):
    """每个分支一份 causal_diff.json。"""

    diff_id: str
    branch_id: str
    lineage_type: str = "divergent_worldline"
    diff_mode: DiffMode = "local_divergence"
    status: DiffStatus = "proposed"
    intervention_summary: dict[str, Any] = Field(default_factory=dict)
    affected_scope: dict[str, Any] = Field(default_factory=dict)
    blocks: list[CausalDiffBlock] = Field(default_factory=list)
    reason: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    compiler_version: str = "v0.7.1-C"

    # 生命周期预留（v0.7.1-C 不实现命令，仅占位，供后续 UI 做确立/抹除/回滚）
    accepted_at: datetime | None = None
    rejected_at: datetime | None = None
    reverted_from: str | None = None
    parent_diff_id: str | None = None

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

# 四类抽象干预（不同于旧的 InterventionType 渠道枚举）
CompilerInterventionType = Literal[
    "information",        # 信息型：告诉角色未来/真相/预兆
    "forced_action",      # 强制行动型：要求角色某时某刻必须做/不做某事
    "resource_injection", # 资源/物品注入型：让角色获得某件物品/资源
    "rule_rewrite",       # 规则改写型：系统、现代武器、穿越者等改写世界前提
]

# 世界线谱系：原规则内分叉 vs 另开异设小说
LineageType = Literal["divergent_worldline", "alternate_novel"]

# 世界观兼容性结论
CompatibilityStatus = Literal["compatible", "partial", "incompatible"]
CompatRisk = Literal["low", "medium", "high"]


class AbstractIntervention(BaseModel):
    """用户自由输入被理解后的高层结构化意图。"""

    raw_input: str
    input_mode: str = "free_text"
    intervention_type: CompilerInterventionType
    intent: str = ""
    target_refs: list[str] = Field(default_factory=list)
    desired_effect: str = ""
    hard_result: bool = False
    markers: list[str] = Field(default_factory=list)


class Compatibility(BaseModel):
    """干预与现有世界观/合约的兼容性判断。"""

    status: CompatibilityStatus
    risk: CompatRisk
    reasons: list[str] = Field(default_factory=list)
    contract_conflicts: list[str] = Field(default_factory=list)


class Realization(BaseModel):
    """干预如何在世界内被具体落地。"""

    mode: str
    description: str = ""
    in_world: bool = True


class BranchAxisItem(BaseModel):
    """本次干预专属的一条分支轴。

    - id/label/description：本次动态生成的语义（不再固定 believe/doubt/reject）
    - stance：底层机制种子（believe/doubt/reject/...），驱动现有 runner，保持 CLI 兼容
    - outcome：该分支对干预的处理结果（accepted/investigated/rejected/translated/alternate/...）
    """

    id: str
    label: str
    description: str = ""
    stance: str = ""
    outcome: str = ""
    lineage_type: LineageType = "divergent_worldline"


class AffectedScope(BaseModel):
    """本次干预触及的世界元素（供 Causal Diff / 状态增量预留）。"""

    characters: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    items: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    scene_flags: list[str] = Field(default_factory=list)


class InterventionCompilation(BaseModel):
    """Intervention Compiler 的稳定 artifact（写入 intervention_compilation.json）。"""

    abstract_intervention: AbstractIntervention
    compatibility: Compatibility
    realization: Realization
    branch_axis: list[BranchAxisItem] = Field(default_factory=list)
    lineage_type: LineageType = "divergent_worldline"
    affected_scope: AffectedScope = Field(default_factory=AffectedScope)
    compiler_version: str = "v0.7.1-B"
    source: str = "rule_based"  # rule_based | llm | fallback
    generation_meta: dict[str, Any] | None = None
    notes: list[str] = Field(default_factory=list)

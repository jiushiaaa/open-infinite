from __future__ import annotations

from dataclasses import dataclass

from living_novel_engine.models import Intervention

# 固定三分支：演示差异稳定，不随 count 改变语义
FIXED_BRANCHES: list[dict[str, str]] = [
    {
        "branch_id": "branch_a",
        "theme": "相信干预",
        "branch_seed": "believe",
        "forced_stance": "believe",
        "description": "目标相信高维低语/异象，采取避险行动",
    },
    {
        "branch_id": "branch_b",
        "theme": "半信半疑调查",
        "branch_seed": "doubt",
        "forced_stance": "doubt",
        "description": "目标将信将疑，拖延赴约并暗中调查",
    },
    {
        "branch_id": "branch_c",
        "theme": "拒绝干预/反弹",
        "branch_seed": "reject",
        "forced_stance": "reject",
        "description": "目标拒绝外部暗示，坚持原选择或反弹怀疑施加者",
    },
]


@dataclass
class BranchSpec:
    branch_id: str
    theme: str
    branch_seed: str
    forced_stance: str
    description: str


def build_continuation_spec(parent_branch_seed: str, parent_branch_id: str) -> BranchSpec:
    """续章单线推进：无新干预，沿父世界线自主演化一章。"""
    return BranchSpec(
        branch_id="linear",
        theme=f"续章·延续{parent_branch_id}",
        branch_seed="linear",
        forced_stance="",
        description=(
            f"沿 {parent_branch_id}（{parent_branch_seed}）世界线自主推进一章，无新干预"
        ),
    )


def build_branch_specs(intervention: Intervention, count: int = 3) -> list[BranchSpec]:
    """固定三条世界线：相信 / 半信半疑 / 拒绝反弹。"""
    n = max(2, min(3, count))
    specs = [
        BranchSpec(
            branch_id=t["branch_id"],
            theme=t["theme"],
            branch_seed=t["branch_seed"],
            forced_stance=t["forced_stance"],
            description=t["description"],
        )
        for t in FIXED_BRANCHES[:n]
    ]
    if intervention.contract_audit and intervention.contract_audit.risk == "high":
        specs[0].description += "（高合约风险：相信亦可能付出代价）"
    return specs

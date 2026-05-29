from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from living_novel_engine.models import Intervention

if TYPE_CHECKING:
    from living_novel_engine.intervention_compiler.models import InterventionCompilation

# 稳定的分支目录 id：动态分支轴映射到这些 id，保持 outputs 结构与既有 browse/测试兼容
STABLE_BRANCH_IDS: list[str] = ["branch_a", "branch_b", "branch_c", "branch_d"]

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


def build_baseline_spec() -> BranchSpec:
    """无干预基线（v0.7.4）：沿现有世界状态与人设自然推进一章，无任何高维干预。

    branch_seed 复用 ``linear``（与 resume continue 相同的"无新干预"语义），
    branch_id 标记为 ``baseline`` 以区分对照组目录。
    """
    return BranchSpec(
        branch_id="baseline",
        theme="无干预基线",
        branch_seed="linear",
        forced_stance="",
        description="无高维干预，角色按现有世界状态、人设与伏笔压力自然发展（对照组）",
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


def build_branch_specs_from_compilation(
    compilation: "InterventionCompilation",
    count: int = 3,
) -> list[BranchSpec]:
    """把 Intervention Compiler 的动态 branch_axis 映射为可执行 BranchSpec。

    - branch_id 仍用稳定的 branch_a/b/c（保持 outputs 结构与既有测试/browse 兼容）
    - branch_seed / forced_stance 取轴的 stance（believe/doubt/reject），驱动现有 runner
    - theme / branch_id 之外的语义（label/outcome/lineage）来自动态轴，写入 description
    - 若 compiler 没产出轴，回退到固定三分支语义
    """
    axis = compilation.branch_axis
    if not axis:
        return [
            BranchSpec(
                branch_id=t["branch_id"],
                theme=t["theme"],
                branch_seed=t["branch_seed"],
                forced_stance=t["forced_stance"],
                description=t["description"],
            )
            for t in FIXED_BRANCHES[: max(2, min(3, count))]
        ]

    n = max(2, min(len(STABLE_BRANCH_IDS), min(len(axis), count)))
    specs: list[BranchSpec] = []
    for i in range(n):
        item = axis[i]
        stance = item.stance or "reject"
        desc = item.description or item.label
        suffix = f"[{item.outcome}·{item.lineage_type}]"
        specs.append(
            BranchSpec(
                branch_id=STABLE_BRANCH_IDS[i],
                theme=item.label,
                branch_seed=stance,
                forced_stance=stance,
                description=f"{desc} {suffix}",
            )
        )
    return specs

from __future__ import annotations

from .models import BranchAxisItem, CompilerInterventionType, LineageType

# 每类干预的本次专属分支轴模板。
# stance 复用现有 runner 的机制种子（believe/doubt/reject），保持 CLI 兼容；
# id/label/outcome 才是面向用户的真实动态语义。
_AXIS_TEMPLATES: dict[CompilerInterventionType, list[dict[str, str]]] = {
    "information": [
        {
            "id": "believe_omen", "label": "相信预知", "stance": "believe",
            "outcome": "accepted",
            "description": "目标采信高维信息/预兆，据此调整行动",
        },
        {
            "id": "doubt_investigate", "label": "怀疑但调查", "stance": "doubt",
            "outcome": "investigated",
            "description": "目标将信将疑，暗中查证而非全盘接受",
        },
        {
            "id": "reject_omen", "label": "拒绝预兆", "stance": "reject",
            "outcome": "rejected",
            "description": "目标拒绝外部暗示，坚持原选择或反弹怀疑",
        },
    ],
    "forced_action": [
        {
            "id": "reroute", "label": "主动改道", "stance": "believe",
            "outcome": "complied",
            "description": "目标内在动机被触动，主动改变行动路线",
        },
        {
            "id": "forced_delay", "label": "被迫延迟", "stance": "doubt",
            "outcome": "delayed",
            "description": "外力让目标延迟原行动，但并未完全顺从",
        },
        {
            "id": "resist_fate", "label": "抗拒命运压力", "stance": "reject",
            "outcome": "resisted",
            "description": "目标抗拒被强加的行动，坚持本心",
        },
        {
            "id": "fail_but_sense", "label": "干预失败但觉察异常", "stance": "reject",
            "outcome": "failed_but_aware",
            "description": "强制未生效，但目标隐约觉察到被外力推动",
        },
    ],
    "resource_injection": [
        {
            "id": "absorb", "label": "同世界合理吸收", "stance": "believe",
            "outcome": "accepted",
            "description": "物品符合世界观，被自然纳入角色资源",
        },
        {
            "id": "downgrade", "label": "降级转译", "stance": "doubt",
            "outcome": "translated",
            "description": "物品被转译为本世界等价物（保留意图、去掉越界设定）",
        },
        {
            "id": "reject_item", "label": "拒绝", "stance": "reject",
            "outcome": "rejected",
            "description": "物品与世界观冲突，角色或世界拒绝其存在",
        },
        {
            "id": "alternate_world", "label": "开启异设世界线", "stance": "reject",
            "outcome": "alternate",
            "description": "若坚持原物品，则另开异设世界线承载它",
        },
    ],
    "rule_rewrite": [
        {
            "id": "reject_rule", "label": "拒绝原世界线", "stance": "reject",
            "outcome": "rejected",
            "description": "原世界线拒绝该改写，干预被剧情修正/失效",
        },
        {
            "id": "translate_rule", "label": "转译成本世界规则", "stance": "doubt",
            "outcome": "translated",
            "description": "把改写意图降维成本世界已有体系（如系统→机缘/传承）",
        },
        {
            "id": "alternate_novel", "label": "另开 Alternate Novel", "stance": "reject",
            "outcome": "alternate",
            "description": "用户坚持改写前提，另开 AU 世界线并记录合约差异",
        },
    ],
}


def build_branch_axis(
    intervention_type: CompilerInterventionType,
    *,
    dominant_lineage: LineageType,
) -> list[BranchAxisItem]:
    """根据干预类型生成本次专属分支轴。

    每条轴标注它各自会落入的 lineage_type：
    outcome == "alternate" 的轴落入 alternate_novel，其余落入 dominant_lineage。
    """
    templates = _AXIS_TEMPLATES.get(intervention_type, _AXIS_TEMPLATES["information"])
    axis: list[BranchAxisItem] = []
    for t in templates:
        per_lineage: LineageType = (
            "alternate_novel" if t["outcome"] == "alternate" else dominant_lineage
        )
        axis.append(
            BranchAxisItem(
                id=t["id"],
                label=t["label"],
                description=t["description"],
                stance=t["stance"],
                outcome=t["outcome"],
                lineage_type=per_lineage,
            )
        )
    return axis

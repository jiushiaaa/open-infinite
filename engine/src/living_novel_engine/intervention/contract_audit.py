from __future__ import annotations

from living_novel_engine.models import CharacterAgent, Intervention, StoryWorld
from living_novel_engine.models.contract_audit import ContractAuditResult, ContractRisk
def audit_intervention(
    intervention: Intervention,
    world: StoryWorld,
    characters: dict[str, CharacterAgent],
) -> Intervention:
    violations: list[str] = []
    repair_suggestions: list[str] = []
    risk: ContractRisk = "low"
    resistance: str = "low"
    target = characters.get(intervention.target)

    strong_markers = ("死", "杀", "立刻", "必须", "不得", "强行", "逆转", "无敌")
    if any(m in intervention.content for m in strong_markers):
        risk = "medium"
        repair_suggestions.append("降低措辞强度，或改为 soft/medium 干预")

    if intervention.strength == "strong":
        risk = "high"
        resistance = "high"
        repair_suggestions.append("强干预易被剧情修正；可改为梦境/谣言等间接方式")
        violations.append("干预强度标记为 strong，世界将积极抵抗")

    for rule in world.rules:
        if "境界压制不可逆" in rule and any(
            w in intervention.content for w in ("秒杀", "碾压", "越级击败")
        ):
            risk = "high"
            violations.append("违反战力规则：境界不可越级秒杀")
            repair_suggestions.append("移除越级战力结果，改为信息、阵法或器物破局")

    if target:
        for boundary in target.persona.boundaries:
            if "不会轻信" in boundary and intervention.type == "rumor":
                resistance = _max_resistance(resistance, "medium")
                repair_suggestions.append(f"{target.name} 对谣言敏感，建议改用梦境或信件")
            if "不会无理由" in boundary and intervention.strength == "strong":
                resistance = _max_resistance(resistance, "high")
                repair_suggestions.append(f"尊重 {target.name} 的 boundaries，给出可理解动机")

        if "不会轻信" in " ".join(target.persona.boundaries) and intervention.type == "whisper":
            if intervention.strength != "soft":
                resistance = _max_resistance(resistance, "medium")

    if intervention.visibility == "world_wide" and intervention.strength != "soft":
        risk = _max_risk(risk, "medium")
        resistance = _max_resistance(resistance, "medium")
        repair_suggestions.append("广域干预考虑降为 scene 或 target_only")

    allowed = risk != "high" or len(violations) == 0
    if risk == "high" and violations:
        allowed = False

    audit = ContractAuditResult(
        allowed=allowed,
        risk=risk,
        violations=violations,
        repair_suggestions=repair_suggestions,
        expected_character_resistance=resistance,  # type: ignore[arg-type]
    )

    notes = violations + repair_suggestions
    return intervention.model_copy(
        update={
            "contract_risk": risk,
            "contract_audit": audit,
            "audit_notes": notes,
        }
    )


def _max_risk(a: ContractRisk, b: ContractRisk) -> ContractRisk:
    order = {"low": 0, "medium": 1, "high": 2}
    return a if order[a] >= order[b] else b


def _max_resistance(a: str, b: str) -> str:
    order = {"low": 0, "medium": 1, "high": 2}
    return a if order.get(a, 0) >= order.get(b, 0) else b

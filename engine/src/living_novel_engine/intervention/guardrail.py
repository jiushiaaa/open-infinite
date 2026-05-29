"""v0.7.2 Intervention Guardrail：读者干预的轻量护栏解释层。

定位：在 `contract_audit` 之前给读者一个**独立预检**，解释一次自由干预
是否越界、越在哪、风险多高，并给出更合理的干预方式或安全替代。

设计原则：
- 只做解释，不阻断现有 intervention API、不改变 run_intervention 主行为。
- deterministic（不调用 LLM），复用 classifier 的四类分类与 world.rules /
  character.boundaries，但**不修改** contract_audit 既有逻辑。
- 护栏不是"禁止用户"，而是"解释世界为何抵抗，并给出更合理干预方式"。

六类检查维度：genre / time_power / persona / world_rule / visibility / strength。
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from living_novel_engine.intervention_compiler.classifier import classify
from living_novel_engine.intervention_compiler.models import CompilerInterventionType
from living_novel_engine.models import CharacterAgent, StoryWorld

GuardrailRisk = Literal["low", "medium", "high"]
GuardrailCategory = Literal[
    "genre",
    "time_power",
    "persona",
    "world_rule",
    "visibility",
    "strength",
]

_RISK_ORDER = {"low": 0, "medium": 1, "high": 2}

# 越级 / 战力相关标记（时代·战力维度）
_POWER_MARKERS = ("秒杀", "碾压", "越级", "无敌", "一招", "瞬杀", "无视境界", "横扫")
# 强措辞标记（强度维度）
_STRONG_MARKERS = ("死", "杀", "立刻", "马上", "必须", "务必", "不得", "强行", "强制", "逆转", "绝不")

_CATEGORY_LABEL: dict[str, str] = {
    "genre": "题材一致性",
    "time_power": "时代与战力",
    "persona": "人设边界",
    "world_rule": "世界规则",
    "visibility": "可见范围",
    "strength": "干预强度",
}


class GuardrailCheck(BaseModel):
    """单维度护栏检查结果。"""

    category: GuardrailCategory
    label: str = ""
    passed: bool = True
    risk: GuardrailRisk = "low"
    detail: str = ""
    repair_suggestion: str = ""


class InterventionGuardrailResult(BaseModel):
    """干预护栏整体解释结果（独立于 contract_audit 的预检）。"""

    allowed: bool = True
    risk: GuardrailRisk = "low"
    intervention_type: CompilerInterventionType = "information"
    categories: list[GuardrailCheck] = Field(default_factory=list)
    violations: list[str] = Field(default_factory=list)
    repair_suggestions: list[str] = Field(default_factory=list)
    safer_alternative: str | None = None
    rewritten_intent: str | None = None
    explanation: str = ""


def _bump(current: GuardrailRisk, candidate: GuardrailRisk) -> GuardrailRisk:
    return current if _RISK_ORDER[current] >= _RISK_ORDER[candidate] else candidate


def _check_genre(itype: CompilerInterventionType, markers: list[str]) -> GuardrailCheck:
    if itype == "rule_rewrite":
        sample = "、".join(markers[:3]) or "金手指/系统/现代武器等"
        return GuardrailCheck(
            category="genre",
            label=_CATEGORY_LABEL["genre"],
            passed=False,
            risk="high",
            detail=f"检测到改写题材前提的元素（{sample}），会把原世界线变成异设小说。",
            repair_suggestion="若坚持，请明确开启 Alternate Novel（异设世界线）；原世界线不会被静默污染。",
        )
    return GuardrailCheck(
        category="genre",
        label=_CATEGORY_LABEL["genre"],
        passed=True,
        detail="与当前题材一致。",
    )


def _check_time_power(content: str, world: StoryWorld) -> GuardrailCheck:
    hits = [m for m in _POWER_MARKERS if m in content]
    power_rule = any(
        ("境界" in r and ("不可逆" in r or "压制" in r)) or "战力" in r
        for r in world.rules
    )
    if hits:
        risk: GuardrailRisk = "high" if power_rule else "medium"
        return GuardrailCheck(
            category="time_power",
            label=_CATEGORY_LABEL["time_power"],
            passed=False,
            risk=risk,
            detail=f"包含越级/秒杀类战力结果（{'、'.join(hits)}），易被世界战力规则修正。",
            repair_suggestion="把『碾压结果』改为信息预警、阵法、器物或人脉破局，让胜负仍有过程。",
        )
    return GuardrailCheck(
        category="time_power",
        label=_CATEGORY_LABEL["time_power"],
        passed=True,
        detail="未越级改写战力。",
    )


def _check_persona(
    itype: CompilerInterventionType,
    target: CharacterAgent | None,
) -> GuardrailCheck:
    if target is None:
        return GuardrailCheck(
            category="persona",
            label=_CATEGORY_LABEL["persona"],
            passed=True,
            detail="未指定具体角色，无法核对人设边界。",
        )
    boundaries = list(target.persona.boundaries)
    bjoined = " ".join(boundaries)
    forced = itype in ("forced_action", "rule_rewrite")
    distrust = "不会轻信" in bjoined
    obey_resist = ("不会无理由" in bjoined) or ("不会无条件" in bjoined) or ("不会背叛" in bjoined)

    if forced and obey_resist:
        return GuardrailCheck(
            category="persona",
            label=_CATEGORY_LABEL["persona"],
            passed=False,
            risk="high",
            detail=f"{target.name} 的人设边界（{boundaries[0] if boundaries else '自主意志'}）"
            "决定其不会无条件服从强制命令。",
            repair_suggestion=f"给 {target.name} 一个符合其欲望/恐惧的理由，让选择由内而发，而非外部强令。",
        )
    if distrust and itype == "information":
        return GuardrailCheck(
            category="persona",
            label=_CATEGORY_LABEL["persona"],
            passed=False,
            risk="medium",
            detail=f"{target.name} 不会轻信凭空而来的信息，可能先怀疑、调查而非直接采信。",
            repair_suggestion="用其信任之人转述、可验证的线索或梦境暗示，替代直白的『预知』。",
        )
    return GuardrailCheck(
        category="persona",
        label=_CATEGORY_LABEL["persona"],
        passed=True,
        detail=f"未明显违背 {target.name} 的人设边界。",
    )


def _check_world_rule(
    itype: CompilerInterventionType,
    world: StoryWorld,
) -> GuardrailCheck:
    conflicts: list[str] = []
    for rule in world.rules:
        if ("禁止" in rule or "不可" in rule or "不得" in rule) and itype == "rule_rewrite":
            conflicts.append(rule)
    if conflicts:
        return GuardrailCheck(
            category="world_rule",
            label=_CATEGORY_LABEL["world_rule"],
            passed=False,
            risk="high",
            detail=f"与世界规则冲突：{conflicts[0]}",
            repair_suggestion="在原规则内寻找等效手段（情报、势力、伏笔），或显式另开异设世界线。",
        )
    return GuardrailCheck(
        category="world_rule",
        label=_CATEGORY_LABEL["world_rule"],
        passed=True,
        detail="未触碰显式世界规则禁区。",
    )


def _check_visibility(visibility: str) -> GuardrailCheck:
    if visibility == "world_wide":
        return GuardrailCheck(
            category="visibility",
            label=_CATEGORY_LABEL["visibility"],
            passed=False,
            risk="medium",
            detail="广域可见的干预会让更多旁观者察觉异常叙事压力。",
            repair_suggestion="若只想影响目标角色，可改为 target_only 或 scene 级可见。",
        )
    return GuardrailCheck(
        category="visibility",
        label=_CATEGORY_LABEL["visibility"],
        passed=True,
        detail="可见范围克制。",
    )


def _check_strength(content: str, strength: str) -> GuardrailCheck:
    hits = [m for m in _STRONG_MARKERS if m in content]
    if strength == "strong" or hits:
        risk: GuardrailRisk = "high" if strength == "strong" else "medium"
        sample = "、".join(hits[:3])
        detail = "强干预易触发世界主动抵抗与角色觉察。"
        if sample:
            detail = f"措辞过强（{sample}），" + detail
        return GuardrailCheck(
            category="strength",
            label=_CATEGORY_LABEL["strength"],
            passed=False,
            risk=risk,
            detail=detail,
            repair_suggestion="改用 soft/medium 的暗示、梦境、谣言等间接方式，降低被剧情修正的概率。",
        )
    return GuardrailCheck(
        category="strength",
        label=_CATEGORY_LABEL["strength"],
        passed=True,
        detail="干预强度温和。",
    )


def evaluate_guardrail(
    content: str,
    *,
    world: StoryWorld,
    characters: dict[str, CharacterAgent] | None = None,
    target: str = "",
    declared_type: CompilerInterventionType | None = None,
    visibility: str = "target_only",
    strength: str = "soft",
) -> InterventionGuardrailResult:
    """对一次自由干预做护栏预检（deterministic，不调用 LLM）。"""
    text = (content or "").strip()
    characters = characters or {}
    target_agent = characters.get(target) if target else None

    itype, markers = classify(text, declared_type)

    checks = [
        _check_genre(itype, markers),
        _check_time_power(text, world),
        _check_persona(itype, target_agent),
        _check_world_rule(itype, world),
        _check_visibility(visibility),
        _check_strength(text, strength),
    ]

    risk: GuardrailRisk = "low"
    violations: list[str] = []
    repairs: list[str] = []
    for c in checks:
        risk = _bump(risk, c.risk)
        if not c.passed:
            violations.append(f"[{c.label}] {c.detail}")
            if c.repair_suggestion and c.repair_suggestion not in repairs:
                repairs.append(c.repair_suggestion)

    # 护栏不阻断：仅当题材/世界规则被改写（异设）时标记 allowed=False，提示需显式另开世界线。
    hard_blocked = any(
        (not c.passed and c.category in ("genre", "world_rule") and c.risk == "high")
        for c in checks
    )
    allowed = not hard_blocked

    safer_alternative: str | None = None
    rewritten_intent: str | None = None
    if itype == "rule_rewrite":
        safer_alternative = (
            "把改写世界前提的元素，转译为同世界内的情报、势力或器物；"
            "若必须保留，请显式开启 Alternate Novel（异设世界线）。"
        )
    elif violations and repairs:
        safer_alternative = repairs[0]

    explanation = _build_explanation(itype, risk, target_agent, violations)

    return InterventionGuardrailResult(
        allowed=allowed,
        risk=risk,
        intervention_type=itype,
        categories=checks,
        violations=violations,
        repair_suggestions=repairs,
        safer_alternative=safer_alternative,
        rewritten_intent=rewritten_intent,
        explanation=explanation,
    )


def _build_explanation(
    itype: CompilerInterventionType,
    risk: GuardrailRisk,
    target_agent: CharacterAgent | None,
    violations: list[str],
) -> str:
    if not violations:
        return "这次干预与世界、角色和规则基本兼容，可以直接尝试施加。"
    who = target_agent.name if target_agent else "相关角色"
    if itype == "rule_rewrite":
        return (
            "这不是普通分支，而更接近 Alternate Novel（异设世界线）。"
            "原世界线不会被静默改写——你可以另开一条异设世界线来探索它。"
        )
    if risk == "high":
        return (
            f"世界会强烈抵抗这次干预：{who} 有自己的人设、记忆与处境，"
            "不会无条件服从。换一种更贴合其动机的方式，更可能真正改变世界线。"
        )
    return (
        f"世界会部分抵抗这次干预。{who} 仍可能怀疑或迟疑；"
        "参考下方建议，可以让干预更自然地被世界吸收。"
    )

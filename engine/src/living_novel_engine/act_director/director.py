from __future__ import annotations

from living_novel_engine.act_director.models import ActionPlanStep, CharacterActionPlan
from living_novel_engine.intervention_compiler.models import InterventionCompilation
from living_novel_engine.models import CharacterAgent, StoryWorld


def plan_character_actions(
    compilation: InterventionCompilation,
    *,
    world: StoryWorld | None = None,
    characters: dict[str, CharacterAgent] | None = None,
    story_slug: str = "",
) -> CharacterActionPlan:
    """把 InterventionCompilation 转成角色动作计划。

    第一刀只产出 artifact，不驱动 runner；后续 runner 可消费该计划。
    """
    characters = characters or {}
    targets = _target_refs(compilation, characters)
    warnings = _warnings(compilation)
    steps: list[ActionPlanStep] = []

    for axis_index, axis in enumerate(compilation.branch_axis, start=1):
        for target in targets:
            agent = characters.get(target)
            steps.append(_build_step(
                compilation=compilation,
                axis_id=axis.id,
                axis_label=axis.label,
                axis_outcome=axis.outcome,
                axis_index=axis_index,
                character_id=target,
                character_name=agent.name if agent else target,
                world=world,
            ))

    return CharacterActionPlan(
        story_slug=story_slug,
        lineage_type=compilation.lineage_type,
        source_compiler_version=compilation.compiler_version,
        steps=steps,
        warnings=warnings,
    )


def _target_refs(
    compilation: InterventionCompilation, characters: dict[str, CharacterAgent]
) -> list[str]:
    refs = list(compilation.abstract_intervention.target_refs)
    if refs:
        return list(dict.fromkeys(refs))
    present = [
        cid for cid, agent in characters.items()
        if getattr(agent, "present_in_scene", True)
    ]
    return present[:1] or list(characters.keys())[:1] or ["unknown_target"]


def _build_step(
    *,
    compilation: InterventionCompilation,
    axis_id: str,
    axis_label: str,
    axis_outcome: str,
    axis_index: int,
    character_id: str,
    character_name: str,
    world: StoryWorld | None,
) -> ActionPlanStep:
    itype = compilation.abstract_intervention.intervention_type
    risk = compilation.compatibility.risk
    action_type, label, preconditions, effects = _action_shape(
        itype, axis_outcome, world
    )
    failure_reason = _failure_reason(itype, compilation)
    repairs = _repair_suggestions(itype, compilation)

    return ActionPlanStep(
        action_id=f"act_{axis_index:03d}_{character_id}",
        branch_axis_id=axis_id,
        branch_label=axis_label,
        character_id=character_id,
        character_name=character_name,
        action_type=action_type,
        action_label=label,
        preconditions=preconditions,
        effects=effects,
        failure_reason=failure_reason,
        repair_suggestions=repairs,
        risk=risk,
        visibility=_visibility(itype),
        rationale=_rationale(itype, axis_outcome),
        metadata={
            "desired_effect": compilation.abstract_intervention.desired_effect,
            "realization_mode": compilation.realization.mode,
        },
    )


def _action_shape(itype: str, outcome: str, world: StoryWorld | None):
    world_rule = "不违反故事合约与角色人格边界"
    if world and world.rules:
        world_rule = f"遵守世界规则：{world.rules[0]}"

    if itype == "information":
        return (
            "verify_information",
            "验证高维信息",
            ["角色能接触到干预信息", world_rule],
            [f"角色对信息作出 {outcome or 'response'} 回应"],
        )
    if itype == "forced_action":
        return (
            "choose_under_pressure",
            "在压力下自主选择",
            ["行动不直接抹除角色自主性", world_rule],
            ["角色可能执行、调查或抗拒该行动"],
        )
    if itype == "resource_injection":
        return (
            "inspect_resource",
            "检查外来资源",
            ["资源来源可被世界解释", world_rule],
            ["资源被吸收、降级或拒绝"],
        )
    return (
        "reject_or_translate_rule",
        "拒绝或转译规则改写",
        ["规则改写不得静默污染原世界线"],
        ["拒绝注入、转译为本世界现象，或另开 Alternate Novel"],
    )


def _failure_reason(itype: str, compilation: InterventionCompilation) -> str:
    if compilation.compatibility.status == "incompatible":
        return "干预与世界合约不兼容，不能按字面直接执行。"
    if itype == "forced_action":
        return "角色可能因人设、记忆或当前状态拒绝硬结果。"
    return ""


def _repair_suggestions(
    itype: str, compilation: InterventionCompilation
) -> list[str]:
    suggestions: list[str] = []
    if compilation.compatibility.status == "incompatible":
        suggestions.append("转译为本世界已有规则可解释的现象。")
        suggestions.append("另开 Alternate Novel 并记录合约差异。")
    elif itype == "forced_action":
        suggestions.append("改为提供线索、压力或诱因，让角色自行选择。")
    elif itype == "resource_injection":
        suggestions.append("补充资源来源、代价和限制。")
    return suggestions


def _visibility(itype: str) -> str:
    return "world_visible" if itype in ("resource_injection", "rule_rewrite") else "target_private"


def _rationale(itype: str, outcome: str) -> str:
    if itype == "information":
        return "信息型干预应保留角色相信、调查或拒绝的自由。"
    if itype == "forced_action":
        return "强制行动只能转成处境压力，不能直接覆盖角色意志。"
    if itype == "resource_injection":
        return "资源注入需要来源、代价和战力边界。"
    return "规则改写必须拒绝、转译或另开异设世界线。"


def _warnings(compilation: InterventionCompilation) -> list[str]:
    warnings: list[str] = []
    if compilation.lineage_type == "alternate_novel":
        warnings.append("本计划倾向 Alternate Novel，不应写回原世界线正史。")
    if compilation.compatibility.contract_conflicts:
        warnings.append("存在故事合约冲突，执行前需要人工确认。")
    return warnings

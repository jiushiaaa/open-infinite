from __future__ import annotations

from living_novel_engine.models import CharacterAgent, StoryWorld

from .branch_axes import build_branch_axis
from .classifier import classify
from .meta import CompilationMeta
from .models import (
    AbstractIntervention,
    AffectedScope,
    Compatibility,
    CompilerInterventionType,
    InterventionCompilation,
    LineageType,
    Realization,
)

# 表示"用户坚持要一个保证发生的硬结果"的标记
_HARD_RESULT_MARKERS = ("必须", "一定", "务必", "绝对", "直接", "无敌", "秒杀")

# 与"另开异设/规则改写"相关的世界规则关键词（用于在 world.rules 中找冲突）
_REWRITE_RULE_KEYWORDS = (
    "重生", "穿越", "系统", "前世记忆", "金手指", "未声明设定",
    "境界压制不可逆", "越级", "OOC",
)


def compile_intervention(
    raw_input: str,
    *,
    target: str = "",
    world: StoryWorld | None = None,
    characters: dict[str, CharacterAgent] | None = None,
    declared_type: CompilerInterventionType | None = None,
    source: str = "rule_based",
) -> InterventionCompilation:
    """把自由输入编译成稳定的 InterventionCompilation artifact（rule-based/确定性版）。

    流程：分类 -> AbstractIntervention -> Compatibility -> Realization
          -> BranchAxis -> lineage_type -> AffectedScope。
    不调用真实 LLM；缺 world/characters 时也能给出合理默认。
    作为 v0.7.1-B LLM compiler 的确定性回退与安全兜底来源。
    """
    characters = characters or {}
    itype, markers = classify(raw_input, declared_type)

    target_refs = _resolve_target_refs(raw_input, target, characters)
    abstract = AbstractIntervention(
        raw_input=raw_input.strip(),
        intervention_type=itype,
        intent=_infer_intent(itype, target_refs),
        target_refs=target_refs,
        desired_effect=_infer_desired_effect(raw_input),
        hard_result=any(m in raw_input for m in _HARD_RESULT_MARKERS),
        markers=markers,
    )

    compatibility = _judge_compatibility(itype, raw_input, markers, world)
    lineage_type = _decide_lineage(itype, compatibility)
    realization = _build_realization(itype, lineage_type)
    branch_axis = build_branch_axis(itype, dominant_lineage=lineage_type)
    affected = _build_affected_scope(raw_input, target_refs, markers, itype, world, compatibility)

    notes = _build_notes(itype, compatibility, lineage_type)

    return InterventionCompilation(
        abstract_intervention=abstract,
        compatibility=compatibility,
        realization=realization,
        branch_axis=branch_axis,
        lineage_type=lineage_type,
        affected_scope=affected,
        source=source,
        generation_meta=CompilationMeta(source=source).to_dict(),
        notes=notes,
    )


def _resolve_target_refs(
    raw_input: str, target: str, characters: dict[str, CharacterAgent]
) -> list[str]:
    refs: list[str] = []
    if target:
        refs.append(target)
    for cid, agent in characters.items():
        if cid in refs:
            continue
        if (agent.name and agent.name in raw_input) or cid in raw_input:
            refs.append(cid)
    return refs


def _infer_intent(itype: CompilerInterventionType, target_refs: list[str]) -> str:
    who = target_refs[0] if target_refs else "unknown_target"
    return {
        "information": f"inform_{who}",
        "forced_action": f"force_action_on_{who}",
        "resource_injection": f"inject_resource_to_{who}",
        "rule_rewrite": f"rewrite_world_rule_via_{who}",
    }[itype]


def _infer_desired_effect(raw_input: str) -> str:
    snippet = (raw_input or "").strip().replace("\n", " ")
    return snippet[:80]


def _judge_compatibility(
    itype: CompilerInterventionType,
    raw_input: str,
    markers: list[str],
    world: StoryWorld | None,
) -> Compatibility:
    conflicts = _world_rule_conflicts(raw_input, markers, world)

    if itype == "rule_rewrite":
        reasons = ["规则改写型干预会改写世界前提/题材/战力，不能静默注入原世界线"]
        if conflicts:
            reasons.append("与已声明世界规则直接冲突")
        return Compatibility(
            status="incompatible", risk="high",
            reasons=reasons, contract_conflicts=conflicts,
        )

    if itype == "resource_injection":
        if conflicts:
            return Compatibility(
                status="incompatible", risk="high",
                reasons=["注入物品越界（题材/时代/战力不符）", "建议降级转译或另开异设世界线"],
                contract_conflicts=conflicts,
            )
        return Compatibility(
            status="partial", risk="medium",
            reasons=["物品大体符合世界观，但需确认来源合理、不破坏战力平衡"],
        )

    if itype == "forced_action":
        return Compatibility(
            status="partial", risk="medium",
            reasons=["强制行动可被理解，但角色可能因人设/记忆抗拒，世界亦可能修正"],
            contract_conflicts=conflicts,
        )

    # information
    return Compatibility(
        status="compatible", risk="low",
        reasons=["信息型干预可被世界自然吸收，角色保留相信/怀疑/拒绝的自由"],
        contract_conflicts=conflicts,
    )


def _world_rule_conflicts(
    raw_input: str, markers: list[str], world: StoryWorld | None
) -> list[str]:
    if world is None:
        return []
    conflicts: list[str] = []
    lowered_markers = {m.lower() for m in markers}
    for rule in world.rules:
        # 规则里禁止某些设定，而输入恰好触发了这些设定
        for kw in _REWRITE_RULE_KEYWORDS:
            if kw in rule and (kw in raw_input or kw.lower() in lowered_markers):
                conflicts.append(rule)
                break
    return conflicts


def _decide_lineage(
    itype: CompilerInterventionType, compatibility: Compatibility
) -> LineageType:
    # 规则改写型默认另开异设小说，不静默污染原世界线
    if itype == "rule_rewrite":
        return "alternate_novel"
    # 物品注入越界到 incompatible 时，主线也应是异设
    if itype == "resource_injection" and compatibility.status == "incompatible":
        return "alternate_novel"
    return "divergent_worldline"


def _build_realization(
    itype: CompilerInterventionType,
    lineage_type: LineageType,
) -> Realization:
    if lineage_type == "alternate_novel":
        return Realization(
            mode="alternate_or_translate",
            description="默认拒绝静默注入；提供转译为本世界规则或另开 Alternate Novel 两条出路",
            in_world=False,
        )
    if itype == "forced_action":
        return Realization(
            mode="pressure_and_choice",
            description="以处境压力/外部事件推动目标，但最终行动取决于角色自主选择",
        )
    if itype == "resource_injection":
        return Realization(
            mode="absorb_or_downgrade",
            description="优先合理吸收物品；越界部分降级转译，不破坏战力与时代设定",
        )
    return Realization(
        mode="omen_and_information",
        description="以预兆/低语/异象等高维渠道传递信息，角色据信任度自行回应",
    )


def _build_affected_scope(
    raw_input: str,
    target_refs: list[str],
    markers: list[str],
    itype: CompilerInterventionType,
    world: StoryWorld | None,
    compatibility: Compatibility,
) -> AffectedScope:
    locations: list[str] = []
    if world is not None:
        for loc in world.locations:
            if (loc.name and loc.name in raw_input) or loc.id in raw_input:
                locations.append(loc.id)

    items: list[str] = []
    if itype in ("resource_injection", "rule_rewrite"):
        items = list(dict.fromkeys(markers))

    return AffectedScope(
        characters=list(dict.fromkeys(target_refs)),
        locations=list(dict.fromkeys(locations)),
        items=items,
        rules=list(dict.fromkeys(compatibility.contract_conflicts)),
        scene_flags=[],
    )


def _build_notes(
    itype: CompilerInterventionType,
    compatibility: Compatibility,
    lineage_type: LineageType,
) -> list[str]:
    notes: list[str] = []
    if itype == "rule_rewrite":
        notes.append(
            "规则改写型：默认 reject / translate / alternate_novel 三选一，"
            "不会静默污染原世界线"
        )
    if lineage_type == "alternate_novel":
        notes.append("本次干预倾向另开 Alternate Novel / AU 世界线，需记录 story_contract 差异")
    if compatibility.contract_conflicts:
        notes.append(f"检测到 {len(compatibility.contract_conflicts)} 条世界规则冲突")
    return notes

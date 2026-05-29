"""v0.7.1-B 真实 LLM Intervention Compiler。

在 v0.7.1-A rule-based compiler 之上增加 LLM 路径：
- 复用现有 OpenAI-compatible `LLMClient`，不引入新依赖。
- LLM 输出结构化为 `InterventionCompilation` schema。
- 失败/超时/非法 JSON/字段缺失/无 API → 稳定回退 rule-based compiler，
  并在 `notes` 与 `generation_meta` 记录 fallback reason。
- 安全兜底：`rule_rewrite`（系统/AK47/穿越者等）无论 LLM 怎么说，都强制
  `alternate_novel` + `reject/translate/alternate`，不静默污染原世界线。
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from living_novel_engine.models import CharacterAgent, StoryWorld

from .classifier import classify
from .compiler import _resolve_target_refs, compile_intervention
from .meta import CompilationMeta
from .models import (
    AbstractIntervention,
    AffectedScope,
    BranchAxisItem,
    Compatibility,
    CompilerInterventionType,
    InterventionCompilation,
    LineageType,
    Realization,
)

if TYPE_CHECKING:
    from living_novel_engine.llm.client import LLMClient

_REQUIRED_REWRITE_OUTCOMES = {"rejected", "translated", "alternate"}


class LLMCompilationDraft(BaseModel):
    """LLM 需要填充的草稿（target_refs/markers/raw_input 由系统侧确定，不交给 LLM）。"""

    intervention_type: CompilerInterventionType
    intent: str = ""
    desired_effect: str = ""
    hard_result: bool = False
    compatibility: Compatibility
    realization: Realization
    branch_axis: list[BranchAxisItem] = Field(default_factory=list)
    lineage_type: LineageType = "divergent_worldline"
    affected_scope: AffectedScope = Field(default_factory=AffectedScope)


_SYSTEM_PROMPT = (
    "你是 Living Novel Engine 的『干预编译器』。读者会自由输入一条对小说世界的干预，"
    "你要把它理解成结构化的 AbstractIntervention，并判断它与既有世界观/合约的兼容性，"
    "再为本次干预生成专属的分支轴（branch_axis），最后判定世界线谱系（lineage_type）。\n\n"
    "干预类型（intervention_type）四选一：\n"
    "- information：告诉角色未来/真相/预兆（角色保留相信/怀疑/拒绝的自由）\n"
    "- forced_action：要求角色某时某刻必须做或不做某事\n"
    "- resource_injection：让角色获得某件物品/资源\n"
    "- rule_rewrite：系统、现代/未来武器、穿越者、重生、金手指等改写世界前提/题材/战力的干预\n\n"
    "compatibility.reasons 必须尽量归类到这些冲突维度（命中才写）：\n"
    "题材冲突 / 时代冲突 / 战力冲突 / 人设冲突 / 资源冲突 / 信息可见性冲突。\n"
    "compatibility.contract_conflicts 必须尽量引用给定的 world.rules 或 character boundaries 原文。\n\n"
    "branch_axis 不要固定为 believe/doubt/reject：\n"
    "- information：相信预知 / 怀疑但调查 / 拒绝预兆\n"
    "- forced_action：主动改道 / 被迫延迟 / 抗拒命运压力 / 干预失败但觉察异常\n"
    "- resource_injection：同世界合理吸收 / 降级转译 / 拒绝 / 开启异设世界线\n"
    "- rule_rewrite：拒绝原世界线 / 转译成本世界规则 / 另开 Alternate Novel\n"
    "每条 branch_axis 的 stance 必须是 believe / doubt / reject 之一（驱动底层推演）。\n\n"
    "世界线谱系（lineage_type）：\n"
    "- divergent_worldline：在原世界规则内分叉\n"
    "- alternate_novel：改写世界前提/题材/战力\n"
    "rule_rewrite 默认 lineage_type=alternate_novel、realization.in_world=false，"
    "绝不能把它伪装成普通分支静默注入原世界线。"
)


def compile_intervention_with_llm(
    raw_input: str,
    *,
    target: str = "",
    world: StoryWorld | None = None,
    characters: dict[str, CharacterAgent] | None = None,
    llm: "LLMClient | None" = None,
    declared_type: CompilerInterventionType | None = None,
) -> InterventionCompilation:
    """优先用 LLM 编译干预；无 API / mock / 任何失败时稳定回退 rule-based。"""
    characters = characters or {}
    # 始终先算 rule-based 结果：既是回退，也是 rule_rewrite 安全兜底的来源
    rule_based = compile_intervention(
        raw_input,
        target=target,
        world=world,
        characters=characters,
        declared_type=declared_type,
        source="rule_based",
    )

    if llm is None or getattr(llm, "mock", False) or not getattr(llm, "available", False):
        return rule_based

    started = time.perf_counter()
    try:
        draft, usage = _call_llm(raw_input, target, world, characters, llm)
    except Exception as exc:  # noqa: BLE001 — 有确定性回退，任何失败都不应阻断主流程
        return _as_fallback(rule_based, reason=f"{type(exc).__name__}: {exc}")

    duration_ms = int((time.perf_counter() - started) * 1000)
    compilation, repairs = _build_from_draft(
        draft, raw_input, target, characters, declared_type, rule_based
    )
    compilation, reconcile_notes = _reconcile_safety(
        compilation, rule_based, raw_input, declared_type
    )

    meta = CompilationMeta(
        source="llm",
        model_name=getattr(llm.settings, "llm_model_name", None),
        attempt_count=1,
        duration_ms=duration_ms,
        usage=usage,
        reconciled=bool(reconcile_notes),
        reconcile_notes=reconcile_notes,
    )
    compilation.source = "llm"
    compilation.generation_meta = meta.to_dict()
    if repairs:
        compilation.notes.append("LLM 输出已就地修复缺失字段：" + "、".join(repairs))
    compilation.notes.extend(reconcile_notes)
    return compilation


def _call_llm(
    raw_input: str,
    target: str,
    world: StoryWorld | None,
    characters: dict[str, CharacterAgent],
    llm: "LLMClient",
) -> tuple[LLMCompilationDraft, dict | None]:
    user = _build_user_prompt(raw_input, target, world, characters)
    return llm.chat_json_with_usage(
        _SYSTEM_PROMPT, user, LLMCompilationDraft, temperature=0.3
    )


def _build_user_prompt(
    raw_input: str,
    target: str,
    world: StoryWorld | None,
    characters: dict[str, CharacterAgent],
) -> str:
    parts = [f"读者干预原文：{raw_input.strip()}"]
    if target:
        parts.append(f"主要目标角色 id：{target}")
    if world is not None:
        if world.rules:
            parts.append("世界规则（world.rules）：\n" + "\n".join(f"- {r}" for r in world.rules))
        if world.locations:
            locs = "、".join(f"{loc.name}({loc.id})" for loc in world.locations)
            parts.append(f"已知地点：{locs}")
    boundaries = _collect_boundaries(characters)
    if boundaries:
        parts.append("相关角色边界（character boundaries）：\n" + "\n".join(boundaries))
    parts.append(
        "请只输出 JSON：intervention_type / intent / desired_effect / hard_result / "
        "compatibility / realization / branch_axis / lineage_type / affected_scope。"
    )
    return "\n\n".join(parts)


def _collect_boundaries(characters: dict[str, CharacterAgent]) -> list[str]:
    lines: list[str] = []
    for cid, agent in characters.items():
        bs = getattr(agent.persona, "boundaries", []) or []
        if bs:
            lines.append(f"- {agent.name}({cid}): " + "；".join(bs))
    return lines


def _build_from_draft(
    draft: LLMCompilationDraft,
    raw_input: str,
    target: str,
    characters: dict[str, CharacterAgent],
    declared_type: CompilerInterventionType | None,
    rule_based: InterventionCompilation,
) -> tuple[InterventionCompilation, list[str]]:
    """把 LLM 草稿组装成完整 InterventionCompilation，并就地修复缺失字段。"""
    repairs: list[str] = []
    _, markers = classify(raw_input, declared_type)
    target_refs = _resolve_target_refs(raw_input, target, characters)

    intent = draft.intent or rule_based.abstract_intervention.intent
    if not draft.intent:
        repairs.append("intent")
    desired = draft.desired_effect or rule_based.abstract_intervention.desired_effect
    if not draft.desired_effect:
        repairs.append("desired_effect")

    branch_axis = draft.branch_axis or list(rule_based.branch_axis)
    if not draft.branch_axis:
        repairs.append("branch_axis")
    branch_axis = _normalize_axis(branch_axis, rule_based.branch_axis)

    affected = draft.affected_scope
    if not (affected.characters or affected.locations or affected.items or affected.rules):
        affected = rule_based.affected_scope
        repairs.append("affected_scope")
    # 目标角色始终并入 affected_scope.characters
    affected.characters = list(dict.fromkeys(list(affected.characters) + target_refs))

    abstract = AbstractIntervention(
        raw_input=raw_input.strip(),
        intervention_type=draft.intervention_type,
        intent=intent,
        target_refs=target_refs,
        desired_effect=desired,
        hard_result=draft.hard_result,
        markers=markers,
    )

    compilation = InterventionCompilation(
        abstract_intervention=abstract,
        compatibility=draft.compatibility,
        realization=draft.realization,
        branch_axis=branch_axis,
        lineage_type=draft.lineage_type,
        affected_scope=affected,
    )
    return compilation, repairs


def _normalize_axis(
    axis: list[BranchAxisItem], fallback_axis: list[BranchAxisItem]
) -> list[BranchAxisItem]:
    """保证每条轴的 stance 合法（believe/doubt/reject），非法则按顺序补默认。"""
    valid = {"believe", "doubt", "reject"}
    default_cycle = ["believe", "doubt", "reject"]
    normalized: list[BranchAxisItem] = []
    for i, item in enumerate(axis):
        if item.stance not in valid:
            item = item.model_copy(update={"stance": default_cycle[i % 3]})
        normalized.append(item)
    return normalized or list(fallback_axis)


def _reconcile_safety(
    compilation: InterventionCompilation,
    rule_based: InterventionCompilation,
    raw_input: str,
    declared_type: CompilerInterventionType | None,
) -> tuple[InterventionCompilation, list[str]]:
    """rule_rewrite 安全兜底：无论 LLM 怎么判，都不允许静默进入原世界线。"""
    itype_rule, _ = classify(raw_input, declared_type)
    is_rewrite = (
        itype_rule == "rule_rewrite"
        or compilation.abstract_intervention.intervention_type == "rule_rewrite"
    )
    if not is_rewrite:
        return compilation, []

    notes: list[str] = []
    ai = compilation.abstract_intervention
    if ai.intervention_type != "rule_rewrite":
        ai.intervention_type = "rule_rewrite"
        notes.append("安全兜底：识别为规则改写型，已强制 intervention_type=rule_rewrite")
    if compilation.lineage_type != "alternate_novel":
        compilation.lineage_type = "alternate_novel"
        notes.append("安全兜底：规则改写强制 lineage_type=alternate_novel")
    if compilation.realization.in_world:
        compilation.realization.in_world = False
        notes.append("安全兜底：规则改写不得静默注入原世界线（realization.in_world=false）")
    if compilation.compatibility.status != "incompatible":
        compilation.compatibility.status = "incompatible"
        notes.append("安全兜底：规则改写 compatibility.status=incompatible")
    if compilation.compatibility.risk != "high":
        compilation.compatibility.risk = "high"

    outcomes = {a.outcome for a in compilation.branch_axis}
    if not _REQUIRED_REWRITE_OUTCOMES.issubset(outcomes):
        compilation.branch_axis = list(rule_based.branch_axis)
        notes.append("安全兜底：分支轴缺 reject/translate/alternate，已替换为 rule-based 安全轴")
    return compilation, notes


def _as_fallback(
    rule_based: InterventionCompilation, *, reason: str
) -> InterventionCompilation:
    fb = rule_based.model_copy(deep=True)
    fb.source = "fallback"
    meta = CompilationMeta(source="fallback", fallback_reason=reason)
    fb.generation_meta = meta.to_dict()
    fb.notes.append(f"LLM 编译失败，已回退 rule-based：{reason}")
    return fb

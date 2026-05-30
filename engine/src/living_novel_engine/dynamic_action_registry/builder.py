from __future__ import annotations

from collections import defaultdict

from living_novel_engine.act_director.models import CharacterActionPlan
from living_novel_engine.dynamic_action_registry.models import (
    ActionRegistryEntry,
    DynamicActionRegistry,
)

_RISK_ORDER = {"low": 0, "medium": 1, "high": 2}


def build_action_registry(plan: CharacterActionPlan) -> DynamicActionRegistry:
    """从 ActDirector 计划汇总动态动作注册表。

    第一刀只沉淀动作类型、别名和审计字段，不驱动 runner 执行。
    """
    buckets: dict[str, list] = defaultdict(list)
    for step in plan.steps:
        buckets[step.action_type].append(step)

    actions: list[ActionRegistryEntry] = []
    alias_map: dict[str, str] = {}
    for action_type, steps in sorted(buckets.items()):
        first = steps[0]
        aliases = _dedupe(
            [action_type, first.action_label]
            + [s.action_label for s in steps]
            + [s.metadata.get("realization_mode", "") for s in steps]
        )
        entry = ActionRegistryEntry(
            action_type=action_type,
            action_label=first.action_label,
            aliases=aliases,
            preconditions=_dedupe_many(s.preconditions for s in steps),
            effects=_dedupe_many(s.effects for s in steps),
            failure_reasons=_dedupe(s.failure_reason for s in steps if s.failure_reason),
            repair_suggestions=_dedupe_many(s.repair_suggestions for s in steps),
            risk=_max_risk(s.risk for s in steps),
            visibility=first.visibility,
            source_step_ids=_dedupe(s.action_id for s in steps),
            branch_axis_ids=_dedupe(s.branch_axis_id for s in steps),
            metadata={
                "character_ids": _dedupe(s.character_id for s in steps),
                "lineage_type": plan.lineage_type,
            },
        )
        actions.append(entry)
        for alias in aliases:
            alias_map[alias] = action_type

    return DynamicActionRegistry(
        story_slug=plan.story_slug,
        source_plan_version=plan.version,
        actions=actions,
        aliases=alias_map,
        warnings=list(plan.warnings),
        summary={
            "action_count": len(actions),
            "source_step_count": len(plan.steps),
            "high_risk_count": sum(1 for action in actions if action.risk == "high"),
        },
    )


def _dedupe(values) -> list[str]:
    seen: dict[str, None] = {}
    for value in values:
        text = str(value or "").strip()
        if text:
            seen.setdefault(text, None)
    return list(seen.keys())


def _dedupe_many(groups) -> list[str]:
    values: list[str] = []
    for group in groups:
        values.extend(group or [])
    return _dedupe(values)


def _max_risk(values) -> str:
    risk = "low"
    for value in values:
        candidate = str(value or "low")
        if _RISK_ORDER.get(candidate, 0) > _RISK_ORDER.get(risk, 0):
            risk = candidate
    return risk

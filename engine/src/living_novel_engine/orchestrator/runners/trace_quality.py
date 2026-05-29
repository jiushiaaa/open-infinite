"""v0.6.5 多 Agent trace 质量校验与修复。

`multi_agent_llm` 让小模型产出 `MultiAgentTrace`，模型可能：
- 漏掉某个在场角色的计划；
- 把私下信息 / 误解 / 暗算意图错标为 public；
- 给出非法回合号（0、负数、due_round < created_round）；
- 没有把读者干预放进目标角色的 private_knowledge。

本模块把这些检查集中起来：

- **硬失败（hard_fail）**：`turn_plans` 为空——无法投影，runner 据此触发重试 / 回退。
- **就地修复（repaired）**：归一化回合号、强制非公开可见性——这些修复保证「私下信息
  绝不因模型乱标而泄漏」，是投影层公开过滤之前的第一道闸。
- **告警（warnings）**：缺角色计划、干预内容未进目标私域——记录但不阻断，写进
  `generation_meta.validator_warnings` 供浏览器/调试查看。

校验器**绝不抛异常、绝不让 CLI 崩溃**；最坏情况返回 hard_fail，由 runner 回退到确定性 trace。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from living_novel_engine.orchestrator.runners.protocol import MultiAgentTrace

# 暗示「不应公开」的意图类型：即便模型标成 public 也降级为 private
SECRET_INTENT_TYPES = {
    "conceal",
    "deceive",
    "scheme",
    "plot",
    "hide",
    "betray",
    "spy",
}


@dataclass
class ValidationResult:
    """校验结果：status ∈ {ok, repaired, hard_fail}。"""

    status: str = "ok"
    warnings: list[str] = field(default_factory=list)
    repaired: bool = False

    def _note(self, msg: str) -> None:
        self.warnings.append(msg)


def _present_character_ids(request) -> list[str]:
    source_chars = (
        request.seed_characters if request.seed_characters is not None else request.characters
    )
    present = [c for c in source_chars if getattr(c, "present_in_scene", True)] or list(source_chars)
    return [c.id for c in present]


def _repair_rounds(trace: MultiAgentTrace) -> bool:
    """回合号归一化到 >=1，且 due_round >= created_round。返回是否有修改。"""
    changed = False
    for plan in trace.turn_plans:
        if plan.round_num < 1:
            plan.round_num = 1
            changed = True
        for da in plan.delayed_actions:
            new_created = max(da.created_round, 1)
            new_due = max(da.due_round, new_created)
            if new_created != da.created_round or new_due != da.due_round:
                da.created_round, da.due_round = new_created, new_due
                changed = True
    return changed


def _repair_visibility(trace: MultiAgentTrace) -> bool:
    """强制：暗算意图不得 public；未 reveal 私下信息、未 corrected 误解保持 private。"""
    changed = False
    for plan in trace.turn_plans:
        for intent in plan.intents:
            if intent.intent_type in SECRET_INTENT_TYPES and intent.visibility == "public":
                intent.visibility = "private"
                changed = True
    for pk in trace.private_knowledge:
        if not pk.revealed and pk.visibility != "private":
            pk.visibility = "private"
            changed = True
    for m in trace.misunderstandings:
        if not m.corrected and m.visibility != "private":
            m.visibility = "private"
            changed = True
    return changed


def _warn_missing_plans(trace: MultiAgentTrace, request, result: ValidationResult) -> None:
    actors = {plan.actor_id for plan in trace.turn_plans}
    for cid in _present_character_ids(request):
        if cid not in actors:
            result._note(f"在场角色 {cid} 缺少 turn_plan")


def _warn_intervention_not_private(trace: MultiAgentTrace, request, result: ValidationResult) -> None:
    inv = request.intervention
    if inv is None or not inv.content:
        return
    needle = inv.content.strip()[:20]
    owned = [pk for pk in trace.private_knowledge if pk.owner_id == inv.target]
    if not any(needle and needle in (pk.content or "") for pk in owned):
        result._note(f"干预内容未进入目标角色 {inv.target} 的 private_knowledge")


def validate_and_repair_trace(trace: MultiAgentTrace, request) -> ValidationResult:
    """就地修复并校验 trace；填补 worldline_id / branch_seed。"""
    result = ValidationResult()
    spec = request.spec
    if not trace.worldline_id:
        trace.worldline_id = spec.branch_id
    if not trace.branch_seed:
        trace.branch_seed = spec.branch_seed

    if not trace.turn_plans:
        result.status = "hard_fail"
        result._note("turn_plans 为空，无法投影")
        return result

    repaired = _repair_rounds(trace)
    repaired = _repair_visibility(trace) or repaired

    _warn_missing_plans(trace, request, result)
    _warn_intervention_not_private(trace, request, result)

    result.repaired = repaired
    result.status = "repaired" if repaired else "ok"
    return result

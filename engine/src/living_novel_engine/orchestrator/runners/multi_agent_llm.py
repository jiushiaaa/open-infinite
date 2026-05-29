"""v0.6.4 `multi_agent_llm` runner：小模型推演多 Agent 轨迹。
v0.6.5 起补工程可靠性：generation_meta、trace 质量校验、有限重试、token usage。

把 v0.6.2 stub 的确定性 `build_demo_trace` 升级为**真正的 LLM 推演**：
通过 OpenAI-compatible API（`LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL_NAME`）
让小模型一次性输出整场 `MultiAgentTrace` JSON（角色计划 / 私下信息 / 误解 /
延迟行动 / 关系信号），再复用 v0.6.2 投影层与共享装配层产出 `SimulationResult`。

可靠性（v0.6.5）：
- **质量校验** `trace_quality.validate_and_repair_trace`：硬失败（空 turn_plans）触发重试 /
  回退；就地修复可见性与回合号（私下信息绝不因模型乱标而泄漏）；告警写入 meta。
- **有限重试**：LLM 调用异常或 validator 硬失败时最多重试 `LNE_MULTI_AGENT_MAX_RETRIES`
  次（默认 1），重试 prompt 带上上一轮的问题；全部失败回退确定性 `build_demo_trace`。
- **生成元数据** `TraceMeta`：source / fallback_reason / model_name / attempt_count /
  duration_ms / validation_status / validator_warnings / usage / cost_estimate，
  以 additive 方式写进 `multi_agent_trace.json`。

定位不变：**非默认**（`lightweight` 仍默认），不本地部署、不引入新依赖。
"""

from __future__ import annotations

import logging
import os
import time

from living_novel_engine.models.events import SimulationResult
from living_novel_engine.orchestrator.runners.assembly import build_result_from_trace
from living_novel_engine.orchestrator.runners.base import SceneRequest, SceneRunner
from living_novel_engine.orchestrator.runners.meta import TraceMeta
from living_novel_engine.orchestrator.runners.projection import build_demo_trace
from living_novel_engine.orchestrator.runners.protocol import MultiAgentTrace
from living_novel_engine.orchestrator.runners.trace_quality import (
    validate_and_repair_trace,
)

logger = logging.getLogger(__name__)

_MAX_RETRIES_ENV = "LNE_MULTI_AGENT_MAX_RETRIES"
_DEFAULT_MAX_RETRIES = 1
_MAX_RETRIES_CAP = 5


class MultiAgentLLMRunner(SceneRunner):
    """小模型推演型多 Agent runner（LLM 产出 trace → 复用投影/装配）。"""

    name = "multi_agent_llm"

    def run(self, request: SceneRequest) -> SimulationResult:
        return run_multi_agent_llm(request)


_SYSTEM_PROMPT = """你是「活体小说」的多 Agent 推演引擎。给定世界、在场角色与一次读者干预，
你要推演这一幕里**每个在场角色各自的内心计划与互动**，输出一份结构化轨迹（MultiAgentTrace）。

严格要求：
1. 只输出合法 JSON，不要 markdown 代码块、不要解释文字。
2. 为每个在场角色生成一条 turn_plan（round_num 从 1 开始），其中：
   - intents：该角色本回合的意图。公开的言行用 visibility="public"；
     内心盘算、隐瞒、暗中观察用 visibility="private"。
   - motivation 写动机（内部，不会进正文）；description 写意图的具体表现。
3. 私下信息放进 private_knowledge，默认 revealed=false（除非这一幕里被当众揭破）。
   误解放进 misunderstandings，默认 corrected=false（除非这一幕被纠正）。
   **读者干预的具体内容应作为目标角色的 private_knowledge，不要直接写进任何 public 意图。**
4. 角色想在以后回合才做的事放进 delayed_actions，用 due_round 表示将来的回合（>=1）。
5. 一次互动改变 A 对 B 的态度，用 relationship_signals 表达（magnitude 在 -1~1）。
6. 角色可以怀疑、拒绝、误解读者干预——不要让所有人都顺从。符合人设的反抗是好的。
7. confidence / magnitude 必须在合法区间内（0~1 / -1~1）；回合号必须 >=1。"""


def _char_brief(char) -> str:
    rel = "，".join(f"{k}:{v}" for k, v in char.relationships.items()) or "无"
    mem = "；".join(char.memory[:3]) or "无"
    return (
        f"- {char.name}（id={char.id}，角色定位={char.narrative_role}）\n"
        f"  {char.persona_summary()}\n"
        f"  记忆: {mem}\n  关系: {rel}"
    )


def _build_user_prompt(request: SceneRequest) -> str:
    world = request.world
    spec = request.spec
    source_chars = (
        request.seed_characters if request.seed_characters is not None else request.characters
    )
    present = [c for c in source_chars if getattr(c, "present_in_scene", True)] or list(source_chars)

    parts = [
        f"【世界】{world.title}",
        f"世界规则:\n{world.rules_text()}",
        f"【场景】{world.scene_description}",
        "【在场角色】",
        "\n".join(_char_brief(c) for c in present),
        f"【世界线种子】{spec.branch_seed}（{spec.description}）",
        f"【最大回合数】{request.max_rounds}",
    ]
    if request.retrieved_context:
        parts.insert(2, f"【检索到的正史事实与上下文】\n{request.retrieved_context}")
    if request.intervention:
        inv = request.intervention
        parts.append(
            f"【读者干预】类型={inv.type}，目标={inv.target}，内容=「{inv.content}」\n"
            "请把该内容作为目标角色的 private_knowledge（owner_id=目标角色），"
            "默认 revealed=false；目标角色可相信/怀疑/拒绝它。"
        )
    else:
        parts.append("【续章模式】无新干预，按人设与当前局势自主推进。")
    parts.append(
        "现在输出该幕的 MultiAgentTrace JSON："
        f"worldline_id 用「{spec.branch_id}」，branch_seed 用「{spec.branch_seed}」。"
    )
    return "\n".join(parts)


def _retry_hint(problems: list[str]) -> str:
    if not problems:
        return ""
    bullets = "\n".join(f"- {p}" for p in problems)
    return (
        "\n\n【上一轮输出存在问题，请修正后重新输出完整 JSON】\n"
        f"{bullets}"
    )


def _max_retries() -> int:
    raw = os.environ.get(_MAX_RETRIES_ENV, "").strip()
    if not raw:
        return _DEFAULT_MAX_RETRIES
    try:
        value = int(raw)
    except ValueError:
        return _DEFAULT_MAX_RETRIES
    return max(0, min(value, _MAX_RETRIES_CAP))


def _model_name(llm) -> str | None:
    settings = getattr(llm, "settings", None)
    return getattr(settings, "llm_model_name", None) if settings is not None else None


def _ms_since(start: float) -> int:
    return int((time.monotonic() - start) * 1000)


def generate_trace(request: SceneRequest) -> tuple[MultiAgentTrace, TraceMeta]:
    """生成多 Agent 轨迹，返回 `(trace, TraceMeta)`。

    - mock / LLM 不可用 → 确定性 `build_demo_trace`，source="fallback"。
    - LLM 调用异常或 validator 硬失败 → 重试（带问题反馈），最多 `LNE_MULTI_AGENT_MAX_RETRIES` 次。
    - 全部失败 → 回退确定性 trace（不抛）。成功 → 经校验/修复的 LLM trace，source="llm"。
    """
    llm = request.llm
    model_name = _model_name(llm)
    start = time.monotonic()

    if getattr(llm, "mock", False) or not getattr(llm, "available", False):
        return build_demo_trace(request), TraceMeta(
            source="fallback",
            fallback_reason="mock_or_unavailable",
            model_name=model_name,
            attempt_count=0,
            duration_ms=_ms_since(start),
            validation_status="fallback",
        )

    system = _SYSTEM_PROMPT
    base_user = _build_user_prompt(request)
    extra = ""
    attempts = 0
    usage: dict | None = None
    last_reason: str | None = None
    last_warnings: list[str] = []

    for _ in range(_max_retries() + 1):
        attempts += 1
        try:
            trace, usage = llm.chat_json_with_usage(
                system, base_user + extra, MultiAgentTrace, temperature=0.5
            )
        except Exception as exc:  # noqa: BLE001 — 任何失败都回退/重试
            last_reason = f"llm_error: {type(exc).__name__}"
            logger.warning("multi_agent_llm 第 %d 次调用失败：%s", attempts, exc)
            extra = _retry_hint([f"上次调用失败：{exc}"])
            continue

        vr = validate_and_repair_trace(trace, request)
        if vr.status == "hard_fail":
            last_reason = "validator_hard_fail"
            last_warnings = vr.warnings
            logger.warning("multi_agent_llm 第 %d 次输出未通过校验：%s", attempts, vr.warnings)
            extra = _retry_hint(vr.warnings)
            continue

        return trace, TraceMeta(
            source="llm",
            model_name=model_name,
            attempt_count=attempts,
            duration_ms=_ms_since(start),
            validation_status=vr.status,
            validator_warnings=vr.warnings,
            usage=usage,
        )

    logger.warning("multi_agent_llm 重试耗尽，回退确定性 trace（reason=%s）", last_reason)
    return build_demo_trace(request), TraceMeta(
        source="fallback",
        fallback_reason=last_reason,
        model_name=model_name,
        attempt_count=attempts,
        duration_ms=_ms_since(start),
        validation_status="fallback",
        validator_warnings=last_warnings,
        usage=usage,
    )


def run_multi_agent_llm(request: SceneRequest) -> SimulationResult:
    trace, meta = generate_trace(request)
    result = build_result_from_trace(
        request,
        trace,
        termination_reason="multi_agent_llm_complete",
        generation_meta=meta.to_dict(),
    )
    result.runner_name = MultiAgentLLMRunner.name
    return result

"""console-free 干预编排服务（v0.7 Web Generate Loop）。

把 `cli.intervene_cmd` 的核心流程抽成无副作用（不打印）的函数，
供 HTTP API（POST /api/interventions）与 CLI 共用，避免复制推演代码。

流程：load_story → audit → compile(LLM/规则) → branch specs →
retrieval → fourth wall → run_scene(每分支) → write_run_output。
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from living_novel_engine.fourth_wall import (
    FourthWallLedger,
    accumulate_intervention,
    fourth_wall_enabled,
)
from living_novel_engine.act_director import plan_character_actions
from living_novel_engine.dynamic_action_registry import build_action_registry
from living_novel_engine.emergence_mining import write_emergence_nodes
from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.intervention_compiler import (
    InterventionCompilation,
    compile_intervention_with_llm,
)
from living_novel_engine.llm.client import LLMClient, LLMSettings
from living_novel_engine.models import Intervention
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import (
    build_branch_specs_from_compilation,
)
from living_novel_engine.output.writer import write_run_output
from living_novel_engine.runtime_memory import build_runtime_memory_context
from living_novel_engine.story_loader import load_story


class InterventionRequestError(ValueError):
    """入参非法（缺 story/target/content、未知 slug/角色）——映射为 HTTP 400。"""


@dataclass
class InterventionServiceResult:
    run_id: str
    run_dir: Path
    branch_ids: list[str]
    compilation: InterventionCompilation
    llm_mock: bool
    story_slug: str
    fallback_reason: str | None = None
    extra: dict[str, object] = field(default_factory=dict)


def resolve_llm_quietly(mock_flag: bool) -> tuple[LLMClient, bool]:
    """解析 LLM 客户端，不打印。返回 (client, used_mock)。

    无 API Key 时自动退化为 mock，保证端到端可用（无 key 不报错）。
    """
    settings = LLMSettings.from_env()
    env_mock = os.environ.get("LNE_MOCK", "").lower() in ("1", "true", "yes")
    use_mock = mock_flag or env_mock or not settings.llm_api_key
    llm = LLMClient(mock=use_mock)
    if not llm.available:
        raise InterventionRequestError(
            "无法初始化 LLM 客户端，请使用 mock=true 或配置 engine/.env"
        )
    return llm, use_mock


def _prepare_retrieval(bundle, query: str, source_type: str, *, current_chapter: int):
    if bundle.project_dir and source_type != "builtin_sample":
        ctx = build_runtime_memory_context(
            bundle.project_dir,
            query,
            current_chapter=current_chapter,
        )
        return (
            ctx.as_prompt_block(),
            ctx.retrieval.to_artifact(),
            ctx.to_artifact(),
        )
    return "", None, None


def _present_ids(bundle) -> list[str]:
    return [c.id for c in bundle.characters if getattr(c, "present_in_scene", True)]


def _prepare_ledger(
    intervention: Intervention, *, chapter: int, present_ids: list[str]
) -> FourthWallLedger | None:
    if not fourth_wall_enabled():
        return None
    ledger = FourthWallLedger(enabled=True)
    accumulate_intervention(ledger, intervention, chapter=chapter, present_ids=present_ids)
    return ledger


def run_intervention(
    *,
    story_slug: str,
    target: str,
    content: str,
    intervention_type: str = "whisper",
    branches: int = 3,
    rounds: int = 4,
    mock: bool = False,
    runner_name: str | None = None,
) -> InterventionServiceResult:
    """执行一次干预，写出多条世界线，返回 run 信息与编译结果。"""
    slug = (story_slug or "").strip()
    target = (target or "").strip()
    content = (content or "").strip()
    if not slug:
        raise InterventionRequestError("缺少 story_slug")
    if not target:
        raise InterventionRequestError("缺少 target（干预目标角色）")
    if not content:
        raise InterventionRequestError("缺少 content（干预内容）")

    try:
        bundle = load_story(slug)
    except FileNotFoundError as exc:
        raise InterventionRequestError(str(exc)) from exc

    char_map = bundle.character_map()
    if target not in char_map:
        raise InterventionRequestError(
            f"未知角色: {target}，可选: {', '.join(char_map.keys())}"
        )

    llm, used_mock = resolve_llm_quietly(mock)

    intervention = build_intervention(
        target=target,
        content=content,
        intervention_type=intervention_type,  # type: ignore[arg-type]
    )
    intervention = audit_intervention(intervention, bundle.world, char_map)

    compilation = compile_intervention_with_llm(
        content,
        target=target,
        world=bundle.world,
        characters=char_map,
        llm=llm,
    )

    specs = build_branch_specs_from_compilation(
        compilation, count=max(2, min(3, branches))
    )

    query = f"{content} {char_map[target].name}"
    intervention_chapter = bundle.intervention_chapter()
    retrieved_ctx, retrieval_record, runtime_memory_record = _prepare_retrieval(
        bundle, query, bundle.world.source_type, current_chapter=intervention_chapter
    )

    ledger = _prepare_ledger(
        intervention, chapter=intervention_chapter, present_ids=_present_ids(bundle)
    )

    results = []
    for spec in specs:
        result = run_scene(
            bundle.world,
            bundle.characters,
            intervention,
            spec,
            llm,
            max_rounds=rounds,
            canon_excerpt=bundle.canon_context_for_narrator(),
            prologue=bundle.prologue,
            canon_opening=bundle.canon_opening,
            canon_chapter=bundle.canon_chapter,
            source_type=bundle.world.source_type,
            retrieved_context=retrieved_ctx,
            ledger=ledger,
            runner_name=runner_name,
        )
        if retrieval_record is not None:
            result.retrieval_record = retrieval_record
        if runtime_memory_record is not None:
            result.runtime_memory_record = runtime_memory_record
        results.append(result)

    intervention.story_slug = slug
    intervention.source_kind = bundle.source_kind
    output = write_run_output(
        intervention,
        results,
        ledger=ledger,
        compilation=compilation,
        old_text=bundle.canon_chapter,
    )
    action_plan = plan_character_actions(
        compilation,
        world=bundle.world,
        characters=char_map,
        story_slug=slug,
    )
    plan_payload = action_plan.model_dump(mode="json")
    (output.run_dir / "act_director_plan.json").write_text(
        json.dumps(plan_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    action_registry = build_action_registry(action_plan)
    registry_payload = action_registry.model_dump(mode="json")
    (output.run_dir / "dynamic_action_registry.yaml").write_text(
        yaml.safe_dump(
            registry_payload,
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    emergence_payload = write_emergence_nodes(output.run_dir)

    meta = compilation.generation_meta or {}
    return InterventionServiceResult(
        run_id=output.run_id,
        run_dir=output.run_dir,
        branch_ids=[r.worldline_id for r in results],
        compilation=compilation,
        llm_mock=used_mock,
        story_slug=slug,
        fallback_reason=meta.get("fallback_reason"),
        extra={
            "act_director_plan": plan_payload,
            "dynamic_action_registry": registry_payload,
            "emergence_nodes": emergence_payload,
        },
    )

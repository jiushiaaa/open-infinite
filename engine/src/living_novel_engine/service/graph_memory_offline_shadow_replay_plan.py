"""Graph Memory Offline Shadow Replay Plan MVP.

This report turns the provider boundary matrix into a deterministic local replay
plan. It does not run GraphRAG, Zep, vector stores, graph databases, rerankers,
embedding providers, or LLMs.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_boundary_matrix import (
    GraphMemoryProviderBoundaryMatrixRequestError,
    get_graph_memory_provider_boundary_matrix,
)

VERSION = "graph-memory-offline-shadow-replay-plan-mvp"


class GraphMemoryOfflineShadowReplayPlanRequestError(ValueError):
    """Invalid graph-memory offline replay request, mapped to HTTP 400."""


def get_graph_memory_offline_shadow_replay_plan(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only offline shadow replay plan."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        boundary_report = get_graph_memory_provider_boundary_matrix(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderBoundaryMatrixRequestError as exc:
        raise GraphMemoryOfflineShadowReplayPlanRequestError(str(exc)) from exc

    source_status = str(boundary_report.get("status") or "deferred")
    status = _status(source_status)
    providers = _candidate_providers(status, boundary_report)
    source_cases = _source_cases(boundary_report)
    provider_plans = _provider_plans(status, providers, boundary_report)
    replay_cases = _replay_cases(status, providers, source_cases, boundary_report)
    replay_steps = _replay_steps(status)
    replay_gate = _replay_gate(status, provider_plans, replay_cases)
    summary = _summary(sid, source_status, status, provider_plans, replay_cases, replay_steps)
    manifest = _manifest(
        generated_at,
        summary,
        replay_gate,
        provider_plans,
        replay_cases,
        replay_steps,
        boundary_report,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_offline_shadow_replay_plan",
        "status": status,
        "story_slug": sid,
        "source_kind": boundary_report.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "replay_gate": replay_gate,
        "provider_plans": provider_plans,
        "replay_cases": replay_cases,
        "replay_steps": replay_steps,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": _no_go_conditions(boundary_report),
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(boundary_report, provider_plans, replay_cases),
        "boundaries": [
            "只读整理离线 shadow replay 计划，不运行 provider，不写项目 artifact。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开 opt-in spike。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryOfflineShadowReplayPlanRequestError("invalid slug")
    return sid


def _status(source_status: str) -> str:
    if source_status == "ready_for_boundary_review":
        return "ready_for_offline_replay"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    return "deferred"


def _candidate_providers(
    status: str,
    boundary_report: dict[str, Any],
) -> list[dict[str, Any]]:
    if status != "ready_for_offline_replay":
        return []
    return [
        item
        for item in boundary_report.get("providers") or []
        if item.get("status") in {"candidate", "monitor"}
    ]


def _source_cases(boundary_report: dict[str, Any]) -> list[dict[str, Any]]:
    manifest = boundary_report.get("manifest") or {}
    source_case_matrix = manifest.get("source_case_matrix") or {}
    cases = source_case_matrix.get("cases") or []
    return [item for item in cases if item.get("eval_id") or item.get("id")]


def _provider_plans(
    status: str,
    providers: list[dict[str, Any]],
    boundary_report: dict[str, Any],
) -> list[dict[str, Any]]:
    if status != "ready_for_offline_replay":
        return []
    plans: list[dict[str, Any]] = []
    for provider in providers:
        provider_id = str(provider.get("id") or "unknown")
        plans.append(
            {
                "provider_id": provider_id,
                "provider_label": str(provider.get("label") or provider_id),
                "service_target": str(provider.get("service_target") or provider_id),
                "provider_kind": str(provider.get("provider_kind") or "memory_provider"),
                "status": "planned",
                "opt_in_required": True,
                "replay_scope": _replay_scope(provider_id),
                "boundary_refs": _boundary_refs(provider_id, boundary_report),
                "acceptance_summary": "离线 replay 必须证明相对 BM25 + canon ledger + entity aliases 有可复核收益。",
                "rollback_strategy": str(provider.get("rollback_strategy") or "关闭 provider，回退本地检索链路。"),
                "manual_review_required": True,
            }
        )
    return plans


def _replay_cases(
    status: str,
    providers: list[dict[str, Any]],
    source_cases: list[dict[str, Any]],
    boundary_report: dict[str, Any],
) -> list[dict[str, Any]]:
    if status != "ready_for_offline_replay":
        return []
    replay_cases: list[dict[str, Any]] = []
    for provider in providers[:3]:
        provider_id = str(provider.get("id") or "unknown")
        for case in source_cases[:2]:
            eval_id = str(case.get("eval_id") or case.get("id") or "")
            replay_cases.append(
                {
                    "id": f"offline-replay-{provider_id}-{eval_id}",
                    "status": "planned",
                    "provider_id": provider_id,
                    "provider_label": str(provider.get("label") or provider_id),
                    "service_target": str(provider.get("service_target") or provider_id),
                    "fixture_kind": "local_shadow_fixture",
                    "eval_id": eval_id,
                    "query": str(case.get("query") or ""),
                    "display_name": str(case.get("display_name") or eval_id),
                    "baseline_status": str(case.get("baseline_status") or "unknown"),
                    "baseline_chain": "BM25 + canon ledger + entity aliases",
                    "replay_input": _replay_input(case, provider, boundary_report),
                    "expected_delta": _expected_delta(provider_id),
                    "acceptance_criteria": _acceptance_criteria(provider_id),
                    "rollback_checklist": _rollback_checklist(provider),
                    "manual_review_checklist": _case_manual_review_checklist(provider_id),
                    "no_go_conditions": _case_no_go_conditions(),
                }
            )
    return replay_cases


def _replay_input(
    case: dict[str, Any],
    provider: dict[str, Any],
    boundary_report: dict[str, Any],
) -> dict[str, Any]:
    provider_id = str(provider.get("id") or "unknown")
    return {
        "query": str(case.get("query") or ""),
        "eval_id": str(case.get("eval_id") or case.get("id") or ""),
        "expected_item_id": str(case.get("expected_item_id") or ""),
        "diagnosis": str(case.get("diagnosis") or ""),
        "provider_id": provider_id,
        "provider_boundary_refs": _boundary_refs(provider_id, boundary_report),
        "baseline_chain": "BM25 + canon ledger + entity aliases",
        "dry_run_only": True,
    }


def _boundary_refs(provider_id: str, boundary_report: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for cell in boundary_report.get("boundary_cells") or []:
        if cell.get("provider_id") != provider_id or cell.get("status") == "deferred":
            continue
        category_id = str(cell.get("category_id") or "")
        if category_id:
            refs.append(f"boundary:{provider_id}:{category_id}")
    return refs


def _replay_scope(provider_id: str) -> str:
    return {
        "graphrag": "只比较实体关系、伏笔因果和势力/道具链路的召回改善。",
        "zep": "只比较长期事实、实体和对话记忆的召回改善。",
        "temporal_memory": "只比较时间线、状态和资源变化解释的召回改善。",
    }.get(provider_id, "只比较本地失败样本的召回改善。")


def _expected_delta(provider_id: str) -> str:
    return {
        "graphrag": "候选输出应补足关系/因果证据，但不得覆盖本地正史真源。",
        "zep": "候选输出应补足长期事实记忆，但不得要求外部账号或真实同步。",
        "temporal_memory": "候选输出应补足时间/状态解释，但不得改写 state_snapshot。",
    }.get(provider_id, "候选输出只能作为离线对照证据。")


def _acceptance_criteria(provider_id: str) -> list[str]:
    return [
        "验收必须基于固定本地 fixture，可重复运行且无需真实 provider。",
        "候选输出必须比当前 BM25 baseline 更接近 expected item 或人工标注事实。",
        f"{provider_id} 候选收益必须能被人工复核，不能只看模型自评。",
    ]


def _rollback_checklist(provider: dict[str, Any]) -> list[str]:
    return [
        "回退时关闭 provider 开关，继续使用 BM25 + canon ledger + entity aliases。",
        str(provider.get("rollback_strategy") or "回退本地检索链路。"),
        "回退不得删除本地 source_raw、memory、canon ledger、state snapshot 或 overlay。",
    ]


def _case_manual_review_checklist(provider_id: str) -> list[str]:
    return [
        "人工复核候选证据是否真的对应 query 和 expected item。",
        "人工复核候选输出是否引入正史冲突、同名实体误连或过度解释。",
        f"人工复核 {provider_id} 的收益是否足以承担成本、隐私和回滚复杂度。",
    ]


def _case_no_go_conditions() -> list[str]:
    return [
        "不能要求真实付费 Key 或外部账号才能完成 replay。",
        "不能把 replay 候选结果写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        "不能在默认 run_scene 或默认检索链路中自动启用 provider。",
    ]


def _replay_steps(status: str) -> list[dict[str, Any]]:
    if status != "ready_for_offline_replay":
        return []
    return [
        {
            "id": "freeze_fixture",
            "label": "冻结本地 fixture",
            "description": "固定 retrieval eval records、case matrix 和 provider boundary matrix，保证 replay 可复现。",
        },
        {
            "id": "capture_baseline",
            "label": "记录 baseline",
            "description": "记录当前 BM25 + canon ledger + entity aliases 对同一 query 的结果和缺口。",
        },
        {
            "id": "mock_provider_delta",
            "label": "生成 mock delta",
            "description": "只用 deterministic/mockable 候选输出描述 provider 可能改善的证据，不调用外部服务。",
        },
        {
            "id": "manual_review",
            "label": "人工复核",
            "description": "人工检查收益、冲突、隐私、成本、回滚和 no-go 条件。",
        },
        {
            "id": "decision_record",
            "label": "记录决策",
            "description": "只记录是否值得进入 opt-in spike 的建议，不修改项目 artifact。",
        },
    ]


def _replay_gate(
    status: str,
    provider_plans: list[dict[str, Any]],
    replay_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    if status == "ready_for_offline_replay" and provider_plans and replay_cases:
        return {
            "id": "graph_memory_offline_shadow_replay_gate",
            "status": "offline_replay_ready",
            "passed": True,
            "reason": "provider 边界已就绪，可先做本地离线 shadow replay 计划。",
            "provider_plan_count": len(provider_plans),
            "replay_case_count": len(replay_cases),
        }
    if status == "needs_more_evidence":
        return {
            "id": "graph_memory_offline_shadow_replay_gate",
            "status": "collect_more_evidence",
            "passed": False,
            "reason": "provider 边界证据不足，先补 case matrix 和失败样本。",
            "provider_plan_count": len(provider_plans),
            "replay_case_count": len(replay_cases),
        }
    return {
        "id": "graph_memory_offline_shadow_replay_gate",
        "status": "deferred",
        "passed": False,
        "reason": "当前项目未达到离线 shadow replay 触发条件。",
        "provider_plan_count": len(provider_plans),
        "replay_case_count": len(replay_cases),
    }


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    provider_plans: list[dict[str, Any]],
    replay_cases: list[dict[str, Any]],
    replay_steps: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_provider_boundary_status": source_status,
        "status": status,
        "candidate_provider_count": len(provider_plans),
        "provider_plan_count": len(provider_plans),
        "replay_case_count": len(replay_cases),
        "replay_step_count": len(replay_steps),
        "manual_review_required_count": len(
            [item for item in replay_cases if item.get("manual_review_checklist")]
        ),
        "writes_artifacts": False,
        "external_services_required": False,
        "provider_calls": False,
        "uses_graphrag": False,
        "uses_zep": False,
        "uses_vector_store": False,
        "uses_reranker": False,
        "uses_embedding_provider": False,
        "plaintext_key_returned": False,
    }


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    replay_gate: dict[str, Any],
    provider_plans: list[dict[str, Any]],
    replay_cases: list[dict[str, Any]],
    replay_steps: list[dict[str, Any]],
    boundary_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "replay_gate": replay_gate,
        "provider_plans": provider_plans,
        "replay_cases": replay_cases,
        "replay_steps": replay_steps,
        "source_provider_boundary": {
            "version": boundary_report.get("version"),
            "status": boundary_report.get("status"),
            "boundary_gate": boundary_report.get("boundary_gate"),
        },
        "contract": {
            "writes_artifacts": False,
            "external_services_required": False,
            "provider_calls": False,
            "plaintext_key_returned": False,
        },
    }


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_offline_replay":
        return []
    return [
        "人工复核 replay case 是否覆盖真实痛点，而不是为了接 provider 而接 provider。",
        "人工复核成本、隐私、数据同步、回滚和失败降级是否全部有明确答案。",
        "人工复核 provider 候选收益是否能通过固定 fixture 重复证明。",
    ]


def _no_go_conditions(boundary_report: dict[str, Any]) -> list[str]:
    conditions: list[str] = []
    for item in [
        "不能要求真实付费 Key 或外部账号才能完成 replay。",
        "不能把 replay 候选结果写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        "不能把离线 replay 计划当成真实 GraphRAG / Zep / Temporal Memory 接入开关。",
    ] + list(boundary_report.get("no_go_conditions") or []):
        if item not in conditions:
            conditions.append(item)
    return conditions


def _warnings(
    boundary_report: dict[str, Any],
    provider_plans: list[dict[str, Any]],
    replay_cases: list[dict[str, Any]],
) -> list[str]:
    warnings = list(boundary_report.get("warnings") or [])
    if not provider_plans:
        warnings.append("没有可计划的候选 provider，离线 replay 暂缓。")
    if not replay_cases:
        warnings.append("没有可复跑的本地 eval case，先补 retrieval failure samples。")
    return warnings


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_offline_replay":
        return [
            "按离线 replay 计划挑 1 个 provider、1 个项目、1 组 fixture 做 mock replay。",
            "真实 provider spike 前先固化 dry-run 配置、成本上限、隐私说明和回滚验收清单。",
        ]
    if status == "needs_more_evidence":
        return [
            "先补 retrieval eval records、case matrix 和 provider boundary matrix。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 provider replay 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 provider boundary matrix 就绪后再生成离线 shadow replay 计划。",
    ]

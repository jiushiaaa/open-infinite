"""Graph Memory Provider Boundary Matrix MVP.

This report turns the local shadow case matrix into an opt-in provider boundary
matrix. It does not connect GraphRAG, Zep, vector stores, graph databases,
rerankers, embedding providers, or LLMs.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_shadow_case_matrix import (
    GraphMemoryShadowCaseMatrixRequestError,
    get_graph_memory_shadow_case_matrix,
)

VERSION = "graph-memory-provider-boundary-matrix-mvp"


BOUNDARY_CATEGORIES = [
    {
        "id": "opt_in",
        "label": "显式开关",
        "must_pass": True,
        "base_requirement": "必须由用户显式开启 provider spike，不允许默认启用。",
    },
    {
        "id": "cost",
        "label": "成本边界",
        "must_pass": True,
        "base_requirement": "必须先定义成本上限、调用频率、失败预算和手动停止方式。",
    },
    {
        "id": "privacy",
        "label": "隐私边界",
        "must_pass": True,
        "base_requirement": "必须明确哪些本地文本、事实、实体和关系会离开本机。",
    },
    {
        "id": "data_sync",
        "label": "数据同步",
        "must_pass": True,
        "base_requirement": "必须定义同步来源、去重键、删除/重建策略和本地真源优先级。",
    },
    {
        "id": "rollback",
        "label": "回滚策略",
        "must_pass": True,
        "base_requirement": "必须能关闭 provider 并回退到 BM25 + canon ledger + entity aliases。",
    },
    {
        "id": "testing",
        "label": "测试夹具",
        "must_pass": True,
        "base_requirement": "必须先用本地 case matrix 和固定 fixture 做离线 shadow replay。",
    },
    {
        "id": "acceptance",
        "label": "验收门槛",
        "must_pass": True,
        "base_requirement": "必须定义相对现有检索链路的可复核收益门槛。",
    },
    {
        "id": "failure_mode",
        "label": "失败降级",
        "must_pass": True,
        "base_requirement": "必须保证 provider 超时、限流、损坏或无凭证时降级为空态而非 500。",
    },
]


class GraphMemoryProviderBoundaryMatrixRequestError(ValueError):
    """Invalid graph-memory provider boundary request, mapped to HTTP 400."""


def get_graph_memory_provider_boundary_matrix(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only provider boundary matrix."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        case_matrix = get_graph_memory_shadow_case_matrix(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryShadowCaseMatrixRequestError as exc:
        raise GraphMemoryProviderBoundaryMatrixRequestError(str(exc)) from exc

    source_status = str(case_matrix.get("status") or "deferred")
    status = _status(source_status)
    providers = _providers(status, case_matrix)
    boundary_cells = _boundary_cells(status, providers, case_matrix)
    boundary_gate = _boundary_gate(status, providers, boundary_cells)
    summary = _summary(sid, source_status, status, providers, boundary_cells)
    manifest = _manifest(
        generated_at,
        summary,
        boundary_gate,
        providers,
        boundary_cells,
        case_matrix,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_boundary_matrix",
        "status": status,
        "story_slug": sid,
        "source_kind": case_matrix.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "boundary_gate": boundary_gate,
        "providers": providers,
        "boundary_categories": BOUNDARY_CATEGORIES,
        "boundary_cells": boundary_cells,
        "no_go_conditions": _no_go_conditions(case_matrix),
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(case_matrix, providers, boundary_cells),
        "boundaries": [
            "只读整理 GraphRAG、Zep、Temporal Memory 的 provider 接入边界，不写项目 artifact。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开 opt-in spike。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderBoundaryMatrixRequestError("invalid slug")
    return sid


def _status(source_status: str) -> str:
    if source_status == "ready":
        return "ready_for_boundary_review"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    return "deferred"


def _providers(status: str, case_matrix: dict[str, Any]) -> list[dict[str, Any]]:
    providers: list[dict[str, Any]] = []
    for layer in case_matrix.get("layers") or []:
        provider_id = str(layer.get("id") or "unknown")
        source_status = str(layer.get("status") or "deferred")
        provider_status = source_status if status == "ready_for_boundary_review" else "deferred"
        providers.append(
            {
                "id": provider_id,
                "label": str(layer.get("label") or provider_id),
                "service_target": _service_target(provider_id),
                "provider_kind": _provider_kind(provider_id),
                "status": provider_status,
                "source_layer_status": source_status,
                "decision": str(layer.get("decision") or "defer")
                if provider_status != "deferred"
                else "defer",
                "opt_in_required": True,
                "projected_gain_score": int(layer.get("projected_gain_score") or 0)
                if provider_status != "deferred"
                else 0,
                "risk_score": int(layer.get("risk_score") or 0)
                if provider_status != "deferred"
                else 0,
                "recommended_for": _recommended_for(provider_id),
                "local_baseline": str(layer.get("baseline") or "BM25 + canon ledger + entity aliases"),
                "rollback_strategy": str(layer.get("rollback_strategy") or _rollback_strategy(provider_id)),
            }
        )
    return providers


def _service_target(provider_id: str) -> str:
    return {
        "graphrag": "GraphRAG",
        "zep": "Zep",
        "temporal_memory": "Temporal Memory",
    }.get(provider_id, provider_id)


def _provider_kind(provider_id: str) -> str:
    return {
        "graphrag": "graph_retrieval",
        "zep": "long_term_memory_service",
        "temporal_memory": "temporal_state_memory",
    }.get(provider_id, "memory_provider")


def _recommended_for(provider_id: str) -> str:
    return {
        "graphrag": "实体关系、伏笔因果、势力/道具链路经常错乱时再评估。",
        "zep": "希望外置长期记忆服务管理事实、实体和对话记忆时再评估。",
        "temporal_memory": "跨章节状态、时间线和资源变化持续解释不清时再评估。",
    }.get(provider_id, "仅作为后续 opt-in provider spike 候选。")


def _rollback_strategy(provider_id: str) -> str:
    return {
        "graphrag": "关闭图检索 provider，回退到 BM25 + canon ledger + entity aliases。",
        "zep": "断开 Zep 同步，继续读取本地文件型记忆，不删除本地真源。",
        "temporal_memory": "关闭时间记忆 provider，保留 state_snapshot 与 overlay 的只读展示。",
    }.get(provider_id, "关闭 provider，回退本地检索链路。")


def _boundary_cells(
    status: str,
    providers: list[dict[str, Any]],
    case_matrix: dict[str, Any],
) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for provider in providers:
        for category in BOUNDARY_CATEGORIES:
            cells.append(_boundary_cell(status, provider, category, case_matrix))
    return cells


def _boundary_cell(
    status: str,
    provider: dict[str, Any],
    category: dict[str, Any],
    case_matrix: dict[str, Any],
) -> dict[str, Any]:
    provider_status = str(provider.get("status") or "deferred")
    cell_status = "requires_opt_in" if status == "ready_for_boundary_review" and provider_status != "deferred" else "deferred"
    category_id = str(category.get("id") or "unknown")
    return {
        "provider_id": str(provider.get("id") or "unknown"),
        "provider_label": str(provider.get("label") or provider.get("id") or "unknown"),
        "category_id": category_id,
        "category_label": str(category.get("label") or category_id),
        "status": cell_status,
        "must_pass": bool(category.get("must_pass")),
        "risk_level": _risk_level(provider, category_id, cell_status),
        "requirement": _requirement(provider, category),
        "evidence_refs": _evidence_refs(cell_status, category_id, case_matrix),
        "fallback": str(provider.get("rollback_strategy") or _rollback_strategy(str(provider.get("id") or ""))),
    }


def _risk_level(provider: dict[str, Any], category_id: str, cell_status: str) -> str:
    if cell_status == "deferred":
        return "low"
    provider_id = str(provider.get("id") or "")
    if category_id in {"privacy", "data_sync"}:
        return "high" if provider_id in {"zep", "graphrag"} else "medium"
    if category_id in {"cost", "failure_mode"}:
        return "medium"
    return "low"


def _requirement(provider: dict[str, Any], category: dict[str, Any]) -> str:
    target = str(provider.get("service_target") or provider.get("label") or "provider")
    base = str(category.get("base_requirement") or "")
    return f"{target}：{base}"


def _evidence_refs(
    cell_status: str,
    category_id: str,
    case_matrix: dict[str, Any],
) -> list[str]:
    if cell_status == "deferred":
        return []
    refs = [
        f"case_matrix:{case_matrix.get('story_slug') or ''}",
        f"source_status:{case_matrix.get('status') or ''}",
    ]
    if category_id == "testing":
        for case in (case_matrix.get("cases") or [])[:5]:
            eval_id = str(case.get("eval_id") or case.get("id") or "")
            if eval_id:
                refs.append(f"retrieval_eval:{eval_id}")
    return refs


def _boundary_gate(
    status: str,
    providers: list[dict[str, Any]],
    boundary_cells: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_count = len([item for item in providers if item.get("status") in {"candidate", "monitor"}])
    required_count = len([cell for cell in boundary_cells if cell.get("status") == "requires_opt_in"])
    if status == "ready_for_boundary_review" and candidate_count and required_count:
        return {
            "id": "graph_memory_provider_boundary_gate",
            "status": "boundary_matrix_ready",
            "passed": True,
            "reason": "候选记忆层已有本地 case matrix，可先审查 provider opt-in 边界。",
            "candidate_provider_count": candidate_count,
            "required_boundary_count": required_count,
        }
    if status == "needs_more_evidence":
        return {
            "id": "graph_memory_provider_boundary_gate",
            "status": "collect_more_evidence",
            "passed": False,
            "reason": "case matrix 证据不足，先补本地失败样本和 trigger evidence。",
            "candidate_provider_count": candidate_count,
            "required_boundary_count": required_count,
        }
    return {
        "id": "graph_memory_provider_boundary_gate",
        "status": "deferred",
        "passed": False,
        "reason": "当前项目未达到 provider 边界审查触发条件。",
        "candidate_provider_count": candidate_count,
        "required_boundary_count": required_count,
    }


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    providers: list[dict[str, Any]],
    boundary_cells: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_count = len([item for item in providers if item.get("status") in {"candidate", "monitor"}])
    required_count = len([cell for cell in boundary_cells if cell.get("status") == "requires_opt_in"])
    return {
        "story_slug": story_slug,
        "source_case_matrix_status": source_status,
        "status": status,
        "provider_count": len(providers),
        "candidate_provider_count": candidate_count,
        "boundary_category_count": len(BOUNDARY_CATEGORIES),
        "boundary_cell_count": len(boundary_cells),
        "requires_opt_in_count": required_count,
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
    boundary_gate: dict[str, Any],
    providers: list[dict[str, Any]],
    boundary_cells: list[dict[str, Any]],
    case_matrix: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "boundary_gate": boundary_gate,
        "providers": providers,
        "boundary_categories": BOUNDARY_CATEGORIES,
        "boundary_cells": boundary_cells,
        "source_case_matrix": {
            "version": case_matrix.get("version"),
            "status": case_matrix.get("status"),
            "case_gate": case_matrix.get("case_gate"),
            "cases": case_matrix.get("cases") or [],
        },
        "contract": {
            "writes_artifacts": False,
            "external_services_required": False,
            "provider_calls": False,
            "plaintext_key_returned": False,
        },
    }


def _no_go_conditions(case_matrix: dict[str, Any]) -> list[str]:
    conditions = list(case_matrix.get("no_go_conditions") or [])
    extra = [
        "不能要求真实付费 Key 或外部账号才能完成最小验证。",
        "不能把 provider 结果写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        "不能在默认 run_scene 或默认检索链路中自动启用 provider。",
    ]
    for item in extra:
        if item not in conditions:
            conditions.append(item)
    return conditions


def _warnings(
    case_matrix: dict[str, Any],
    providers: list[dict[str, Any]],
    boundary_cells: list[dict[str, Any]],
) -> list[str]:
    warnings = list(case_matrix.get("warnings") or [])
    if not any(item.get("status") in {"candidate", "monitor"} for item in providers):
        warnings.append("没有可审查的候选 provider，边界矩阵暂缓。")
    if not any(cell.get("status") == "requires_opt_in" for cell in boundary_cells):
        warnings.append("没有 requires_opt_in 边界格，先补 case matrix 证据。")
    return warnings


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_boundary_review":
        return [
            "逐项复核 provider 边界，再决定是否进入单 provider、单项目、单 fixture 的 opt-in spike。",
            "真实 spike 前先写 dry-run 配置、成本上限、隐私说明和回滚验收清单。",
        ]
    if status == "needs_more_evidence":
        return [
            "先补 retrieval eval records、case matrix 和 trigger evidence，再生成 provider boundary matrix。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 provider 接入暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 case matrix 出现稳定候选 provider 后再审查 provider 边界。",
    ]

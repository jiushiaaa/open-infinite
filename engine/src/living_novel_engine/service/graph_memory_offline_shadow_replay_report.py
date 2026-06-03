"""Graph Memory Offline Shadow Replay Report MVP.

This report evaluates the offline replay plan with deterministic mock results.
It does not run GraphRAG, Zep, vector stores, graph databases, rerankers,
embedding providers, or LLMs.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_offline_shadow_replay_plan import (
    GraphMemoryOfflineShadowReplayPlanRequestError,
    get_graph_memory_offline_shadow_replay_plan,
)

VERSION = "graph-memory-offline-shadow-replay-report-mvp"


class GraphMemoryOfflineShadowReplayReportRequestError(ValueError):
    """Invalid graph-memory offline replay report request, mapped to HTTP 400."""


def get_graph_memory_offline_shadow_replay_report(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only offline replay result report."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        replay_plan = get_graph_memory_offline_shadow_replay_plan(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryOfflineShadowReplayPlanRequestError as exc:
        raise GraphMemoryOfflineShadowReplayReportRequestError(str(exc)) from exc

    source_status = str(replay_plan.get("status") or "deferred")
    status = _status(source_status)
    case_results = _case_results(status, replay_plan)
    provider_results = _provider_results(status, replay_plan, case_results)
    report_gate = _report_gate(status, provider_results, case_results)
    decision = _decision(status, provider_results, case_results)
    summary = _summary(sid, source_status, status, provider_results, case_results)
    manifest = _manifest(
        generated_at,
        summary,
        report_gate,
        decision,
        provider_results,
        case_results,
        replay_plan,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_offline_shadow_replay_report",
        "status": status,
        "story_slug": sid,
        "source_kind": replay_plan.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "report_gate": report_gate,
        "decision": decision,
        "provider_results": provider_results,
        "case_results": case_results,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": _no_go_conditions(replay_plan),
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(replay_plan, provider_results, case_results),
        "boundaries": [
            "只读生成离线 shadow replay 结果报告，不运行 provider，不写项目 artifact。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开 opt-in spike。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryOfflineShadowReplayReportRequestError("invalid slug")
    return sid


def _status(source_status: str) -> str:
    if source_status == "ready_for_offline_replay":
        return "ready_for_review"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    return "deferred"


def _case_results(status: str, replay_plan: dict[str, Any]) -> list[dict[str, Any]]:
    if status != "ready_for_review":
        return []
    results: list[dict[str, Any]] = []
    for item in replay_plan.get("replay_cases") or []:
        provider_id = str(item.get("provider_id") or "unknown")
        eval_id = str(item.get("eval_id") or "")
        results.append(
            {
                "id": f"offline-replay-result-{provider_id}-{eval_id}",
                "source_case_id": str(item.get("id") or ""),
                "status": "mock_candidate_gain",
                "provider_id": provider_id,
                "provider_label": str(item.get("provider_label") or provider_id),
                "service_target": str(item.get("service_target") or provider_id),
                "fixture_kind": str(item.get("fixture_kind") or "local_shadow_fixture"),
                "eval_id": eval_id,
                "query": str(item.get("query") or ""),
                "display_name": str(item.get("display_name") or eval_id),
                "baseline_status": str(item.get("baseline_status") or "unknown"),
                "baseline_chain": str(item.get("baseline_chain") or "BM25 + canon ledger + entity aliases"),
                "mock_delta": _mock_delta(item),
                "gain_assessment": _gain_assessment(provider_id, item),
                "risk_assessment": _risk_assessment(provider_id),
                "acceptance_status": "candidate_gain_needs_review",
                "failure_mode": _failure_mode(item),
                "manual_review_result": _manual_review_result(provider_id),
                "no_go_conditions": list(item.get("no_go_conditions") or []),
            }
        )
    return results


def _mock_delta(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "dry_run_only": True,
        "provider_id": str(item.get("provider_id") or "unknown"),
        "expected_delta": str(item.get("expected_delta") or ""),
        "baseline_chain": str(item.get("baseline_chain") or "BM25 + canon ledger + entity aliases"),
        "query": str(item.get("query") or ""),
        "candidate_summary": "mock replay 只证明该 case 值得人工复核，不代表真实 provider 已接入。",
    }


def _gain_assessment(provider_id: str, item: dict[str, Any]) -> str:
    query = str(item.get("query") or item.get("eval_id") or "该 case")
    return {
        "graphrag": f"GraphRAG mock 结果显示「{query}」可能从关系/因果图谱中获得候选收益。",
        "zep": f"Zep mock 结果显示「{query}」可能从长期事实记忆中获得候选收益。",
        "temporal_memory": f"Temporal Memory mock 结果显示「{query}」可能从时间/状态记忆中获得候选收益。",
    }.get(provider_id, f"{provider_id} mock 结果显示「{query}」需要人工复核收益。")


def _risk_assessment(provider_id: str) -> str:
    return {
        "graphrag": "主要风险是实体误连、关系过度解释和图谱同步成本。",
        "zep": "主要风险是外部长期记忆服务的隐私、同步和删除/重建策略。",
        "temporal_memory": "主要风险是时间线解释与 state_snapshot / overlay 真源冲突。",
    }.get(provider_id, "主要风险是 provider 结果污染本地真源。")


def _failure_mode(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "fallback": "keep_local_baseline",
        "reason": "mock replay 失败或人工复核不通过时继续使用当前本地检索链路。",
        "rollback_checklist": list(item.get("rollback_checklist") or []),
    }


def _manual_review_result(provider_id: str) -> dict[str, Any]:
    return {
        "status": "required",
        "status_label": "需要人工复核",
        "review_focus": [
            "候选收益是否真实覆盖 query 和 expected item。",
            "候选结果是否引入正史冲突、同名实体误连或过度解释。",
            f"{provider_id} 的收益是否足以承担成本、隐私和回滚复杂度。",
        ],
    }


def _provider_results(
    status: str,
    replay_plan: dict[str, Any],
    case_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if status != "ready_for_review":
        return []
    results: list[dict[str, Any]] = []
    for plan in replay_plan.get("provider_plans") or []:
        provider_id = str(plan.get("provider_id") or "unknown")
        provider_cases = [
            item for item in case_results if item.get("provider_id") == provider_id
        ]
        candidate_count = len(
            [item for item in provider_cases if item.get("status") == "mock_candidate_gain"]
        )
        results.append(
            {
                "provider_id": provider_id,
                "provider_label": str(plan.get("provider_label") or provider_id),
                "service_target": str(plan.get("service_target") or provider_id),
                "status": "manual_review_required" if candidate_count else "collect_more_evidence",
                "case_result_count": len(provider_cases),
                "candidate_gain_count": candidate_count,
                "recommendation": "manual_review_before_opt_in_spike"
                if candidate_count
                else "collect_more_evidence",
                "rollback_strategy": str(plan.get("rollback_strategy") or "回退本地检索链路。"),
            }
        )
    return results


def _report_gate(
    status: str,
    provider_results: list[dict[str, Any]],
    case_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if status == "ready_for_review" and provider_results and case_results:
        return {
            "id": "graph_memory_offline_shadow_replay_report_gate",
            "status": "offline_replay_report_ready",
            "passed": True,
            "reason": "离线 replay plan 已生成 mock result，可进入人工复核。",
            "provider_result_count": len(provider_results),
            "case_result_count": len(case_results),
        }
    if status == "needs_more_evidence":
        return {
            "id": "graph_memory_offline_shadow_replay_report_gate",
            "status": "collect_more_evidence",
            "passed": False,
            "reason": "离线 replay plan 证据不足，先补 provider boundary 和 replay case。",
            "provider_result_count": len(provider_results),
            "case_result_count": len(case_results),
        }
    return {
        "id": "graph_memory_offline_shadow_replay_report_gate",
        "status": "deferred",
        "passed": False,
        "reason": "当前项目未达到离线 replay report 触发条件。",
        "provider_result_count": len(provider_results),
        "case_result_count": len(case_results),
    }


def _decision(
    status: str,
    provider_results: list[dict[str, Any]],
    case_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if status == "ready_for_review" and case_results:
        return {
            "status": "manual_review_required",
            "recommendation": "先人工复核 mock result，再决定是否进入单 provider opt-in spike。",
            "candidate_gain_count": len(
                [item for item in case_results if item.get("status") == "mock_candidate_gain"]
            ),
            "provider_result_count": len(provider_results),
        }
    return {
        "status": "deferred",
        "recommendation": "继续补本地证据，不接真实 provider。",
        "candidate_gain_count": 0,
        "provider_result_count": 0,
    }


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    provider_results: list[dict[str, Any]],
    case_results: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_replay_plan_status": source_status,
        "status": status,
        "provider_result_count": len(provider_results),
        "case_result_count": len(case_results),
        "candidate_gain_count": len(
            [item for item in case_results if item.get("status") == "mock_candidate_gain"]
        ),
        "manual_review_required_count": len(
            [item for item in case_results if item.get("manual_review_result")]
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
    report_gate: dict[str, Any],
    decision: dict[str, Any],
    provider_results: list[dict[str, Any]],
    case_results: list[dict[str, Any]],
    replay_plan: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "report_gate": report_gate,
        "decision": decision,
        "provider_results": provider_results,
        "case_results": case_results,
        "source_replay_plan": {
            "version": replay_plan.get("version"),
            "status": replay_plan.get("status"),
            "replay_gate": replay_plan.get("replay_gate"),
        },
        "contract": {
            "writes_artifacts": False,
            "external_services_required": False,
            "provider_calls": False,
            "plaintext_key_returned": False,
        },
    }


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_review":
        return []
    return [
        "人工复核每个 mock result 是否对应真实长篇痛点。",
        "人工复核候选收益是否超过成本、隐私、同步和回滚复杂度。",
        "人工复核是否仍能用本地 BM25 + canon ledger + entity aliases 解决。",
    ]


def _no_go_conditions(replay_plan: dict[str, Any]) -> list[str]:
    conditions: list[str] = []
    for item in list(replay_plan.get("no_go_conditions") or []) + [
        "不能把 mock replay result 当成真实 provider 结果。",
        "不能要求真实付费 Key 或外部账号才能完成 report。",
        "不能把 report 写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
    ]:
        if item not in conditions:
            conditions.append(item)
    return conditions


def _warnings(
    replay_plan: dict[str, Any],
    provider_results: list[dict[str, Any]],
    case_results: list[dict[str, Any]],
) -> list[str]:
    warnings = list(replay_plan.get("warnings") or [])
    if not provider_results:
        warnings.append("没有可汇总的 provider result，离线 replay report 暂缓。")
    if not case_results:
        warnings.append("没有可汇总的 case result，先生成 offline replay plan。")
    return warnings


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_review":
        return [
            "人工复核 mock result 后，再决定是否进入单 provider、单项目、单 fixture 的 opt-in spike。",
            "真实 spike 前继续固化 dry-run 配置、成本上限、隐私说明和回滚验收清单。",
        ]
    if status == "needs_more_evidence":
        return [
            "先补 provider boundary matrix 与 offline replay plan。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 provider replay report 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 offline replay plan 就绪后再生成 mock report。",
    ]

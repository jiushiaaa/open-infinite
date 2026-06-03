"""Graph Memory Provider Spike Review Gate MVP.

This read-only gate turns deterministic mock result records into a manual
review decision surface. It does not persist review decisions, create provider
configs, read keys, write artifacts, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_mock_result_report import (
    GraphMemoryProviderSpikeMockResultReportRequestError,
    get_graph_memory_provider_spike_mock_result_report,
)

VERSION = "graph-memory-provider-spike-review-gate-mvp"


class GraphMemoryProviderSpikeReviewGateRequestError(ValueError):
    """Invalid graph-memory provider review-gate request, mapped to HTTP 400."""


def get_graph_memory_provider_spike_review_gate(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only provider spike review gate."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        mock_report = get_graph_memory_provider_spike_mock_result_report(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeMockResultReportRequestError as exc:
        raise GraphMemoryProviderSpikeReviewGateRequestError(str(exc)) from exc

    source_status = str(mock_report.get("status") or "deferred")
    provider_reviews = _provider_reviews(mock_report)
    status = _status(source_status, provider_reviews)
    summary = _summary(sid, source_status, status, provider_reviews, mock_report)
    review_gate = _review_gate(status, provider_reviews)
    decision = _decision(status, provider_reviews)
    no_go_conditions = _no_go_conditions(mock_report, provider_reviews)
    manifest = _manifest(
        generated_at,
        summary,
        review_gate,
        decision,
        provider_reviews,
        mock_report,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_review_gate",
        "status": status,
        "story_slug": sid,
        "source_kind": mock_report.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "review_gate": review_gate,
        "decision": decision,
        "provider_reviews": provider_reviews,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(mock_report, provider_reviews),
        "boundaries": [
            "只读生成 provider spike review gate，不保存人工复核结论，不写项目 artifact。",
            "Review Gate 只能说明是否可人工复核，不能自动创建真实 provider 配置。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeReviewGateRequestError("invalid slug")
    return sid


def _status(source_status: str, provider_reviews: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_manual_review" and provider_reviews:
        return "ready_for_manual_review_gate"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _provider_reviews(mock_report: dict[str, Any]) -> list[dict[str, Any]]:
    if mock_report.get("status") != "ready_for_manual_review":
        return []

    reviews: list[dict[str, Any]] = []
    for record in mock_report.get("mock_result_records") or []:
        manual_decision = str(record.get("manual_decision") or "collect_more_evidence")
        gate_decision = _gate_decision(manual_decision)
        review_items = _review_items(record)
        reviews.append(
            {
                "id": f"review-gate-{record.get('provider_id') or 'unknown'}",
                "status": "manual_review_required",
                "provider_id": str(record.get("provider_id") or "unknown"),
                "provider_label": str(record.get("provider_label") or "unknown"),
                "service_target": str(record.get("service_target") or "unknown"),
                "source_record_id": str(record.get("id") or ""),
                "fixture_id": str(record.get("fixture_id") or ""),
                "source_case_id": str(record.get("source_case_id") or ""),
                "eval_id": str(record.get("eval_id") or ""),
                "manual_decision": manual_decision,
                "gate_decision": gate_decision,
                "candidate_gain": manual_decision
                in {"collect_more_evidence", "upgrade_manual_opt_in_spike"},
                "review_item_count": len(review_items),
                "review_items": review_items,
                "gain_summary": str(record.get("gain_summary") or ""),
                "risk_summary": str(record.get("risk_summary") or ""),
                "review_summary": str(record.get("review_summary") or ""),
                "pause_or_upgrade_decision": record.get("pause_or_upgrade_decision")
                or {},
                "evidence_refs": _dedupe(list(record.get("evidence_refs") or [])),
                "no_go_conditions": list(record.get("no_go_conditions") or []),
                "recommendation": _recommendation(gate_decision),
            }
        )
    return reviews


def _gate_decision(manual_decision: str) -> str:
    if manual_decision == "upgrade_manual_opt_in_spike":
        return "manual_approval_required"
    if manual_decision == "pause_no_stable_gain":
        return "pause_no_stable_gain"
    return "collect_more_evidence"


def _review_items(record: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "id": "gain",
            "label": "候选收益",
            "status": "manual_review_required",
            "evidence": str(record.get("gain_summary") or "待人工确认收益。"),
        },
        {
            "id": "risk",
            "label": "误召回与同步风险",
            "status": "manual_review_required",
            "evidence": str(record.get("risk_summary") or "待人工确认风险。"),
        },
        {
            "id": "evidence_refs",
            "label": "证据引用",
            "status": "manual_review_required",
            "evidence": "、".join(str(item) for item in record.get("evidence_refs") or [])
            or "缺少证据引用。",
        },
        {
            "id": "no_go",
            "label": "no-go 条件",
            "status": "manual_review_required",
            "evidence": "、".join(
                str(item) for item in record.get("no_go_conditions") or []
            )
            or "缺少 no-go 条件。",
        },
    ]


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    provider_reviews: list[dict[str, Any]],
    mock_report: dict[str, Any],
) -> dict[str, Any]:
    candidate_count = sum(1 for item in provider_reviews if item["candidate_gain"])
    pause_count = sum(1 for item in provider_reviews if item["gate_decision"].startswith("pause"))
    manual_approval_count = sum(
        1 for item in provider_reviews if item["gate_decision"] == "manual_approval_required"
    )
    return {
        "story_slug": story_slug,
        "source_mock_result_status": source_status,
        "status": status,
        "mock_record_count": len(mock_report.get("mock_result_records") or []),
        "provider_review_count": len(provider_reviews),
        "candidate_gain_count": candidate_count,
        "manual_review_required_count": len(provider_reviews),
        "pause_decision_count": pause_count,
        "manual_approval_required_count": manual_approval_count,
        "no_go_condition_count": len(mock_report.get("no_go_conditions") or []),
        "writes_artifacts": False,
        "result_write_allowed": False,
        "external_services_required": False,
        "provider_calls": False,
        "real_provider_config_allowed": False,
        "uses_graphrag": False,
        "uses_zep": False,
        "uses_vector_store": False,
        "uses_reranker": False,
        "uses_embedding_provider": False,
        "plaintext_key_returned": False,
    }


def _review_gate(
    status: str,
    provider_reviews: list[dict[str, Any]],
) -> dict[str, Any]:
    if status == "ready_for_manual_review_gate":
        return {
            "id": "graph_memory_provider_spike_review_gate",
            "status": "manual_review_gate_ready",
            "passed": True,
            "approval_required": True,
            "automatic_upgrade_allowed": False,
            "real_provider_config_allowed": False,
            "reason": "mock result 已可进入人工复核 gate，但仍不能自动创建真实 provider 配置。",
            "provider_review_count": len(provider_reviews),
        }
    return {
        "id": "graph_memory_provider_spike_review_gate",
        "status": status,
        "passed": False,
        "approval_required": False,
        "automatic_upgrade_allowed": False,
        "real_provider_config_allowed": False,
        "reason": "mock result report 尚不足以进入人工复核 gate。",
        "provider_review_count": len(provider_reviews),
    }


def _decision(
    status: str,
    provider_reviews: list[dict[str, Any]],
) -> dict[str, Any]:
    if status == "ready_for_manual_review_gate":
        return {
            "status": "review_required_no_real_provider_config",
            "recommendation": "人工复核候选收益、风险和 no-go；真实 provider 配置仍需另行显式确认。",
            "next_slice": "Graph Memory Provider Spike Manual Approval Pack",
            "provider_review_count": len(provider_reviews),
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 mock result report 证据，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Review Gate",
        "provider_review_count": len(provider_reviews),
    }


def _no_go_conditions(
    mock_report: dict[str, Any],
    provider_reviews: list[dict[str, Any]],
) -> list[str]:
    items = list(mock_report.get("no_go_conditions") or [])
    for review in provider_reviews:
        items.extend(review.get("no_go_conditions") or [])
    items.extend(
        [
            "不能把 review gate 当成真实 provider 配置许可。",
            "不能保存人工复核结论或自动写入 dry-run result。",
            "不能要求真实付费 Key 或外部账号才能生成 review gate。",
            "不能把 review gate 写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(
    mock_report: dict[str, Any],
    provider_reviews: list[dict[str, Any]],
) -> list[str]:
    warnings = list(mock_report.get("warnings") or [])
    if not provider_reviews:
        warnings.append("没有可复核的 provider review row，先补 mock result report。")
    return _dedupe(warnings)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_manual_review_gate":
        return []
    return [
        "人工复核每个 provider 的候选收益是否来自真实长篇痛点。",
        "人工复核误召回、隐私、成本、数据同步和回滚复杂度。",
        "人工确认 review gate 不能自动升级为真实 provider 配置。",
    ]


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    review_gate: dict[str, Any],
    decision: dict[str, Any],
    provider_reviews: list[dict[str, Any]],
    mock_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "review_gate": review_gate,
        "decision": decision,
        "provider_reviews": provider_reviews,
        "source_mock_result_report": {
            "version": mock_report.get("version"),
            "status": mock_report.get("status"),
            "report_gate": mock_report.get("report_gate"),
        },
        "contract": {
            "writes_artifacts": False,
            "result_write_allowed": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_manual_review_gate":
        return [
            "人工复核 review gate 中的候选收益、风险、no-go 和证据引用。",
            "若仍需真实服务，只能另开显式 opt-in 的人工审批包。",
        ]
    if status == "blocked":
        return [
            "先修复 mock result report blockers，再重新生成 review gate。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 review gate 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 mock result report 就绪后再生成 review gate。",
    ]


def _recommendation(gate_decision: str) -> str:
    if gate_decision == "manual_approval_required":
        return "仅可进入人工审批包，不能自动创建真实 provider 配置。"
    if gate_decision == "pause_no_stable_gain":
        return "暂停真实 provider spike，继续沿用本地检索链路。"
    return "继续收集更多 mock 证据，再决定是否进入人工审批包。"


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

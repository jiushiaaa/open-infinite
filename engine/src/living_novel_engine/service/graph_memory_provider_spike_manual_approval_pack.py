"""Graph Memory Provider Spike Manual Approval Pack MVP.

This read-only pack turns review-gate rows into manual approval materials.
It does not persist signatures, create provider configs, read keys, write
artifacts, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_review_gate import (
    GraphMemoryProviderSpikeReviewGateRequestError,
    get_graph_memory_provider_spike_review_gate,
)

VERSION = "graph-memory-provider-spike-manual-approval-pack-mvp"


class GraphMemoryProviderSpikeManualApprovalPackRequestError(ValueError):
    """Invalid graph-memory provider manual-approval request, mapped to HTTP 400."""


def get_graph_memory_provider_spike_manual_approval_pack(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return deterministic read-only provider spike manual approval materials."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        review_gate = get_graph_memory_provider_spike_review_gate(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeReviewGateRequestError as exc:
        raise GraphMemoryProviderSpikeManualApprovalPackRequestError(str(exc)) from exc

    source_status = str(review_gate.get("status") or "deferred")
    approval_items = _approval_items(review_gate)
    status = _status(source_status, approval_items)
    summary = _summary(sid, source_status, status, approval_items, review_gate)
    approval_pack = _approval_pack(status, approval_items)
    decision = _decision(status, approval_items)
    no_go_conditions = _no_go_conditions(review_gate, approval_items)
    manifest = _manifest(
        generated_at,
        summary,
        approval_pack,
        decision,
        approval_items,
        review_gate,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_manual_approval_pack",
        "status": status,
        "story_slug": sid,
        "source_kind": review_gate.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "approval_pack": approval_pack,
        "decision": decision,
        "approval_items": approval_items,
        "manual_approval_checklist": _manual_approval_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(review_gate, approval_items),
        "boundaries": [
            "只读生成 provider spike manual approval pack，不保存人工签收结论。",
            "审批包只能作为人工 opt-in 前置材料，不能自动创建真实 provider 配置。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeManualApprovalPackRequestError("invalid slug")
    return sid


def _status(source_status: str, approval_items: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_manual_review_gate" and approval_items:
        return "ready_for_manual_approval_pack"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _approval_items(review_gate: dict[str, Any]) -> list[dict[str, Any]]:
    if review_gate.get("status") != "ready_for_manual_review_gate":
        return []

    items: list[dict[str, Any]] = []
    for review in review_gate.get("provider_reviews") or []:
        risk_signoffs = _risk_signoffs(review)
        rollback_confirmations = _rollback_confirmations(review)
        opt_in_materials = _opt_in_materials(review)
        items.append(
            {
                "id": f"manual-approval-{review.get('provider_id') or 'unknown'}",
                "status": "manual_approval_required",
                "provider_id": str(review.get("provider_id") or "unknown"),
                "provider_label": str(review.get("provider_label") or "unknown"),
                "service_target": str(review.get("service_target") or "unknown"),
                "source_review_id": str(review.get("id") or ""),
                "source_record_id": str(review.get("source_record_id") or ""),
                "fixture_id": str(review.get("fixture_id") or ""),
                "source_case_id": str(review.get("source_case_id") or ""),
                "eval_id": str(review.get("eval_id") or ""),
                "manual_decision": str(review.get("manual_decision") or ""),
                "gate_decision": str(review.get("gate_decision") or ""),
                "approval_required": True,
                "manual_signature_required": True,
                "real_provider_config_allowed": False,
                "risk_signoff_count": len(risk_signoffs),
                "rollback_confirmation_count": len(rollback_confirmations),
                "opt_in_material_count": len(opt_in_materials),
                "risk_signoffs": risk_signoffs,
                "rollback_confirmations": rollback_confirmations,
                "opt_in_materials": opt_in_materials,
                "gain_summary": str(review.get("gain_summary") or ""),
                "risk_summary": str(review.get("risk_summary") or ""),
                "evidence_refs": _dedupe(list(review.get("evidence_refs") or [])),
                "no_go_conditions": list(review.get("no_go_conditions") or []),
                "recommendation": "仅可准备人工审批材料，不能自动创建真实 provider 配置。",
            }
        )
    return items


def _risk_signoffs(review: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "id": "candidate_gain",
            "label": "候选收益已人工确认",
            "status": "signature_required",
            "evidence": str(review.get("gain_summary") or "待确认候选收益。"),
        },
        {
            "id": "misretrieval_risk",
            "label": "误召回风险已人工确认",
            "status": "signature_required",
            "evidence": str(review.get("risk_summary") or "待确认误召回风险。"),
        },
        {
            "id": "privacy_cost",
            "label": "隐私、成本与账号风险已人工确认",
            "status": "signature_required",
            "evidence": "真实付费服务、外部账号与数据同步仍禁止自动启用。",
        },
        {
            "id": "no_auto_config",
            "label": "禁止自动创建真实 provider 配置",
            "status": "signature_required",
            "evidence": "审批包只读生成，不写配置、不保存签名、不调用外部服务。",
        },
    ]


def _rollback_confirmations(review: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "id": "local_retrieval_fallback",
            "label": "回滚到本地检索链路",
            "status": "confirmation_required",
            "evidence": "BM25 + canon ledger + entity aliases 保持默认可用。",
        },
        {
            "id": "no_artifact_mutation",
            "label": "不修改既有 artifact",
            "status": "confirmation_required",
            "evidence": "不覆盖 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        },
        {
            "id": "provider_disable_path",
            "label": "真实 provider 可完全停用",
            "status": "confirmation_required",
            "evidence": str(review.get("recommendation") or "真实 provider 仍需另行 opt-in。"),
        },
    ]


def _opt_in_materials(review: dict[str, Any]) -> list[dict[str, str]]:
    refs = _dedupe(list(review.get("evidence_refs") or []))
    return [
        {
            "id": "fixture",
            "label": "dry-run fixture",
            "value": str(review.get("fixture_id") or ""),
        },
        {
            "id": "eval_case",
            "label": "eval case",
            "value": str(review.get("eval_id") or review.get("source_case_id") or ""),
        },
        {
            "id": "gate_decision",
            "label": "review gate decision",
            "value": str(review.get("gate_decision") or ""),
        },
        {
            "id": "evidence_refs",
            "label": "evidence refs",
            "value": "、".join(refs),
        },
    ]


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    approval_items: list[dict[str, Any]],
    review_gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_review_gate_status": source_status,
        "status": status,
        "provider_review_count": int(
            (review_gate.get("summary") or {}).get("provider_review_count") or 0
        ),
        "approval_item_count": len(approval_items),
        "risk_signoff_count": sum(item["risk_signoff_count"] for item in approval_items),
        "rollback_confirmation_count": sum(
            item["rollback_confirmation_count"] for item in approval_items
        ),
        "opt_in_material_count": sum(
            item["opt_in_material_count"] for item in approval_items
        ),
        "no_go_condition_count": len(review_gate.get("no_go_conditions") or []),
        "writes_artifacts": False,
        "approval_write_allowed": False,
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


def _approval_pack(
    status: str,
    approval_items: list[dict[str, Any]],
) -> dict[str, Any]:
    if status == "ready_for_manual_approval_pack":
        return {
            "id": "graph_memory_provider_spike_manual_approval_pack",
            "status": "manual_approval_pack_ready",
            "ready": True,
            "approval_required": True,
            "manual_signature_required": True,
            "automatic_upgrade_allowed": False,
            "real_provider_config_allowed": False,
            "approval_item_count": len(approval_items),
            "reason": "review gate 已可汇总为人工审批包，但仍不能自动创建真实 provider 配置。",
        }
    return {
        "id": "graph_memory_provider_spike_manual_approval_pack",
        "status": status,
        "ready": False,
        "approval_required": False,
        "manual_signature_required": False,
        "automatic_upgrade_allowed": False,
        "real_provider_config_allowed": False,
        "approval_item_count": len(approval_items),
        "reason": "review gate 尚不足以生成审批包。",
    }


def _decision(
    status: str,
    approval_items: list[dict[str, Any]],
) -> dict[str, Any]:
    if status == "ready_for_manual_approval_pack":
        return {
            "status": "approval_pack_ready_no_real_provider_config",
            "recommendation": "只读审批包已就绪；真实 provider 配置仍需另行显式人工确认。",
            "next_slice": "Graph Memory Provider Spike Manual Approval Evidence Checklist",
            "approval_item_count": len(approval_items),
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 review gate 证据，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Manual Approval Pack",
        "approval_item_count": len(approval_items),
    }


def _no_go_conditions(
    review_gate: dict[str, Any],
    approval_items: list[dict[str, Any]],
) -> list[str]:
    items = list(review_gate.get("no_go_conditions") or [])
    for approval in approval_items:
        items.extend(approval.get("no_go_conditions") or [])
    items.extend(
        [
            "不能把 manual approval pack 当成真实 provider 配置许可。",
            "不能写真实 provider 配置或保存人工签收结果。",
            "不能要求真实付费 Key 或外部账号才能生成审批包。",
            "不能把审批包写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(
    review_gate: dict[str, Any],
    approval_items: list[dict[str, Any]],
) -> list[str]:
    warnings = list(review_gate.get("warnings") or [])
    if not approval_items:
        warnings.append("没有可审批的 provider review row，先补 review gate。")
    return _dedupe(warnings)


def _manual_approval_checklist(status: str) -> list[str]:
    if status != "ready_for_manual_approval_pack":
        return []
    return [
        "人工确认每个 provider 的风险签收项均可接受。",
        "人工确认回滚路径不依赖外部服务或未提交配置。",
        "人工确认审批包不能自动升级为真实 provider 配置。",
    ]


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    approval_pack: dict[str, Any],
    decision: dict[str, Any],
    approval_items: list[dict[str, Any]],
    review_gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "approval_pack": approval_pack,
        "decision": decision,
        "approval_items": approval_items,
        "source_review_gate": {
            "version": review_gate.get("version"),
            "status": review_gate.get("status"),
            "review_gate": review_gate.get("review_gate"),
        },
        "contract": {
            "writes_artifacts": False,
            "approval_write_allowed": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_manual_approval_pack":
        return [
            "人工核对审批包中的风险签收、回滚确认和 opt-in 材料。",
            "若仍需真实服务，只能另开显式 opt-in spike，不能由本报告自动创建配置。",
        ]
    if status == "blocked":
        return [
            "先修复 review gate blockers，再重新生成审批包。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持审批包暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 review gate 就绪后再生成 manual approval pack。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

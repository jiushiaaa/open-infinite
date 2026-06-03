"""Graph Memory Provider Spike Manual Approval Evidence Checklist MVP.

This read-only checklist turns a manual approval pack into evidence and gap
rows. It does not persist signatures, create provider configs, read keys,
write artifacts, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_manual_approval_pack import (
    GraphMemoryProviderSpikeManualApprovalPackRequestError,
    get_graph_memory_provider_spike_manual_approval_pack,
)

VERSION = "graph-memory-provider-spike-manual-approval-evidence-checklist-mvp"


class GraphMemoryProviderSpikeManualApprovalEvidenceChecklistRequestError(ValueError):
    """Invalid graph-memory provider approval-evidence request, mapped to HTTP 400."""


def get_graph_memory_provider_spike_manual_approval_evidence_checklist(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return deterministic read-only approval evidence checklist rows."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        approval_pack = get_graph_memory_provider_spike_manual_approval_pack(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeManualApprovalPackRequestError as exc:
        raise GraphMemoryProviderSpikeManualApprovalEvidenceChecklistRequestError(
            str(exc)
        ) from exc

    source_status = str(approval_pack.get("status") or "deferred")
    checklist_items = _checklist_items(approval_pack)
    status = _status(source_status, checklist_items)
    summary = _summary(sid, source_status, status, checklist_items, approval_pack)
    evidence_checklist = _evidence_checklist(status, checklist_items)
    decision = _decision(status, checklist_items)
    no_go_conditions = _no_go_conditions(approval_pack, checklist_items)
    manifest = _manifest(
        generated_at,
        summary,
        evidence_checklist,
        decision,
        checklist_items,
        approval_pack,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_manual_approval_evidence_checklist",
        "status": status,
        "story_slug": sid,
        "source_kind": approval_pack.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "evidence_checklist": evidence_checklist,
        "decision": decision,
        "checklist_items": checklist_items,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(approval_pack, checklist_items),
        "boundaries": [
            "只读生成 approval evidence checklist，不保存人工签收结论。",
            "Evidence Checklist 只能指出证据和签收缺口，不能自动创建真实 provider 配置。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeManualApprovalEvidenceChecklistRequestError(
            "invalid slug"
        )
    return sid


def _status(source_status: str, checklist_items: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_manual_approval_pack" and checklist_items:
        return "ready_for_manual_approval_evidence_checklist"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _checklist_items(approval_pack: dict[str, Any]) -> list[dict[str, Any]]:
    if approval_pack.get("status") != "ready_for_manual_approval_pack":
        return []

    items: list[dict[str, Any]] = []
    for approval in approval_pack.get("approval_items") or []:
        pending_signoffs = [
            item
            for item in approval.get("risk_signoffs") or []
            if item.get("status") == "signature_required"
        ]
        material_gaps = [
            item
            for item in approval.get("opt_in_materials") or []
            if not str(item.get("value") or "").strip()
        ]
        rollback_material_gaps = [
            item
            for item in approval.get("rollback_confirmations") or []
            if not str(item.get("evidence") or "").strip()
        ]
        items.append(
            {
                "id": f"approval-evidence-{approval.get('provider_id') or 'unknown'}",
                "status": _item_status(pending_signoffs, material_gaps, rollback_material_gaps),
                "provider_id": str(approval.get("provider_id") or "unknown"),
                "provider_label": str(approval.get("provider_label") or "unknown"),
                "service_target": str(approval.get("service_target") or "unknown"),
                "source_approval_id": str(approval.get("id") or ""),
                "source_review_id": str(approval.get("source_review_id") or ""),
                "fixture_id": str(approval.get("fixture_id") or ""),
                "eval_id": str(approval.get("eval_id") or ""),
                "gate_decision": str(approval.get("gate_decision") or ""),
                "evidence_status": _evidence_status(
                    pending_signoffs,
                    material_gaps,
                    rollback_material_gaps,
                ),
                "pending_signoff_count": len(pending_signoffs),
                "material_gap_count": len(material_gaps),
                "rollback_material_gap_count": len(rollback_material_gaps),
                "pending_signoffs": pending_signoffs,
                "material_gaps": material_gaps,
                "rollback_material_gaps": rollback_material_gaps,
                "available_materials": list(approval.get("opt_in_materials") or []),
                "rollback_confirmations": list(
                    approval.get("rollback_confirmations") or []
                ),
                "evidence_refs": _dedupe(list(approval.get("evidence_refs") or [])),
                "no_go_conditions": list(approval.get("no_go_conditions") or []),
                "recommendation": "材料已可核对，但人工签收未完成前不能进入真实 provider 配置。",
            }
        )
    return items


def _item_status(
    pending_signoffs: list[dict[str, Any]],
    material_gaps: list[dict[str, Any]],
    rollback_material_gaps: list[dict[str, Any]],
) -> str:
    if material_gaps or rollback_material_gaps:
        return "materials_gap"
    if pending_signoffs:
        return "manual_signoff_required"
    return "complete_no_real_config"


def _evidence_status(
    pending_signoffs: list[dict[str, Any]],
    material_gaps: list[dict[str, Any]],
    rollback_material_gaps: list[dict[str, Any]],
) -> str:
    if material_gaps or rollback_material_gaps:
        return "materials_gap"
    if pending_signoffs:
        return "materials_ready_signoff_pending"
    return "materials_ready"


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    checklist_items: list[dict[str, Any]],
    approval_pack: dict[str, Any],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_approval_pack_status": source_status,
        "status": status,
        "approval_item_count": int(
            (approval_pack.get("summary") or {}).get("approval_item_count") or 0
        ),
        "checklist_item_count": len(checklist_items),
        "pending_signoff_count": sum(
            item["pending_signoff_count"] for item in checklist_items
        ),
        "material_gap_count": sum(item["material_gap_count"] for item in checklist_items),
        "rollback_material_gap_count": sum(
            item["rollback_material_gap_count"] for item in checklist_items
        ),
        "no_go_condition_count": len(approval_pack.get("no_go_conditions") or []),
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


def _evidence_checklist(
    status: str,
    checklist_items: list[dict[str, Any]],
) -> dict[str, Any]:
    pending = sum(item["pending_signoff_count"] for item in checklist_items)
    material_gaps = sum(item["material_gap_count"] for item in checklist_items)
    rollback_gaps = sum(item["rollback_material_gap_count"] for item in checklist_items)
    if status == "ready_for_manual_approval_evidence_checklist":
        return {
            "id": "graph_memory_provider_spike_manual_approval_evidence_checklist",
            "status": "evidence_checklist_ready",
            "ready": True,
            "manual_signoff_required": pending > 0,
            "materials_complete": material_gaps == 0 and rollback_gaps == 0,
            "automatic_upgrade_allowed": False,
            "real_provider_config_allowed": False,
            "checklist_item_count": len(checklist_items),
            "reason": "审批证据核对表已就绪；人工签收完成前仍禁止真实 provider 配置。",
        }
    return {
        "id": "graph_memory_provider_spike_manual_approval_evidence_checklist",
        "status": status,
        "ready": False,
        "manual_signoff_required": False,
        "materials_complete": False,
        "automatic_upgrade_allowed": False,
        "real_provider_config_allowed": False,
        "checklist_item_count": len(checklist_items),
        "reason": "manual approval pack 尚不足以生成审批证据核对表。",
    }


def _decision(
    status: str,
    checklist_items: list[dict[str, Any]],
) -> dict[str, Any]:
    if status == "ready_for_manual_approval_evidence_checklist":
        return {
            "status": "checklist_ready_no_real_provider_config",
            "recommendation": "只读证据核对表已就绪；真实 provider 配置仍需另行显式人工确认。",
            "next_slice": "Graph Memory Provider Spike Opt-in Evidence Snapshot",
            "checklist_item_count": len(checklist_items),
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 manual approval pack 证据，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Manual Approval Evidence Checklist",
        "checklist_item_count": len(checklist_items),
    }


def _no_go_conditions(
    approval_pack: dict[str, Any],
    checklist_items: list[dict[str, Any]],
) -> list[str]:
    items = list(approval_pack.get("no_go_conditions") or [])
    for checklist in checklist_items:
        items.extend(checklist.get("no_go_conditions") or [])
    items.extend(
        [
            "不能把 approval evidence checklist 当成真实 provider 配置许可。",
            "不能保存人工签名或把待签收项标记为已完成。",
            "不能要求真实付费 Key 或外部账号才能生成核对表。",
            "不能把核对表写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(
    approval_pack: dict[str, Any],
    checklist_items: list[dict[str, Any]],
) -> list[str]:
    warnings = list(approval_pack.get("warnings") or [])
    if not checklist_items:
        warnings.append("没有可核对的 approval item，先补 manual approval pack。")
    return _dedupe(warnings)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_manual_approval_evidence_checklist":
        return []
    return [
        "人工逐项核对 pending signoff 是否仍为待签收。",
        "人工确认 fixture、eval case、evidence refs 和回滚材料没有缺口。",
        "人工确认核对表不能自动升级为真实 provider 配置。",
    ]


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    evidence_checklist: dict[str, Any],
    decision: dict[str, Any],
    checklist_items: list[dict[str, Any]],
    approval_pack: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "evidence_checklist": evidence_checklist,
        "decision": decision,
        "checklist_items": checklist_items,
        "source_manual_approval_pack": {
            "version": approval_pack.get("version"),
            "status": approval_pack.get("status"),
            "approval_pack": approval_pack.get("approval_pack"),
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
    if status == "ready_for_manual_approval_evidence_checklist":
        return [
            "人工核对 pending signoff、材料缺口和回滚缺口。",
            "若仍需真实服务，只能另开显式 opt-in spike，不能由本报告自动创建配置。",
        ]
    if status == "blocked":
        return [
            "先修复 manual approval pack blockers，再重新生成核对表。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持核对表暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 manual approval pack 就绪后再生成 evidence checklist。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

"""Graph Memory Provider Spike Opt-in Evidence Snapshot MVP.

This read-only snapshot turns the approval evidence checklist into an
opt-in evidence view. It does not save approvals, create provider configs,
read keys, write artifacts, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_manual_approval_evidence_checklist import (
    GraphMemoryProviderSpikeManualApprovalEvidenceChecklistRequestError,
    get_graph_memory_provider_spike_manual_approval_evidence_checklist,
)

VERSION = "graph-memory-provider-spike-opt-in-evidence-snapshot-mvp"


class GraphMemoryProviderSpikeOptInEvidenceSnapshotRequestError(ValueError):
    """Invalid graph-memory provider opt-in snapshot request, mapped to HTTP 400."""


def get_graph_memory_provider_spike_opt_in_evidence_snapshot(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return deterministic read-only opt-in evidence snapshot rows."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        checklist = get_graph_memory_provider_spike_manual_approval_evidence_checklist(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeManualApprovalEvidenceChecklistRequestError as exc:
        raise GraphMemoryProviderSpikeOptInEvidenceSnapshotRequestError(str(exc)) from exc

    source_status = str(checklist.get("status") or "deferred")
    snapshot_items = _snapshot_items(checklist)
    status = _status(source_status, snapshot_items)
    summary = _summary(sid, source_status, status, snapshot_items, checklist)
    opt_in_snapshot = _opt_in_snapshot(status, snapshot_items, summary)
    decision = _decision(status, snapshot_items, summary)
    no_go_conditions = _no_go_conditions(checklist, snapshot_items)
    manifest = _manifest(
        generated_at,
        summary,
        opt_in_snapshot,
        decision,
        snapshot_items,
        checklist,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_opt_in_evidence_snapshot",
        "status": status,
        "story_slug": sid,
        "source_kind": checklist.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "opt_in_snapshot": opt_in_snapshot,
        "decision": decision,
        "snapshot_items": snapshot_items,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(checklist, snapshot_items),
        "boundaries": [
            "只读生成 opt-in evidence snapshot，不保存人工签收或审批结论。",
            "Opt-in Evidence Snapshot 只能展示待签收与阻塞原因，不能自动创建真实 provider 配置。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeOptInEvidenceSnapshotRequestError("invalid slug")
    return sid


def _status(source_status: str, snapshot_items: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_manual_approval_evidence_checklist" and snapshot_items:
        return "ready_for_opt_in_evidence_snapshot"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _snapshot_items(checklist: dict[str, Any]) -> list[dict[str, Any]]:
    if checklist.get("status") != "ready_for_manual_approval_evidence_checklist":
        return []

    items: list[dict[str, Any]] = []
    for source in checklist.get("checklist_items") or []:
        signoff_todos = list(source.get("pending_signoffs") or [])
        material_gaps = list(source.get("material_gaps") or [])
        rollback_material_gaps = list(source.get("rollback_material_gaps") or [])
        blocker_reasons = _blocker_reasons(
            signoff_todos,
            material_gaps,
            rollback_material_gaps,
        )
        items.append(
            {
                "id": f"opt-in-evidence-{source.get('provider_id') or 'unknown'}",
                "status": _item_status(
                    signoff_todos,
                    material_gaps,
                    rollback_material_gaps,
                ),
                "provider_id": str(source.get("provider_id") or "unknown"),
                "provider_label": str(source.get("provider_label") or "unknown"),
                "service_target": str(source.get("service_target") or "unknown"),
                "source_checklist_id": str(source.get("id") or ""),
                "source_approval_id": str(source.get("source_approval_id") or ""),
                "source_review_id": str(source.get("source_review_id") or ""),
                "fixture_id": str(source.get("fixture_id") or ""),
                "eval_id": str(source.get("eval_id") or ""),
                "evidence_status": str(source.get("evidence_status") or ""),
                "signoff_todo_count": len(signoff_todos),
                "material_gap_count": len(material_gaps),
                "rollback_material_gap_count": len(rollback_material_gaps),
                "blocker_count": len(blocker_reasons),
                "signoff_todos": signoff_todos,
                "material_gaps": material_gaps,
                "rollback_material_gaps": rollback_material_gaps,
                "available_materials": list(source.get("available_materials") or []),
                "evidence_refs": _dedupe(list(source.get("evidence_refs") or [])),
                "no_go_conditions": list(source.get("no_go_conditions") or []),
                "blocker_reasons": blocker_reasons,
                "recommendation": _item_recommendation(blocker_reasons),
            }
        )
    return items


def _item_status(
    signoff_todos: list[dict[str, Any]],
    material_gaps: list[dict[str, Any]],
    rollback_material_gaps: list[dict[str, Any]],
) -> str:
    if material_gaps or rollback_material_gaps:
        return "blocked_by_material_gap"
    if signoff_todos:
        return "blocked_by_pending_signoff"
    return "materials_ready_real_config_still_blocked"


def _blocker_reasons(
    signoff_todos: list[dict[str, Any]],
    material_gaps: list[dict[str, Any]],
    rollback_material_gaps: list[dict[str, Any]],
) -> list[str]:
    reasons: list[str] = []
    if signoff_todos:
        reasons.append("人工签收仍待完成，不能进入真实 provider 配置。")
    if material_gaps:
        reasons.append("opt-in 材料仍有缺口。")
    if rollback_material_gaps:
        reasons.append("回滚材料仍有缺口。")
    if not reasons:
        reasons.append("材料已齐，但本快照仍不能自动开启真实 provider 配置。")
    return reasons


def _item_recommendation(blocker_reasons: list[str]) -> str:
    if any("签收" in reason for reason in blocker_reasons):
        return "先完成人工签收和复核，再另开显式真实 provider opt-in spike。"
    if any("缺口" in reason for reason in blocker_reasons):
        return "先补齐 opt-in 与回滚材料，不创建真实 provider 配置。"
    return "仅保留证据快照；如需真实 provider，必须另行显式审批。"


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    snapshot_items: list[dict[str, Any]],
    checklist: dict[str, Any],
) -> dict[str, Any]:
    blocker_count = sum(item["blocker_count"] for item in snapshot_items)
    return {
        "story_slug": story_slug,
        "source_evidence_checklist_status": source_status,
        "status": status,
        "checklist_item_count": int(
            (checklist.get("summary") or {}).get("checklist_item_count") or 0
        ),
        "snapshot_item_count": len(snapshot_items),
        "signoff_todo_count": sum(item["signoff_todo_count"] for item in snapshot_items),
        "material_gap_count": sum(item["material_gap_count"] for item in snapshot_items),
        "rollback_material_gap_count": sum(
            item["rollback_material_gap_count"] for item in snapshot_items
        ),
        "blocker_count": blocker_count,
        "no_go_condition_count": len(checklist.get("no_go_conditions") or []),
        "writes_artifacts": False,
        "snapshot_write_allowed": False,
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


def _opt_in_snapshot(
    status: str,
    snapshot_items: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    if status == "ready_for_opt_in_evidence_snapshot":
        return {
            "id": "graph_memory_provider_spike_opt_in_evidence_snapshot",
            "status": "opt_in_evidence_snapshot_ready",
            "ready": True,
            "opt_in_blocked": summary["blocker_count"] > 0,
            "real_provider_config_allowed": False,
            "snapshot_item_count": len(snapshot_items),
            "reason": "opt-in 证据快照已就绪；待签收项完成前仍禁止真实 provider 配置。",
        }
    return {
        "id": "graph_memory_provider_spike_opt_in_evidence_snapshot",
        "status": status,
        "ready": False,
        "opt_in_blocked": True,
        "real_provider_config_allowed": False,
        "snapshot_item_count": len(snapshot_items),
        "reason": "approval evidence checklist 尚不足以生成 opt-in 证据快照。",
    }


def _decision(
    status: str,
    snapshot_items: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    if status == "ready_for_opt_in_evidence_snapshot":
        return {
            "status": "snapshot_ready_real_provider_still_blocked",
            "recommendation": "只读 opt-in 证据快照已就绪；真实 provider 配置仍需另行显式人工确认。",
            "next_slice": "Graph Memory Provider Spike Opt-in No-go Matrix",
            "snapshot_item_count": len(snapshot_items),
            "blocker_count": summary["blocker_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 approval evidence checklist 证据，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Opt-in Evidence Snapshot",
        "snapshot_item_count": len(snapshot_items),
        "blocker_count": summary["blocker_count"],
    }


def _no_go_conditions(
    checklist: dict[str, Any],
    snapshot_items: list[dict[str, Any]],
) -> list[str]:
    items = list(checklist.get("no_go_conditions") or [])
    for snapshot in snapshot_items:
        items.extend(snapshot.get("no_go_conditions") or [])
    items.extend(
        [
            "不能把 opt-in evidence snapshot 当成真实 provider 配置许可。",
            "不能保存人工签名或把待签收项标记为已完成。",
            "不能要求真实付费 Key 或外部账号才能生成证据快照。",
            "不能把证据快照写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(
    checklist: dict[str, Any],
    snapshot_items: list[dict[str, Any]],
) -> list[str]:
    warnings = list(checklist.get("warnings") or [])
    if not snapshot_items:
        warnings.append("没有可生成 opt-in 快照的 checklist item，先补 approval evidence checklist。")
    return _dedupe(warnings)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_opt_in_evidence_snapshot":
        return []
    return [
        "人工核对所有 signoff todo 是否仍保持待签收状态。",
        "人工确认 opt-in 证据快照没有被写入真实 provider 配置。",
        "人工确认真实 provider spike 必须另行显式审批，不能由本快照自动触发。",
    ]


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    opt_in_snapshot: dict[str, Any],
    decision: dict[str, Any],
    snapshot_items: list[dict[str, Any]],
    checklist: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "opt_in_snapshot": opt_in_snapshot,
        "decision": decision,
        "snapshot_items": snapshot_items,
        "source_evidence_checklist": {
            "version": checklist.get("version"),
            "status": checklist.get("status"),
            "evidence_checklist": checklist.get("evidence_checklist"),
        },
        "contract": {
            "writes_artifacts": False,
            "snapshot_write_allowed": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_opt_in_evidence_snapshot":
        return [
            "人工核对 signoff todo、材料缺口、回滚缺口和 no-go 条件。",
            "若仍需真实服务，只能另开显式 opt-in spike，不能由本快照自动创建配置。",
        ]
    if status == "blocked":
        return [
            "先修复 approval evidence checklist blockers，再重新生成 opt-in 证据快照。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 opt-in 证据快照暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 approval evidence checklist 就绪后再生成证据快照。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

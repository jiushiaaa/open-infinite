"""Graph Memory Provider Spike Opt-in Decision Ledger Preview MVP.

This read-only preview turns the review packet into decision ledger rows.
It does not save signoffs, create provider configs, read keys, write artifacts,
or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_opt_in_review_packet import (
    GraphMemoryProviderSpikeOptInReviewPacketRequestError,
    get_graph_memory_provider_spike_opt_in_review_packet,
)

VERSION = "graph-memory-provider-spike-opt-in-decision-ledger-preview-mvp"


class GraphMemoryProviderSpikeOptInDecisionLedgerPreviewRequestError(ValueError):
    """Invalid graph-memory provider opt-in decision ledger preview request."""


def get_graph_memory_provider_spike_opt_in_decision_ledger_preview(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return deterministic read-only decision ledger preview rows."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        packet = get_graph_memory_provider_spike_opt_in_review_packet(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeOptInReviewPacketRequestError as exc:
        raise GraphMemoryProviderSpikeOptInDecisionLedgerPreviewRequestError(
            str(exc)
        ) from exc

    source_status = str(packet.get("status") or "deferred")
    ledger_rows = _ledger_rows(packet)
    status = _status(source_status, ledger_rows)
    summary = _summary(sid, source_status, status, ledger_rows, packet)
    preview = _decision_ledger_preview(status, ledger_rows, summary)
    decision = _decision(status, ledger_rows, summary)
    ledger_preview_materials = _ledger_preview_materials(status, ledger_rows)
    no_go_conditions = _no_go_conditions(packet, ledger_rows)
    manifest = _manifest(
        generated_at,
        summary,
        preview,
        decision,
        ledger_rows,
        packet,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_opt_in_decision_ledger_preview",
        "status": status,
        "story_slug": sid,
        "source_kind": packet.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "decision_ledger_preview": preview,
        "decision": decision,
        "ledger_rows": ledger_rows,
        "ledger_preview_materials": ledger_preview_materials,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(packet, ledger_rows),
        "boundaries": [
            "只读生成 opt-in decision ledger preview，不保存签名或复核结论。",
            "Decision Ledger Preview 只能展示未来应记录字段，不能自动创建真实 provider 配置。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeOptInDecisionLedgerPreviewRequestError(
            "invalid slug"
        )
    return sid


def _status(source_status: str, rows: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_opt_in_review_packet" and rows:
        return "ready_for_opt_in_decision_ledger_preview"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _ledger_rows(packet: dict[str, Any]) -> list[dict[str, Any]]:
    if packet.get("status") != "ready_for_opt_in_review_packet":
        return []

    rows: list[dict[str, Any]] = []
    for section in packet.get("packet_sections") or []:
        pending_fields = _pending_signoff_fields(section)
        decision_fields = _decision_fields(section)
        rows.append(
            {
                "id": f"decision-ledger-preview-{section.get('provider_id') or 'unknown'}",
                "status": "blocked" if section.get("pause_required") else "review",
                "provider_id": str(section.get("provider_id") or "unknown"),
                "provider_label": str(section.get("provider_label") or "unknown"),
                "service_target": str(section.get("service_target") or "unknown"),
                "source_review_packet_section_id": str(section.get("id") or ""),
                "source_checklist_section_id": str(
                    section.get("source_checklist_section_id") or ""
                ),
                "fixture_id": str(section.get("fixture_id") or ""),
                "eval_id": str(section.get("eval_id") or ""),
                "evidence_item_count": int(section.get("evidence_item_count") or 0),
                "blocked_step_count": int(section.get("blocked_step_count") or 0),
                "pause_material_count": len(section.get("pause_materials") or []),
                "escalation_material_count": len(
                    section.get("escalation_materials") or []
                ),
                "pending_signoff_fields": pending_fields,
                "decision_fields": decision_fields,
                "preview_notes": _preview_notes(section),
                "audit_refs": _dedupe(list(section.get("evidence_refs") or [])),
                "approved": False,
                "ledger_write_allowed": False,
                "real_provider_config_allowed": False,
            }
        )
    return rows


def _pending_signoff_fields(section: dict[str, Any]) -> list[dict[str, Any]]:
    field_specs = [
        ("reviewer_name", "复核人"),
        ("reviewed_at", "复核时间"),
        ("risk_signoff", "风险签收"),
        ("rollback_signoff", "回滚确认"),
        ("pause_materials_confirmed", "暂停材料确认"),
    ]
    return [
        {
            "id": f"{section.get('provider_id') or 'unknown'}-{field_id}",
            "field": field_id,
            "label": label,
            "value": None,
            "required": True,
            "saved": False,
        }
        for field_id, label in field_specs
    ]


def _decision_fields(section: dict[str, Any]) -> dict[str, Any]:
    return {
        "target_decision": "pause_real_provider",
        "pause_required": bool(section.get("pause_required")),
        "blocked_step_count": int(section.get("blocked_step_count") or 0),
        "evidence_item_count": int(section.get("evidence_item_count") or 0),
        "approved": False,
        "can_enable_real_provider": False,
        "reason": "只读预览字段，不能保存为审批结论。",
    }


def _preview_notes(section: dict[str, Any]) -> list[str]:
    notes = [
        "该 row 只是未来 ledger 字段预览，不写入项目文件。",
        "所有签收字段默认 value=null、saved=false。",
    ]
    if section.get("pause_required"):
        notes.append("仍有暂停材料，真实 provider 配置保持禁止。")
    notes.append(str(section.get("recommendation") or "保持只读复核。"))
    return _dedupe(notes)


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    rows: list[dict[str, Any]],
    packet: dict[str, Any],
) -> dict[str, Any]:
    pending_fields = [
        field for row in rows for field in row["pending_signoff_fields"]
    ]
    return {
        "story_slug": story_slug,
        "source_review_packet_status": source_status,
        "status": status,
        "provider_count": len(rows),
        "source_packet_section_count": int(
            (packet.get("summary") or {}).get("packet_section_count") or 0
        ),
        "ledger_row_count": len(rows),
        "pending_signoff_field_count": len(pending_fields),
        "blocked_row_count": sum(1 for row in rows if row["status"] == "blocked"),
        "pause_material_count": sum(row["pause_material_count"] for row in rows),
        "escalation_material_count": sum(
            row["escalation_material_count"] for row in rows
        ),
        "writes_artifacts": False,
        "ledger_write_allowed": False,
        "approval_saved": False,
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


def _decision_ledger_preview(
    status: str,
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    if status == "ready_for_opt_in_decision_ledger_preview":
        return {
            "id": "graph_memory_provider_spike_opt_in_decision_ledger_preview",
            "status": "decision_ledger_preview_ready",
            "ready": True,
            "ledger_row_count": len(rows),
            "pending_signoff_field_count": summary["pending_signoff_field_count"],
            "ledger_write_allowed": False,
            "approval_saved": False,
            "real_provider_config_allowed": False,
            "reason": "opt-in decision ledger preview 已就绪；仍禁止真实 provider 配置。",
        }
    return {
        "id": "graph_memory_provider_spike_opt_in_decision_ledger_preview",
        "status": status,
        "ready": False,
        "ledger_row_count": len(rows),
        "pending_signoff_field_count": summary["pending_signoff_field_count"],
        "ledger_write_allowed": False,
        "approval_saved": False,
        "real_provider_config_allowed": False,
        "reason": "review packet 尚不足以生成 decision ledger preview。",
    }


def _decision(
    status: str,
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    if status == "ready_for_opt_in_decision_ledger_preview":
        return {
            "status": "decision_ledger_preview_ready_real_provider_still_blocked",
            "recommendation": "只读 decision ledger preview 已就绪；真实 provider 配置仍需另行显式人工确认。",
            "next_slice": "Graph Memory Provider Spike Opt-in Final Readiness Summary",
            "ledger_row_count": len(rows),
            "blocked_row_count": summary["blocked_row_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 review packet 证据，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Opt-in Decision Ledger Preview",
        "ledger_row_count": len(rows),
        "blocked_row_count": summary["blocked_row_count"],
    }


def _ledger_preview_materials(
    status: str,
    rows: list[dict[str, Any]],
) -> list[str]:
    if status != "ready_for_opt_in_decision_ledger_preview":
        return []
    materials: list[str] = []
    for row in rows:
        materials.append(f"签收字段预览：{row['service_target']} / {row['provider_id']}")
        materials.append(f"暂停依据：{row['pause_material_count']} 项暂停材料")
        materials.append(f"升级依据：{row['escalation_material_count']} 项升级材料")
    materials.append("所有签收字段保持 value=null、saved=false。")
    return _dedupe(materials)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_opt_in_decision_ledger_preview":
        return []
    return [
        "人工只阅读 ledger preview，不在本报告中填写签名。",
        "人工确认所有 pending_signoff_fields 均未保存。",
        "人工确认真实 provider 配置仍需另开显式 opt-in spike。",
    ]


def _no_go_conditions(
    packet: dict[str, Any],
    rows: list[dict[str, Any]],
) -> list[str]:
    items = list(packet.get("no_go_conditions") or [])
    for row in rows:
        if row["status"] == "blocked":
            items.append(
                f"{row['service_target']} ledger row 仍 blocked，不能启用真实 provider。"
            )
    items.extend(
        [
            "不能把 decision ledger preview 当成真实审批记录。",
            "不能保存签名、风险签收或回滚确认。",
            "不能要求真实付费 Key 或外部账号才能生成 ledger preview。",
            "不能把 ledger preview 写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(packet: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    warnings = list(packet.get("warnings") or [])
    if not rows:
        warnings.append("没有可生成 decision ledger preview 的 review packet，先补复核包。")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    preview: dict[str, Any],
    decision: dict[str, Any],
    rows: list[dict[str, Any]],
    packet: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "decision_ledger_preview": preview,
        "decision": decision,
        "ledger_rows": rows,
        "source_review_packet": {
            "version": packet.get("version"),
            "status": packet.get("status"),
            "review_packet": packet.get("review_packet"),
        },
        "contract": {
            "writes_artifacts": False,
            "ledger_write_allowed": False,
            "approval_saved": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_opt_in_decision_ledger_preview":
        return [
            "人工阅读 decision ledger preview，确认字段仅为占位。",
            "若仍需真实服务，只能另开显式 opt-in spike，不能由本预览自动创建配置。",
        ]
    if status == "blocked":
        return [
            "先修复 review packet blockers，再重新生成 decision ledger preview。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 decision ledger preview 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 review packet 就绪后再生成 decision ledger preview。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

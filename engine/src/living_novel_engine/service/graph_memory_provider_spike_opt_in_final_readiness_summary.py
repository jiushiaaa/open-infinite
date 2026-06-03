"""Graph Memory Provider Spike Opt-in Final Readiness Summary MVP.

This read-only summary turns the decision ledger preview into a final
readiness view. It does not save signoffs, write a ledger, create provider
configs, read keys, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_opt_in_decision_ledger_preview import (
    GraphMemoryProviderSpikeOptInDecisionLedgerPreviewRequestError,
    get_graph_memory_provider_spike_opt_in_decision_ledger_preview,
)

VERSION = "graph-memory-provider-spike-opt-in-final-readiness-summary-mvp"


class GraphMemoryProviderSpikeOptInFinalReadinessSummaryRequestError(ValueError):
    """Invalid graph-memory provider opt-in final readiness summary request."""


def get_graph_memory_provider_spike_opt_in_final_readiness_summary(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return deterministic read-only final readiness summary."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        ledger = get_graph_memory_provider_spike_opt_in_decision_ledger_preview(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeOptInDecisionLedgerPreviewRequestError as exc:
        raise GraphMemoryProviderSpikeOptInFinalReadinessSummaryRequestError(
            str(exc)
        ) from exc

    source_status = str(ledger.get("status") or "deferred")
    rows = _readiness_rows(ledger)
    unresolved_signoffs = _unresolved_signoffs(rows)
    status = _status(source_status, rows)
    summary = _summary(
        sid,
        source_status,
        status,
        rows,
        unresolved_signoffs,
        ledger,
    )
    final_summary = _final_readiness_summary(status, summary)
    decision = _decision(status, summary)
    final_readiness_materials = _final_readiness_materials(status, rows)
    no_go_conditions = _no_go_conditions(ledger, rows)
    manifest = _manifest(
        generated_at,
        summary,
        final_summary,
        decision,
        rows,
        unresolved_signoffs,
        ledger,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_opt_in_final_readiness_summary",
        "status": status,
        "story_slug": sid,
        "source_kind": ledger.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "final_readiness_summary": final_summary,
        "decision": decision,
        "readiness_rows": rows,
        "unresolved_signoff_fields": unresolved_signoffs,
        "final_readiness_materials": final_readiness_materials,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(ledger, rows),
        "boundaries": [
            "只读生成 opt-in final readiness summary，不保存签名或最终结论。",
            "Final Readiness Summary 只能说明真实 provider 仍未就绪，不能自动创建配置。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeOptInFinalReadinessSummaryRequestError(
            "invalid slug"
        )
    return sid


def _status(source_status: str, rows: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_opt_in_decision_ledger_preview" and rows:
        return "ready_for_opt_in_final_readiness_summary"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _readiness_rows(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    if ledger.get("status") != "ready_for_opt_in_decision_ledger_preview":
        return []

    rows: list[dict[str, Any]] = []
    for row in ledger.get("ledger_rows") or []:
        unresolved = _row_unresolved_signoffs(row)
        blockers = _row_blockers(row, unresolved)
        rows.append(
            {
                "id": f"final-readiness-{row.get('provider_id') or 'unknown'}",
                "gate_status": "not_ready_for_real_provider",
                "provider_id": str(row.get("provider_id") or "unknown"),
                "provider_label": str(row.get("provider_label") or "unknown"),
                "service_target": str(row.get("service_target") or "unknown"),
                "source_decision_ledger_row_id": str(row.get("id") or ""),
                "source_review_packet_section_id": str(
                    row.get("source_review_packet_section_id") or ""
                ),
                "fixture_id": str(row.get("fixture_id") or ""),
                "eval_id": str(row.get("eval_id") or ""),
                "unresolved_signoff_fields": unresolved,
                "unresolved_blockers": blockers,
                "readiness_notes": _readiness_notes(row, unresolved, blockers),
                "audit_refs": _dedupe(list(row.get("audit_refs") or [])),
                "real_provider_ready": False,
                "final_decision_saved": False,
                "real_provider_config_allowed": False,
            }
        )
    return rows


def _row_unresolved_signoffs(row: dict[str, Any]) -> list[dict[str, Any]]:
    fields = []
    for field in row.get("pending_signoff_fields") or []:
        if field.get("saved") is True and field.get("value"):
            continue
        item = {
            "id": str(field.get("id") or ""),
            "field": str(field.get("field") or ""),
            "label": str(field.get("label") or ""),
            "value": field.get("value"),
            "required": bool(field.get("required", True)),
            "saved": bool(field.get("saved", False)),
            "provider_id": str(row.get("provider_id") or "unknown"),
            "service_target": str(row.get("service_target") or "unknown"),
            "source_decision_ledger_row_id": str(row.get("id") or ""),
        }
        fields.append(item)
    return fields


def _row_blockers(
    row: dict[str, Any],
    unresolved: list[dict[str, Any]],
) -> list[str]:
    blockers: list[str] = []
    if row.get("status") == "blocked":
        blockers.append("decision ledger row 仍处于 blocked。")
    if unresolved:
        blockers.append(f"{len(unresolved)} 个签收字段仍未保存。")
    if not row.get("ledger_write_allowed"):
        blockers.append("decision ledger write 仍被禁止。")
    if not row.get("real_provider_config_allowed"):
        blockers.append("真实 provider 配置仍被禁止。")
    pause_count = int(row.get("pause_material_count") or 0)
    if pause_count:
        blockers.append(f"{pause_count} 项暂停材料仍需人工复核。")
    return _dedupe(blockers)


def _readiness_notes(
    row: dict[str, Any],
    unresolved: list[dict[str, Any]],
    blockers: list[str],
) -> list[str]:
    notes = [
        "最终就绪摘要只读，不写入项目文件。",
        "真实 provider 仍未达到启用条件。",
    ]
    if unresolved:
        notes.append("仍有未签收字段，不能进入真实配置。")
    if blockers:
        notes.append("存在阻塞项，继续保持 mock/deterministic 路径。")
    notes.append(str((row.get("decision_fields") or {}).get("reason") or "保持暂缓。"))
    return _dedupe(notes)


def _unresolved_signoffs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [field for row in rows for field in row["unresolved_signoff_fields"]]


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    rows: list[dict[str, Any]],
    unresolved_signoffs: list[dict[str, Any]],
    ledger: dict[str, Any],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_decision_ledger_status": source_status,
        "status": status,
        "provider_count": len(rows),
        "source_ledger_row_count": int(
            (ledger.get("summary") or {}).get("ledger_row_count") or 0
        ),
        "readiness_row_count": len(rows),
        "unresolved_signoff_field_count": len(unresolved_signoffs),
        "blocked_row_count": sum(
            1 for row in rows if row["gate_status"] == "not_ready_for_real_provider"
        ),
        "unresolved_blocker_count": sum(
            len(row["unresolved_blockers"]) for row in rows
        ),
        "writes_artifacts": False,
        "final_decision_saved": False,
        "approval_saved": False,
        "external_services_required": False,
        "provider_calls": False,
        "real_provider_ready": False,
        "real_provider_config_allowed": False,
        "uses_graphrag": False,
        "uses_zep": False,
        "uses_vector_store": False,
        "uses_reranker": False,
        "uses_embedding_provider": False,
        "plaintext_key_returned": False,
    }


def _final_readiness_summary(
    status: str,
    summary: dict[str, Any],
) -> dict[str, Any]:
    if status == "ready_for_opt_in_final_readiness_summary":
        return {
            "id": "graph_memory_provider_spike_opt_in_final_readiness_summary",
            "status": "final_readiness_summary_ready",
            "ready": True,
            "real_provider_ready": False,
            "readiness_label": "not_ready_for_real_provider",
            "readiness_row_count": summary["readiness_row_count"],
            "unresolved_signoff_field_count": summary[
                "unresolved_signoff_field_count"
            ],
            "unresolved_blocker_count": summary["unresolved_blocker_count"],
            "final_decision_saved": False,
            "real_provider_config_allowed": False,
            "reason": "最终就绪摘要已可读；真实 provider 仍未就绪。",
        }
    return {
        "id": "graph_memory_provider_spike_opt_in_final_readiness_summary",
        "status": status,
        "ready": False,
        "real_provider_ready": False,
        "readiness_label": "deferred",
        "readiness_row_count": summary["readiness_row_count"],
        "unresolved_signoff_field_count": summary[
            "unresolved_signoff_field_count"
        ],
        "unresolved_blocker_count": summary["unresolved_blocker_count"],
        "final_decision_saved": False,
        "real_provider_config_allowed": False,
        "reason": "decision ledger preview 尚不足以生成最终就绪摘要。",
    }


def _decision(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    if status == "ready_for_opt_in_final_readiness_summary":
        return {
            "status": "final_readiness_summary_ready_real_provider_still_blocked",
            "recommendation": "最终就绪摘要已生成；真实 provider 仍需另行显式人工 opt-in。",
            "next_slice": "Graph Memory Provider Spike Opt-in Human Signoff Schema Draft",
            "readiness_row_count": summary["readiness_row_count"],
            "unresolved_blocker_count": summary["unresolved_blocker_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 decision ledger preview，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Opt-in Final Readiness Summary",
        "readiness_row_count": summary["readiness_row_count"],
        "unresolved_blocker_count": summary["unresolved_blocker_count"],
    }


def _final_readiness_materials(
    status: str,
    rows: list[dict[str, Any]],
) -> list[str]:
    if status != "ready_for_opt_in_final_readiness_summary":
        return []
    materials: list[str] = []
    for row in rows:
        materials.append(
            f"最终就绪摘要：{row['service_target']} / {row['provider_id']} 仍未就绪"
        )
        materials.append(
            f"未签收字段：{len(row['unresolved_signoff_fields'])} 项"
        )
        materials.append(f"阻塞原因：{len(row['unresolved_blockers'])} 项")
    materials.append("所有 provider 继续保持真实配置禁止。")
    return _dedupe(materials)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_opt_in_final_readiness_summary":
        return []
    return [
        "人工确认 final readiness summary 仅为只读摘要。",
        "人工确认 unresolved_signoff_fields 仍未保存。",
        "人工确认真实 provider 仍需另开显式 opt-in spike。",
    ]


def _no_go_conditions(
    ledger: dict[str, Any],
    rows: list[dict[str, Any]],
) -> list[str]:
    items = list(ledger.get("no_go_conditions") or [])
    for row in rows:
        if row["gate_status"] == "not_ready_for_real_provider":
            items.append(
                f"{row['service_target']} final readiness 仍 not ready，不能启用真实 provider。"
            )
    items.extend(
        [
            "不能把 final readiness summary 当成真实审批记录。",
            "不能保存签名、风险签收、回滚确认或最终结论。",
            "不能要求真实付费 Key 或外部账号才能生成最终摘要。",
            "不能把最终摘要写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(ledger: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    warnings = list(ledger.get("warnings") or [])
    if not rows:
        warnings.append("没有可生成 final readiness summary 的 decision ledger preview。")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    final_summary: dict[str, Any],
    decision: dict[str, Any],
    rows: list[dict[str, Any]],
    unresolved_signoffs: list[dict[str, Any]],
    ledger: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "final_readiness_summary": final_summary,
        "decision": decision,
        "readiness_rows": rows,
        "unresolved_signoff_fields": unresolved_signoffs,
        "source_decision_ledger_preview": {
            "version": ledger.get("version"),
            "status": ledger.get("status"),
            "decision_ledger_preview": ledger.get("decision_ledger_preview"),
        },
        "contract": {
            "writes_artifacts": False,
            "final_decision_saved": False,
            "approval_saved": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_ready": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_opt_in_final_readiness_summary":
        return [
            "人工阅读 final readiness summary，确认仍不启用真实 provider。",
            "若仍需真实服务，只能另开显式 opt-in spike，不能由本摘要自动创建配置。",
        ]
    if status == "blocked":
        return [
            "先修复 decision ledger blockers，再重新生成 final readiness summary。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 final readiness summary 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 decision ledger preview 就绪后再生成 final readiness summary。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

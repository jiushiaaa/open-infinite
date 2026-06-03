"""Graph Memory Provider Spike Opt-in Review Packet MVP.

This read-only packet turns the operator checklist into review materials.
It does not save review results, create provider configs, read keys, write
artifacts, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_opt_in_operator_checklist import (
    GraphMemoryProviderSpikeOptInOperatorChecklistRequestError,
    get_graph_memory_provider_spike_opt_in_operator_checklist,
)

VERSION = "graph-memory-provider-spike-opt-in-review-packet-mvp"


class GraphMemoryProviderSpikeOptInReviewPacketRequestError(ValueError):
    """Invalid graph-memory provider opt-in review packet request."""


def get_graph_memory_provider_spike_opt_in_review_packet(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return deterministic read-only opt-in review packet materials."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        checklist = get_graph_memory_provider_spike_opt_in_operator_checklist(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeOptInOperatorChecklistRequestError as exc:
        raise GraphMemoryProviderSpikeOptInReviewPacketRequestError(str(exc)) from exc

    source_status = str(checklist.get("status") or "deferred")
    packet_sections = _packet_sections(checklist)
    status = _status(source_status, packet_sections)
    summary = _summary(sid, source_status, status, packet_sections, checklist)
    review_packet = _review_packet(status, packet_sections, summary)
    decision = _decision(status, packet_sections, summary)
    review_packet_materials = _review_packet_materials(status, packet_sections)
    no_go_conditions = _no_go_conditions(checklist, packet_sections)
    manifest = _manifest(
        generated_at,
        summary,
        review_packet,
        decision,
        packet_sections,
        checklist,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_opt_in_review_packet",
        "status": status,
        "story_slug": sid,
        "source_kind": checklist.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "review_packet": review_packet,
        "decision": decision,
        "packet_sections": packet_sections,
        "review_packet_materials": review_packet_materials,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(checklist, packet_sections),
        "boundaries": [
            "只读生成 opt-in review packet，不保存人工复核或审批结论。",
            "Review Packet 只能汇总证据、暂停材料和升级材料，不能自动创建真实 provider 配置。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeOptInReviewPacketRequestError("invalid slug")
    return sid


def _status(source_status: str, sections: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_opt_in_operator_checklist" and sections:
        return "ready_for_opt_in_review_packet"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _packet_sections(checklist: dict[str, Any]) -> list[dict[str, Any]]:
    if checklist.get("status") != "ready_for_opt_in_operator_checklist":
        return []

    sections: list[dict[str, Any]] = []
    for source in checklist.get("checklist_sections") or []:
        evidence_sequence = [
            _evidence_item(source, step, index)
            for index, step in enumerate(source.get("steps") or [], 1)
        ]
        blocked_count = sum(
            1 for item in evidence_sequence if item["status"] == "blocked"
        )
        sections.append(
            {
                "id": f"review-packet-{source.get('provider_id') or 'unknown'}",
                "status": "blocked" if blocked_count else "review",
                "provider_id": str(source.get("provider_id") or "unknown"),
                "provider_label": str(source.get("provider_label") or "unknown"),
                "service_target": str(source.get("service_target") or "unknown"),
                "source_checklist_section_id": str(source.get("id") or ""),
                "source_matrix_row_id": str(source.get("source_matrix_row_id") or ""),
                "source_snapshot_id": str(source.get("source_snapshot_id") or ""),
                "fixture_id": str(source.get("fixture_id") or ""),
                "eval_id": str(source.get("eval_id") or ""),
                "evidence_item_count": len(evidence_sequence),
                "blocked_step_count": blocked_count,
                "review_step_count": len(evidence_sequence) - blocked_count,
                "pause_required": blocked_count > 0,
                "evidence_sequence": evidence_sequence,
                "pause_materials": _pause_materials(source, evidence_sequence),
                "escalation_materials": _escalation_materials(
                    source,
                    evidence_sequence,
                ),
                "reviewer_todos": _reviewer_todos(blocked_count),
                "evidence_refs": _dedupe(list(source.get("evidence_refs") or [])),
                "recommendation": (
                    "复核包只整理材料；真实 provider 配置仍需另行显式审批。"
                ),
            }
        )
    return sections


def _evidence_item(
    section: dict[str, Any],
    step: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    category = str(step.get("category") or "unknown")
    status = str(step.get("status") or "review")
    return {
        "id": f"{section.get('provider_id') or 'unknown'}-review-evidence-{index}",
        "order": index,
        "source_step_id": str(step.get("id") or ""),
        "category": category,
        "label": str(step.get("label") or category),
        "status": status,
        "action": str(step.get("action") or ""),
        "reason": str(step.get("reason") or ""),
        "blocker_count": int(step.get("blocker_count") or 0),
        "evidence_refs": _dedupe(list(step.get("evidence_refs") or [])),
        "pause_required": bool(step.get("pause_required") or status == "blocked"),
        "review_note": _review_note(category, status),
        "upgrade_allowed": False,
        "real_provider_config_allowed": False,
    }


def _review_note(category: str, status: str) -> str:
    if category == "manual_signoff":
        return "人工签收证据必须逐项复核；未签收时只能暂停。"
    if category == "opt_in_materials":
        return "opt-in 材料必须齐备；缺材料时只允许补证据。"
    if category == "rollback_materials":
        return "回滚材料必须可复核；缺回滚路径时不能升级。"
    if category == "real_provider_config":
        return "真实 provider 配置在本复核包内始终禁止。"
    if category == "external_account_or_key":
        return "外部账号或真实 Key 不能成为生成复核包的前置条件。"
    if status == "blocked":
        return "阻塞项解除前保持暂停。"
    return "当前项只进入人工复核，不触发真实配置。"


def _pause_materials(
    section: dict[str, Any],
    evidence_sequence: list[dict[str, Any]],
) -> list[str]:
    materials = [
        f"暂停：{item['label']} -> {item['review_note']}"
        for item in evidence_sequence
        if item["pause_required"]
    ]
    if not materials:
        materials.append(
            f"暂停：{section.get('service_target') or 'unknown'} 仍需另行显式 opt-in。"
        )
    return _dedupe(materials)


def _escalation_materials(
    section: dict[str, Any],
    evidence_sequence: list[dict[str, Any]],
) -> list[str]:
    materials = [
        f"升级前核对：{item['label']} / {item['category']}"
        for item in evidence_sequence
    ]
    materials.append(
        f"升级前核对：{section.get('service_target') or 'unknown'} 的人工复核结论不能由本报告保存。"
    )
    return _dedupe(materials)


def _reviewer_todos(blocked_count: int) -> list[str]:
    todos = [
        "按 evidence_sequence 顺序核对证据。",
        "确认复核包不保存签名、不写配置、不调用外部服务。",
    ]
    if blocked_count:
        todos.insert(0, "优先处理 blocked evidence item，未解除前暂停真实 provider。")
    else:
        todos.insert(0, "没有 blocked evidence item 时仍需另行显式 opt-in。")
    return todos


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    sections: list[dict[str, Any]],
    checklist: dict[str, Any],
) -> dict[str, Any]:
    evidence_items = [
        item for section in sections for item in section["evidence_sequence"]
    ]
    blocked_items = [item for item in evidence_items if item["status"] == "blocked"]
    return {
        "story_slug": story_slug,
        "source_operator_checklist_status": source_status,
        "status": status,
        "provider_count": len(sections),
        "source_checklist_section_count": int(
            (checklist.get("summary") or {}).get("checklist_section_count") or 0
        ),
        "packet_section_count": len(sections),
        "evidence_item_count": len(evidence_items),
        "blocked_step_count": len(blocked_items),
        "pause_material_count": sum(len(s["pause_materials"]) for s in sections),
        "escalation_material_count": sum(
            len(s["escalation_materials"]) for s in sections
        ),
        "manual_signoff_item_count": _category_items(
            evidence_items,
            "manual_signoff",
        ),
        "real_config_item_count": _category_items(
            evidence_items,
            "real_provider_config",
        ),
        "no_go_condition_count": len(checklist.get("no_go_conditions") or []),
        "writes_artifacts": False,
        "review_packet_write_allowed": False,
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


def _category_items(items: list[dict[str, Any]], category: str) -> int:
    return sum(
        1
        for item in items
        if item.get("category") == category and item.get("status") == "blocked"
    )


def _review_packet(
    status: str,
    sections: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    if status == "ready_for_opt_in_review_packet":
        return {
            "id": "graph_memory_provider_spike_opt_in_review_packet",
            "status": "review_packet_ready",
            "ready": True,
            "opt_in_blocked": summary["blocked_step_count"] > 0,
            "real_provider_config_allowed": False,
            "packet_section_count": len(sections),
            "evidence_item_count": summary["evidence_item_count"],
            "reason": "opt-in review packet 已就绪；仍禁止真实 provider 配置。",
        }
    return {
        "id": "graph_memory_provider_spike_opt_in_review_packet",
        "status": status,
        "ready": False,
        "opt_in_blocked": True,
        "real_provider_config_allowed": False,
        "packet_section_count": len(sections),
        "evidence_item_count": summary["evidence_item_count"],
        "reason": "operator checklist 尚不足以生成 review packet。",
    }


def _decision(
    status: str,
    sections: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    if status == "ready_for_opt_in_review_packet":
        return {
            "status": "review_packet_ready_real_provider_still_blocked",
            "recommendation": "只读 review packet 已就绪；真实 provider 配置仍需另行显式人工确认。",
            "next_slice": "Graph Memory Provider Spike Opt-in Decision Ledger Preview",
            "packet_section_count": len(sections),
            "blocked_step_count": summary["blocked_step_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 operator checklist 证据，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Opt-in Review Packet",
        "packet_section_count": len(sections),
        "blocked_step_count": summary["blocked_step_count"],
    }


def _review_packet_materials(
    status: str,
    sections: list[dict[str, Any]],
) -> list[str]:
    if status != "ready_for_opt_in_review_packet":
        return []
    materials: list[str] = []
    for section in sections:
        materials.extend(section["pause_materials"])
        materials.extend(section["escalation_materials"][:2])
    materials.append("复核包禁止保存人工签收、真实 Key 或 provider 配置。")
    return _dedupe(materials)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_opt_in_review_packet":
        return []
    return [
        "人工按 packet_sections 顺序复核每个 provider。",
        "人工先处理 pause_materials，再判断 escalation_materials 是否齐备。",
        "人工确认 review packet 不保存签名、不写配置、不调用外部服务。",
    ]


def _no_go_conditions(
    checklist: dict[str, Any],
    sections: list[dict[str, Any]],
) -> list[str]:
    items = list(checklist.get("no_go_conditions") or [])
    for section in sections:
        if section["pause_required"]:
            items.append(
                f"{section['service_target']} 仍有暂停材料，不能启用真实 provider。"
            )
    items.extend(
        [
            "不能把 opt-in review packet 当成真实 provider 配置许可。",
            "不能保存人工复核结果或把待签收项标记为已完成。",
            "不能要求真实付费 Key 或外部账号才能生成 review packet。",
            "不能把 review packet 写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(
    checklist: dict[str, Any],
    sections: list[dict[str, Any]],
) -> list[str]:
    warnings = list(checklist.get("warnings") or [])
    if not sections:
        warnings.append("没有可生成 review packet 的 operator checklist，先补操作清单。")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    review_packet: dict[str, Any],
    decision: dict[str, Any],
    sections: list[dict[str, Any]],
    checklist: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "review_packet": review_packet,
        "decision": decision,
        "packet_sections": sections,
        "source_operator_checklist": {
            "version": checklist.get("version"),
            "status": checklist.get("status"),
            "operator_checklist": checklist.get("operator_checklist"),
        },
        "contract": {
            "writes_artifacts": False,
            "review_packet_write_allowed": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_opt_in_review_packet":
        return [
            "人工按 review packet 顺序复核暂停材料和升级材料。",
            "若仍需真实服务，只能另开显式 opt-in spike，不能由本复核包自动创建配置。",
        ]
    if status == "blocked":
        return [
            "先修复 operator checklist blockers，再重新生成 review packet。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 review packet 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 operator checklist 就绪后再生成 review packet。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

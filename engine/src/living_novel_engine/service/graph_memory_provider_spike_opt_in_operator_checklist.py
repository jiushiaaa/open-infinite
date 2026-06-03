"""Graph Memory Provider Spike Opt-in Operator Checklist MVP.

This read-only checklist turns the no-go matrix into operator review steps.
It does not save checklist results, create provider configs, read keys, write
artifacts, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_opt_in_no_go_matrix import (
    GraphMemoryProviderSpikeOptInNoGoMatrixRequestError,
    get_graph_memory_provider_spike_opt_in_no_go_matrix,
)

VERSION = "graph-memory-provider-spike-opt-in-operator-checklist-mvp"


class GraphMemoryProviderSpikeOptInOperatorChecklistRequestError(ValueError):
    """Invalid graph-memory provider opt-in operator checklist request."""


def get_graph_memory_provider_spike_opt_in_operator_checklist(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return deterministic read-only operator checklist sections."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        matrix = get_graph_memory_provider_spike_opt_in_no_go_matrix(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeOptInNoGoMatrixRequestError as exc:
        raise GraphMemoryProviderSpikeOptInOperatorChecklistRequestError(
            str(exc)
        ) from exc

    source_status = str(matrix.get("status") or "deferred")
    checklist_sections = _checklist_sections(matrix)
    status = _status(source_status, checklist_sections)
    summary = _summary(sid, source_status, status, checklist_sections, matrix)
    operator_checklist = _operator_checklist(status, checklist_sections, summary)
    decision = _decision(status, checklist_sections, summary)
    no_go_conditions = _no_go_conditions(matrix, checklist_sections)
    manifest = _manifest(
        generated_at,
        summary,
        operator_checklist,
        decision,
        checklist_sections,
        matrix,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_opt_in_operator_checklist",
        "status": status,
        "story_slug": sid,
        "source_kind": matrix.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "operator_checklist": operator_checklist,
        "decision": decision,
        "checklist_sections": checklist_sections,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(matrix, checklist_sections),
        "boundaries": [
            "只读生成 opt-in operator checklist，不保存人工操作或审批结论。",
            "Operator Checklist 只能指导人工复核，不能自动创建真实 provider 配置。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeOptInOperatorChecklistRequestError(
            "invalid slug"
        )
    return sid


def _status(source_status: str, sections: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_opt_in_no_go_matrix" and sections:
        return "ready_for_opt_in_operator_checklist"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _checklist_sections(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    if matrix.get("status") != "ready_for_opt_in_no_go_matrix":
        return []

    sections: list[dict[str, Any]] = []
    for row in matrix.get("matrix_rows") or []:
        steps = [_step(row, cell, index) for index, cell in enumerate(row.get("cells") or [], 1)]
        blocked_count = sum(1 for step in steps if step["status"] == "blocked")
        sections.append(
            {
                "id": f"operator-checklist-{row.get('provider_id') or 'unknown'}",
                "status": "blocked" if blocked_count else "review",
                "provider_id": str(row.get("provider_id") or "unknown"),
                "provider_label": str(row.get("provider_label") or "unknown"),
                "service_target": str(row.get("service_target") or "unknown"),
                "source_matrix_row_id": str(row.get("id") or ""),
                "source_snapshot_id": str(row.get("source_snapshot_id") or ""),
                "fixture_id": str(row.get("fixture_id") or ""),
                "eval_id": str(row.get("eval_id") or ""),
                "step_count": len(steps),
                "blocked_step_count": blocked_count,
                "steps": steps,
                "pause_reason": _pause_reason(blocked_count),
                "evidence_refs": _dedupe(list(row.get("evidence_refs") or [])),
                "recommendation": "按顺序人工核对阻塞项；真实 provider 配置仍需另行显式审批。",
            }
        )
    return sections


def _step(row: dict[str, Any], cell: dict[str, Any], index: int) -> dict[str, Any]:
    category = str(cell.get("category") or "unknown")
    status = "blocked" if cell.get("status") == "blocked" else "review"
    return {
        "id": f"{row.get('provider_id') or 'unknown'}-operator-step-{index}",
        "category": category,
        "label": str(cell.get("label") or category),
        "status": status,
        "action": _action(category, status),
        "source_cell_id": str(cell.get("id") or ""),
        "blocker_count": int(cell.get("blocker_count") or 0),
        "reason": str(cell.get("reason") or ""),
        "evidence_refs": _dedupe(list(row.get("evidence_refs") or [])),
        "pause_required": status == "blocked",
        "upgrade_allowed": False,
        "real_provider_config_allowed": False,
    }


def _action(category: str, status: str) -> str:
    if category == "manual_signoff":
        return "逐项核对待签收项，未完成前暂停真实 provider 配置。"
    if category == "opt_in_materials":
        return "核对 opt-in 材料是否齐备，缺口未补齐前保持暂缓。"
    if category == "rollback_materials":
        return "核对回滚材料和恢复路径，缺口未补齐前保持暂缓。"
    if category == "real_provider_config":
        return "确认本地只读报告不能创建或启用真实 provider 配置。"
    if category == "external_account_or_key":
        return "确认不要求外部账号、真实付费 Key 或联网服务。"
    if status == "blocked":
        return "核对阻塞原因，未解除前保持暂缓。"
    return "复核当前分类证据，保持只读。"


def _pause_reason(blocked_count: int) -> str:
    if blocked_count:
        return "仍有阻塞步骤，必须暂停真实 provider 配置。"
    return "没有阻塞步骤，但仍需另行显式 opt-in 才能评估真实 provider。"


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    sections: list[dict[str, Any]],
    matrix: dict[str, Any],
) -> dict[str, Any]:
    steps = [step for section in sections for step in section["steps"]]
    blocked_steps = [step for step in steps if step["status"] == "blocked"]
    return {
        "story_slug": story_slug,
        "source_no_go_matrix_status": source_status,
        "status": status,
        "provider_count": len(sections),
        "matrix_row_count": int(
            (matrix.get("summary") or {}).get("matrix_row_count") or 0
        ),
        "checklist_section_count": len(sections),
        "operator_step_count": len(steps),
        "blocked_step_count": len(blocked_steps),
        "manual_signoff_step_count": _category_steps(steps, "manual_signoff"),
        "real_config_step_count": _category_steps(steps, "real_provider_config"),
        "external_account_or_key_step_count": _category_steps(
            steps,
            "external_account_or_key",
        ),
        "no_go_condition_count": len(matrix.get("no_go_conditions") or []),
        "writes_artifacts": False,
        "checklist_write_allowed": False,
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


def _category_steps(steps: list[dict[str, Any]], category: str) -> int:
    return sum(
        1
        for step in steps
        if step.get("category") == category and step.get("status") == "blocked"
    )


def _operator_checklist(
    status: str,
    sections: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    if status == "ready_for_opt_in_operator_checklist":
        return {
            "id": "graph_memory_provider_spike_opt_in_operator_checklist",
            "status": "operator_checklist_ready",
            "ready": True,
            "opt_in_blocked": summary["blocked_step_count"] > 0,
            "real_provider_config_allowed": False,
            "checklist_section_count": len(sections),
            "reason": "opt-in operator checklist 已就绪；仍禁止真实 provider 配置。",
        }
    return {
        "id": "graph_memory_provider_spike_opt_in_operator_checklist",
        "status": status,
        "ready": False,
        "opt_in_blocked": True,
        "real_provider_config_allowed": False,
        "checklist_section_count": len(sections),
        "reason": "opt-in no-go matrix 尚不足以生成 operator checklist。",
    }


def _decision(
    status: str,
    sections: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    if status == "ready_for_opt_in_operator_checklist":
        return {
            "status": "operator_checklist_ready_real_provider_still_blocked",
            "recommendation": "只读 operator checklist 已就绪；真实 provider 配置仍需另行显式人工确认。",
            "next_slice": "Graph Memory Provider Spike Opt-in Review Packet",
            "checklist_section_count": len(sections),
            "blocked_step_count": summary["blocked_step_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 opt-in no-go matrix 证据，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Opt-in Operator Checklist",
        "checklist_section_count": len(sections),
        "blocked_step_count": summary["blocked_step_count"],
    }


def _no_go_conditions(
    matrix: dict[str, Any],
    sections: list[dict[str, Any]],
) -> list[str]:
    items = list(matrix.get("no_go_conditions") or [])
    for section in sections:
        items.append(section.get("pause_reason") or "")
    items.extend(
        [
            "不能把 opt-in operator checklist 当成真实 provider 配置许可。",
            "不能保存人工操作结果或把待签收项标记为已完成。",
            "不能要求真实付费 Key 或外部账号才能生成 operator checklist。",
            "不能把 operator checklist 写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(
    matrix: dict[str, Any],
    sections: list[dict[str, Any]],
) -> list[str]:
    warnings = list(matrix.get("warnings") or [])
    if not sections:
        warnings.append("没有可生成 operator checklist 的 matrix row，先补 opt-in no-go matrix。")
    return _dedupe(warnings)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_opt_in_operator_checklist":
        return []
    return [
        "人工按 provider 顺序核对每个 operator step。",
        "人工确认所有 blocked step 未解除前不能进入真实 provider 配置。",
        "人工确认 operator checklist 不保存签名、不写配置、不调用外部服务。",
    ]


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    operator_checklist: dict[str, Any],
    decision: dict[str, Any],
    sections: list[dict[str, Any]],
    matrix: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "operator_checklist": operator_checklist,
        "decision": decision,
        "checklist_sections": sections,
        "source_no_go_matrix": {
            "version": matrix.get("version"),
            "status": matrix.get("status"),
            "no_go_matrix": matrix.get("no_go_matrix"),
        },
        "contract": {
            "writes_artifacts": False,
            "checklist_write_allowed": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_opt_in_operator_checklist":
        return [
            "人工按 operator checklist 顺序核对阻塞项。",
            "若仍需真实服务，只能另开显式 opt-in spike，不能由本清单自动创建配置。",
        ]
    if status == "blocked":
        return [
            "先修复 opt-in no-go matrix blockers，再重新生成 operator checklist。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 operator checklist 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 opt-in no-go matrix 就绪后再生成 operator checklist。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

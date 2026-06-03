"""Graph Memory Provider Spike Opt-in No-go Matrix MVP.

This read-only matrix groups opt-in evidence snapshot blockers by category.
It does not save approvals, create provider configs, read keys, write
artifacts, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_opt_in_evidence_snapshot import (
    GraphMemoryProviderSpikeOptInEvidenceSnapshotRequestError,
    get_graph_memory_provider_spike_opt_in_evidence_snapshot,
)

VERSION = "graph-memory-provider-spike-opt-in-no-go-matrix-mvp"


class GraphMemoryProviderSpikeOptInNoGoMatrixRequestError(ValueError):
    """Invalid graph-memory provider opt-in no-go matrix request, mapped to HTTP 400."""


def get_graph_memory_provider_spike_opt_in_no_go_matrix(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return deterministic read-only no-go matrix rows."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        snapshot = get_graph_memory_provider_spike_opt_in_evidence_snapshot(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeOptInEvidenceSnapshotRequestError as exc:
        raise GraphMemoryProviderSpikeOptInNoGoMatrixRequestError(str(exc)) from exc

    source_status = str(snapshot.get("status") or "deferred")
    matrix_rows = _matrix_rows(snapshot)
    status = _status(source_status, matrix_rows)
    summary = _summary(sid, source_status, status, matrix_rows, snapshot)
    no_go_matrix = _no_go_matrix(status, matrix_rows, summary)
    decision = _decision(status, matrix_rows, summary)
    no_go_conditions = _no_go_conditions(snapshot, matrix_rows)
    manifest = _manifest(
        generated_at,
        summary,
        no_go_matrix,
        decision,
        matrix_rows,
        snapshot,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_opt_in_no_go_matrix",
        "status": status,
        "story_slug": sid,
        "source_kind": snapshot.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "no_go_matrix": no_go_matrix,
        "decision": decision,
        "matrix_rows": matrix_rows,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(snapshot, matrix_rows),
        "boundaries": [
            "只读生成 opt-in no-go matrix，不保存人工签收或审批结论。",
            "No-go Matrix 只能分类展示阻塞原因，不能自动创建真实 provider 配置。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeOptInNoGoMatrixRequestError("invalid slug")
    return sid


def _status(source_status: str, matrix_rows: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_opt_in_evidence_snapshot" and matrix_rows:
        return "ready_for_opt_in_no_go_matrix"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _matrix_rows(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    if snapshot.get("status") != "ready_for_opt_in_evidence_snapshot":
        return []

    rows: list[dict[str, Any]] = []
    for item in snapshot.get("snapshot_items") or []:
        cells = _cells(item)
        no_go_reasons = [
            str(cell.get("reason") or "")
            for cell in cells
            if cell.get("status") == "blocked" and cell.get("reason")
        ]
        rows.append(
            {
                "id": f"no-go-matrix-{item.get('provider_id') or 'unknown'}",
                "status": "blocked" if no_go_reasons else "clear_no_real_config",
                "provider_id": str(item.get("provider_id") or "unknown"),
                "provider_label": str(item.get("provider_label") or "unknown"),
                "service_target": str(item.get("service_target") or "unknown"),
                "source_snapshot_id": str(item.get("id") or ""),
                "source_checklist_id": str(item.get("source_checklist_id") or ""),
                "fixture_id": str(item.get("fixture_id") or ""),
                "eval_id": str(item.get("eval_id") or ""),
                "cell_count": len(cells),
                "blocked_cell_count": sum(
                    1 for cell in cells if cell.get("status") == "blocked"
                ),
                "cells": cells,
                "no_go_reasons": _dedupe(no_go_reasons),
                "evidence_refs": _dedupe(list(item.get("evidence_refs") or [])),
                "source_blocker_reasons": list(item.get("blocker_reasons") or []),
                "recommendation": "阻塞原因已分类；真实 provider 配置仍需另行显式审批。",
            }
        )
    return rows


def _cells(item: dict[str, Any]) -> list[dict[str, Any]]:
    signoff_count = int(item.get("signoff_todo_count") or 0)
    material_gap_count = int(item.get("material_gap_count") or 0)
    rollback_gap_count = int(item.get("rollback_material_gap_count") or 0)
    real_config_allowed = bool(item.get("real_provider_config_allowed") or False)
    return [
        _cell(
            item,
            "manual_signoff",
            "人工签收",
            "blocked" if signoff_count > 0 else "clear",
            signoff_count,
            "人工签收仍待完成，不能进入真实 provider 配置。",
        ),
        _cell(
            item,
            "opt_in_materials",
            "Opt-in 材料",
            "blocked" if material_gap_count > 0 else "clear",
            material_gap_count,
            "opt-in 材料仍有缺口。",
        ),
        _cell(
            item,
            "rollback_materials",
            "回滚材料",
            "blocked" if rollback_gap_count > 0 else "clear",
            rollback_gap_count,
            "回滚材料仍有缺口。",
        ),
        _cell(
            item,
            "real_provider_config",
            "真实 provider 配置",
            "clear" if real_config_allowed else "blocked",
            0 if real_config_allowed else 1,
            "本地报告仍禁止真实 provider 配置。",
        ),
        _cell(
            item,
            "external_account_or_key",
            "外部账号或 Key",
            "blocked",
            1,
            "本切片不能要求外部账号、真实付费 Key 或联网服务。",
        ),
    ]


def _cell(
    item: dict[str, Any],
    category: str,
    label: str,
    status: str,
    blocker_count: int,
    reason: str,
) -> dict[str, Any]:
    return {
        "id": f"{item.get('provider_id') or 'unknown'}-{category}",
        "category": category,
        "label": label,
        "status": status,
        "blocker_count": blocker_count,
        "reason": reason if status == "blocked" else "当前分类没有阻塞项。",
        "evidence_ref_count": len(item.get("evidence_refs") or []),
    }


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    matrix_rows: list[dict[str, Any]],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    cells = [cell for row in matrix_rows for cell in row["cells"]]
    blocked = [cell for cell in cells if cell["status"] == "blocked"]
    return {
        "story_slug": story_slug,
        "source_opt_in_snapshot_status": source_status,
        "status": status,
        "provider_count": len(matrix_rows),
        "snapshot_item_count": int(
            (snapshot.get("summary") or {}).get("snapshot_item_count") or 0
        ),
        "matrix_row_count": len(matrix_rows),
        "matrix_cell_count": len(cells),
        "blocked_cell_count": len(blocked),
        "signoff_blocker_count": _category_blockers(cells, "manual_signoff"),
        "material_blocker_count": _category_blockers(cells, "opt_in_materials"),
        "rollback_blocker_count": _category_blockers(cells, "rollback_materials"),
        "real_config_blocker_count": _category_blockers(cells, "real_provider_config"),
        "external_account_or_key_blocker_count": _category_blockers(
            cells,
            "external_account_or_key",
        ),
        "no_go_condition_count": len(snapshot.get("no_go_conditions") or []),
        "writes_artifacts": False,
        "matrix_write_allowed": False,
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


def _category_blockers(cells: list[dict[str, Any]], category: str) -> int:
    return sum(
        1
        for cell in cells
        if cell.get("category") == category and cell.get("status") == "blocked"
    )


def _no_go_matrix(
    status: str,
    matrix_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    if status == "ready_for_opt_in_no_go_matrix":
        return {
            "id": "graph_memory_provider_spike_opt_in_no_go_matrix",
            "status": "no_go_matrix_ready",
            "ready": True,
            "opt_in_blocked": summary["blocked_cell_count"] > 0,
            "real_provider_config_allowed": False,
            "matrix_row_count": len(matrix_rows),
            "reason": "opt-in no-go 矩阵已就绪；仍禁止真实 provider 配置。",
        }
    return {
        "id": "graph_memory_provider_spike_opt_in_no_go_matrix",
        "status": status,
        "ready": False,
        "opt_in_blocked": True,
        "real_provider_config_allowed": False,
        "matrix_row_count": len(matrix_rows),
        "reason": "opt-in evidence snapshot 尚不足以生成 no-go 矩阵。",
    }


def _decision(
    status: str,
    matrix_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    if status == "ready_for_opt_in_no_go_matrix":
        return {
            "status": "no_go_matrix_ready_real_provider_still_blocked",
            "recommendation": "只读 no-go 矩阵已就绪；真实 provider 配置仍需另行显式人工确认。",
            "next_slice": "Graph Memory Provider Spike Opt-in Operator Checklist",
            "matrix_row_count": len(matrix_rows),
            "blocked_cell_count": summary["blocked_cell_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 opt-in evidence snapshot 证据，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Opt-in No-go Matrix",
        "matrix_row_count": len(matrix_rows),
        "blocked_cell_count": summary["blocked_cell_count"],
    }


def _no_go_conditions(
    snapshot: dict[str, Any],
    matrix_rows: list[dict[str, Any]],
) -> list[str]:
    items = list(snapshot.get("no_go_conditions") or [])
    for row in matrix_rows:
        items.extend(row.get("no_go_reasons") or [])
    items.extend(
        [
            "不能把 opt-in no-go matrix 当成真实 provider 配置许可。",
            "不能保存人工签名或把待签收项标记为已完成。",
            "不能要求真实付费 Key 或外部账号才能生成 no-go 矩阵。",
            "不能把 no-go 矩阵写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(
    snapshot: dict[str, Any],
    matrix_rows: list[dict[str, Any]],
) -> list[str]:
    warnings = list(snapshot.get("warnings") or [])
    if not matrix_rows:
        warnings.append("没有可生成 no-go 矩阵的 snapshot item，先补 opt-in evidence snapshot。")
    return _dedupe(warnings)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_opt_in_no_go_matrix":
        return []
    return [
        "人工核对每个 provider 的签收、材料、回滚和真实配置阻塞类别。",
        "人工确认 no-go 矩阵没有被写入真实 provider 配置。",
        "人工确认真实 provider spike 必须另行显式审批，不能由本矩阵自动触发。",
    ]


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    no_go_matrix: dict[str, Any],
    decision: dict[str, Any],
    matrix_rows: list[dict[str, Any]],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "no_go_matrix": no_go_matrix,
        "decision": decision,
        "matrix_rows": matrix_rows,
        "source_opt_in_evidence_snapshot": {
            "version": snapshot.get("version"),
            "status": snapshot.get("status"),
            "opt_in_snapshot": snapshot.get("opt_in_snapshot"),
        },
        "contract": {
            "writes_artifacts": False,
            "matrix_write_allowed": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_opt_in_no_go_matrix":
        return [
            "人工核对 no-go 分类矩阵和每项阻塞原因。",
            "若仍需真实服务，只能另开显式 opt-in spike，不能由本矩阵自动创建配置。",
        ]
    if status == "blocked":
        return [
            "先修复 opt-in evidence snapshot blockers，再重新生成 no-go 矩阵。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 no-go 矩阵暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 opt-in evidence snapshot 就绪后再生成 no-go 矩阵。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

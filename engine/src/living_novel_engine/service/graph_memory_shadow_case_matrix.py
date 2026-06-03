"""Graph Memory Shadow Case Matrix MVP.

This service expands the shadow compare pack into a deterministic per-case
matrix. It stays read-only: no artifacts, provider calls, vector stores, graph
databases, rerankers, embeddings, or plaintext keys.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_shadow_compare_pack import (
    GraphMemoryShadowComparePackRequestError,
    get_graph_memory_shadow_compare_pack,
)

VERSION = "graph-memory-shadow-case-matrix-mvp"


class GraphMemoryShadowCaseMatrixRequestError(ValueError):
    """Invalid graph-memory shadow case matrix request, mapped to HTTP 400."""


def get_graph_memory_shadow_case_matrix(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a read-only Graph Memory shadow case matrix."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        compare_pack = get_graph_memory_shadow_compare_pack(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryShadowComparePackRequestError as exc:
        raise GraphMemoryShadowCaseMatrixRequestError(str(exc)) from exc

    source_status = str(compare_pack.get("status") or "deferred")
    status = _status(source_status)
    layers = _layers(compare_pack)
    cases = _cases(compare_pack)
    cells = _cells(status, layers, cases)
    case_gate = _case_gate(status, cases, cells)
    summary = _summary(sid, source_status, status, layers, cases, cells)
    manifest = _manifest(
        generated_at,
        summary,
        case_gate,
        layers,
        cases,
        cells,
        compare_pack,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_shadow_case_matrix",
        "status": status,
        "story_slug": sid,
        "source_kind": compare_pack.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "case_gate": case_gate,
        "layers": layers,
        "cases": cases,
        "cells": cells,
        "no_go_conditions": list(compare_pack.get("no_go_conditions") or []),
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(compare_pack, cases, cells),
        "boundaries": [
            "只读展开 GraphRAG、Zep、Temporal Memory 候选层的 per-case 证据矩阵，不写项目 artifact。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开 opt-in spike。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryShadowCaseMatrixRequestError("invalid slug")
    return sid


def _status(source_status: str) -> str:
    if source_status == "ready_for_shadow_compare":
        return "ready"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    return "deferred"


def _layers(compare_pack: dict[str, Any]) -> list[dict[str, Any]]:
    layers: list[dict[str, Any]] = []
    for item in compare_pack.get("comparisons") or []:
        layer_id = str(item.get("id") or "unknown")
        layers.append(
            {
                "id": layer_id,
                "label": str(item.get("label") or layer_id),
                "status": str(item.get("status") or "deferred"),
                "decision": str(item.get("decision") or "defer"),
                "baseline": str(item.get("baseline") or ""),
                "shadow_method": str(item.get("shadow_method") or ""),
                "projected_gain_score": int(item.get("projected_gain_score") or 0),
                "risk_score": int(item.get("risk_score") or 0),
                "missing_evidence": list(item.get("missing_evidence") or []),
                "rollback_strategy": str(item.get("rollback_strategy") or ""),
            }
        )
    return layers


def _cases(compare_pack: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for item in compare_pack.get("sample_cases") or []:
        eval_id = str(item.get("eval_id") or "")
        cases.append(
            {
                "id": eval_id,
                "eval_id": eval_id,
                "story_slug": str(item.get("story_slug") or ""),
                "display_name": str(item.get("display_name") or ""),
                "query": str(item.get("query") or ""),
                "expected_item_id": str(item.get("expected_item_id") or ""),
                "baseline_status": str(item.get("baseline_status") or "unknown"),
                "diagnosis": str(item.get("diagnosis") or ""),
                "shadow_targets": list(item.get("shadow_targets") or []),
            }
        )
    return cases


def _cells(
    status: str,
    layers: list[dict[str, Any]],
    cases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for case in cases:
        for layer in layers:
            cells.append(_cell(status, case, layer))
    return cells


def _cell(status: str, case: dict[str, Any], layer: dict[str, Any]) -> dict[str, Any]:
    layer_status = str(layer.get("status") or "deferred")
    cell_status = layer_status if status == "ready" else "deferred"
    missing_evidence = _cell_missing_evidence(cell_status, layer)
    evidence_status = _evidence_status(cell_status, missing_evidence)
    return {
        "case_id": str(case.get("eval_id") or case.get("id") or ""),
        "layer_id": str(layer.get("id") or "unknown"),
        "layer_label": str(layer.get("label") or layer.get("id") or "unknown"),
        "status": cell_status,
        "decision": _cell_decision(cell_status, str(layer.get("decision") or "defer")),
        "baseline_status": str(case.get("baseline_status") or "unknown"),
        "evidence_status": evidence_status,
        "evidence_refs": _evidence_refs(evidence_status, case),
        "missing_evidence": missing_evidence,
        "shadow_question": _shadow_question(case, layer),
        "rollback_strategy": str(layer.get("rollback_strategy") or ""),
        "projected_gain_score": int(layer.get("projected_gain_score") or 0)
        if cell_status != "deferred"
        else 0,
        "risk_score": int(layer.get("risk_score") or 0) if cell_status != "deferred" else 0,
    }


def _cell_missing_evidence(cell_status: str, layer: dict[str, Any]) -> list[str]:
    missing = [str(item) for item in layer.get("missing_evidence") or []]
    if cell_status == "deferred" and "candidate_trigger" not in missing:
        missing.append("candidate_trigger")
    return missing


def _evidence_status(cell_status: str, missing_evidence: list[str]) -> str:
    if cell_status == "deferred":
        return "deferred"
    if missing_evidence:
        return "needs_local_evidence"
    return "local_evidence_ready"


def _cell_decision(cell_status: str, layer_decision: str) -> str:
    if cell_status == "deferred":
        return "defer"
    return layer_decision


def _evidence_refs(evidence_status: str, case: dict[str, Any]) -> list[str]:
    if evidence_status != "local_evidence_ready":
        return []
    refs = [f"retrieval_eval:{case.get('eval_id') or case.get('id') or ''}"]
    query = str(case.get("query") or "")
    if query:
        refs.append(f"query:{query}")
    baseline = str(case.get("baseline_status") or "")
    if baseline:
        refs.append(f"baseline:{baseline}")
    return refs


def _shadow_question(case: dict[str, Any], layer: dict[str, Any]) -> str:
    label = str(layer.get("label") or layer.get("id") or "候选层")
    query = str(case.get("query") or case.get("eval_id") or "")
    if label.lower().startswith("graphrag"):
        return f"GraphRAG 能否用实体关系图召回「{query}」对应的事实/因果链？"
    if label.lower().startswith("zep"):
        return f"Zep 能否用长期记忆补足「{query}」的跨章事实缺口？"
    return f"{label} 能否解释「{query}」的时间、状态或上下文缺口？"


def _case_gate(
    status: str,
    cases: list[dict[str, Any]],
    cells: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_cells = [cell for cell in cells if cell.get("status") in {"candidate", "monitor"}]
    if status == "ready" and cases and candidate_cells:
        gate_status = "case_matrix_ready"
        passed = True
        reason = "已有本地检索失败样本和候选层，可进入只读 case-by-case shadow 对照。"
    elif status == "needs_more_evidence":
        gate_status = "collect_more_evidence"
        passed = False
        reason = "触发证据不足，先补 retrieval eval records 或本地 ledger/alias/state 信号。"
    else:
        gate_status = "deferred"
        passed = False
        reason = "当前项目未达到 Graph 记忆 shadow case 矩阵触发条件。"
    return {
        "id": "graph_memory_shadow_case_matrix_gate",
        "status": gate_status,
        "passed": passed,
        "reason": reason,
        "case_count": len(cases),
        "candidate_cell_count": len(candidate_cells),
    }


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    layers: list[dict[str, Any]],
    cases: list[dict[str, Any]],
    cells: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_cells = [cell for cell in cells if cell.get("status") in {"candidate", "monitor"}]
    evidence_ready_cells = [
        cell for cell in cells if cell.get("evidence_status") == "local_evidence_ready"
    ]
    return {
        "story_slug": story_slug,
        "source_compare_status": source_status,
        "status": status,
        "case_count": len(cases),
        "layer_count": len(layers),
        "matrix_cell_count": len(cells),
        "candidate_cell_count": len(candidate_cells),
        "evidence_ready_cell_count": len(evidence_ready_cells),
        "writes_artifacts": False,
        "external_services_required": False,
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
    case_gate: dict[str, Any],
    layers: list[dict[str, Any]],
    cases: list[dict[str, Any]],
    cells: list[dict[str, Any]],
    compare_pack: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "case_gate": case_gate,
        "layers": layers,
        "cases": cases,
        "cells": cells,
        "source_compare": {
            "version": compare_pack.get("version"),
            "status": compare_pack.get("status"),
            "shadow_gate": compare_pack.get("shadow_gate"),
        },
        "contract": {
            "writes_artifacts": False,
            "external_services_required": False,
            "provider_calls": False,
            "plaintext_key_returned": False,
        },
    }


def _warnings(
    compare_pack: dict[str, Any],
    cases: list[dict[str, Any]],
    cells: list[dict[str, Any]],
) -> list[str]:
    warnings = list(compare_pack.get("warnings") or [])
    if not cases:
        warnings.append("未发现可展开的 retrieval eval 样本，矩阵暂为空。")
    if not any(cell.get("evidence_status") == "local_evidence_ready" for cell in cells):
        warnings.append("尚无可直接复核的本地证据格。")
    return warnings


def _next_steps(status: str) -> list[str]:
    if status == "ready":
        return [
            "用该矩阵挑 3-5 个高收益 case 做离线 shadow replay，不接真实 provider。",
            "补充每个候选层的成本、隐私、回滚和验收边界，再决定是否进入 opt-in provider spike。",
        ]
    if status == "needs_more_evidence":
        return [
            "继续补 retrieval failure sample 与 replay report，让 case 矩阵能覆盖真实失败样本。",
            "优先补 canon ledger / entity aliases / state 信号，再重新读取本报告。",
        ]
    return [
        "保持 GraphRAG、Zep、向量库、reranker 为触发式增强，不接入重型服务。",
        "等项目达到更长篇幅或出现稳定检索失败样本后再生成 case 矩阵。",
    ]

"""Graph Memory Shadow Compare Pack MVP.

This report compares GraphRAG / Zep / Temporal Memory candidate layers using
only local trigger evidence and design-pack data. It stays read-only and does
not connect providers, vector stores, graph databases, rerankers, or LLMs.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_spike_design_pack import (
    GraphMemorySpikeDesignPackRequestError,
    get_graph_memory_spike_design_pack,
)

VERSION = "graph-memory-shadow-compare-pack-mvp"
BASELINE = "BM25 + canon ledger + entity aliases"


class GraphMemoryShadowComparePackRequestError(ValueError):
    """Invalid graph-memory shadow compare request, mapped to HTTP 400."""


def get_graph_memory_shadow_compare_pack(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only shadow compare pack."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        design_pack = get_graph_memory_spike_design_pack(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemorySpikeDesignPackRequestError as exc:
        raise GraphMemoryShadowComparePackRequestError(str(exc)) from exc

    status = _status(design_pack)
    source_records = _source_records(design_pack)
    sample_cases = _sample_cases(source_records, design_pack)
    comparisons = _comparisons(status, design_pack, sample_cases)
    acceptance_results = _acceptance_results(status, design_pack, sample_cases, comparisons)
    no_go_conditions = list(design_pack.get("no_go_conditions") or [])
    shadow_gate = _shadow_gate(status, design_pack, sample_cases, comparisons)
    summary = _summary(
        sid,
        design_pack,
        comparisons,
        sample_cases,
        acceptance_results,
        no_go_conditions,
    )
    manifest = _manifest(
        generated_at,
        status,
        summary,
        shadow_gate,
        comparisons,
        sample_cases,
        acceptance_results,
        no_go_conditions,
        design_pack,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_shadow_compare_pack",
        "status": status,
        "story_slug": sid,
        "source_kind": design_pack.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "shadow_gate": shadow_gate,
        "comparisons": comparisons,
        "sample_cases": sample_cases,
        "acceptance_results": acceptance_results,
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(design_pack, comparisons, sample_cases),
        "boundaries": [
            "只读比较 GraphRAG、Zep、Temporal Memory 候选层收益，不写项目 artifact。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开 opt-in spike。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryShadowComparePackRequestError("invalid slug")
    return sid


def _status(design_pack: dict[str, Any]) -> str:
    design_status = str(design_pack.get("status") or "")
    if design_status == "ready_for_spike":
        return "ready_for_shadow_compare"
    if design_status == "needs_more_evidence":
        return "needs_more_evidence"
    return "deferred"


def _source_records(design_pack: dict[str, Any]) -> list[dict[str, Any]]:
    manifest = design_pack.get("manifest") or {}
    source_evidence = manifest.get("source_evidence") or {}
    return [record for record in source_evidence.get("records") or [] if isinstance(record, dict)]


def _sample_cases(
    records: list[dict[str, Any]],
    design_pack: dict[str, Any],
) -> list[dict[str, Any]]:
    candidate_ids = [
        str(layer.get("id") or "")
        for layer in design_pack.get("layer_plans") or []
        if layer.get("status") in {"candidate", "monitor"}
    ]
    cases: list[dict[str, Any]] = []
    for record in records[:10]:
        eval_id = str(record.get("eval_id") or record.get("id") or "")
        cases.append(
            {
                "eval_id": eval_id,
                "story_slug": str(record.get("story_slug") or ""),
                "display_name": str(record.get("display_name") or record.get("story_slug") or ""),
                "query": str(record.get("query") or ""),
                "expected_item_id": str(record.get("expected_item_id") or ""),
                "baseline_status": str(record.get("replay_status") or "unknown"),
                "diagnosis": str(record.get("diagnosis") or record.get("reason") or ""),
                "shadow_targets": candidate_ids,
            }
        )
    return cases


def _comparisons(
    status: str,
    design_pack: dict[str, Any],
    sample_cases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    summary = design_pack.get("summary") or {}
    comparisons: list[dict[str, Any]] = []
    for layer in design_pack.get("layer_plans") or []:
        layer_id = str(layer.get("id") or "unknown")
        layer_status = _comparison_status(status, str(layer.get("status") or "deferred"))
        projected_gain_score = _projected_gain_score(layer_id, layer_status, summary, sample_cases)
        risk_score = _risk_score(layer_id, layer_status, layer)
        missing_evidence = _missing_evidence(layer_id, layer_status, sample_cases, summary)
        comparisons.append(
            {
                "id": layer_id,
                "label": str(layer.get("label") or layer_id),
                "status": layer_status,
                "source_status": str(layer.get("status") or "unknown"),
                "baseline": BASELINE,
                "shadow_method": _shadow_method(layer_id),
                "projected_gain_score": projected_gain_score,
                "risk_score": risk_score,
                "decision": _decision(layer_id, layer_status, projected_gain_score, missing_evidence),
                "sample_case_count": len(sample_cases),
                "required_gate_ids": list(layer.get("acceptance_gate_ids") or []),
                "missing_evidence": missing_evidence,
                "notes": _notes(layer_id, layer_status, projected_gain_score),
                "rollback_strategy": str(layer.get("rollback_strategy") or ""),
            }
        )
    return comparisons


def _comparison_status(status: str, layer_status: str) -> str:
    if status == "ready_for_shadow_compare" and layer_status == "candidate":
        return "candidate"
    if status == "needs_more_evidence" and layer_status in {"candidate", "monitor"}:
        return "monitor"
    return "deferred"


def _projected_gain_score(
    layer_id: str,
    layer_status: str,
    summary: dict[str, Any],
    sample_cases: list[dict[str, Any]],
) -> int:
    if layer_status == "deferred":
        return 0
    lexical_gap = int(summary.get("trend_lexical_gap_count") or 0)
    relation = int(summary.get("relation_signal_count") or 0)
    causal = int(summary.get("causal_signal_count") or 0)
    state = int(summary.get("state_signal_count") or 0)
    samples = len(sample_cases)
    if layer_id == "graphrag":
        return min(100, 20 + lexical_gap * 12 + relation * 8 + causal * 6 + samples * 10)
    if layer_id == "zep":
        return min(100, 15 + lexical_gap * 8 + samples * 8 + _foundation_gap_score(summary))
    if layer_id == "temporal_memory":
        return min(100, 10 + state * 10 + causal * 4 + samples * 6)
    return min(100, 10 + samples * 5)


def _foundation_gap_score(summary: dict[str, Any]) -> int:
    score = 0
    if str(summary.get("evidence_status") or "") == "triggered":
        score += 8
    if int(summary.get("trend_lexical_gap_count") or 0) > 0:
        score += 8
    return score


def _risk_score(layer_id: str, layer_status: str, layer: dict[str, Any]) -> int:
    if layer_status == "deferred":
        return 0
    base = len(layer.get("risks") or []) * 10
    extra = {"graphrag": 10, "zep": 18, "temporal_memory": 12}.get(layer_id, 8)
    return min(100, base + extra)


def _missing_evidence(
    layer_id: str,
    layer_status: str,
    sample_cases: list[dict[str, Any]],
    summary: dict[str, Any],
) -> list[str]:
    missing: list[str] = []
    if layer_status == "deferred":
        missing.append("candidate_trigger")
    if not sample_cases:
        missing.append("retrieval_eval_records")
    if layer_id == "temporal_memory" and int(summary.get("state_signal_count") or 0) == 0:
        missing.append("state_signal_records")
    return missing


def _shadow_method(layer_id: str) -> str:
    return {
        "graphrag": "用本地 ledger 实体关系和样本 query 生成图检索影子命中，不进入默认召回。",
        "zep": "用本地账本/别名缺口模拟长期记忆收益，不同步外部 Zep 服务。",
        "temporal_memory": "用状态/时间信号对照跨章节状态解释，不覆盖 state_snapshot。",
    }.get(layer_id, "保留为只读观察项。")


def _decision(
    layer_id: str,
    layer_status: str,
    projected_gain_score: int,
    missing_evidence: list[str],
) -> str:
    if layer_status == "deferred":
        return "defer"
    if "retrieval_eval_records" in missing_evidence:
        return "collect_samples"
    if layer_id == "zep" and projected_gain_score < 35:
        return "collect_foundation_evidence"
    if projected_gain_score > 0:
        return "shadow_compare"
    return "defer"


def _notes(layer_id: str, layer_status: str, projected_gain_score: int) -> list[str]:
    if layer_status == "deferred":
        return ["当前设计包未把该层列为候选，继续观察。"]
    return [
        f"预计收益分 {projected_gain_score}，只用于排序候选层，不代表真实 provider 性能。",
        "对照结果必须能回溯到本地 eval records、canon ledger 或状态信号。",
    ]


def _acceptance_results(
    status: str,
    design_pack: dict[str, Any],
    sample_cases: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    comparison_by_gate: dict[str, list[dict[str, Any]]] = {}
    for comparison in comparisons:
        for gate_id in comparison.get("required_gate_ids") or []:
            comparison_by_gate.setdefault(str(gate_id), []).append(comparison)
    results: list[dict[str, Any]] = []
    for gate in design_pack.get("acceptance_gates") or []:
        gate_id = str(gate.get("id") or "")
        related = comparison_by_gate.get(gate_id, [])
        passed = _gate_passed(gate_id, status, sample_cases, related)
        results.append(
            {
                "gate_id": gate_id,
                "label": str(gate.get("label") or gate_id),
                "status": str(gate.get("status") or "unknown"),
                "passed": passed,
                "result_status": "ready" if passed else "needs_evidence",
                "target": str(gate.get("target") or ""),
                "evidence": _gate_evidence(gate_id, sample_cases, related),
            }
        )
    return results


def _gate_passed(
    gate_id: str,
    status: str,
    sample_cases: list[dict[str, Any]],
    related: list[dict[str, Any]],
) -> bool:
    if gate_id == "contract_safety":
        return True
    if status != "ready_for_shadow_compare":
        return False
    if gate_id == "retrieval_gain":
        return bool(sample_cases) and any(
            item["decision"] == "shadow_compare" for item in related
        )
    if gate_id == "zep_foundation_gap_reduction":
        return bool(related) and bool(sample_cases)
    if gate_id in {"relation_traceability", "temporal_state_traceability"}:
        return bool(related)
    return False


def _gate_evidence(
    gate_id: str,
    sample_cases: list[dict[str, Any]],
    related: list[dict[str, Any]],
) -> str:
    if gate_id == "contract_safety":
        return "本报告只读生成，不写 artifact，不改变 runner 或检索默认链路。"
    if sample_cases:
        return f"{len(sample_cases)} 条本地 eval records，{len(related)} 个候选层关联该门槛。"
    return "暂无本地样本，先继续采集 retrieval failure samples。"


def _shadow_gate(
    status: str,
    design_pack: dict[str, Any],
    sample_cases: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_count = sum(1 for item in comparisons if item["status"] == "candidate")
    status_map = {
        "ready_for_shadow_compare": "shadow_compare_ready",
        "needs_more_evidence": "collect_more_evidence",
        "deferred": "deferred",
    }
    return {
        "id": "graph_memory_shadow_compare_ready",
        "status": status_map[status],
        "passed": status == "ready_for_shadow_compare" and candidate_count > 0,
        "reason": _gate_reason(status, candidate_count, len(sample_cases)),
        "design_status": str(design_pack.get("status") or "unknown"),
        "candidate_layer_count": candidate_count,
        "sample_case_count": len(sample_cases),
    }


def _gate_reason(status: str, candidate_count: int, sample_count: int) -> str:
    if status == "ready_for_shadow_compare" and candidate_count > 0:
        return f"{candidate_count} 个候选层可做本地 shadow compare，当前样本 {sample_count} 条。"
    if status == "needs_more_evidence":
        return "设计包仍需补证据，先积累样本和本地记忆层状态。"
    return "当前证据不足，继续使用现有文件型记忆与 BM25 检索。"


def _summary(
    story_slug: str,
    design_pack: dict[str, Any],
    comparisons: list[dict[str, Any]],
    sample_cases: list[dict[str, Any]],
    acceptance_results: list[dict[str, Any]],
    no_go_conditions: list[str],
) -> dict[str, Any]:
    design_summary = design_pack.get("summary") or {}
    best = max((item["projected_gain_score"] for item in comparisons), default=0)
    best_layer = next(
        (item["id"] for item in comparisons if item["projected_gain_score"] == best and best > 0),
        "",
    )
    return {
        "story_slug": story_slug,
        "source_kind": design_pack.get("source_kind") or "unknown",
        "design_status": design_pack.get("status") or "unknown",
        "evidence_status": design_summary.get("evidence_status") or "unknown",
        "design_gate_status": (design_pack.get("design_gate") or {}).get("status") or "unknown",
        "candidate_layer_count": sum(
            1 for item in comparisons if item["status"] == "candidate"
        ),
        "monitor_layer_count": sum(1 for item in comparisons if item["status"] == "monitor"),
        "comparison_count": len(comparisons),
        "sample_case_count": len(sample_cases),
        "acceptance_result_count": len(acceptance_results),
        "no_go_condition_count": len(no_go_conditions),
        "best_projected_gain_score": best,
        "best_candidate_layer": best_layer,
        "trend_record_count": int(design_summary.get("trend_record_count") or 0),
        "trend_lexical_gap_count": int(design_summary.get("trend_lexical_gap_count") or 0),
        "relation_signal_count": int(design_summary.get("relation_signal_count") or 0),
        "causal_signal_count": int(design_summary.get("causal_signal_count") or 0),
        "state_signal_count": int(design_summary.get("state_signal_count") or 0),
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
    status: str,
    summary: dict[str, Any],
    shadow_gate: dict[str, Any],
    comparisons: list[dict[str, Any]],
    sample_cases: list[dict[str, Any]],
    acceptance_results: list[dict[str, Any]],
    no_go_conditions: list[str],
    design_pack: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": status,
        "summary": summary,
        "shadow_gate": shadow_gate,
        "comparisons": comparisons,
        "sample_cases": sample_cases,
        "acceptance_results": acceptance_results,
        "no_go_conditions": no_go_conditions,
        "source_design_pack": {
            "version": design_pack.get("version"),
            "status": design_pack.get("status"),
            "design_gate": design_pack.get("design_gate"),
            "layer_plans": design_pack.get("layer_plans") or [],
        },
    }


def _warnings(
    design_pack: dict[str, Any],
    comparisons: list[dict[str, Any]],
    sample_cases: list[dict[str, Any]],
) -> list[str]:
    warnings = [str(item) for item in design_pack.get("warnings") or []]
    if not any(item["status"] == "candidate" for item in comparisons):
        warnings.append("当前没有候选层进入 shadow compare。")
    if not sample_cases:
        warnings.append("当前没有本地 eval records，收益只能暂缓判断。")
    return warnings[:8]


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_shadow_compare":
        return [
            "先把候选层对照结果做成只读报告，不进入默认检索或 runner。",
            "优先比较 GraphRAG 与 Zep 的本地样本收益和回退成本。",
            "只有 shadow compare 稳定证明收益后，再评估真实 provider opt-in spike。",
        ]
    if status == "needs_more_evidence":
        return [
            "继续积累 retrieval failure samples 和跨项目趋势快照。",
            "先补本地 canon ledger、entity aliases 与状态信号，再做 shadow compare。",
        ]
    return [
        "继续使用 BM25、canon ledger、entity aliases 与 runtime memory。",
        "等真实长篇样本持续暴露关系/因果/状态缺口后再进入 shadow compare。",
    ]

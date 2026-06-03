"""GraphRAG / Zep Trigger Evidence MVP.

This read-only report combines the older v0.9.3 graph-memory trigger with the
new retrieval-sample trend snapshot. It only prepares evidence for a later
spike and never connects GraphRAG, Zep, vector stores, rerankers, or providers.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_evaluation import (
    evaluate_graph_memory_trigger,
)
from living_novel_engine.service.project_health import resolve_story_path
from living_novel_engine.service.retrieval_probe import evaluate_retrieval_probes
from living_novel_engine.service.retrieval_samples_trend_snapshot import (
    get_retrieval_samples_trend_snapshot,
)

VERSION = "graph-memory-trigger-evidence-mvp"


class GraphMemoryTriggerEvidenceRequestError(ValueError):
    """Invalid graph-memory trigger evidence request, mapped to HTTP 400."""


def get_graph_memory_trigger_evidence(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return read-only evidence for GraphRAG / Zep spike decisions."""

    sid = _safe_slug(slug)
    project_dir, source_kind = resolve_story_path(sid, projects_dir)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    graph_report = evaluate_graph_memory_trigger(sid, projects_dir=projects_dir)
    retrieval_probe = evaluate_retrieval_probes(sid, projects_dir=projects_dir)
    trend = get_retrieval_samples_trend_snapshot(projects_dir=projects_dir, now=now)
    ledger_signals = _ledger_signals(project_dir / "memory" / "canon_ledger.jsonl")
    summary = _summary(sid, source_kind, graph_report, retrieval_probe, trend, ledger_signals)
    status = _status(summary)
    trigger_gate = _trigger_gate(status, summary)
    signals = _signals(summary)
    candidate_layers = _candidate_layers(status, summary)
    records = list(trend.get("records") or [])[:20]
    manifest = _manifest(
        generated_at,
        status,
        summary,
        trigger_gate,
        signals,
        candidate_layers,
        records,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_trigger_evidence",
        "status": status,
        "story_slug": sid,
        "source_kind": source_kind,
        "generated_at": generated_at,
        "summary": summary,
        "trigger_gate": trigger_gate,
        "signals": signals,
        "candidate_layers": candidate_layers,
        "records": records,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(graph_report, trend),
        "boundaries": [
            "只读聚合现有 Graph Memory trigger、retrieval probe、跨项目样本趋势和 canon ledger 信号。",
            "不写 artifact，不生成 embedding，不创建向量索引。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker 或真实 LLM。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryTriggerEvidenceRequestError("invalid slug")
    return sid


def _summary(
    story_slug: str,
    source_kind: str,
    graph_report: dict[str, Any],
    retrieval_probe: dict[str, Any],
    trend: dict[str, Any],
    ledger_signals: dict[str, int],
) -> dict[str, Any]:
    graph_metrics = graph_report.get("metrics") or {}
    graph_trigger = graph_report.get("trigger") or {}
    trend_summary = trend.get("summary") or {}
    probe_metrics = retrieval_probe.get("metrics") or {}
    lexical_gap_count = int(trend_summary.get("still_failing_lexically_count") or 0)
    relation_signal_count = int(ledger_signals.get("relation_signal_count") or 0)
    causal_signal_count = int(ledger_signals.get("causal_signal_count") or 0)
    state_signal_count = int(ledger_signals.get("state_signal_count") or 0)
    return {
        "story_slug": story_slug,
        "source_kind": source_kind,
        "graph_memory_status": str(graph_report.get("status") or "unknown"),
        "graph_memory_should_evaluate": bool(graph_trigger.get("should_evaluate")),
        "graph_memory_reasons": list(graph_trigger.get("reasons") or []),
        "chapter_count": int(graph_metrics.get("chapter_count") or 0),
        "character_count": int(graph_metrics.get("character_count") or 0),
        "canon_ledger_count": int(graph_metrics.get("canon_ledger_count") or 0),
        "canon_ledger_status": str(graph_metrics.get("canon_ledger_status") or "unknown"),
        "entity_alias_count": int(graph_metrics.get("entity_alias_count") or 0),
        "entity_alias_status": str(graph_metrics.get("entity_alias_status") or "unknown"),
        "consistency_severe_issue_count": int(
            graph_metrics.get("consistency_severe_issue_count") or 0
        ),
        "retrieval_probe_status": str(retrieval_probe.get("status") or "unknown"),
        "retrieval_probe_hit_rate": float(probe_metrics.get("hit_rate") or 0.0),
        "trend_project_count": int(trend_summary.get("project_count") or 0),
        "trend_record_count": int(trend_summary.get("record_count") or 0),
        "trend_lexical_gap_count": lexical_gap_count,
        "trend_empty_project_count": int(trend_summary.get("empty_project_count") or 0),
        "relation_signal_count": relation_signal_count,
        "causal_signal_count": causal_signal_count,
        "state_signal_count": state_signal_count,
        "relation_or_state_pressure": (
            relation_signal_count + causal_signal_count + state_signal_count
        )
        > 0,
        "writes_artifacts": False,
        "external_services_required": False,
        "uses_graphrag": False,
        "uses_zep": False,
        "uses_vector_store": False,
        "uses_reranker": False,
        "plaintext_key_returned": False,
    }


def _status(summary: dict[str, Any]) -> str:
    if summary["graph_memory_should_evaluate"]:
        return "triggered"
    if summary["trend_lexical_gap_count"] > 0 or summary["graph_memory_status"] == "monitor":
        return "monitor"
    return "not_triggered"


def _trigger_gate(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    status_map = {
        "triggered": "ready_for_spike_design",
        "monitor": "needs_more_evidence",
        "not_triggered": "deferred",
    }
    return {
        "id": "graph_memory_trigger_evidence_ready",
        "status": status_map.get(status, status),
        "passed": status == "triggered",
        "reason": _gate_reason(status),
        "graph_memory_status": summary["graph_memory_status"],
        "trend_record_count": summary["trend_record_count"],
        "trend_lexical_gap_count": summary["trend_lexical_gap_count"],
    }


def _signals(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": "graph_memory_trigger",
            "label": "图记忆触发",
            "status": summary["graph_memory_status"],
            "value": int(summary["graph_memory_should_evaluate"]),
            "detail": _graph_detail(summary),
        },
        {
            "id": "retrieval_trend_pressure",
            "label": "检索趋势压力",
            "status": "attention" if summary["trend_lexical_gap_count"] > 0 else "ready",
            "value": summary["trend_lexical_gap_count"],
            "detail": (
                f"{summary['trend_lexical_gap_count']} 个跨项目样本仍是词面缺口。"
                if summary["trend_lexical_gap_count"] > 0
                else "跨项目趋势暂未暴露词面缺口。"
            ),
        },
        {
            "id": "relation_chain_pressure",
            "label": "关系链压力",
            "status": "attention" if summary["relation_signal_count"] > 0 else "ready",
            "value": summary["relation_signal_count"],
            "detail": f"{summary['relation_signal_count']} 条 ledger 记录含多实体关系信号。",
        },
        {
            "id": "causal_state_pressure",
            "label": "因果/状态压力",
            "status": (
                "attention"
                if summary["causal_signal_count"] + summary["state_signal_count"] > 0
                else "ready"
            ),
            "value": summary["causal_signal_count"] + summary["state_signal_count"],
            "detail": (
                f"{summary['causal_signal_count']} 条因果信号，"
                f"{summary['state_signal_count']} 条状态信号。"
            ),
        },
        {
            "id": "external_service_boundary",
            "label": "外部服务边界",
            "status": "deferred",
            "value": 0,
            "detail": "本报告只输出触发证据，不自动接入 GraphRAG、Zep、向量库或 reranker。",
        },
    ]


def _candidate_layers(status: str, summary: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = status == "triggered"
    trend_pressure = summary["trend_lexical_gap_count"] > 0
    foundation_gap = (
        summary["canon_ledger_status"] != "ready"
        or summary["canon_ledger_count"] == 0
        or summary["entity_alias_status"] != "ready"
        or summary["entity_alias_count"] == 0
    )
    return [
        {
            "id": "graphrag",
            "label": "GraphRAG",
            "status": "candidate" if candidate or trend_pressure else "deferred",
            "reason": (
                "已有图记忆触发或跨项目词面缺口，可进入 GraphRAG spike 设计。"
                if candidate or trend_pressure
                else "当前证据不足，继续使用 BM25 + canon ledger + entity aliases。"
            ),
        },
        {
            "id": "zep",
            "label": "Zep",
            "status": "candidate" if candidate and foundation_gap else "deferred",
            "reason": (
                "当前账本/别名层存在缺口，可比较 Zep 记忆服务是否补足事实/关系管理。"
                if candidate and foundation_gap
                else "暂不需要长期记忆服务；先补足本地文件型记忆。"
            ),
        },
        {
            "id": "temporal_memory",
            "label": "Temporal Memory",
            "status": (
                "candidate"
                if candidate and summary["state_signal_count"] > 0
                else "deferred"
            ),
            "reason": (
                "状态信号较多，可在 spike 中评估时间/状态链记忆。"
                if candidate and summary["state_signal_count"] > 0
                else "状态链证据不足，继续用现有 state_snapshot 与 runtime memory。"
            ),
        },
    ]


def _ledger_signals(path: Path) -> dict[str, int]:
    relation_count = 0
    causal_count = 0
    state_count = 0
    if not path.exists():
        return {
            "relation_signal_count": 0,
            "causal_signal_count": 0,
            "state_signal_count": 0,
        }
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return {
            "relation_signal_count": 0,
            "causal_signal_count": 0,
            "state_signal_count": 0,
        }
    for raw in lines:
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type") or "").lower()
        statement = str(item.get("statement") or "")
        entities = [str(entity) for entity in item.get("entities") or [] if str(entity)]
        if len(entities) >= 2 or item_type in {"relationship", "relation"}:
            relation_count += 1
        if _contains_any(statement, ("因为", "导致", "所以", "后果", "代价", "触发", "引发", "伏笔")):
            causal_count += 1
        if item_type in {"state", "resource"} or _contains_any(
            statement,
            ("受伤", "拥有", "失去", "身份", "秘密", "灵力", "道具", "位置", "状态"),
        ):
            state_count += 1
    return {
        "relation_signal_count": relation_count,
        "causal_signal_count": causal_count,
        "state_signal_count": state_count,
    }


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _manifest(
    generated_at: str,
    status: str,
    summary: dict[str, Any],
    trigger_gate: dict[str, Any],
    signals: list[dict[str, Any]],
    candidate_layers: list[dict[str, Any]],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": status,
        "summary": summary,
        "trigger_gate": trigger_gate,
        "signals": signals,
        "candidate_layers": candidate_layers,
        "records": records,
    }


def _graph_detail(summary: dict[str, Any]) -> str:
    reasons = ", ".join(summary["graph_memory_reasons"]) or "无触发原因"
    return (
        f"{summary['chapter_count']} 章，账本 {summary['canon_ledger_status']}/"
        f"{summary['canon_ledger_count']} 条，别名 {summary['entity_alias_status']}/"
        f"{summary['entity_alias_count']} 条；原因：{reasons}。"
    )


def _gate_reason(status: str) -> str:
    if status == "triggered":
        return "已有足够证据进入 GraphRAG/Zep spike 设计，但仍不自动接入外部服务。"
    if status == "monitor":
        return "已有部分趋势压力，继续积累样本和修复本地记忆层。"
    return "当前证据不足，继续使用现有文件型记忆与 BM25 检索。"


def _warnings(graph_report: dict[str, Any], trend: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    warnings.extend(str(item) for item in graph_report.get("warnings") or [])
    warnings.extend(str(item) for item in trend.get("warnings") or [])
    return warnings[:8]


def _next_steps(status: str) -> list[str]:
    if status == "triggered":
        return [
            "先写 GraphRAG/Zep spike 设计，不直接接生产服务。",
            "优先补本地 ledger/aliases/样本复跑，确认缺口不是坏数据造成。",
            "如果进入 spike，保持现有 artifact 和 runner 契约 additive。",
        ]
    if status == "monitor":
        return [
            "继续积累 retrieval failure samples 和跨项目趋势快照。",
            "先修复本地账本、别名、状态投影，再判断是否需要 GraphRAG/Zep。",
        ]
    return [
        "继续使用当前 BM25、canon ledger、entity aliases 与 runtime memory。",
        "等真实长篇样本持续暴露关系/因果/状态缺口后再评估重型记忆。",
    ]

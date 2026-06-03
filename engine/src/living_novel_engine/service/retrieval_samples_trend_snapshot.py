"""Retrieval Samples Trend Snapshot MVP.

Builds a read-only snapshot from the cross-project retrieval samples index.
It does not persist trend history, call providers, create embeddings, or connect
vector stores.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.service.cross_project_retrieval_samples_index import (
    get_cross_project_retrieval_samples_index,
)

VERSION = "retrieval-samples-trend-snapshot-mvp"


def get_retrieval_samples_trend_snapshot(
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a read-only trend snapshot over local retrieval sample records."""

    index = get_cross_project_retrieval_samples_index(projects_dir=projects_dir, now=now)
    generated_at = str(index.get("generated_at") or (now or datetime.now()).isoformat())
    summary = _summary(index)
    status = _status(summary)
    trend_gate = _trend_gate(status, summary)
    signals = _signals(summary)
    project_trends = _project_trends(index.get("projects") or [])
    manifest = _manifest(
        generated_at,
        status,
        summary,
        trend_gate,
        signals,
        project_trends,
        index.get("records") or [],
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_retrieval_samples_trend_snapshot",
        "status": status,
        "generated_at": generated_at,
        "summary": summary,
        "trend_gate": trend_gate,
        "signals": signals,
        "project_trends": project_trends,
        "records": list(index.get("records") or [])[:50],
        "manifest": manifest,
        "content_json": content_json,
        "warnings": list(index.get("warnings") or []),
        "boundaries": [
            "只读复用跨项目样本索引，不写趋势 artifact。",
            "不生成 embedding，不创建向量索引，不连接 GraphRAG、Zep、向量库或 reranker。",
            "不读取、不返回也不记录明文 Key。",
            "不替换 retrieve_context，不改变 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status, summary),
    }


def _summary(index: dict[str, Any]) -> dict[str, Any]:
    source = index.get("summary") or {}
    project_count = int(source.get("project_count") or 0)
    record_count = int(source.get("record_count") or 0)
    empty_project_count = int(source.get("empty_project_count") or 0)
    blocked_project_count = int(source.get("blocked_project_count") or 0)
    attention_project_count = int(source.get("attention_project_count") or 0)
    still_failing = int(source.get("still_failing_lexically_count") or 0)
    covered = int(source.get("covered_by_current_retrieval_count") or 0)
    skipped = int(source.get("skipped_count") or 0)
    return {
        "project_count": project_count,
        "ready_project_count": int(source.get("ready_project_count") or 0),
        "empty_project_count": empty_project_count,
        "attention_project_count": attention_project_count,
        "blocked_project_count": blocked_project_count,
        "record_count": record_count,
        "replay_case_count": int(source.get("replay_case_count") or 0),
        "still_failing_lexically_count": still_failing,
        "covered_by_current_retrieval_count": covered,
        "skipped_count": skipped,
        "sampled_project_ratio": _ratio(
            project_count - empty_project_count - blocked_project_count,
            project_count,
        ),
        "lexical_gap_ratio": _ratio(still_failing, max(record_count + skipped, 1)),
        "writes_artifacts": False,
        "external_services_required": False,
        "uses_embedding_provider": False,
        "uses_vector_store": False,
        "plaintext_key_returned": False,
    }


def _status(summary: dict[str, Any]) -> str:
    if summary["project_count"] == 0:
        return "empty"
    if summary["record_count"] > 0:
        return "ready"
    if summary["blocked_project_count"] > 0:
        return "blocked"
    return "attention"


def _trend_gate(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    status_map = {
        "ready": "ready",
        "empty": "needs_projects",
        "attention": "needs_records",
        "blocked": "blocked",
    }
    return {
        "id": "retrieval_samples_trend_snapshot_ready",
        "status": status_map.get(status, status),
        "passed": status == "ready",
        "reason": _gate_reason(status),
        "project_count": summary["project_count"],
        "record_count": summary["record_count"],
    }


def _signals(summary: dict[str, Any]) -> list[dict[str, Any]]:
    project_count = summary["project_count"]
    record_count = summary["record_count"]
    empty_count = summary["empty_project_count"]
    blocked_count = summary["blocked_project_count"]
    lexical_gap_count = summary["still_failing_lexically_count"]
    covered_count = summary["covered_by_current_retrieval_count"]
    return [
        {
            "id": "sample_coverage",
            "label": "样本覆盖",
            "status": "ready" if record_count > 0 else "attention",
            "value": record_count,
            "detail": (
                "已有可比较 records。"
                if record_count > 0
                else "暂无可比较 records，先积累失败样本。"
            ),
        },
        {
            "id": "lexical_gap_pressure",
            "label": "词面缺口压力",
            "status": "attention" if lexical_gap_count > 0 else "ready",
            "value": lexical_gap_count,
            "detail": (
                f"{lexical_gap_count} 个 case 仍未被当前词面检索覆盖。"
                if lexical_gap_count > 0
                else "当前样本未暴露词面缺口。"
            ),
        },
        {
            "id": "empty_project_pressure",
            "label": "空样本项目",
            "status": "attention" if empty_count > 0 else "ready",
            "value": empty_count,
            "detail": (
                f"{empty_count} 个项目暂无迁移 records。"
                if empty_count > 0
                else "本地项目均有可比较样本或已被跳过。"
            ),
        },
        {
            "id": "blocked_project_pressure",
            "label": "损坏样本项目",
            "status": "blocked" if blocked_count > 0 else "ready",
            "value": blocked_count,
            "detail": (
                f"{blocked_count} 个项目样本需要先修复。"
                if blocked_count > 0
                else "未发现 blocked 项目。"
            ),
        },
        {
            "id": "external_provider_pressure",
            "label": "重型检索触发",
            "status": "deferred",
            "value": max(lexical_gap_count - covered_count, 0),
            "detail": (
                "该快照只给证据，不自动接入 Embedding、GraphRAG、Zep、向量库或 reranker。"
                if project_count > 0
                else "暂无项目证据，不触发外部检索服务。"
            ),
        },
    ]


def _project_trends(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for project in projects:
        status = str(project.get("status") or "")
        record_count = int(project.get("record_count") or 0)
        lexical_gap_count = int(project.get("still_failing_lexically_count") or 0)
        covered_count = int(project.get("covered_by_current_retrieval_count") or 0)
        skipped_count = int(project.get("skipped_count") or 0)
        rows.append(
            {
                "story_slug": str(project.get("story_slug") or ""),
                "display_name": str(project.get("display_name") or ""),
                "status": status,
                "record_count": record_count,
                "replay_case_count": int(project.get("replay_case_count") or 0),
                "lexical_gap_count": lexical_gap_count,
                "covered_count": covered_count,
                "skipped_count": skipped_count,
                "trend_bucket": _trend_bucket(status, record_count, lexical_gap_count),
            }
        )
    rows.sort(
        key=lambda item: (
            int(item["record_count"]),
            int(item["lexical_gap_count"]),
            str(item["story_slug"]),
        ),
        reverse=True,
    )
    return rows


def _trend_bucket(status: str, record_count: int, lexical_gap_count: int) -> str:
    if status == "blocked":
        return "blocked"
    if record_count == 0:
        return "empty_samples"
    if lexical_gap_count > 0:
        return "has_samples"
    return "covered_samples"


def _manifest(
    generated_at: str,
    status: str,
    summary: dict[str, Any],
    trend_gate: dict[str, Any],
    signals: list[dict[str, Any]],
    project_trends: list[dict[str, Any]],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": status,
        "summary": summary,
        "trend_gate": trend_gate,
        "signals": signals,
        "project_trends": project_trends,
        "records": list(records)[:50],
    }


def _gate_reason(status: str) -> str:
    if status == "ready":
        return "已有跨项目 records，可观察词面缺口、覆盖和空样本趋势。"
    if status == "empty":
        return "暂无本地项目，无法形成趋势快照。"
    if status == "attention":
        return "已有项目但暂无 records，先补失败样本或迁移包。"
    return "存在 blocked 项目，先修复样本或记忆目标。"


def _next_steps(status: str, summary: dict[str, Any]) -> list[str]:
    if status == "ready":
        steps = [
            "持续积累 retrieval failure samples，观察 lexical gap 是否跨项目重复出现。",
            "先用该快照评估 GraphRAG/Zep/向量库触发条件，不直接接入重型服务。",
        ]
        if summary["still_failing_lexically_count"] > 0:
            steps.append("下一刀可做 GraphRAG / Zep Trigger Evidence，只产出触发证据。")
        return steps
    if status == "blocked":
        return ["先修复 blocked 项目样本，再重新生成趋势快照。"]
    if status == "attention":
        return ["先迁移至少一个项目的失败样本，再观察趋势。"]
    return ["先创建或导入本地项目，再记录检索失败样本。"]


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 3)

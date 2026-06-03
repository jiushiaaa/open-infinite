"""Retrieval Sample Migration Pack MVP.

Builds a read-only JSON migration pack from replayed retrieval failure cases.
It prepares stable evaluation records without writing artifacts, calling
providers, creating embeddings, or connecting vector stores.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.retrieval_sample_replay_report import (
    get_retrieval_sample_replay_report,
)

VERSION = "retrieval-sample-migration-pack-mvp"


class RetrievalSampleMigrationPackRequestError(ValueError):
    """Invalid retrieval sample migration pack request, mapped to HTTP 400."""


def get_retrieval_sample_migration_pack(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a read-only migration pack for stable retrieval eval records."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    replay = get_retrieval_sample_replay_report(sid, projects_dir=projects_dir, now=now)
    records = _records(sid, generated_at, replay)
    summary = _summary(replay, records)
    status = _status(replay, summary)
    gate = _gate(status, summary)
    manifest = _manifest(sid, generated_at, status, summary, gate, records)
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_retrieval_sample_migration_pack",
        "status": status,
        "story_slug": sid,
        "source_kind": replay.get("source_kind", ""),
        "generated_at": generated_at,
        "filename": f"{sid}-retrieval-migration-pack.json",
        "content_type": "application/json; charset=utf-8",
        "summary": summary,
        "migration_gate": gate,
        "manifest": manifest,
        "records": records,
        "content_json": content_json,
        "warnings": list(replay.get("warnings") or []),
        "boundaries": [
            "只读整理本地失败样本复跑 case，不写迁移包 artifact。",
            "不生成 embedding，不创建向量索引，不连接向量库或 reranker。",
            "不读取、不返回也不记录明文 Key。",
            "不替换 retrieve_context，不改变 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise RetrievalSampleMigrationPackRequestError("invalid slug")
    return sid


def _records(
    story_slug: str,
    generated_at: str,
    replay: dict[str, Any],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, case in enumerate(replay.get("cases") or [], start=1):
        if not _is_migratable(case):
            continue
        expected_item_id = str(case.get("target_item_id") or "")
        records.append(
            {
                "eval_id": f"{story_slug}-retrieval-eval-{len(records) + 1:03d}",
                "query": str(case.get("query") or ""),
                "current_chapter": int(case.get("current_chapter") or 1),
                "expected_entities": list(case.get("expected_entities") or []),
                "expected_item_id": expected_item_id,
                "expected_source": _expected_source(expected_item_id),
                "target_statement": str(case.get("target_statement") or ""),
                "diagnosis": str(case.get("diagnosis") or ""),
                "replay_status": str(case.get("replay_status") or ""),
                "labels": _labels(case),
                "assertions": {
                    "must_retrieve_item_id": expected_item_id,
                    "should_include_entities": list(case.get("expected_entities") or []),
                },
                "provenance": {
                    "story_slug": story_slug,
                    "generated_at": generated_at,
                    "original_case_id": str(case.get("case_id") or f"case-{index:03d}"),
                    "source_report": "retrieval-sample-replay-report",
                },
            }
        )
    return records[:50]


def _is_migratable(case: dict[str, Any]) -> bool:
    if str(case.get("replay_status") or "") in {
        "missing_memory_target",
        "invalid_case",
        "needs_review",
    }:
        return False
    return bool(str(case.get("target_item_id") or ""))


def _expected_source(expected_item_id: str) -> str:
    if ":" in expected_item_id:
        return expected_item_id.split(":", 1)[0]
    return ""


def _labels(case: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for key in ("diagnosis", "replay_status"):
        value = str(case.get(key) or "")
        if value and value not in labels:
            labels.append(value)
    return labels


def _summary(replay: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    replay_summary = replay.get("summary") or {}
    replay_case_count = int(replay_summary.get("case_count") or 0)
    record_count = len(records)
    return {
        "replay_case_count": replay_case_count,
        "record_count": record_count,
        "migratable_count": record_count,
        "skipped_count": max(replay_case_count - record_count, 0),
        "still_failing_lexically_count": int(
            replay_summary.get("still_failing_lexically_count") or 0
        ),
        "missing_memory_target_count": int(
            replay_summary.get("missing_memory_target_count") or 0
        ),
        "covered_by_current_retrieval_count": int(
            replay_summary.get("covered_by_current_retrieval_count") or 0
        ),
        "invalid_case_count": int(replay_summary.get("invalid_case_count") or 0),
        "writes_artifacts": False,
        "external_services_required": False,
        "uses_embedding_provider": False,
        "uses_vector_store": False,
        "plaintext_key_returned": False,
    }


def _status(replay: dict[str, Any], summary: dict[str, Any]) -> str:
    if replay.get("status") == "blocked" or summary["invalid_case_count"] > 0:
        return "blocked"
    if summary["replay_case_count"] == 0:
        return "empty"
    if summary["record_count"] == 0:
        return "attention"
    return "ready"


def _gate(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    status_map = {
        "ready": "ready",
        "empty": "needs_samples",
        "attention": "needs_migratable_cases",
        "blocked": "blocked",
    }
    return {
        "id": "retrieval_sample_migration_pack_ready",
        "status": status_map.get(status, status),
        "passed": status == "ready",
        "reason": _gate_reason(status),
        "record_count": summary["record_count"],
        "skipped_count": summary["skipped_count"],
    }


def _gate_reason(status: str) -> str:
    if status == "ready":
        return "存在可迁移 eval records，可作为后续检索策略对照输入。"
    if status == "empty":
        return "暂无失败样本，无法生成迁移包。"
    if status == "attention":
        return "存在 case 但缺少可断言目标项，先补记忆或样本目标。"
    return "存在损坏样本或无效 case，先修复样本。"


def _manifest(
    story_slug: str,
    generated_at: str,
    status: str,
    summary: dict[str, Any],
    gate: dict[str, Any],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "story_slug": story_slug,
        "generated_at": generated_at,
        "status": status,
        "summary": summary,
        "migration_gate": gate,
        "record_schema": {
            "required": [
                "eval_id",
                "query",
                "expected_entities",
                "expected_item_id",
                "assertions",
                "provenance",
            ],
            "purpose": "stable_retrieval_evaluation_input",
        },
        "records": records,
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready":
        return [
            "把该迁移包作为后续检索策略变化的稳定评测输入。",
            "下一步可做跨项目样本索引，统计 lexical gap、covered 和 skipped case。",
            "真实 embedding 或向量库仍需等跨样本证据充分后再 opt-in。",
        ]
    if status == "attention":
        return ["先补齐 expected_item_id 或 canon ledger target，再迁移为评测集。"]
    if status == "blocked":
        return ["先修复无效样本，再生成 migration pack。"]
    return ["先记录本地失败样本，再生成 replay report 和 migration pack。"]

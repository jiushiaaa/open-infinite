"""Cross Project Retrieval Samples Index MVP.

Aggregates per-project retrieval migration packs into a read-only local index.
It never writes index artifacts, calls providers, creates embeddings, or
connects vector stores.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from living_novel_engine.browser.paths import projects_dir as default_projects_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.retrieval_sample_migration_pack import (
    get_retrieval_sample_migration_pack,
)

VERSION = "cross-project-retrieval-samples-index-mvp"


def get_cross_project_retrieval_samples_index(
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a read-only index of retrieval sample migration packs."""

    root = Path(projects_dir) if projects_dir is not None else default_projects_dir()
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    projects, records, warnings = _scan_projects(root, generated_at, now)
    summary = _summary(projects, records)
    status = _status(summary)
    gate = _gate(status, summary)
    manifest = _manifest(generated_at, status, summary, gate, projects, records)
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_cross_project_retrieval_samples_index",
        "status": status,
        "generated_at": generated_at,
        "summary": summary,
        "index_gate": gate,
        "projects": projects,
        "records": records,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": warnings,
        "boundaries": [
            "只读扫描本地 projects，不写跨项目索引 artifact。",
            "不生成 embedding，不创建向量索引，不连接向量库或 reranker。",
            "不读取、不返回也不记录明文 Key。",
            "不替换 retrieve_context，不改变 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _scan_projects(
    root: Path,
    generated_at: str,
    now: datetime | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    projects: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not root.exists():
        return projects, records, warnings

    try:
        entries = sorted(root.iterdir(), key=lambda item: item.name)
    except OSError:
        return projects, records, ["projects 目录无法读取，跨项目索引已降级为空。"]

    for project_dir in entries:
        if not project_dir.is_dir() or not (project_dir / "world.yaml").exists():
            continue
        sid = safe_id(project_dir.name)
        if sid is None:
            warnings.append(f"项目目录名不安全，已跳过：{project_dir.name}")
            continue
        display_name = _display_name(project_dir, sid)
        try:
            pack = get_retrieval_sample_migration_pack(sid, projects_dir=root, now=now)
        except Exception as exc:
            projects.append(_blocked_project(sid, display_name, str(exc)))
            continue

        pack_summary = pack.get("summary") or {}
        gate = pack.get("migration_gate") or {}
        project_records = list(pack.get("records") or [])[:10]
        projects.append(
            {
                "story_slug": sid,
                "display_name": display_name,
                "status": str(pack.get("status") or ""),
                "migration_gate_status": str(gate.get("status") or ""),
                "migration_gate_passed": bool(gate.get("passed")),
                "record_count": int(pack_summary.get("record_count") or 0),
                "replay_case_count": int(pack_summary.get("replay_case_count") or 0),
                "still_failing_lexically_count": int(
                    pack_summary.get("still_failing_lexically_count") or 0
                ),
                "covered_by_current_retrieval_count": int(
                    pack_summary.get("covered_by_current_retrieval_count") or 0
                ),
                "skipped_count": int(pack_summary.get("skipped_count") or 0),
                "filename": str(pack.get("filename") or ""),
                "sample_records": _compact_records(project_records),
            }
        )
        for record in project_records:
            compact = dict(record)
            compact["story_slug"] = sid
            compact["display_name"] = display_name
            compact["indexed_at"] = generated_at
            records.append(compact)

    projects.sort(
        key=lambda item: (
            int(item.get("record_count") or 0),
            int(item.get("replay_case_count") or 0),
            str(item.get("story_slug") or ""),
        ),
        reverse=True,
    )
    return projects, records[:100], warnings


def _display_name(project_dir: Path, slug: str) -> str:
    try:
        data = yaml.safe_load((project_dir / "world.yaml").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return slug
    if isinstance(data, dict):
        return str(data.get("display_name") or data.get("title") or slug)
    return slug


def _blocked_project(slug: str, display_name: str, reason: str) -> dict[str, Any]:
    return {
        "story_slug": slug,
        "display_name": display_name,
        "status": "blocked",
        "migration_gate_status": "blocked",
        "migration_gate_passed": False,
        "record_count": 0,
        "replay_case_count": 0,
        "still_failing_lexically_count": 0,
        "covered_by_current_retrieval_count": 0,
        "skipped_count": 0,
        "filename": "",
        "sample_records": [],
        "reason": reason[:180],
    }


def _compact_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "eval_id": str(record.get("eval_id") or ""),
            "query": str(record.get("query") or ""),
            "expected_item_id": str(record.get("expected_item_id") or ""),
            "replay_status": str(record.get("replay_status") or ""),
        }
        for record in records[:3]
    ]


def _summary(projects: list[dict[str, Any]], records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "project_count": len(projects),
        "ready_project_count": _count_projects(projects, "ready"),
        "empty_project_count": _count_projects(projects, "empty"),
        "attention_project_count": _count_projects(projects, "attention"),
        "blocked_project_count": _count_projects(projects, "blocked"),
        "record_count": len(records),
        "replay_case_count": sum(int(item.get("replay_case_count") or 0) for item in projects),
        "still_failing_lexically_count": sum(
            int(item.get("still_failing_lexically_count") or 0) for item in projects
        ),
        "covered_by_current_retrieval_count": sum(
            int(item.get("covered_by_current_retrieval_count") or 0)
            for item in projects
        ),
        "skipped_count": sum(int(item.get("skipped_count") or 0) for item in projects),
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


def _gate(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    status_map = {
        "ready": "ready",
        "empty": "needs_projects",
        "attention": "needs_records",
        "blocked": "blocked",
    }
    return {
        "id": "cross_project_retrieval_samples_index_ready",
        "status": status_map.get(status, status),
        "passed": status == "ready",
        "reason": _gate_reason(status),
        "project_count": summary["project_count"],
        "record_count": summary["record_count"],
    }


def _gate_reason(status: str) -> str:
    if status == "ready":
        return "跨项目索引已有可比较 records，可继续做样本趋势或真实 embedding 前评估。"
    if status == "empty":
        return "暂无本地项目，无法生成跨项目样本索引。"
    if status == "attention":
        return "已有项目但暂无可迁移 records，先收集或迁移失败样本。"
    return "存在项目样本损坏，先修复 blocked 项。"


def _manifest(
    generated_at: str,
    status: str,
    summary: dict[str, Any],
    gate: dict[str, Any],
    projects: list[dict[str, Any]],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": status,
        "summary": summary,
        "index_gate": gate,
        "projects": projects,
        "records": records,
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready":
        return [
            "用该索引比较不同项目的 lexical gap、covered 和 skipped case。",
            "继续积累真实失败样本，避免单项目样本驱动外部 provider 决策。",
            "真实 embedding / 向量库 / reranker 仍需等跨项目证据充分后再 opt-in。",
        ]
    if status == "attention":
        return ["先为本地项目生成 migration pack records，再观察跨项目趋势。"]
    if status == "blocked":
        return ["先修复 blocked 项目的失败样本或记忆目标，再重新索引。"]
    return ["先创建或导入本地项目，再记录检索失败样本。"]


def _count_projects(projects: list[dict[str, Any]], status: str) -> int:
    return sum(1 for project in projects if project.get("status") == status)

"""v1.0-beta Cloud Persistence Boundary-G：云端持久化迁移边界。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir, projects_dir

VERSION = "v1.0-beta-cloud-persistence-boundary-g"


def get_cloud_persistence_boundary(
    *,
    projects_root: Path | None = None,
    outputs_root: Path | None = None,
    ingest_sessions_root: Path | None = None,
) -> dict[str, Any]:
    """Return a read-only map from local artifacts to future platform resources."""

    projects = projects_root or projects_dir()
    outputs = outputs_root or outputs_dir()
    sessions = ingest_sessions_root or _default_ingest_sessions_dir(projects)
    inventory = _local_inventory(projects, outputs, sessions)

    return {
        "version": VERSION,
        "status": "boundary_defined",
        "scope": {
            "domain": "cloud_persistence",
            "name": "Cloud Persistence Boundary-G",
            "implementation_mode": "read_only_boundary_report",
            "principle": "先把本地 artifact 映射成未来平台资源，再决定是否接对象存储、数据库或队列。",
        },
        "migration": {
            "mode": "not_started",
            "source_of_truth": "local_file_artifacts",
            "external_services_required": False,
            "writes_remote_state": False,
            "platform_targets": [
                "private_object_storage",
                "metadata_database",
                "durable_job_queue",
                "append_only_audit_store",
            ],
        },
        "local_inventory": inventory,
        "resource_map": _resource_map(),
        "retention_policy": _retention_policy(),
        "readiness_checks": _readiness_checks(inventory),
        "deferred_actions": [
            {
                "id": "object_storage_upload",
                "label": "接入对象存储上传原文、holdout 与生成资产",
                "reason": "需先确认项目归属、版权声明和删除策略。",
            },
            {
                "id": "metadata_database",
                "label": "把项目、run、branch、选择记录落到数据库",
                "reason": "当前文件型索引仍能支撑本地 alpha/beta 验证。",
            },
            {
                "id": "durable_job_queue",
                "label": "把导入、生成、回放任务迁移到持久队列",
                "reason": "需要外部用户并发和失败恢复需求后再定。",
            },
        ],
        "warnings": [
            {
                "code": "cloud_migration_not_started",
                "message": "当前只是迁移边界报告，不会上传文件、创建数据库或启动云端队列。",
            }
        ],
        "next_steps": [
            "先把项目删除、导出、holdout 私有集和审计日志的保留规则固化成产品口径。",
            "再为对象存储、数据库和队列分别定义最小迁移 adapter。",
            "真实外部用户前再接账号归属、团队权限和云端监控。",
        ],
    }


def _default_ingest_sessions_dir(projects: Path) -> Path:
    raw = os.environ.get("LNE_INGEST_SESSIONS_DIR")
    if raw:
        return Path(raw)
    return projects.parent / "_ingest_sessions"


def _count_dirs(root: Path, *, prefix: str | None = None) -> int:
    try:
        if not root.exists() or not root.is_dir():
            return 0
        return sum(
            1
            for item in root.iterdir()
            if item.is_dir() and (prefix is None or item.name.startswith(prefix))
        )
    except OSError:
        return 0


def _local_inventory(projects: Path, outputs: Path, sessions: Path) -> dict[str, Any]:
    return {
        "project_count": _count_dirs(projects),
        "run_count": _count_dirs(outputs, prefix="run_"),
        "ingest_session_count": _count_dirs(sessions),
        "roots": [
            {
                "id": "projects",
                "pattern": "projects/<story_slug>/",
                "status": "present" if projects.exists() else "missing",
            },
            {
                "id": "outputs",
                "pattern": "outputs/run_*/",
                "status": "present" if outputs.exists() else "missing",
            },
            {
                "id": "ingest_sessions",
                "pattern": "_ingest_sessions/<session_id>/",
                "status": "present" if sessions.exists() else "missing",
            },
        ],
    }


def _resource_map() -> list[dict[str, str]]:
    return [
        {
            "id": "uploaded_source_private",
            "local_pattern": "projects/<story_slug>/source_raw/",
            "platform_candidate": "private_object_storage",
            "sensitivity": "uploaded_original_text",
            "visibility": "owner_private",
            "migration_rule": "仅在项目归属、版权声明和删除策略明确后迁移。",
        },
        {
            "id": "runtime_visible_source",
            "local_pattern": "projects/<story_slug>/source/",
            "platform_candidate": "private_object_storage",
            "sensitivity": "runtime_visible_source_text",
            "visibility": "runtime_visible",
            "migration_rule": "可随项目迁移，但不得包含 holdout 私有章节。",
        },
        {
            "id": "project_memory",
            "local_pattern": "projects/<story_slug>/memory/",
            "platform_candidate": "metadata_database_or_json_object_storage",
            "sensitivity": "derived_project_memory",
            "visibility": "project_members",
            "migration_rule": "保持 manifest 与 JSON/YAML artifact 可回放，先只做映射。",
        },
        {
            "id": "canon_holdout_private",
            "local_pattern": "projects/<story_slug>/canon/holdout_private/",
            "platform_candidate": "private_object_storage",
            "sensitivity": "private_evaluation_text",
            "visibility": "evaluator_private",
            "migration_rule": "必须与 runtime_visible 隔离，默认不进入检索或 narrator。",
        },
        {
            "id": "run_artifacts",
            "local_pattern": "outputs/run_*/",
            "platform_candidate": "object_storage_plus_metadata_database",
            "sensitivity": "generated_story_artifacts",
            "visibility": "project_members",
            "migration_rule": "保持 chapter/events/snapshot/trace/diff 契约 additive。",
        },
        {
            "id": "ingest_upload_parts",
            "local_pattern": "_ingest_sessions/<session_id>/",
            "platform_candidate": "temporary_object_storage",
            "sensitivity": "temporary_upload_chunks",
            "visibility": "owner_private",
            "migration_rule": "只保留到导入完成或过期清理，不作为长期资产。",
        },
        {
            "id": "selected_worldlines",
            "local_pattern": "outputs/story_selections/<story_slug>/selected_worldline.json",
            "platform_candidate": "metadata_database",
            "sensitivity": "project_decision_state",
            "visibility": "project_members",
            "migration_rule": "作为项目决策状态迁移，继续保持 run/branch id 安全校验。",
        },
    ]


def _retention_policy() -> list[dict[str, str]]:
    return [
        {
            "id": "project_delete",
            "scope": "source_raw/source/memory/canon/assets",
            "local_now": "手动删除项目目录。",
            "platform_rule": "平台化前必须定义项目删除后原文、派生产物、holdout 和视觉资产的删除链。",
        },
        {
            "id": "ingest_chunk_expiry",
            "scope": "temporary_upload_chunks",
            "local_now": "ingest session 已有过期时间和清理逻辑。",
            "platform_rule": "云端分片必须短期保留，导入完成或过期后清理。",
        },
        {
            "id": "audit_append_only",
            "scope": "project_audit_log",
            "local_now": "当前只读聚合，预留 project_audit_log.jsonl schema。",
            "platform_rule": "外部用户阶段再迁移到追加式或不可篡改审计存储。",
        },
        {
            "id": "holdout_private_isolation",
            "scope": "canon/holdout_private",
            "local_now": "visibility_manifest 区分 runtime_visible 与 holdout_private。",
            "platform_rule": "平台迁移后仍不得把 holdout 私有章节暴露给运行时 prompt。",
        },
    ]


def _readiness_checks(inventory: dict[str, Any]) -> list[dict[str, str]]:
    has_projects = inventory["project_count"] > 0
    has_runs = inventory["run_count"] > 0
    return [
        {
            "id": "artifact_contracts",
            "status": "ready",
            "detail": "已有 chapter/events/snapshot/trace/diff 等稳定文件契约，可作为迁移边界。",
        },
        {
            "id": "project_inventory",
            "status": "ready" if has_projects else "attention",
            "detail": "已发现本地项目。" if has_projects else "当前未发现本地导入项目。",
        },
        {
            "id": "run_inventory",
            "status": "ready" if has_runs else "attention",
            "detail": "已发现本地 run artifact。" if has_runs else "当前未发现本地 run artifact。",
        },
        {
            "id": "platform_prerequisites",
            "status": "blocked",
            "detail": "仍需真实账号归属、删除/保留策略、对象存储与数据库 adapter 方案。",
        },
    ]

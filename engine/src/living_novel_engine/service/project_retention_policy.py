"""v1.0-beta Project Retention Policy-J：项目删除/保留策略。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.commercial_audit_log import append_project_audit_log_event
from living_novel_engine.service.project_health import resolve_story_path

VERSION = "v1.0-beta-project-retention-policy-j"
ARTIFACT_PATH = "memory/project_retention_policy.json"

_PROJECT_RETENTION = {"keep_until_manual_delete", "delete_on_request", "archive_only"}
_UPLOADED_SOURCE_RETENTION = {
    "owner_private",
    "delete_on_project_delete",
    "archive_private",
}
_GENERATED_ARTIFACT_RETENTION = {
    "keep_with_project",
    "delete_on_project_delete",
    "archive_with_project",
}
_HOLDOUT_RETENTION = {
    "evaluator_private_until_delete",
    "delete_on_project_delete",
}
_AUDIT_LOG_RETENTION = {
    "append_only_until_project_delete",
    "export_before_delete",
}
_INGEST_CHUNK_RETENTION = {
    "expire_after_import",
    "delete_after_complete",
}
_SECRET_MARKERS = (
    "LLM_API_KEY",
    "SEEDREAM_API_KEY",
    "OPENAI_API_KEY",
    "sk-",
    "sd-",
    "secret",
)


class ProjectRetentionPolicyRequestError(ValueError):
    """Invalid project retention policy request, mapped to HTTP 400."""


class ProjectRetentionPolicyConflictError(ValueError):
    """Retention policy write conflict, mapped to HTTP 409."""


def get_project_retention_policy(
    slug: str,
    *,
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    """Return local project retention/deletion policy."""

    sid = _safe_slug(slug)
    project_dir, source_kind = resolve_story_path(sid, projects_dir)
    base = _base_report(sid, source_kind)
    path = project_dir / ARTIFACT_PATH

    if source_kind == "builtin":
        base["status"] = "builtin_sample"
        base["policy"] = {
            **_default_policy(),
            "project_retention": "keep_until_manual_delete",
            "notes": "内置样例为只读模板，不写入用户项目删除策略。",
        }
        base["next_steps"] = ["内置样例不支持写入项目保留策略。"]
        return base

    if not path.exists():
        base["status"] = "missing"
        base["policy"] = _default_policy()
        base["next_steps"] = [
            "补充项目原文、生成产物、holdout 私有集与审计日志的保留策略。",
            "删除项目前保持二次确认，不自动清理本地目录。",
            "云端对象存储或数据库接入前先冻结本地策略口径。",
        ]
        return base

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        base["status"] = "damaged"
        base["policy"] = _default_policy()
        base["warnings"].append(
            {
                "code": "damaged_retention_policy",
                "message": "项目删除/保留策略无法解析，已按默认保留处理。",
            }
        )
        base["next_steps"] = ["重新保存项目删除/保留策略。"]
        return base

    if not isinstance(raw, dict):
        base["status"] = "damaged"
        base["policy"] = _default_policy()
        base["warnings"].append(
            {
                "code": "damaged_retention_policy",
                "message": "项目删除/保留策略不是对象结构，已按默认保留处理。",
            }
        )
        return base

    policy = _normalize_policy(raw.get("policy") or raw, strict=False)
    base["status"] = "declared"
    base["updated_at"] = str(raw.get("updated_at") or "")
    base["policy"] = policy
    base["next_steps"] = _next_steps_for_policy(policy)
    return base


def write_project_retention_policy(
    slug: str,
    payload: dict[str, Any],
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Persist local project retention/deletion policy without deleting files."""

    sid = _safe_slug(slug)
    project_dir, source_kind = resolve_story_path(sid, projects_dir)
    if source_kind == "builtin":
        raise ProjectRetentionPolicyConflictError("内置样例不可写项目保留策略")
    if not isinstance(payload, dict):
        raise ProjectRetentionPolicyRequestError("请求体必须是对象")

    policy = _normalize_policy(payload, strict=True)
    updated = now or datetime.now()
    updated_at = updated.isoformat(timespec="seconds")
    record = {
        "schema_version": VERSION,
        "kind": "project_retention_policy",
        "status": "declared",
        "updated_at": updated_at,
        "policy": policy,
    }
    path = project_dir / ARTIFACT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    append_project_audit_log_event(
        sid,
        {
            "action": "retention_policy_reviewed",
            "label": "保存项目删除/保留策略",
            "summary": "已更新项目删除/保留策略。",
            "actor_type": "user",
            "severity": "info",
            "metadata": {
                "artifact_path": ARTIFACT_PATH,
                "project_retention": policy["project_retention"],
            },
        },
        projects_dir=projects_dir,
        now=updated,
    )
    return get_project_retention_policy(sid, projects_dir=projects_dir)


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise ProjectRetentionPolicyRequestError("invalid slug")
    return sid


def _base_report(slug: str, source_kind: str) -> dict[str, Any]:
    return {
        "version": VERSION,
        "kind": "project_retention_policy",
        "story_slug": slug,
        "source_kind": source_kind,
        "status": "missing",
        "artifact_path": ARTIFACT_PATH,
        "policy": _default_policy(),
        "warnings": [],
        "next_steps": [],
    }


def _default_policy() -> dict[str, Any]:
    return {
        "project_retention": "keep_until_manual_delete",
        "uploaded_source_retention": "owner_private",
        "generated_artifact_retention": "keep_with_project",
        "holdout_retention": "evaluator_private_until_delete",
        "audit_log_retention": "append_only_until_project_delete",
        "ingest_chunk_retention": "expire_after_import",
        "deletion_confirmation_required": True,
        "notes": "",
    }


def _normalize_policy(payload: dict[str, Any], *, strict: bool) -> dict[str, Any]:
    defaults = _default_policy()
    return {
        "project_retention": _clean_choice(
            payload.get("project_retention"),
            allowed=_PROJECT_RETENTION,
            default=defaults["project_retention"],
            field="project_retention",
            strict=strict,
        ),
        "uploaded_source_retention": _clean_choice(
            payload.get("uploaded_source_retention"),
            allowed=_UPLOADED_SOURCE_RETENTION,
            default=defaults["uploaded_source_retention"],
            field="uploaded_source_retention",
            strict=strict,
        ),
        "generated_artifact_retention": _clean_choice(
            payload.get("generated_artifact_retention"),
            allowed=_GENERATED_ARTIFACT_RETENTION,
            default=defaults["generated_artifact_retention"],
            field="generated_artifact_retention",
            strict=strict,
        ),
        "holdout_retention": _clean_choice(
            payload.get("holdout_retention"),
            allowed=_HOLDOUT_RETENTION,
            default=defaults["holdout_retention"],
            field="holdout_retention",
            strict=strict,
        ),
        "audit_log_retention": _clean_choice(
            payload.get("audit_log_retention"),
            allowed=_AUDIT_LOG_RETENTION,
            default=defaults["audit_log_retention"],
            field="audit_log_retention",
            strict=strict,
        ),
        "ingest_chunk_retention": _clean_choice(
            payload.get("ingest_chunk_retention"),
            allowed=_INGEST_CHUNK_RETENTION,
            default=defaults["ingest_chunk_retention"],
            field="ingest_chunk_retention",
            strict=strict,
        ),
        "deletion_confirmation_required": _clean_bool(
            payload.get("deletion_confirmation_required"),
            default=True,
        ),
        "notes": _clean_text(payload.get("notes"), field="notes", max_len=300),
    }


def _clean_choice(
    value: Any,
    *,
    allowed: set[str],
    default: str,
    field: str,
    strict: bool,
) -> str:
    if value is None or value == "":
        return default
    choice = str(value).strip()
    if choice in allowed:
        return choice
    if strict:
        raise ProjectRetentionPolicyRequestError(f"{field} 不支持: {choice}")
    return default


def _clean_bool(value: Any, *, default: bool) -> bool:
    if value is None or value == "":
        return default
    return bool(value)


def _clean_text(value: Any, *, field: str, max_len: int) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    lowered = text.lower()
    if any(marker.lower() in lowered for marker in _SECRET_MARKERS):
        raise ProjectRetentionPolicyRequestError(f"{field} 包含疑似密钥内容")
    if len(text) > max_len:
        raise ProjectRetentionPolicyRequestError(f"{field} 超过 {max_len} 字符")
    return text


def _next_steps_for_policy(policy: dict[str, Any]) -> list[str]:
    steps: list[str] = []
    if policy.get("project_retention") == "delete_on_request":
        steps.append("删除项目前仍需二次确认；当前版本不会自动删除本地目录。")
    if policy.get("uploaded_source_retention") == "owner_private":
        steps.append("上传原文继续保持 owner-private 语义，公开分享前需另行授权。")
    steps.append("云端对象存储或数据库接入前，继续以该本地策略作为迁移输入。")
    return steps

"""v1.0-beta Commercial Audit Log Schema-B.

This slice defines a local project audit event schema and returns a read-only
timeline synthesized from existing project artifacts. It does not write the
future project_audit_log.jsonl yet.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from living_novel_engine.service.project_health import resolve_story_path

_VERSION = "v1.0-beta-commercial-audit-log-schema-b"
_APPEND_VERSION = "v1.0-beta-audit-log-append-policy-i"
_STORAGE = "memory/project_audit_log.jsonl"
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_APPEND_ACTIONS = {
    "manual_note",
    "rights_reviewed",
    "retention_policy_reviewed",
    "project_space_reviewed",
    "audit_reviewed",
}
_APPEND_SEVERITIES = {"info", "warning", "action_required"}
_ACTOR_TYPES = {"user", "system"}
_SENSITIVE_MARKERS = ("api_key", "secret", "token", "password", "llm_api_key", "seedream_api_key")


class ProjectAuditLogRequestError(ValueError):
    """Invalid audit log request, mapped to HTTP 400."""


class ProjectAuditLogConflictError(ValueError):
    """Audit log write conflicts, mapped to HTTP 409."""


def _validate_slug(slug: str) -> str:
    value = (slug or "").strip()
    if not value or ".." in value or not _SAFE_ID_RE.match(value):
        raise ProjectAuditLogRequestError("story_slug 非法")
    return value


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _mtime_iso(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
    except OSError:
        return ""


def _event(
    *,
    event_id: str,
    action: str,
    label: str,
    artifact: str,
    summary: str,
    created_at: str = "",
    actor_type: str = "system",
    severity: str = "info",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "action": action,
        "label": label,
        "actor_type": actor_type,
        "scope": "project",
        "artifact": artifact,
        "created_at": created_at,
        "severity": severity,
        "summary": summary,
        "metadata": metadata or {},
    }


def _artifact_event(
    project_dir: Path,
    rel_path: str,
    *,
    event_id: str,
    action: str,
    label: str,
    summary_from: str | None = None,
    created_at_from: str | None = None,
    metadata_keys: list[str] | None = None,
) -> dict[str, Any] | None:
    path = project_dir / rel_path
    if not path.exists():
        return None
    data = _read_json(path)
    if data is None:
        return None
    metadata = {
        key: data.get(key)
        for key in (metadata_keys or [])
        if key in data and data.get(key) not in (None, "")
    }
    summary = str(data.get(summary_from or "") or label)
    created_at = str(data.get(created_at_from or "") or "") or _mtime_iso(path)
    return _event(
        event_id=event_id,
        action=action,
        label=label,
        artifact=rel_path,
        summary=summary,
        created_at=created_at,
        metadata=metadata,
    )


def _builtin_artifact_events(project_dir: Path) -> list[dict[str, Any]]:
    specs = [
        (
            "import_report.json",
            {
                "event_id": "artifact-import-report",
                "action": "import_review_generated",
                "label": "生成导入检查报告",
                "created_at_from": "created_at",
                "metadata_keys": ["version", "status", "total_chapters"],
            },
        ),
        (
            "selected_worldline.json",
            {
                "event_id": "artifact-selected-worldline",
                "action": "worldline_selected",
                "label": "选择继续世界线",
                "created_at_from": "selected_at",
                "metadata_keys": ["run_id", "branch_id", "status"],
            },
        ),
        (
            "memory/master_setting_update_report.json",
            {
                "event_id": "artifact-master-setting-update",
                "action": "master_setting_updated",
                "label": "保存设定轻编辑",
                "metadata_keys": ["version", "status", "changed", "backup"],
            },
        ),
        (
            "creation_loop_alpha_closeout.json",
            {
                "event_id": "artifact-creation-loop-closeout",
                "action": "creation_loop_closed",
                "label": "记录创作闭环收口",
                "created_at_from": "created_at",
                "metadata_keys": ["version", "status", "completion_status"],
            },
        ),
    ]
    events: list[dict[str, Any]] = []
    for rel_path, kwargs in specs:
        item = _artifact_event(project_dir, rel_path, **kwargs)
        if item:
            events.append(item)
    return events


def _normalize_project_log_event(raw: dict[str, Any], index: int) -> dict[str, Any]:
    action = str(raw.get("action") or "manual_note")[:80]
    label = str(raw.get("label") or raw.get("summary") or "项目审计事件")[:80]
    return _event(
        event_id=str(raw.get("event_id") or f"project-log-{index}"),
        action=action,
        label=label,
        actor_type=str(raw.get("actor_type") or "user"),
        artifact=_STORAGE,
        created_at=str(raw.get("created_at") or ""),
        severity=str(raw.get("severity") or "info"),
        summary=str(raw.get("summary") or label)[:240],
        metadata=dict(raw.get("metadata") or {}),
    )


def _project_log_events(project_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    path = project_dir / _STORAGE
    if not path.exists():
        return [], []
    events: list[dict[str, Any]] = []
    warnings: list[dict[str, str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return [], [
            {
                "code": "damaged_project_audit_log",
                "message": f"{_STORAGE} 读取失败，已跳过：{exc}",
            }
        ]
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            warnings.append(
                {
                    "code": "damaged_project_audit_log",
                    "message": f"{_STORAGE} 第 {index} 行无法解析，已跳过：{exc}",
                }
            )
            continue
        if not isinstance(raw, dict):
            warnings.append(
                {
                    "code": "damaged_project_audit_log",
                    "message": f"{_STORAGE} 第 {index} 行不是对象，已跳过。",
                }
            )
            continue
        events.append(_normalize_project_log_event(raw, index))
    return events, warnings


def _schema() -> dict[str, Any]:
    return {
        "storage": _STORAGE,
        "write_policy": "local_append_jsonl_opt_in",
        "required_fields": [
            "event_id",
            "action",
            "label",
            "actor_type",
            "scope",
            "artifact",
            "created_at",
            "severity",
            "summary",
        ],
        "known_actions": [
            "import_review_generated",
            "worldline_selected",
            "master_setting_updated",
            "creation_loop_closed",
            "manual_note",
            "rights_reviewed",
            "retention_policy_reviewed",
            "project_space_reviewed",
            "audit_reviewed",
        ],
    }


def _summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    action_counts: dict[str, int] = {}
    source_artifacts = set()
    for event in events:
        action = str(event.get("action") or "unknown")
        action_counts[action] = action_counts.get(action, 0) + 1
        artifact = str(event.get("artifact") or "")
        if artifact:
            source_artifacts.add(artifact)
    return {
        "event_count": len(events),
        "source_count": len(source_artifacts),
        "action_counts": action_counts,
    }


def get_project_audit_log(
    story_slug: str, *, projects_dir: Path | None = None
) -> dict[str, Any]:
    """Return a read-only project audit timeline.

    Existing artifact reports are synthesized into schema-compatible events.
    Future slices may append real events to memory/project_audit_log.jsonl, but
    this function never writes that file.
    """
    slug = _validate_slug(story_slug)
    project_dir, source_kind = resolve_story_path(slug, projects_dir)

    events = _builtin_artifact_events(project_dir)
    project_log, warnings = _project_log_events(project_dir)
    events.extend(project_log)
    events.sort(key=lambda item: str(item.get("created_at") or ""))

    status = "ready" if events else "empty"
    return {
        "version": _VERSION,
        "status": status,
        "story_slug": slug,
        "source_kind": source_kind,
        "schema": _schema(),
        "summary": _summary(events),
        "events": events,
        "warnings": warnings,
        "next_steps": [
            "后续写操作逐步追加 project_audit_log.jsonl，而不是覆盖既有 artifact。",
            "权限矩阵接入前，先用该只读时间线核对项目关键动作。",
            "云端不可篡改审计存储留到真实外部用户阶段。",
        ],
    }


def _clean_text(value: Any, *, max_len: int, fallback: str = "") -> str:
    text = str(value or "").strip()
    if not text:
        text = fallback
    return text[:max_len]


def _looks_sensitive(key: str, value: Any) -> bool:
    lowered_key = key.lower()
    if any(marker in lowered_key for marker in _SENSITIVE_MARKERS):
        return True
    if isinstance(value, str):
        lowered_value = value.lower()
        return "secret" in lowered_value or lowered_value.startswith(("sk-", "sd-"))
    return False


def _safe_metadata(raw: Any) -> tuple[dict[str, Any], list[dict[str, str]]]:
    if raw in (None, ""):
        return {}, []
    if not isinstance(raw, dict):
        return {}, [
            {
                "code": "metadata_dropped",
                "message": "metadata 不是对象，已跳过。",
            }
        ]

    metadata: dict[str, Any] = {}
    warnings: list[dict[str, str]] = []
    for key, value in raw.items():
        clean_key = _clean_text(key, max_len=80)
        if not clean_key:
            continue
        if _looks_sensitive(clean_key, value):
            warnings.append(
                {
                    "code": "metadata_key_dropped",
                    "message": f"metadata.{clean_key} 疑似敏感字段，已跳过。",
                }
            )
            continue
        if isinstance(value, bool) or isinstance(value, (int, float)):
            metadata[clean_key] = value
        elif isinstance(value, str):
            metadata[clean_key] = value[:240]
        elif isinstance(value, list):
            metadata[clean_key] = [
                item if isinstance(item, (bool, int, float)) else str(item)[:120]
                for item in value[:10]
            ]
        else:
            metadata[clean_key] = str(value)[:240]
    return metadata, warnings


def append_project_audit_log_event(
    story_slug: str,
    payload: dict[str, Any],
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Append one safe local event to memory/project_audit_log.jsonl."""

    slug = _validate_slug(story_slug)
    if not isinstance(payload, dict):
        raise ProjectAuditLogRequestError("payload 必须是对象")
    action = _clean_text(payload.get("action"), max_len=80)
    if action not in _APPEND_ACTIONS:
        raise ProjectAuditLogRequestError("action 不在允许的审计事件白名单内")
    summary = _clean_text(payload.get("summary"), max_len=240)
    if not summary:
        raise ProjectAuditLogRequestError("summary 不能为空")
    severity = _clean_text(payload.get("severity"), max_len=40, fallback="info")
    if severity not in _APPEND_SEVERITIES:
        raise ProjectAuditLogRequestError("severity 不合法")
    actor_type = _clean_text(payload.get("actor_type"), max_len=40, fallback="user")
    if actor_type not in _ACTOR_TYPES:
        raise ProjectAuditLogRequestError("actor_type 不合法")

    project_dir, source_kind = resolve_story_path(slug, projects_dir)
    if source_kind == "builtin":
        raise ProjectAuditLogConflictError("内置样例为只读目录，不能追加项目审计日志")

    created = now or datetime.now()
    created_at = created.isoformat(timespec="seconds")
    metadata, warnings = _safe_metadata(payload.get("metadata"))
    event = _event(
        event_id=f"audit-{created.strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}",
        action=action,
        label=_clean_text(payload.get("label"), max_len=80, fallback=summary),
        artifact=_STORAGE,
        created_at=created_at,
        actor_type=actor_type,
        severity=severity,
        summary=summary,
        metadata=metadata,
    )

    log_path = project_dir / _STORAGE
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")

    return {
        "version": _APPEND_VERSION,
        "status": "appended",
        "story_slug": slug,
        "source_kind": source_kind,
        "storage": _STORAGE,
        "event": event,
        "warnings": warnings,
        "audit_log": get_project_audit_log(slug, projects_dir=projects_dir),
        "next_steps": [
            "继续保持 project_audit_log.jsonl 追加写入，不覆盖既有 artifact。",
            "接真实账号前，actor_type 只表达本地事件来源，不代表已鉴权身份。",
            "云端不可篡改审计存储留到真实外部用户阶段。",
        ],
    }

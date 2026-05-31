"""v1.0-beta Project Copyright Statement-D：项目级版权/来源声明 schema。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.commercial_audit_log import append_project_audit_log_event
from living_novel_engine.service.project_health import resolve_story_path

VERSION = "v1.0-beta-project-copyright-statement-d"
ARTIFACT_PATH = "memory/project_copyright_statement.json"

_LICENSE_STATUSES = {
    "unknown",
    "owned_by_user",
    "authorized",
    "public_domain",
    "generated_original",
    "reference_only",
}
_PERMITTED_USES = {
    "private_research",
    "local_export",
    "internal_review",
    "public_share",
    "commercial_use",
}
_SECRET_MARKERS = (
    "LLM_API_KEY",
    "SEEDREAM_API_KEY",
    "OPENAI_API_KEY",
    "sk-",
    "sd-",
)


class ProjectCopyrightStatementRequestError(ValueError):
    """Invalid project copyright statement request, mapped to HTTP 400."""


class ProjectCopyrightStatementConflictError(ValueError):
    """Write conflict for project copyright statement, mapped to HTTP 409."""


def get_project_copyright_statement(
    slug: str,
    *,
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    """Return project-level copyright/source declaration.

    The report is local and additive. Missing or damaged statement artifacts
    degrade to explicit status values instead of breaking export/read flows.
    """

    sid = _safe_slug(slug)
    project_dir, source_kind = resolve_story_path(sid, projects_dir)
    base = _base_report(sid, project_dir, source_kind)
    path = project_dir / ARTIFACT_PATH

    if source_kind == "builtin":
        return _with_builtin_statement(base)

    if not path.exists():
        base["status"] = "missing"
        base["statement"] = _empty_statement()
        base["share_policy"] = _share_policy("missing")
        base["next_steps"] = [
            "补充原作标题、作者或权利来源。",
            "确认当前导出仅用于本地个人评估。",
            "公开分享或商用前另行取得明确授权。",
        ]
        return base

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        base["status"] = "damaged"
        base["statement"] = _empty_statement()
        base["share_policy"] = _share_policy("damaged")
        base["warnings"].append(
            {
                "code": "damaged_copyright_statement",
                "message": "项目版权/来源声明无法解析，已按未声明处理。",
            }
        )
        base["next_steps"] = [
            "重新保存项目版权/来源声明。",
            "导出前人工确认上传文本和生成内容的使用边界。",
        ]
        return base

    if not isinstance(raw, dict):
        base["status"] = "damaged"
        base["statement"] = _empty_statement()
        base["share_policy"] = _share_policy("damaged")
        base["warnings"].append(
            {
                "code": "damaged_copyright_statement",
                "message": "项目版权/来源声明不是对象结构，已按未声明处理。",
            }
        )
        return base

    statement = _normalize_statement(raw.get("statement") or raw, strict=False)
    status = "declared" if statement["license_status"] != "unknown" else "draft"
    base["status"] = status
    base["updated_at"] = str(raw.get("updated_at") or "")
    base["statement"] = statement
    base["share_policy"] = _share_policy(status, statement=statement)
    base["next_steps"] = _next_steps_for_statement(statement)
    return base


def write_project_copyright_statement(
    slug: str,
    payload: dict[str, Any],
    *,
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    """Persist a local project copyright/source declaration artifact."""

    sid = _safe_slug(slug)
    project_dir, source_kind = resolve_story_path(sid, projects_dir)
    if source_kind == "builtin":
        raise ProjectCopyrightStatementConflictError("内置样例不可写版权声明")
    if not isinstance(payload, dict):
        raise ProjectCopyrightStatementRequestError("请求体必须是对象")

    statement = _normalize_statement(payload, strict=True)
    status = "declared" if statement["license_status"] != "unknown" else "draft"
    now = datetime.now().isoformat(timespec="seconds")
    record = {
        "schema_version": VERSION,
        "kind": "project_copyright_statement",
        "status": status,
        "updated_at": now,
        "statement": statement,
        "share_policy": _share_policy(status, statement=statement),
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
            "action": "rights_reviewed",
            "label": "保存版权/来源声明",
            "summary": "已更新项目版权/来源声明。",
            "actor_type": "user",
            "severity": "info",
            "metadata": {
                "artifact_path": ARTIFACT_PATH,
                "license_status": statement["license_status"],
            },
        },
        projects_dir=projects_dir,
    )
    return get_project_copyright_statement(sid, projects_dir=projects_dir)


def build_rights_basis_for_story(story_slug: str) -> dict[str, Any]:
    """Compact rights basis consumed by export share guards."""

    try:
        report = get_project_copyright_statement(story_slug)
    except (FileNotFoundError, ProjectCopyrightStatementRequestError):
        return {
            "status": "unavailable",
            "artifact_path": ARTIFACT_PATH,
            "license_status": "unknown",
            "source_title": "",
            "permitted_uses": [],
            "attestation_present": False,
        }

    statement = report.get("statement") if isinstance(report, dict) else {}
    if not isinstance(statement, dict):
        statement = {}
    return {
        "status": str(report.get("status") or "unknown"),
        "artifact_path": ARTIFACT_PATH,
        "license_status": str(statement.get("license_status") or "unknown"),
        "source_title": str(statement.get("source_title") or ""),
        "source_author": str(statement.get("source_author") or ""),
        "rights_holder": str(statement.get("rights_holder") or ""),
        "permitted_uses": list(statement.get("permitted_uses") or []),
        "attestation_present": bool(statement.get("attestation")),
        "updated_at": str(report.get("updated_at") or ""),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise ProjectCopyrightStatementRequestError("invalid slug")
    return sid


def _base_report(slug: str, project_dir: Path, source_kind: str) -> dict[str, Any]:
    return {
        "version": VERSION,
        "kind": "project_copyright_statement",
        "story_slug": slug,
        "status": "missing",
        "artifact_path": ARTIFACT_PATH,
        "source": {
            "source_kind": source_kind,
            "import_source": _import_source(project_dir) if source_kind != "builtin" else {},
        },
        "statement": _empty_statement(),
        "share_policy": _share_policy("missing"),
        "warnings": [],
        "next_steps": [],
    }


def _import_source(project_dir: Path) -> dict[str, Any]:
    path = project_dir / "import_report.json"
    if not path.exists():
        return {"type": "unknown", "name": "", "file_count": 0}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {"type": "unknown", "name": "", "file_count": 0}
    source = data.get("source") if isinstance(data, dict) else {}
    if not isinstance(source, dict):
        source = {}
    return {
        "type": str(source.get("type") or "unknown"),
        "name": str(source.get("name") or ""),
        "file_count": int(source.get("file_count") or 0),
    }


def _with_builtin_statement(report: dict[str, Any]) -> dict[str, Any]:
    statement = {
        **_empty_statement(),
        "source_title": "内置样例",
        "license_status": "reference_only",
        "permitted_uses": ["private_research", "local_export"],
        "attestation": "内置样例仅用于本地功能验证与演示。",
    }
    report["status"] = "builtin_sample"
    report["statement"] = statement
    report["share_policy"] = _share_policy("builtin_sample", statement=statement)
    report["next_steps"] = [
        "如需对外展示，请单独确认样例素材与平台规则。",
        "不要把样例导出误标为外部商业授权。",
    ]
    return report


def _empty_statement() -> dict[str, Any]:
    return {
        "source_title": "",
        "source_author": "",
        "rights_holder": "",
        "license_status": "unknown",
        "permitted_uses": [],
        "attestation": "",
        "notes": "",
    }


def _normalize_statement(payload: dict[str, Any], *, strict: bool) -> dict[str, Any]:
    license_status = _clean_choice(
        payload.get("license_status"),
        allowed=_LICENSE_STATUSES,
        default="unknown",
        field="license_status",
        strict=strict,
    )
    permitted_uses = _clean_list(
        payload.get("permitted_uses"),
        allowed=_PERMITTED_USES,
        field="permitted_uses",
        strict=strict,
    )
    return {
        "source_title": _clean_text(payload.get("source_title"), "source_title", 120),
        "source_author": _clean_text(payload.get("source_author"), "source_author", 120),
        "rights_holder": _clean_text(payload.get("rights_holder"), "rights_holder", 120),
        "license_status": license_status,
        "permitted_uses": permitted_uses,
        "attestation": _clean_text(payload.get("attestation"), "attestation", 300),
        "notes": _clean_text(payload.get("notes"), "notes", 300),
    }


def _clean_text(value: Any, field: str, max_len: int) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if any(marker in text for marker in _SECRET_MARKERS):
        raise ProjectCopyrightStatementRequestError(f"{field} 包含疑似密钥内容")
    if len(text) > max_len:
        raise ProjectCopyrightStatementRequestError(f"{field} 超过 {max_len} 字符")
    return text


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
        raise ProjectCopyrightStatementRequestError(f"{field} 不支持: {choice}")
    return default


def _clean_list(
    value: Any,
    *,
    allowed: set[str],
    field: str,
    strict: bool,
) -> list[str]:
    if value is None or value == "":
        return []
    if not isinstance(value, list):
        if strict:
            raise ProjectCopyrightStatementRequestError(f"{field} 必须是数组")
        return []
    cleaned: list[str] = []
    for item in value:
        val = str(item).strip()
        if val not in allowed:
            if strict:
                raise ProjectCopyrightStatementRequestError(f"{field} 不支持: {val}")
            continue
        if val not in cleaned:
            cleaned.append(val)
    return cleaned


def _share_policy(
    status: str,
    *,
    statement: dict[str, Any] | None = None,
) -> dict[str, Any]:
    statement = statement or _empty_statement()
    warnings = [
        "当前版本不提供公开发布入口。",
        "导出不等于获得公开传播或商用授权。",
    ]
    if status not in {"declared", "builtin_sample"}:
        warnings.insert(0, "项目级版权/来源声明尚未补齐。")
    if "public_share" in statement.get("permitted_uses", []):
        warnings.append("即便声明包含公开分享用途，当前产品仍不会自动放开公开发布。")
    return {
        "private_use_allowed": True,
        "local_export_allowed": True,
        "public_publish_enabled": False,
        "requires_export_confirmation": True,
        "basis_status": status,
        "warnings": warnings,
    }


def _next_steps_for_statement(statement: dict[str, Any]) -> list[str]:
    steps: list[str] = []
    if not statement.get("source_title"):
        steps.append("补充原作或来源标题。")
    if statement.get("license_status") == "unknown":
        steps.append("标记权利状态：自有、已授权、公版、原创生成或仅作参考。")
    if not statement.get("attestation"):
        steps.append("补充上传者/项目维护者的权利确认说明。")
    steps.append("公开分享或商用前仍需单独确认授权。")
    return steps

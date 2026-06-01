"""v1.0-beta Rights Approval Checklist-S：项目版权审批只读清单。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.commercial_audit_log import get_project_audit_log
from living_novel_engine.service.copyright_statement import get_project_copyright_statement

VERSION = "v1.0-beta-rights-approval-checklist-s"


class RightsApprovalRequestError(ValueError):
    """Invalid rights approval request, mapped to HTTP 400."""


def get_rights_approval_checklist(
    story_slug: str,
    *,
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    """Return a read-only local rights approval checklist for one project."""

    slug = _safe_slug(story_slug)
    rights = get_project_copyright_statement(slug, projects_dir=projects_dir)
    audit = get_project_audit_log(slug, projects_dir=projects_dir)
    statement = rights.get("statement") if isinstance(rights.get("statement"), dict) else {}
    share_policy = (
        rights.get("share_policy") if isinstance(rights.get("share_policy"), dict) else {}
    )
    permitted = set(statement.get("permitted_uses") or [])
    events = audit.get("events") if isinstance(audit.get("events"), list) else []
    has_rights_event = any(event.get("action") == "rights_reviewed" for event in events)

    checkpoints = [
        _checkpoint(
            checkpoint_id="project_rights_statement",
            label="版权/来源声明",
            status="ready"
            if rights.get("status") in {"declared", "builtin_sample"}
            else "attention",
            evidence=str(rights.get("status") or "missing"),
            next_step=_first_text(rights.get("next_steps"), "补充项目版权/来源声明。"),
        ),
        _checkpoint(
            checkpoint_id="rights_attestation",
            label="权利确认说明",
            status="ready" if statement.get("attestation") else "attention",
            evidence="已填写" if statement.get("attestation") else "未填写",
            next_step="导出前补充上传者/项目维护者的权利确认说明。",
        ),
        _checkpoint(
            checkpoint_id="local_export_scope",
            label="本地导出用途",
            status="ready" if "local_export" in permitted else "attention",
            evidence="允许本地导出" if "local_export" in permitted else "尚未声明本地导出用途",
            next_step="若需要导出 Markdown，请在 permitted_uses 中声明 local_export。",
        ),
        _checkpoint(
            checkpoint_id="rights_audit_event",
            label="版权审计事件",
            status="ready"
            if has_rights_event or rights.get("status") == "builtin_sample"
            else "attention",
            evidence="已记录 rights_reviewed" if has_rights_event else "尚未记录 rights_reviewed",
            next_step="保存版权/来源声明后会追加本地 rights_reviewed 审计事件。",
        ),
        _checkpoint(
            checkpoint_id="public_publish_guard",
            label="公开发布护栏",
            status="ready",
            evidence="公开发布入口未启用",
            next_step="公开分享或商用前仍需独立审批，不由本地清单自动放行。",
        ),
    ]
    attention = sum(1 for item in checkpoints if item["status"] == "attention")
    ready = len(checkpoints) - attention
    return {
        "version": VERSION,
        "mode": "read_only_rights_approval_checklist",
        "status": "ready" if attention == 0 else "attention",
        "story_slug": slug,
        "source_kind": str(rights.get("source", {}).get("source_kind") or ""),
        "summary": {
            "checkpoint_count": len(checkpoints),
            "ready_count": ready,
            "attention_count": attention,
            "public_publish_enabled": bool(share_policy.get("public_publish_enabled")),
            "requires_export_confirmation": bool(
                share_policy.get("requires_export_confirmation", True)
            ),
        },
        "checkpoints": checkpoints,
        "warnings": list(share_policy.get("warnings") or []),
        "next_steps": [
            "公开分享或商用前仍需单独审批授权，当前产品不会自动放开公开发布。",
            "导出章节或审计日志前，继续使用中文确认弹窗提醒权利责任。",
        ],
    }


def _checkpoint(
    *,
    checkpoint_id: str,
    label: str,
    status: str,
    evidence: str,
    next_step: str,
) -> dict[str, str]:
    return {
        "id": checkpoint_id,
        "label": label,
        "status": status,
        "status_label": "已具备" if status == "ready" else "需留意",
        "evidence": evidence,
        "next_step": next_step,
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise RightsApprovalRequestError("invalid slug")
    return sid


def _first_text(items: list[Any] | None, fallback: str) -> str:
    if not items:
        return fallback
    value = items[0]
    return value if isinstance(value, str) and value else fallback

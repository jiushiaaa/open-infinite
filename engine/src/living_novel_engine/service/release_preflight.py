"""v1.0-beta Release Preflight Checklist-R：发布前只读检查清单。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.commercial_audit_log import get_project_audit_log
from living_novel_engine.service.commercial_permissions import get_permission_matrix_draft
from living_novel_engine.service.commercial_status_overview import (
    get_commercial_status_overview,
)
from living_novel_engine.service.copyright_statement import (
    get_project_copyright_statement,
)
from living_novel_engine.service.deployment_readiness import (
    get_local_deployment_readiness,
    get_settings_local_smoke_checklist,
)
from living_novel_engine.service.project_retention_policy import (
    get_project_retention_policy,
)

VERSION = "v1.0-beta-release-preflight-checklist-r"


class ReleasePreflightRequestError(ValueError):
    """Invalid release preflight request, mapped to HTTP 400."""


def get_release_preflight_checklist(
    story_slug: str | None = None,
    *,
    projects_dir: Path | None = None,
    api_host: str = "127.0.0.1",
    api_port: int = 8765,
) -> dict[str, Any]:
    """Return a read-only local release preflight checklist.

    The report aggregates existing local beta checks. It does not execute HTTP
    requests, persist state, call providers, publish content, or imply cloud
    deployment readiness.
    """

    sid = _safe_story_slug(story_slug) if story_slug else None
    deployment = get_local_deployment_readiness(api_host=api_host, api_port=api_port)
    smoke = get_settings_local_smoke_checklist(api_host=api_host, api_port=api_port)
    commercial = get_commercial_status_overview(api_host=api_host, api_port=api_port)
    permissions = get_permission_matrix_draft()

    checkpoints = [
        _checkpoint(
            checkpoint_id="local_deployment",
            label="本地部署就绪",
            status="ready" if deployment.get("status") == "ready" else "attention",
            evidence=str(deployment.get("status") or "unknown"),
            source_endpoint="GET /api/settings/deployment-readiness",
            next_step=_first_text(deployment.get("next_steps"), "先完成本地部署就绪检查。"),
        ),
        _checkpoint(
            checkpoint_id="local_smoke",
            label="本地冒烟清单",
            status="ready" if smoke.get("status") == "ready" else "attention",
            evidence=f"{smoke.get('summary', {}).get('check_count', 0)} 条路径待核对",
            source_endpoint="GET /api/settings/local-smoke-checklist",
            next_step=_first_text(smoke.get("next_steps"), "按清单执行本地 HTTP 冒烟。"),
        ),
        _checkpoint(
            checkpoint_id="commercial_status",
            label="商业化状态总览",
            status="ready"
            if commercial.get("overall_status") == "ready"
            else "attention",
            evidence=str(commercial.get("overall_status") or "attention"),
            source_endpoint="GET /api/settings/commercial-status-overview",
            next_step=_first_text(commercial.get("next_steps"), "继续按本地优先方式拆分小刀。"),
        ),
        _permission_checkpoint(permissions),
    ]
    checkpoints.extend(_project_checkpoints(sid, projects_dir=projects_dir))

    counts = {
        "ready": sum(1 for item in checkpoints if item["status"] == "ready"),
        "attention": sum(1 for item in checkpoints if item["status"] == "attention"),
    }
    return {
        "version": VERSION,
        "mode": "read_only_release_preflight",
        "status": "ready" if counts["attention"] == 0 else "attention",
        "story_slug": sid or "",
        "summary": {
            "checkpoint_count": len(checkpoints),
            "ready_count": counts["ready"],
            "attention_count": counts["attention"],
            "external_services_required": False,
        },
        "checkpoints": checkpoints,
        "warnings": [
            "发布前检查只读聚合本地证据，不执行真实发布、权限拦截或云端迁移。",
        ],
        "next_steps": [
            "不执行真实发布；先用本清单核对本地闭环、版权、保留策略和审计证据。",
            "外部用户阶段再接认证、对象存储、云端观测、不可篡改审计和计费系统。",
        ],
    }


def _project_checkpoints(
    story_slug: str | None,
    *,
    projects_dir: Path | None,
) -> list[dict[str, str]]:
    if not story_slug:
        return [
            _project_placeholder(
                "project_rights",
                "版权/来源声明",
                "GET /api/stories/<slug>/copyright-statement",
            ),
            _project_placeholder(
                "project_retention",
                "项目保留策略",
                "GET /api/stories/<slug>/retention-policy",
            ),
            _project_placeholder(
                "project_audit_export",
                "审计日志导出",
                "GET /api/stories/<slug>/audit-log/export",
            ),
        ]

    rights = get_project_copyright_statement(story_slug, projects_dir=projects_dir)
    retention = get_project_retention_policy(story_slug, projects_dir=projects_dir)
    audit = get_project_audit_log(story_slug, projects_dir=projects_dir)
    return [
        _checkpoint(
            checkpoint_id="project_rights",
            label="版权/来源声明",
            status="ready"
            if rights.get("status") in {"declared", "builtin_sample"}
            else "attention",
            evidence=str(rights.get("status") or "missing"),
            source_endpoint="GET /api/stories/<slug>/copyright-statement",
            next_step=_first_text(rights.get("next_steps"), "补充项目版权/来源声明。"),
        ),
        _checkpoint(
            checkpoint_id="project_retention",
            label="项目保留策略",
            status="ready"
            if retention.get("status") in {"declared", "builtin_sample"}
            else "attention",
            evidence=str(retention.get("status") or "missing"),
            source_endpoint="GET /api/stories/<slug>/retention-policy",
            next_step=_first_text(retention.get("next_steps"), "补充项目保留策略。"),
        ),
        _checkpoint(
            checkpoint_id="project_audit_export",
            label="审计日志导出",
            status="ready"
            if audit.get("summary", {}).get("event_count", 0) > 0
            else "attention",
            evidence=f"{audit.get('summary', {}).get('event_count', 0)} 条审计事件",
            source_endpoint="GET /api/stories/<slug>/audit-log/export",
            next_step=_first_text(audit.get("next_steps"), "导出前核对项目审计时间线。"),
        ),
    ]


def _permission_checkpoint(permissions: dict[str, Any]) -> dict[str, str]:
    enforcement = permissions.get("enforcement", {})
    status = "attention" if enforcement.get("mode") == "not_enforced" else "ready"
    return _checkpoint(
        checkpoint_id="permission_matrix",
        label="权限矩阵草案",
        status=status,
        evidence=f"执行模式：{enforcement.get('mode') or 'not_enforced'}",
        source_endpoint="GET /api/settings/permission-matrix",
        next_step=_first_text(permissions.get("next_steps"), "接真实认证前保持草案口径。"),
    )


def _project_placeholder(
    checkpoint_id: str,
    label: str,
    source_endpoint: str,
) -> dict[str, str]:
    return _checkpoint(
        checkpoint_id=checkpoint_id,
        label=label,
        status="attention",
        evidence="选择具体项目后核对",
        source_endpoint=source_endpoint,
        next_step="进入项目工作台后补齐该项证据。",
    )


def _checkpoint(
    *,
    checkpoint_id: str,
    label: str,
    status: str,
    evidence: str,
    source_endpoint: str,
    next_step: str,
) -> dict[str, str]:
    return {
        "id": checkpoint_id,
        "label": label,
        "status": status,
        "status_label": "已具备" if status == "ready" else "需留意",
        "evidence": evidence,
        "source_endpoint": source_endpoint,
        "next_step": next_step,
    }


def _safe_story_slug(story_slug: str) -> str:
    sid = safe_id(str(story_slug or ""))
    if sid is None:
        raise ReleasePreflightRequestError("invalid story_slug")
    return sid


def _first_text(items: list[Any] | None, fallback: str) -> str:
    if not items:
        return fallback
    value = items[0]
    return value if isinstance(value, str) and value else fallback

"""v1.0-beta Auth Boundary Checklist-U：认证边界只读清单。"""

from __future__ import annotations

from typing import Any

from living_novel_engine.service.account_project_space import (
    get_account_project_space_boundary,
)
from living_novel_engine.service.commercial_permissions import get_permission_matrix_draft
from living_novel_engine.service.deployment_observability import (
    get_deployment_observability_checklist,
)

VERSION = "v1.0-beta-auth-boundary-checklist-u"


def get_auth_boundary_checklist(
    *,
    api_host: str = "127.0.0.1",
    api_port: int = 8765,
) -> dict[str, Any]:
    """Return a local-first authentication boundary checklist.

    This is documentation-as-data. It does not authenticate requests, create
    users, read secrets, or enforce ACL decisions.
    """

    account = get_account_project_space_boundary()
    permissions = get_permission_matrix_draft()
    observability = get_deployment_observability_checklist(
        api_host=api_host,
        api_port=api_port,
    )
    account_model = account.get("account_model", {})
    enforcement = permissions.get("enforcement", {})
    checkpoints = [
        _checkpoint(
            checkpoint_id="local_operator_mode",
            label="本地单人操作模式",
            status="ready"
            if account_model.get("mode") == "local_single_operator"
            else "attention",
            evidence=str(account_model.get("mode") or "unknown"),
            source_endpoint="GET /api/settings/account-project-space-boundary",
            next_step="真实外部用户前再引入账号身份和团队归属。",
        ),
        _checkpoint(
            checkpoint_id="permission_matrix",
            label="权限矩阵草案",
            status="attention"
            if enforcement.get("mode") == "not_enforced"
            else "ready",
            evidence=f"执行模式：{enforcement.get('mode') or 'not_enforced'}",
            source_endpoint="GET /api/settings/permission-matrix",
            next_step=_first_text(permissions.get("next_steps"), "接真实认证前保持草案口径。"),
        ),
        _checkpoint(
            checkpoint_id="request_acl",
            label="请求级 ACL",
            status="attention",
            evidence="当前 HTTP 服务没有用户上下文",
            source_endpoint="server request handlers",
            next_step="接真实认证后再把 owner/editor/viewer 转为服务端 guardrail。",
        ),
        _checkpoint(
            checkpoint_id="project_space_mapping",
            label="项目空间映射",
            status="ready" if account.get("status") == "boundary_defined" else "attention",
            evidence=str(account.get("status") or "unknown"),
            source_endpoint="GET /api/settings/account-project-space-boundary",
            next_step=_first_text(account.get("next_steps"), "先稳定本地项目空间语义。"),
        ),
        _checkpoint(
            checkpoint_id="deployment_observability",
            label="部署观测边界",
            status="ready"
            if observability.get("status") in {"ready", "attention"}
            else "attention",
            evidence=f"{observability.get('summary', {}).get('signal_count', 0)} 条观测信号",
            source_endpoint="GET /api/settings/deployment-observability",
            next_step=_first_text(observability.get("next_steps"), "上线前补部署观测清单。"),
        ),
    ]
    attention = sum(1 for item in checkpoints if item["status"] == "attention")
    ready = len(checkpoints) - attention
    return {
        "version": VERSION,
        "mode": "read_only_auth_boundary_checklist",
        "status": "ready" if attention == 0 else "attention",
        "summary": {
            "checkpoint_count": len(checkpoints),
            "ready_count": ready,
            "attention_count": attention,
            "auth_enforced": False,
            "external_services_required": False,
        },
        "checkpoints": checkpoints,
        "warnings": [
            "当前没有真实认证、团队空间、请求上下文或 ACL 拦截，本清单只定义接入边界。",
        ],
        "next_steps": [
            "真实认证接入前，继续保持本地单人操作模式，不伪装多用户权限。",
            "后续可先定义认证 provider adapter 边界，再把权限矩阵逐步接入服务端 guardrail。",
        ],
    }


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


def _first_text(items: list[Any] | None, fallback: str) -> str:
    if not items:
        return fallback
    value = items[0]
    return value if isinstance(value, str) and value else fallback

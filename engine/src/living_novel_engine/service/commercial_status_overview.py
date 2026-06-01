"""v1.0-beta Commercial Status Overview-O：设置页商业化状态总览。"""

from __future__ import annotations

from typing import Any

from living_novel_engine.service.account_project_space import (
    get_account_project_space_boundary,
)
from living_novel_engine.service.cloud_persistence_boundary import (
    get_cloud_persistence_boundary,
)
from living_novel_engine.service.commercial_hardening import (
    get_commercial_hardening_scope,
)
from living_novel_engine.service.commercial_permissions import (
    get_permission_matrix_draft,
)
from living_novel_engine.service.deployment_readiness import (
    get_local_deployment_readiness,
)
from living_novel_engine.service.quota_observability import (
    get_quota_observability_lite,
)
from living_novel_engine.service.runtime_settings import get_provider_gateway_summary

VERSION = "v1.0-beta-commercial-status-overview-o"


def _first_text(items: list[Any] | None, fallback: str) -> str:
    if not items:
        return fallback
    value = items[0]
    return value if isinstance(value, str) and value else fallback


def _domain(
    *,
    domain_id: str,
    label: str,
    status: str,
    evidence: str,
    source_endpoint: str,
    next_step: str,
) -> dict[str, str]:
    status_label = {
        "ready": "本地已就绪",
        "attention": "需要留意",
        "deferred": "平台化暂缓",
    }.get(status, "需要留意")
    return {
        "id": domain_id,
        "label": label,
        "status": status,
        "status_label": status_label,
        "evidence": evidence,
        "source_endpoint": source_endpoint,
        "next_step": next_step,
    }


def get_commercial_status_overview(
    *,
    api_host: str = "127.0.0.1",
    api_port: int = 8765,
) -> dict[str, Any]:
    """Return a compact read-only commercial status summary for settings UI.

    This function intentionally returns only summarized, secret-safe evidence. It
    does not write files, start network clients, enforce auth, or imply cloud
    migration has begun.
    """

    scope = get_commercial_hardening_scope()
    permissions = get_permission_matrix_draft()
    account_space = get_account_project_space_boundary()
    cloud = get_cloud_persistence_boundary()
    quota = get_quota_observability_lite()
    deployment = get_local_deployment_readiness(api_host=api_host, api_port=api_port)
    provider = get_provider_gateway_summary()

    routing = provider.get("routing", {})
    quota_policy = quota.get("quota_policy", {})
    deployment_readiness = deployment.get("readiness", {})
    cloud_migration = cloud.get("migration", {})
    account_model = account_space.get("account_model", {})
    enforcement = permissions.get("enforcement", {})

    domains = [
        _domain(
            domain_id="commercial_scope",
            label="商业化范围复核",
            status="ready",
            evidence=str(scope.get("status") or "scope_defined"),
            source_endpoint="GET /api/settings/commercial-hardening-scope",
            next_step=_first_text(scope.get("next_steps"), "继续按本地优先方式拆分小刀。"),
        ),
        _domain(
            domain_id="provider_cost",
            label="模型与成本口径",
            status="ready" if routing.get("llm_route") != "primary_llm" else "attention",
            evidence=f"文本路由：{routing.get('llm_route') or 'mock'}；视觉路由：{routing.get('visual_route') or 'placeholder'}",
            source_endpoint="GET /api/settings/providers",
            next_step="继续只显示脱敏状态和手动成本估算，不内置真实价格表。",
        ),
        _domain(
            domain_id="quota_observability",
            label="配额与观测",
            status="attention" if quota_policy.get("mode") == "not_enforced" else "ready",
            evidence=f"配额模式：{quota_policy.get('mode') or 'not_enforced'}",
            source_endpoint="GET /api/settings/quota-observability",
            next_step=_first_text(quota.get("next_steps"), "先补本地软配额 warning。"),
        ),
        _domain(
            domain_id="permission_model",
            label="权限矩阵",
            status="attention" if enforcement.get("mode") == "not_enforced" else "ready",
            evidence=f"执行模式：{enforcement.get('mode') or 'not_enforced'}",
            source_endpoint="GET /api/settings/permission-matrix",
            next_step=_first_text(permissions.get("next_steps"), "接真实认证前保持草案口径。"),
        ),
        _domain(
            domain_id="account_project_space",
            label="账号与项目空间",
            status="attention"
            if account_model.get("mode") == "local_single_operator"
            else "ready",
            evidence=f"账号模式：{account_model.get('mode') or 'local_single_operator'}",
            source_endpoint="GET /api/settings/account-project-space-boundary",
            next_step=_first_text(account_space.get("next_steps"), "先保持本地单用户项目空间。"),
        ),
        _domain(
            domain_id="cloud_persistence",
            label="云端持久化边界",
            status="deferred"
            if cloud_migration.get("mode") == "not_started"
            else "attention",
            evidence=f"迁移状态：{cloud_migration.get('mode') or 'not_started'}",
            source_endpoint="GET /api/settings/cloud-persistence-boundary",
            next_step=_first_text(cloud.get("next_steps"), "平台化前不上传文件或创建数据库。"),
        ),
        _domain(
            domain_id="local_deployment",
            label="本地部署就绪",
            status="ready" if deployment.get("status") == "ready" else "attention",
            evidence=(
                "无需外部服务"
                if deployment_readiness.get("external_services_required") is False
                else "需要继续检查本地依赖"
            ),
            source_endpoint="GET /api/settings/deployment-readiness",
            next_step=_first_text(deployment.get("next_steps"), "先执行本地 API 冒烟。"),
        ),
        _domain(
            domain_id="audit_and_rights",
            label="审计与版权边界",
            status="ready",
            evidence="项目审计 JSONL、版权声明、保留策略与关键写操作审计钩子已建立。",
            source_endpoint="GET /api/stories/<slug>/audit-log",
            next_step="后续可继续拆版权审批、部署观测或最小发布前检查。",
        ),
    ]
    counts = {
        "ready": sum(1 for domain in domains if domain["status"] == "ready"),
        "attention": sum(1 for domain in domains if domain["status"] == "attention"),
        "deferred": sum(1 for domain in domains if domain["status"] == "deferred"),
    }
    overall = "ready" if counts["attention"] == 0 and counts["deferred"] == 0 else "attention"

    return {
        "version": VERSION,
        "mode": "read_only_settings_overview",
        "overall_status": overall,
        "summary": {
            "total_domains": len(domains),
            "ready_domains": counts["ready"],
            "attention_domains": counts["attention"],
            "deferred_domains": counts["deferred"],
        },
        "domains": domains,
        "warnings": [
            "当前总览只读展示本地商业化状态，不执行真实认证、云端迁移、对象存储或计费。",
            "所有 Key 仅以现有设置层脱敏状态参与判断，本接口不返回明文密钥或变量名。",
        ],
        "next_steps": [
            "继续以设置页商业化状态总览作为本地 beta 检查入口。",
            "后续可继续拆版权审批、部署观测或最小发布前检查，仍保持 additive artifact 契约。",
            "真实外部用户前再评估账号、对象存储、不可篡改审计和计费系统。",
        ],
    }

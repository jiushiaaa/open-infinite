"""v1.0-beta Quota Enforcement Boundary Checklist-W：配额执行边界只读清单。"""

from __future__ import annotations

from typing import Any

from living_novel_engine.service.auth_boundary import get_auth_boundary_checklist
from living_novel_engine.service.deployment_observability import (
    get_deployment_observability_checklist,
)
from living_novel_engine.service.quota_observability import get_quota_observability_lite

VERSION = "v1.0-beta-quota-enforcement-boundary-checklist-w"


def get_quota_enforcement_boundary_checklist(
    *,
    api_host: str = "127.0.0.1",
    api_port: int = 8765,
) -> dict[str, Any]:
    """Return a local-first quota enforcement boundary checklist.

    The report maps existing quota and observability evidence to future hard
    limit guardrails. It does not block generation, write quota state, call
    billing services, or read provider secrets.
    """

    quota = get_quota_observability_lite()
    observability = get_deployment_observability_checklist(
        api_host=api_host,
        api_port=api_port,
    )
    auth = get_auth_boundary_checklist(api_host=api_host, api_port=api_port)
    quota_policy = quota.get("quota_policy", {})
    usage = quota.get("usage", {})
    jobs = quota.get("jobs", {})
    checks = [
        _check(
            check_id="soft_quota_policy",
            label="软配额口径",
            status="ready" if quota_policy.get("mode") == "not_enforced" else "attention",
            evidence=f"{len(quota_policy.get('soft_limits') or [])} 条软配额口径",
            source_endpoint="GET /api/settings/quota-observability",
            next_step="先把软配额提示稳定在设置页和发布前检查里。",
        ),
        _check(
            check_id="usage_metadata",
            label="用量 metadata",
            status="attention"
            if int(usage.get("missing_usage_record_count") or 0)
            else "ready",
            evidence=f"{usage.get('record_count', 0)} 条 usage / {usage.get('missing_usage_record_count', 0)} 条缺失",
            source_endpoint="GET /api/settings/provider-usage",
            next_step="真实计费前继续补齐 LLM usage metadata 与成本口径。",
        ),
        _check(
            check_id="job_retention_window",
            label="任务保留窗口",
            status="ready",
            evidence=f"{jobs.get('total_jobs', 0)} 个近期 job / 上限 {jobs.get('retention', {}).get('max_jobs', 0)}",
            source_endpoint="GET /api/settings/quota-observability",
            next_step="长耗时任务上线前再接持久队列、失败重试和告警。",
        ),
        _check(
            check_id="project_scope",
            label="项目归属范围",
            status="attention"
            if auth.get("summary", {}).get("auth_enforced") is False
            else "ready",
            evidence="当前仍是本地单人操作模式",
            source_endpoint="GET /api/settings/auth-boundary",
            next_step="硬配额执行前必须先绑定用户、项目、团队和权限上下文。",
        ),
        _check(
            check_id="observability_loop",
            label="观测闭环",
            status="ready"
            if observability.get("status") in {"ready", "attention"}
            else "attention",
            evidence=f"{observability.get('summary', {}).get('signal_count', 0)} 条观测信号",
            source_endpoint="GET /api/settings/deployment-observability",
            next_step="真实外部用户前再接云端日志、告警和账单对账。",
        ),
        _check(
            check_id="hard_limit_guardrail",
            label="硬配额拦截",
            status="attention",
            evidence="当前不拦截生成、导入、导出或视觉生成请求",
            source_endpoint="future quota guardrail",
            next_step="先定义 project/user/team 粒度的硬配额错误语义，再接服务端 guardrail。",
        ),
        _check(
            check_id="billing_adapter",
            label="账单 adapter",
            status="attention",
            evidence="尚未接真实计费、余额、套餐或欠费状态",
            source_endpoint="future billing adapter",
            next_step="商业化前再把真实账单 provider 映射为只读状态与可审计拦截。",
        ),
    ]
    attention = sum(1 for item in checks if item["status"] == "attention")
    ready = len(checks) - attention
    return {
        "version": VERSION,
        "mode": "read_only_quota_enforcement_boundary_checklist",
        "status": "ready" if attention == 0 else "attention",
        "summary": {
            "check_count": len(checks),
            "ready_count": ready,
            "attention_count": attention,
            "enforcement_enabled": False,
            "hard_limits_enabled": False,
            "external_billing_required": False,
        },
        "checks": checks,
        "warnings": [
            "当前只是配额执行边界清单，不拦截请求、不写远端账单、不改变生成行为。",
        ],
        "next_steps": [
            "配额执行前先稳定软配额、usage metadata、项目归属和观测闭环。",
            "真实商业化阶段再接硬配额 guardrail、账单 adapter、欠费状态和审计事件。",
        ],
    }


def _check(
    *,
    check_id: str,
    label: str,
    status: str,
    evidence: str,
    source_endpoint: str,
    next_step: str,
) -> dict[str, str]:
    return {
        "id": check_id,
        "label": label,
        "status": status,
        "status_label": "已具备" if status == "ready" else "需留意",
        "evidence": evidence,
        "source_endpoint": source_endpoint,
        "next_step": next_step,
    }

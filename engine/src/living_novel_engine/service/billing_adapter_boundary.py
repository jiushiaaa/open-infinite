"""v1.0-beta Billing Adapter Boundary Checklist-X：计费 adapter 边界只读清单。"""

from __future__ import annotations

from typing import Any

from living_novel_engine.service.auth_boundary import get_auth_boundary_checklist
from living_novel_engine.service.quota_enforcement_boundary import (
    get_quota_enforcement_boundary_checklist,
)
from living_novel_engine.service.runtime_settings import get_provider_usage_summary

VERSION = "v1.0-beta-billing-adapter-boundary-checklist-x"


def get_billing_adapter_boundary_checklist(
    *,
    api_host: str = "127.0.0.1",
    api_port: int = 8765,
) -> dict[str, Any]:
    """Return a local-first billing adapter boundary checklist.

    The report only describes what a future billing adapter would need. It
    does not create invoices, write balances, call payment providers, or read
    provider secrets.
    """

    usage = get_provider_usage_summary()
    quota = get_quota_enforcement_boundary_checklist(
        api_host=api_host,
        api_port=api_port,
    )
    auth = get_auth_boundary_checklist(api_host=api_host, api_port=api_port)
    totals = usage.get("totals") if isinstance(usage, dict) else {}
    cost = usage.get("cost_estimate") if isinstance(usage, dict) else {}
    checks = [
        _check(
            check_id="usage_pricing_input",
            label="用量与单价输入",
            status="ready",
            evidence=f"{usage.get('record_count', 0)} 条 usage / {totals.get('total_tokens', 0)} token",
            source_endpoint="GET /api/settings/provider-usage",
            next_step="真实计费前继续保证 usage metadata 和手动单价口径可解释。",
        ),
        _check(
            check_id="cost_estimate_policy",
            label="成本估算口径",
            status="ready" if cost else "attention",
            evidence="仅使用本地手动单价估算，不内置厂商价格表",
            source_endpoint="GET /api/settings/provider-usage",
            next_step="接账单前先冻结估算字段、币种和 rounding 规则。",
        ),
        _check(
            check_id="quota_enforcement_boundary",
            label="配额执行边界",
            status="ready"
            if quota.get("mode") == "read_only_quota_enforcement_boundary_checklist"
            else "attention",
            evidence=f"{quota.get('summary', {}).get('check_count', 0)} 条配额执行检查",
            source_endpoint="GET /api/settings/quota-enforcement-boundary",
            next_step="账单 adapter 只能在硬配额语义明确后参与拦截判断。",
        ),
        _check(
            check_id="billable_identity",
            label="计费身份绑定",
            status="attention"
            if auth.get("summary", {}).get("auth_enforced") is False
            else "ready",
            evidence="当前仍是本地单人操作模式",
            source_endpoint="GET /api/settings/auth-boundary",
            next_step="真实计费前必须先绑定用户、团队、项目和权限上下文。",
        ),
        _check(
            check_id="payment_provider_adapter",
            label="支付 provider adapter",
            status="attention",
            evidence="尚未实现 customer/subscription/checkout/webhook adapter",
            source_endpoint="future billing adapter",
            next_step="先定义 adapter 合约、幂等键、webhook 签名和本地 fallback。",
        ),
        _check(
            check_id="invoice_refund_trail",
            label="发票与退款轨迹",
            status="attention",
            evidence="尚未落地 invoice、refund、credit 与 reconciliation 事件",
            source_endpoint="future billing adapter",
            next_step="真实账单前先定义审计事件、退款语义和对账状态。",
        ),
        _check(
            check_id="billing_writes",
            label="计费写入",
            status="attention",
            evidence="当前不会写余额、账单、套餐、欠费或支付状态",
            source_endpoint="read-only checklist",
            next_step="外部用户阶段再启用真实计费写入，并保持可审计回放。",
        ),
    ]
    attention = sum(1 for item in checks if item["status"] == "attention")
    ready = len(checks) - attention
    return {
        "version": VERSION,
        "mode": "read_only_billing_adapter_boundary_checklist",
        "status": "ready" if attention == 0 else "attention",
        "summary": {
            "check_count": len(checks),
            "ready_count": ready,
            "attention_count": attention,
            "adapter_implemented": False,
            "billing_writes_enabled": False,
            "external_billing_required": False,
        },
        "checks": checks,
        "warnings": [
            "当前只是计费 adapter 边界清单，不创建账单、不写余额、不调用支付 provider。",
        ],
        "next_steps": [
            "计费接入前先稳定 usage、成本估算、计费身份、硬配额语义和审计事件。",
            "真实商业化阶段再接支付 provider、webhook、发票退款和对账状态。",
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

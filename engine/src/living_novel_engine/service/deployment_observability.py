"""v1.0-beta Deployment Observability Checklist-T：部署观测只读清单。"""

from __future__ import annotations

from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.deployment_readiness import (
    get_local_deployment_readiness,
    get_settings_local_smoke_checklist,
)
from living_novel_engine.service.quota_observability import get_quota_observability_lite
from living_novel_engine.service.release_preflight import get_release_preflight_checklist

VERSION = "v1.0-beta-deployment-observability-checklist-t"


class DeploymentObservabilityRequestError(ValueError):
    """Invalid deployment observability request, mapped to HTTP 400."""


def get_deployment_observability_checklist(
    story_slug: str | None = None,
    *,
    api_host: str = "127.0.0.1",
    api_port: int = 8765,
) -> dict[str, Any]:
    """Return a local-first deployment observability checklist.

    The report points to existing local evidence. It does not open ports, tail
    logs, call cloud monitoring services, or persist observability state.
    """

    sid = _safe_story_slug(story_slug) if story_slug else None
    deployment = get_local_deployment_readiness(api_host=api_host, api_port=api_port)
    smoke = get_settings_local_smoke_checklist(api_host=api_host, api_port=api_port)
    quota = get_quota_observability_lite(story_slug=sid)
    preflight = get_release_preflight_checklist(
        story_slug=sid,
        api_host=api_host,
        api_port=api_port,
    )

    signals = [
        _signal(
            signal_id="local_deployment_health",
            label="本地部署健康",
            status="ready" if deployment.get("status") == "ready" else "attention",
            evidence=str(deployment.get("status") or "unknown"),
            source_endpoint="GET /api/settings/deployment-readiness",
            next_step=_first_text(deployment.get("next_steps"), "先确认本地部署就绪。"),
        ),
        _signal(
            signal_id="local_smoke_paths",
            label="本地冒烟路径",
            status="ready" if smoke.get("status") == "ready" else "attention",
            evidence=f"{smoke.get('summary', {}).get('check_count', 0)} 条路径",
            source_endpoint="GET /api/settings/local-smoke-checklist",
            next_step=_first_text(smoke.get("next_steps"), "按清单核对本地 HTTP 路径。"),
        ),
        _signal(
            signal_id="quota_usage",
            label="配额与用量",
            status="ready"
            if quota.get("status") == "local_observability_ready"
            else "attention",
            evidence=f"{quota.get('usage', {}).get('record_count', 0)} 条 usage 记录",
            source_endpoint="GET /api/settings/quota-observability",
            next_step=_first_text(quota.get("next_steps"), "继续补本地用量观测摘要。"),
        ),
        _signal(
            signal_id="in_memory_jobs",
            label="内存任务状态",
            status="ready",
            evidence=f"{quota.get('jobs', {}).get('total_jobs', 0)} 个近期 job",
            source_endpoint="GET /api/settings/quota-observability",
            next_step="长耗时任务上线前再接持久队列与失败告警。",
        ),
        _signal(
            signal_id="project_audit_timeline",
            label="项目审计时间线",
            status="ready" if sid else "attention",
            evidence=sid or "替换 slug 后核对",
            source_endpoint="GET /api/stories/<slug>/audit-log",
            next_step="进入项目工作台核对最近写操作、版权与导出审计事件。",
        ),
        _signal(
            signal_id="rights_approval",
            label="版权审批检查",
            status="ready" if sid else "attention",
            evidence=sid or "替换 slug 后核对",
            source_endpoint="GET /api/stories/<slug>/rights-approval-checklist",
            next_step="公开分享前先核对项目版权审批准备度。",
        ),
        _signal(
            signal_id="release_preflight",
            label="发布前检查",
            status="ready" if preflight.get("status") == "ready" else "attention",
            evidence=str(preflight.get("status") or "attention"),
            source_endpoint="GET /api/settings/release-preflight",
            next_step=_first_text(preflight.get("next_steps"), "继续补发布前检查缺口。"),
        ),
    ]
    attention = sum(1 for item in signals if item["status"] == "attention")
    ready = len(signals) - attention
    return {
        "version": VERSION,
        "mode": "read_only_deployment_observability_checklist",
        "status": "ready" if attention == 0 else "attention",
        "story_slug": sid or "",
        "summary": {
            "signal_count": len(signals),
            "ready_count": ready,
            "attention_count": attention,
            "external_services_required": False,
            "cloud_monitoring_enabled": False,
        },
        "signals": signals,
        "warnings": [
            "当前仅聚合本地进程、HTTP、用量、job 与审计证据，不接云端观测平台。",
        ],
        "next_steps": [
            "本地部署后先按本清单核对健康、冒烟、用量、job、审计和发布前检查。",
            "真实外部用户阶段再接云端观测、日志采集、告警、对象存储和持久队列。",
        ],
    }


def _signal(
    *,
    signal_id: str,
    label: str,
    status: str,
    evidence: str,
    source_endpoint: str,
    next_step: str,
) -> dict[str, str]:
    return {
        "id": signal_id,
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
        raise DeploymentObservabilityRequestError("invalid story_slug")
    return sid


def _first_text(items: list[Any] | None, fallback: str) -> str:
    if not items:
        return fallback
    value = items[0]
    return value if isinstance(value, str) and value else fallback

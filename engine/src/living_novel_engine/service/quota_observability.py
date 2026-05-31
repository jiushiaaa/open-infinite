"""v1.0-beta Quota & Observability Lite-E：本地配额与观测口径。"""

from __future__ import annotations

from collections import Counter
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.jobs import JOBS, JobStore
from living_novel_engine.service.runtime_settings import get_provider_usage_summary

VERSION = "v1.0-beta-quota-observability-lite-e"


class QuotaObservabilityRequestError(ValueError):
    """Invalid quota/observability request, mapped to HTTP 400."""


def get_quota_observability_lite(
    *,
    story_slug: str | None = None,
    job_store: JobStore | None = None,
) -> dict[str, Any]:
    """Return local quota/usage/job observability without enforcing limits."""

    story = None
    if story_slug:
        story = safe_id(story_slug)
        if story is None:
            raise QuotaObservabilityRequestError("invalid story_slug")

    usage = get_provider_usage_summary(story_slug=story)
    jobs = _job_summary(job_store or JOBS)
    totals = usage.get("totals") if isinstance(usage, dict) else {}
    total_tokens = int((totals or {}).get("total_tokens") or 0)
    missing_usage = int(usage.get("missing_usage_record_count") or 0)

    warnings: list[dict[str, str]] = [
        {
            "code": "quota_not_enforced",
            "message": "当前只提供本地软配额口径，不拦截生成请求。",
        }
    ]
    if missing_usage:
        warnings.append(
            {
                "code": "usage_metadata_missing",
                "message": "部分生成记录缺少 usage metadata，成本与配额统计可能偏低。",
            }
        )
    if jobs["status_counts"].get("failed", 0):
        warnings.append(
            {
                "code": "failed_jobs_present",
                "message": "近期存在失败 job，请在继续生成前查看错误原因。",
            }
        )

    return {
        "version": VERSION,
        "status": "local_observability_ready",
        "story_slug": story,
        "quota_policy": {
            "mode": "not_enforced",
            "scope": "local_process",
            "hard_limits": [],
            "soft_limits": [
                {
                    "id": "total_tokens",
                    "label": "累计 token 用量",
                    "current": total_tokens,
                    "limit": None,
                    "status": "observed",
                },
                {
                    "id": "recent_jobs_retained",
                    "label": "内存 job 保留数量",
                    "current": jobs["total_jobs"],
                    "limit": jobs["retention"]["max_jobs"],
                    "status": "observed",
                },
            ],
            "enforcement": "none",
        },
        "usage": {
            "version": usage.get("version"),
            "run_count": usage.get("run_count", 0),
            "record_count": usage.get("record_count", 0),
            "missing_usage_record_count": missing_usage,
            "totals": totals or {},
            "by_provider": usage.get("by_provider", []),
            "cost_estimate": usage.get("cost_estimate", {}),
        },
        "jobs": jobs,
        "observability": {
            "external_monitoring": "not_configured",
            "data_sources": [
                "generation_meta.usage",
                "service.jobs.JOBS",
                "runtime settings",
            ],
            "durability": "process_memory_only",
            "status": "attention" if warnings[1:] else "ok",
        },
        "warnings": warnings,
        "next_steps": [
            "先定义真实计费前的项目级软配额 warning。",
            "补充 job 失败原因与长耗时任务的本地观测摘要。",
            "真实外部用户前再接云端监控、团队配额和账单系统。",
        ],
    }


def _job_summary(job_store: JobStore) -> dict[str, Any]:
    records = job_store.snapshot()
    status_counts = Counter(str(rec.get("status") or "unknown") for rec in records)
    kind_counts = Counter(str(rec.get("kind") or "unknown") for rec in records)
    latest = [
        {
            "job_id": str(rec.get("job_id") or ""),
            "kind": str(rec.get("kind") or ""),
            "status": str(rec.get("status") or ""),
            "progress": int(rec.get("progress") or 0),
            "stage": str(rec.get("stage") or ""),
            "error_present": bool(rec.get("error")),
        }
        for rec in records[-10:]
    ]
    return {
        "total_jobs": len(records),
        "status_counts": dict(status_counts),
        "kind_counts": dict(kind_counts),
        "latest": latest,
        "latest_limit": 10,
        "retention": {
            "mode": "recent_in_memory",
            "max_jobs": job_store.max_jobs,
        },
    }

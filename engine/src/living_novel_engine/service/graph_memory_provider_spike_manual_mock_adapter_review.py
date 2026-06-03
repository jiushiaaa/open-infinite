"""Graph Memory Provider Spike Manual Mock Adapter Review MVP.

This read-only report turns mock-compatible adapter specs into a manual review
packet. It does not save review decisions, create real adapters, read keys, or
call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_mock_compatible_adapter import (
    GraphMemoryProviderSpikeMockCompatibleAdapterRequestError,
    get_graph_memory_provider_spike_mock_compatible_adapter,
)

VERSION = "graph-memory-provider-spike-manual-mock-adapter-review-mvp"


class GraphMemoryProviderSpikeManualMockAdapterReviewRequestError(ValueError):
    """Invalid graph-memory provider spike manual mock adapter review request."""


def get_graph_memory_provider_spike_manual_mock_adapter_review(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only manual mock adapter review packet."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        adapter = get_graph_memory_provider_spike_mock_compatible_adapter(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeMockCompatibleAdapterRequestError as exc:
        raise GraphMemoryProviderSpikeManualMockAdapterReviewRequestError(
            str(exc)
        ) from exc

    source_status = str(adapter.get("status") or "deferred")
    rows = _review_rows(adapter)
    checks = _compliance_checks(adapter, rows)
    status = _status(source_status, rows)
    summary = _summary(sid, source_status, status, rows, checks)
    review = _manual_mock_adapter_review(status, summary)
    decision = _decision(status, summary)
    manifest = _manifest(
        generated_at,
        summary,
        review,
        decision,
        rows,
        checks,
        adapter,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_manual_mock_adapter_review",
        "status": status,
        "story_slug": sid,
        "source_kind": adapter.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "manual_mock_adapter_review": review,
        "decision": decision,
        "review_rows": rows,
        "compliance_checks": checks,
        "review_materials": _review_materials(status, rows),
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": _no_go_conditions(adapter, rows),
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(adapter, rows),
        "boundaries": [
            "只读生成 manual mock adapter review，不保存人工复核结论。",
            "复核包只检查 local mock adapter 规格，不能创建真实 provider adapter。",
            "不读取、不返回、不记录明文 Key。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "本刀完成后暂停继续开发，等待人工选择下一步。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeManualMockAdapterReviewRequestError(
            "invalid slug"
        )
    return sid


def _status(source_status: str, rows: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_mock_compatible_adapter" and rows:
        return "ready_for_manual_mock_adapter_review"
    if source_status in {"needs_more_evidence", "blocked"}:
        return source_status
    return "deferred"


def _review_rows(adapter: dict[str, Any]) -> list[dict[str, Any]]:
    if adapter.get("status") != "ready_for_mock_compatible_adapter":
        return []

    rows: list[dict[str, Any]] = []
    for spec in adapter.get("adapter_specs") or []:
        methods = [str(method) for method in spec.get("implements_contract_methods") or []]
        missing_methods = [
            method
            for method in (
                "prepare_fixture_payload",
                "run_mock_fixture",
                "validate_mock_result",
            )
            if method not in methods
        ]
        rows.append(
            {
                "id": f"manual-mock-review-{spec.get('provider_id') or 'unknown'}",
                "provider_id": str(spec.get("provider_id") or "unknown"),
                "service_target": str(spec.get("service_target") or "unknown"),
                "source_adapter_spec_id": str(spec.get("id") or ""),
                "source_fixture_harness_id": str(
                    spec.get("source_fixture_harness_id") or ""
                ),
                "adapter_mode": str(spec.get("adapter_mode") or "unknown"),
                "review_status": "requires_manual_review",
                "risk_level": "low_mock_only",
                "required_methods": methods,
                "missing_methods": missing_methods,
                "fixture_bindings": [str(item) for item in spec.get("fixture_bindings") or []],
                "review_prompts": _row_review_prompts(spec, missing_methods),
                "real_provider_calls_allowed": False,
                "external_network_allowed": False,
                "plaintext_key_allowed": False,
                "writes_artifacts": False,
                "manual_decision_saved": False,
            }
        )
    return rows


def _row_review_prompts(
    spec: dict[str, Any],
    missing_methods: list[str],
) -> list[str]:
    prompts = [
        f"人工确认 {spec.get('service_target') or 'unknown'} adapter 只支持 local mock。",
        "人工确认 mock result template 不包含真实 provider 输出或明文 Key。",
        "人工确认 validation cases 足以阻止真实 provider call。",
    ]
    if missing_methods:
        prompts.append(f"补齐缺失方法：{', '.join(missing_methods)}")
    return prompts


def _compliance_checks(
    adapter: dict[str, Any],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not rows:
        return []

    checks: list[dict[str, Any]] = []
    for row in rows:
        checks.extend(
            [
                _check(row, "mode-local-mock-only", row["adapter_mode"] == "local_mock_only"),
                _check(row, "no-real-provider-calls", not row["real_provider_calls_allowed"]),
                _check(row, "no-plaintext-key", not row["plaintext_key_allowed"]),
                _check(row, "no-artifact-write", not row["writes_artifacts"]),
                _check(row, "all-contract-methods-present", not row["missing_methods"]),
            ]
        )

    adapter_summary = adapter.get("summary") or {}
    checks.append(
        {
            "id": "source-mock-adapter-summary-safe",
            "provider_id": "all",
            "service_target": "all",
            "check": "source_mock_adapter_summary_safe",
            "status": "pass"
            if not adapter_summary.get("real_provider_adapter_allowed")
            else "blocked",
            "external_services_required": False,
            "real_provider_adapter_allowed": False,
            "reason": "source mock adapter summary 仍禁止真实 provider adapter。",
        }
    )
    return checks


def _check(row: dict[str, Any], name: str, passed: bool) -> dict[str, Any]:
    return {
        "id": f"{name}-{row['provider_id']}",
        "provider_id": row["provider_id"],
        "service_target": row["service_target"],
        "check": name,
        "status": "pass" if passed else "blocked",
        "external_services_required": False,
        "real_provider_adapter_allowed": False,
        "reason": f"{name} {'通过' if passed else '未通过'}。",
    }


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    rows: list[dict[str, Any]],
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_mock_adapter_status": source_status,
        "status": status,
        "review_row_count": len(rows),
        "compliance_check_count": len(checks),
        "blocked_check_count": sum(1 for check in checks if check["status"] != "pass"),
        "writes_artifacts": False,
        "manual_decision_saved": False,
        "external_services_required": False,
        "provider_calls": False,
        "real_provider_adapter_allowed": False,
        "plaintext_key_returned": False,
        "pause_after_this_slice": status == "ready_for_manual_mock_adapter_review",
    }


def _manual_mock_adapter_review(
    status: str,
    summary: dict[str, Any],
) -> dict[str, Any]:
    ready = status == "ready_for_manual_mock_adapter_review"
    return {
        "id": "graph_memory_provider_spike_manual_mock_adapter_review",
        "status": "manual_mock_adapter_review_ready" if ready else status,
        "ready": ready,
        "review_row_count": summary["review_row_count"],
        "compliance_check_count": summary["compliance_check_count"],
        "blocked_check_count": summary["blocked_check_count"],
        "save_allowed": False,
        "manual_decision_saved": False,
        "real_provider_adapter_allowed": False,
        "pause_after_this_slice": ready,
        "reason": (
            "manual mock adapter review 已可读；本刀后暂停继续开发。"
            if ready
            else "mock-compatible adapter 尚不足以生成 manual review。"
        ),
    }


def _decision(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    if status == "ready_for_manual_mock_adapter_review":
        return {
            "status": "manual_mock_adapter_review_ready_pause_after_this_slice",
            "recommendation": "人工复核 mock adapter 规格后再决定是否继续；当前先暂停开发。",
            "next_slice": "Pause Development",
            "review_row_count": summary["review_row_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 mock-compatible adapter，不创建真实 adapter。",
        "next_slice": "Graph Memory Provider Spike Manual Mock Adapter Review",
        "review_row_count": summary["review_row_count"],
    }


def _review_materials(status: str, rows: list[dict[str, Any]]) -> list[str]:
    if status != "ready_for_manual_mock_adapter_review":
        return []
    materials = [
        f"Mock adapter 复核：{row['service_target']} / {row['provider_id']}"
        for row in rows
    ]
    materials.append("本复核包只读，不保存人工决定。")
    materials.append("本刀完成后暂停继续开发。")
    return _dedupe(materials)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_manual_mock_adapter_review":
        return []
    return [
        "人工确认所有 adapter 仍是 local_mock_only。",
        "人工确认没有明文 Key、外网请求或 artifact 写入。",
        "人工确认本刀后暂停，不继续自动进入真实 provider。",
    ]


def _no_go_conditions(adapter: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    items = list(adapter.get("no_go_conditions") or [])
    for row in rows:
        items.append(
            f"{row['service_target']} manual mock adapter review 尚未保存人工结论，不能启用真实 provider adapter。"
        )
    items.extend(
        [
            "不能把 manual mock adapter review 当成真实 provider approval。",
            "不能保存人工复核结论、真实配置或明文 Key。",
            "不能在本刀后自动继续开发真实 provider 链路。",
        ]
    )
    return _dedupe(items)


def _warnings(adapter: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    warnings = list(adapter.get("warnings") or [])
    if not rows:
        warnings.append("没有可生成 manual mock adapter review 的 mock adapter 规格。")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    review: dict[str, Any],
    decision: dict[str, Any],
    rows: list[dict[str, Any]],
    checks: list[dict[str, Any]],
    adapter: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "manual_mock_adapter_review": review,
        "decision": decision,
        "review_rows": rows,
        "compliance_checks": checks,
        "source_mock_compatible_adapter": {
            "version": adapter.get("version"),
            "status": adapter.get("status"),
            "mock_compatible_adapter": adapter.get("mock_compatible_adapter"),
        },
        "contract": {
            "writes_artifacts": False,
            "manual_decision_saved": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_adapter_allowed": False,
            "plaintext_key_returned": False,
            "pause_after_this_slice": summary["pause_after_this_slice"],
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_manual_mock_adapter_review":
        return [
            "人工复核 mock adapter review packet。",
            "本刀完成后暂停继续开发，等待用户明确下一步。",
        ]
    return ["保持 manual mock adapter review 暂缓，不创建真实 provider adapter。"]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

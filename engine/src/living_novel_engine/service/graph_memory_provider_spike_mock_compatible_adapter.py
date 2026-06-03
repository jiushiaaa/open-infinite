"""Graph Memory Provider Spike Mock-compatible Adapter MVP."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_single_fixture_dry_run_harness import (
    GraphMemoryProviderSpikeSingleFixtureDryRunHarnessRequestError,
    get_graph_memory_provider_spike_single_fixture_dry_run_harness,
)

VERSION = "graph-memory-provider-spike-mock-compatible-adapter-mvp"


class GraphMemoryProviderSpikeMockCompatibleAdapterRequestError(ValueError):
    """Invalid graph-memory provider spike mock-compatible adapter request."""


def get_graph_memory_provider_spike_mock_compatible_adapter(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a read-only mock-compatible adapter specification."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        harness = get_graph_memory_provider_spike_single_fixture_dry_run_harness(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeSingleFixtureDryRunHarnessRequestError as exc:
        raise GraphMemoryProviderSpikeMockCompatibleAdapterRequestError(str(exc)) from exc

    source_status = str(harness.get("status") or "deferred")
    specs = _adapter_specs(harness)
    status = _status(source_status, specs)
    summary = _summary(sid, source_status, status, specs)
    adapter = _mock_compatible_adapter(status, summary)
    decision = _decision(status, summary)
    manifest = _manifest(generated_at, summary, adapter, decision, specs, harness)
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_mock_compatible_adapter",
        "status": status,
        "story_slug": sid,
        "source_kind": harness.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "mock_compatible_adapter": adapter,
        "decision": decision,
        "adapter_specs": specs,
        "validation_cases": _validation_cases(status, specs),
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": _no_go_conditions(harness, specs),
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(harness, specs),
        "boundaries": [
            "只读生成 mock-compatible adapter 规格，不创建真实 adapter。",
            "Adapter 规格只服务 local mock fixture，不调用真实 provider。",
            "不读取、不返回、不记录明文 Key。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeMockCompatibleAdapterRequestError("invalid slug")
    return sid


def _status(source_status: str, specs: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_single_fixture_dry_run_harness" and specs:
        return "ready_for_mock_compatible_adapter"
    if source_status in {"needs_more_evidence", "blocked"}:
        return source_status
    return "deferred"


def _adapter_specs(harness: dict[str, Any]) -> list[dict[str, Any]]:
    if harness.get("status") != "ready_for_single_fixture_dry_run_harness":
        return []
    specs: list[dict[str, Any]] = []
    for item in harness.get("fixture_harnesses") or []:
        provider_id = str(item.get("provider_id") or "unknown")
        specs.append(
            {
                "id": f"mock-compatible-adapter-{provider_id}",
                "provider_id": provider_id,
                "service_target": str(item.get("service_target") or "unknown"),
                "source_fixture_harness_id": str(item.get("id") or ""),
                "adapter_mode": "local_mock_only",
                "implements_contract_methods": [
                    "prepare_fixture_payload",
                    "run_mock_fixture",
                    "validate_mock_result",
                ],
                "fixture_bindings": [str(item.get("fixture_id") or "")],
                "mock_result_template": {
                    "status": "mock_ready",
                    "provider_id": provider_id,
                    "coverage_delta": 0,
                    "risk_notes": ["mock adapter does not contact external services"],
                },
                "real_provider_calls_allowed": False,
                "external_network_allowed": False,
                "plaintext_key_allowed": False,
                "writes_artifacts": False,
            }
        )
    return specs


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    specs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_single_fixture_harness_status": source_status,
        "status": status,
        "adapter_count": len(specs),
        "mock_adapter_ready": bool(specs),
        "real_provider_adapter_allowed": False,
        "writes_artifacts": False,
        "external_services_required": False,
        "provider_calls": False,
        "plaintext_key_returned": False,
    }


def _mock_compatible_adapter(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    ready = status == "ready_for_mock_compatible_adapter"
    return {
        "id": "graph_memory_provider_spike_mock_compatible_adapter",
        "status": "mock_adapter_ready" if ready else status,
        "ready": ready,
        "adapter_count": summary["adapter_count"],
        "mock_adapter_ready": ready,
        "real_provider_adapter_allowed": False,
        "reason": (
            "mock-compatible adapter 规格已可读，真实 provider 仍禁止。"
            if ready
            else "single fixture dry-run harness 尚不足以生成 mock adapter。"
        ),
    }


def _decision(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    if status == "ready_for_mock_compatible_adapter":
        return {
            "status": "mock_compatible_adapter_ready_real_provider_still_blocked",
            "recommendation": "mock adapter 规格已就绪；真实 provider 仍需后续显式 opt-in。",
            "next_slice": "Graph Memory Provider Spike Manual Mock Adapter Review",
            "adapter_count": summary["adapter_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 single fixture dry-run harness，不创建真实 adapter。",
        "next_slice": "Graph Memory Provider Spike Mock-compatible Adapter",
        "adapter_count": summary["adapter_count"],
    }


def _validation_cases(status: str, specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if status != "ready_for_mock_compatible_adapter":
        return []
    return [
        {
            "id": f"validate-{spec['provider_id']}",
            "provider_id": spec["provider_id"],
            "assertions": [
                "adapter_mode == local_mock_only",
                "real_provider_calls_allowed == false",
                "plaintext_key_allowed == false",
                "writes_artifacts == false",
            ],
        }
        for spec in specs
    ]


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_mock_compatible_adapter":
        return []
    return [
        "人工确认 mock adapter 不进行真实网络请求。",
        "人工确认 adapter 规格没有明文 Key 字段。",
    ]


def _no_go_conditions(harness: dict[str, Any], specs: list[dict[str, Any]]) -> list[str]:
    items = list(harness.get("no_go_conditions") or [])
    for spec in specs:
        items.append(
            f"{spec['service_target']} mock adapter 仍禁止真实 provider calls。"
        )
    return _dedupe(items)


def _warnings(harness: dict[str, Any], specs: list[dict[str, Any]]) -> list[str]:
    warnings = list(harness.get("warnings") or [])
    if not specs:
        warnings.append("没有可生成 mock-compatible adapter 的 dry-run harness。")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    adapter: dict[str, Any],
    decision: dict[str, Any],
    specs: list[dict[str, Any]],
    harness: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "mock_compatible_adapter": adapter,
        "decision": decision,
        "adapter_specs": specs,
        "source_single_fixture_harness": {
            "version": harness.get("version"),
            "status": harness.get("status"),
            "dry_run_harness": harness.get("dry_run_harness"),
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_mock_compatible_adapter":
        return ["人工复核 mock adapter 规格；仍不创建真实 provider 配置。"]
    return ["保持 mock adapter 暂缓，不创建真实 provider adapter。"]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

"""Graph Memory Provider Spike Single Fixture Dry-run Harness MVP."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_local_provider_contract import (
    GraphMemoryProviderSpikeLocalProviderContractRequestError,
    get_graph_memory_provider_spike_local_provider_contract,
)

VERSION = "graph-memory-provider-spike-single-fixture-dry-run-harness-mvp"


class GraphMemoryProviderSpikeSingleFixtureDryRunHarnessRequestError(ValueError):
    """Invalid graph-memory provider spike dry-run harness request."""


def get_graph_memory_provider_spike_single_fixture_dry_run_harness(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a read-only single-fixture local mock dry-run harness."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        contract = get_graph_memory_provider_spike_local_provider_contract(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeLocalProviderContractRequestError as exc:
        raise GraphMemoryProviderSpikeSingleFixtureDryRunHarnessRequestError(str(exc)) from exc

    source_status = str(contract.get("status") or "deferred")
    harnesses = _fixture_harnesses(contract)
    status = _status(source_status, harnesses)
    summary = _summary(sid, source_status, status, harnesses)
    dry_run_harness = _dry_run_harness(status, summary)
    decision = _decision(status, summary)
    manifest = _manifest(
        generated_at,
        summary,
        dry_run_harness,
        decision,
        harnesses,
        contract,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_single_fixture_dry_run_harness",
        "status": status,
        "story_slug": sid,
        "source_kind": contract.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "dry_run_harness": dry_run_harness,
        "decision": decision,
        "fixture_harnesses": harnesses,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": _no_go_conditions(contract, harnesses),
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(contract, harnesses),
        "boundaries": [
            "只读生成 single fixture dry-run harness，不保存 dry-run 结果。",
            "Harness 只允许 local_mock_only，不运行真实 provider。",
            "不读取、不返回、不记录明文 Key。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeSingleFixtureDryRunHarnessRequestError(
            "invalid slug"
        )
    return sid


def _status(source_status: str, harnesses: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_local_provider_contract" and harnesses:
        return "ready_for_single_fixture_dry_run_harness"
    if source_status in {"needs_more_evidence", "blocked"}:
        return source_status
    return "deferred"


def _fixture_harnesses(contract: dict[str, Any]) -> list[dict[str, Any]]:
    if contract.get("status") != "ready_for_local_provider_contract":
        return []
    harnesses: list[dict[str, Any]] = []
    for item in contract.get("provider_contracts") or []:
        provider_id = str(item.get("provider_id") or "unknown")
        harnesses.append(
            {
                "id": f"single-fixture-harness-{provider_id}",
                "provider_id": provider_id,
                "service_target": str(item.get("service_target") or "unknown"),
                "source_contract_id": str(item.get("id") or ""),
                "fixture_id": str(item.get("fixture_id") or ""),
                "eval_id": str(item.get("eval_id") or ""),
                "execution_mode": "local_mock_only",
                "mock_execution_allowed": True,
                "real_provider_execution_allowed": False,
                "writes_artifacts": False,
                "input_payload": {
                    "provider_id": provider_id,
                    "fixture_id": str(item.get("fixture_id") or ""),
                    "eval_id": str(item.get("eval_id") or ""),
                    "contract_id": str(item.get("id") or ""),
                },
                "expected_result_schema": {
                    "status": "mock_ready",
                    "coverage_delta": "number",
                    "risk_notes": "string[]",
                },
                "validation_steps": [
                    "prepare_fixture_payload",
                    "run_mock_fixture",
                    "validate_mock_result",
                ],
            }
        )
    return harnesses


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    harnesses: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_local_provider_contract_status": source_status,
        "status": status,
        "fixture_harness_count": len(harnesses),
        "mock_execution_allowed": bool(harnesses),
        "real_provider_execution_allowed": False,
        "writes_artifacts": False,
        "external_services_required": False,
        "provider_calls": False,
        "plaintext_key_returned": False,
    }


def _dry_run_harness(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    ready = status == "ready_for_single_fixture_dry_run_harness"
    return {
        "id": "graph_memory_provider_spike_single_fixture_dry_run_harness",
        "status": "single_fixture_harness_ready" if ready else status,
        "ready": ready,
        "mock_execution_allowed": ready,
        "real_provider_execution_allowed": False,
        "fixture_harness_count": summary["fixture_harness_count"],
        "reason": (
            "单 fixture dry-run harness 已可用，且仅限本地 mock。"
            if ready
            else "local provider contract 尚不足以生成 dry-run harness。"
        ),
    }


def _decision(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    if status == "ready_for_single_fixture_dry_run_harness":
        return {
            "status": "single_fixture_harness_ready_real_provider_still_blocked",
            "recommendation": "下一步只生成 mock-compatible adapter 规格。",
            "next_slice": "Graph Memory Provider Spike Mock-compatible Adapter",
            "fixture_harness_count": summary["fixture_harness_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 local provider contract，不运行真实 provider。",
        "next_slice": "Graph Memory Provider Spike Single Fixture Dry-run Harness",
        "fixture_harness_count": summary["fixture_harness_count"],
    }


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_single_fixture_dry_run_harness":
        return []
    return [
        "人工确认 harness 只运行 local mock。",
        "人工确认 harness 不保存 dry-run 结果。",
    ]


def _no_go_conditions(contract: dict[str, Any], harnesses: list[dict[str, Any]]) -> list[str]:
    items = list(contract.get("no_go_conditions") or [])
    for harness in harnesses:
        items.append(
            f"{harness['service_target']} dry-run harness 仍禁止真实 provider execution。"
        )
    return _dedupe(items)


def _warnings(contract: dict[str, Any], harnesses: list[dict[str, Any]]) -> list[str]:
    warnings = list(contract.get("warnings") or [])
    if not harnesses:
        warnings.append("没有可生成 single fixture dry-run harness 的 provider contract。")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    dry_run_harness: dict[str, Any],
    decision: dict[str, Any],
    harnesses: list[dict[str, Any]],
    contract: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "dry_run_harness": dry_run_harness,
        "decision": decision,
        "fixture_harnesses": harnesses,
        "source_local_provider_contract": {
            "version": contract.get("version"),
            "status": contract.get("status"),
            "local_provider_contract": contract.get("local_provider_contract"),
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_single_fixture_dry_run_harness":
        return ["进入 mock-compatible adapter，只定义本地 mock adapter 规格。"]
    return ["保持 dry-run harness 暂缓，不运行真实 provider。"]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

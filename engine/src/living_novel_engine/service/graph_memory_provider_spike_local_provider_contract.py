"""Graph Memory Provider Spike Local Provider Contract / Adapter Boundary MVP."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_opt_in_config_draft import (
    GraphMemoryProviderSpikeOptInConfigDraftRequestError,
    get_graph_memory_provider_spike_opt_in_config_draft,
)

VERSION = "graph-memory-provider-spike-local-provider-contract-mvp"


class GraphMemoryProviderSpikeLocalProviderContractRequestError(ValueError):
    """Invalid graph-memory provider spike local contract request."""


def get_graph_memory_provider_spike_local_provider_contract(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a read-only local provider contract and adapter boundary."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        config = get_graph_memory_provider_spike_opt_in_config_draft(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeOptInConfigDraftRequestError as exc:
        raise GraphMemoryProviderSpikeLocalProviderContractRequestError(str(exc)) from exc

    source_status = str(config.get("status") or "deferred")
    contracts = _provider_contracts(config)
    boundaries = _adapter_boundaries(contracts)
    methods = _contract_methods()
    status = _status(source_status, contracts)
    summary = _summary(sid, source_status, status, contracts, boundaries)
    local_contract = _local_provider_contract(status, summary)
    decision = _decision(status, summary)
    manifest = _manifest(
        generated_at,
        summary,
        local_contract,
        decision,
        contracts,
        boundaries,
        methods,
        config,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_local_provider_contract",
        "status": status,
        "story_slug": sid,
        "source_kind": config.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "local_provider_contract": local_contract,
        "decision": decision,
        "provider_contracts": contracts,
        "adapter_boundaries": boundaries,
        "contract_methods": methods,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": _no_go_conditions(config, boundaries),
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(config, contracts),
        "boundaries": [
            "只读生成 local provider contract，不创建真实 adapter 实例。",
            "Adapter boundary 只允许 local_mock_only，不允许真实 provider call。",
            "不读取、不返回、不记录明文 Key。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeLocalProviderContractRequestError("invalid slug")
    return sid


def _status(source_status: str, contracts: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_opt_in_config_draft" and contracts:
        return "ready_for_local_provider_contract"
    if source_status in {"needs_more_evidence", "blocked"}:
        return source_status
    return "deferred"


def _provider_contracts(config: dict[str, Any]) -> list[dict[str, Any]]:
    if config.get("status") != "ready_for_opt_in_config_draft":
        return []
    contracts: list[dict[str, Any]] = []
    for entry in config.get("config_entries") or []:
        provider_id = str(entry.get("provider_id") or "unknown")
        contracts.append(
            {
                "id": f"local-contract-{provider_id}",
                "provider_id": provider_id,
                "provider_label": str(entry.get("provider_label") or "unknown"),
                "service_target": str(entry.get("service_target") or "unknown"),
                "source_config_entry_id": str(entry.get("id") or ""),
                "fixture_id": str(entry.get("fixture_id") or ""),
                "eval_id": str(entry.get("eval_id") or ""),
                "contract_version": "draft-v1",
                "adapter_mode": "local_mock_only",
                "mock_adapter_required": True,
                "real_provider_calls_allowed": False,
                "plaintext_key_allowed": False,
                "writes_artifacts": False,
                "implements_methods": [
                    "prepare_fixture_payload",
                    "run_mock_fixture",
                    "validate_mock_result",
                ],
                "input_schema": {
                    "fixture_id": "string",
                    "provider_id": "string",
                    "config_entry_id": "string",
                },
                "output_schema": {
                    "status": "mock_ready | deferred | blocked",
                    "coverage_delta": "number",
                    "risk_notes": "string[]",
                },
            }
        )
    return contracts


def _adapter_boundaries(contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"adapter-boundary-{contract['provider_id']}",
            "provider_id": contract["provider_id"],
            "service_target": contract["service_target"],
            "allowed_mode": "local_mock_only",
            "blocked_modes": ["real_provider_call", "production_sync"],
            "plaintext_key_allowed": False,
            "external_network_allowed": False,
            "writes_artifacts": False,
            "real_provider_adapter_allowed": False,
        }
        for contract in contracts
    ]


def _contract_methods() -> list[dict[str, Any]]:
    return [
        {
            "name": "prepare_fixture_payload",
            "description": "把单 fixture 输入整理成 adapter payload。",
            "external_services_required": False,
        },
        {
            "name": "run_mock_fixture",
            "description": "在本地 deterministic/mock adapter 中运行 fixture。",
            "external_services_required": False,
        },
        {
            "name": "validate_mock_result",
            "description": "校验 mock result 是否满足 shadow replay 验收字段。",
            "external_services_required": False,
        },
    ]


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    contracts: list[dict[str, Any]],
    boundaries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_config_draft_status": source_status,
        "status": status,
        "provider_contract_count": len(contracts),
        "adapter_boundary_count": len(boundaries),
        "writes_artifacts": False,
        "external_services_required": False,
        "provider_calls": False,
        "real_provider_config_allowed": False,
        "real_provider_adapter_allowed": False,
        "plaintext_key_returned": False,
    }


def _local_provider_contract(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    ready = status == "ready_for_local_provider_contract"
    return {
        "id": "graph_memory_provider_spike_local_provider_contract",
        "status": "local_provider_contract_ready" if ready else status,
        "ready": ready,
        "contract_version": "draft-v1",
        "provider_contract_count": summary["provider_contract_count"],
        "real_provider_adapter_allowed": False,
        "mock_only": ready,
        "reason": (
            "本地 provider contract 与 adapter 边界已可读。"
            if ready
            else "config draft 尚不足以生成 provider contract。"
        ),
    }


def _decision(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    if status == "ready_for_local_provider_contract":
        return {
            "status": "local_provider_contract_ready_real_provider_still_blocked",
            "recommendation": "下一步只生成单 fixture dry-run harness，不运行真实 provider。",
            "next_slice": "Graph Memory Provider Spike Single Fixture Dry-run Harness",
            "provider_contract_count": summary["provider_contract_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 opt-in config draft，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Local Provider Contract",
        "provider_contract_count": summary["provider_contract_count"],
    }


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_local_provider_contract":
        return []
    return [
        "人工确认 provider contract 只描述本地 mock 接口。",
        "人工确认 adapter boundary 禁止外网、明文 Key 和 artifact 写入。",
    ]


def _no_go_conditions(config: dict[str, Any], boundaries: list[dict[str, Any]]) -> list[str]:
    items = list(config.get("no_go_conditions") or [])
    for boundary in boundaries:
        items.append(
            f"{boundary['service_target']} adapter boundary 仍禁止真实 provider call。"
        )
    return _dedupe(items)


def _warnings(config: dict[str, Any], contracts: list[dict[str, Any]]) -> list[str]:
    warnings = list(config.get("warnings") or [])
    if not contracts:
        warnings.append("没有可生成 local provider contract 的 config draft。")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    local_contract: dict[str, Any],
    decision: dict[str, Any],
    contracts: list[dict[str, Any]],
    boundaries: list[dict[str, Any]],
    methods: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "local_provider_contract": local_contract,
        "decision": decision,
        "provider_contracts": contracts,
        "adapter_boundaries": boundaries,
        "contract_methods": methods,
        "source_config_draft": {
            "version": config.get("version"),
            "status": config.get("status"),
            "config_draft": config.get("config_draft"),
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_local_provider_contract":
        return ["进入单 fixture dry-run harness，只运行本地 mock。"]
    return ["保持 provider contract 暂缓，不接真实服务。"]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

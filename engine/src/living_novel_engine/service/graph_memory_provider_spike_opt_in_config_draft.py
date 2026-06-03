"""Graph Memory Provider Spike Opt-in Config Draft MVP.

This read-only draft turns the human signoff schema into a local opt-in config
draft. It does not save config, read keys, create provider accounts, or call
external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_opt_in_human_signoff_schema_draft import (
    GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftRequestError,
    get_graph_memory_provider_spike_opt_in_human_signoff_schema_draft,
)

VERSION = "graph-memory-provider-spike-opt-in-config-draft-mvp"


class GraphMemoryProviderSpikeOptInConfigDraftRequestError(ValueError):
    """Invalid graph-memory provider opt-in config draft request."""


def get_graph_memory_provider_spike_opt_in_config_draft(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only opt-in config draft."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        schema = get_graph_memory_provider_spike_opt_in_human_signoff_schema_draft(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftRequestError as exc:
        raise GraphMemoryProviderSpikeOptInConfigDraftRequestError(str(exc)) from exc

    source_status = str(schema.get("status") or "deferred")
    entries = _config_entries(schema)
    mappings = _field_mappings(entries)
    status = _status(source_status, entries)
    summary = _summary(sid, source_status, status, schema, entries, mappings)
    config_draft = _config_draft(status, summary)
    adapter_boundary = _adapter_boundary(status, entries)
    decision = _decision(status, summary)
    manifest = _manifest(
        generated_at,
        summary,
        config_draft,
        adapter_boundary,
        decision,
        entries,
        mappings,
        schema,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_opt_in_config_draft",
        "status": status,
        "story_slug": sid,
        "source_kind": schema.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "config_draft": config_draft,
        "adapter_boundary": adapter_boundary,
        "decision": decision,
        "config_entries": entries,
        "field_mappings": mappings,
        "draft_materials": _draft_materials(status, entries),
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": _no_go_conditions(schema, entries),
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(schema, entries),
        "boundaries": [
            "只读生成 opt-in config draft，不保存配置、不写项目 artifact。",
            "配置草案只描述本地字段映射，不能创建真实 provider 配置。",
            "不读取、不返回、不记录明文 Key；凭据只能在后续显式切片中人工处理。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeOptInConfigDraftRequestError("invalid slug")
    return sid


def _status(source_status: str, entries: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_human_signoff_schema_draft" and entries:
        return "ready_for_opt_in_config_draft"
    if source_status in {"needs_more_evidence", "blocked"}:
        return source_status
    return "deferred"


def _config_entries(schema: dict[str, Any]) -> list[dict[str, Any]]:
    if schema.get("status") != "ready_for_human_signoff_schema_draft":
        return []

    entries: list[dict[str, Any]] = []
    for section in schema.get("schema_sections") or []:
        provider_id = str(section.get("provider_id") or "unknown")
        fields = list(section.get("schema_fields") or [])
        entries.append(
            {
                "id": f"opt-in-config-{provider_id}",
                "provider_id": provider_id,
                "provider_label": str(section.get("provider_label") or "unknown"),
                "service_target": str(section.get("service_target") or "unknown"),
                "source_schema_section_id": str(section.get("id") or ""),
                "fixture_id": str(section.get("fixture_id") or ""),
                "eval_id": str(section.get("eval_id") or ""),
                "config_key": f"graph_memory.providers.{provider_id}",
                "config_format": "draft_json",
                "storage_policy": "not_saved",
                "save_allowed": False,
                "config_saved": False,
                "plaintext_key_required": False,
                "plaintext_key_returned": False,
                "real_provider_config_allowed": False,
                "mock_compatible": True,
                "field_mapping_count": len(fields),
                "required_signoff_count": sum(
                    1 for field in fields if field.get("required", True)
                ),
                "draft_values": {
                    "enabled": False,
                    "mode": "local_mock_only_until_explicit_opt_in",
                    "provider_id": provider_id,
                    "service_target": str(section.get("service_target") or "unknown"),
                    "credential_reference": "manual_reference_required_later",
                    "budget_policy": "manual_budget_required_later",
                    "rollback_policy": "manual_rollback_required_later",
                },
                "field_mappings": [_entry_field_mapping(provider_id, field) for field in fields],
            }
        )
    return entries


def _entry_field_mapping(provider_id: str, field: dict[str, Any]) -> dict[str, Any]:
    field_name = str(field.get("field") or "unknown")
    return {
        "id": f"config-map-{provider_id}-{field_name}",
        "provider_id": provider_id,
        "field": field_name,
        "label": str(field.get("label") or field_name),
        "source_schema_field_id": str(field.get("id") or ""),
        "source_decision_ledger_row_id": str(
            field.get("source_decision_ledger_row_id") or ""
        ),
        "target_config_path": f"graph_memory.providers.{provider_id}.signoff.{field_name}",
        "required": bool(field.get("required", True)),
        "saved": False,
        "storage_policy": "not_saved",
    }


def _field_mappings(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [mapping for entry in entries for mapping in entry["field_mappings"]]


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    schema: dict[str, Any],
    entries: list[dict[str, Any]],
    mappings: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_human_signoff_schema_status": source_status,
        "source_schema_draft_status": str(
            (schema.get("schema_draft") or {}).get("status") or "unknown"
        ),
        "status": status,
        "provider_count": len(entries),
        "config_entry_count": len(entries),
        "field_mapping_count": len(mappings),
        "writes_artifacts": False,
        "config_saved": False,
        "signoff_saved": False,
        "external_services_required": False,
        "provider_calls": False,
        "real_provider_config_allowed": False,
        "uses_graphrag": False,
        "uses_zep": False,
        "uses_vector_store": False,
        "uses_reranker": False,
        "uses_embedding_provider": False,
        "plaintext_key_returned": False,
    }


def _config_draft(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    ready = status == "ready_for_opt_in_config_draft"
    return {
        "id": "graph_memory_provider_spike_opt_in_config_draft",
        "status": "opt_in_config_draft_ready" if ready else status,
        "ready": ready,
        "draft_version": "draft-v1",
        "config_entry_count": summary["config_entry_count"],
        "field_mapping_count": summary["field_mapping_count"],
        "save_allowed": False,
        "config_saved": False,
        "mock_compatible": ready,
        "real_provider_config_allowed": False,
        "reason": (
            "配置草案已可读；真实 provider 仍禁止配置。"
            if ready
            else "human signoff schema draft 尚不足以生成配置草案。"
        ),
    }


def _adapter_boundary(status: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": "graph_memory_provider_spike_adapter_boundary",
        "status": "adapter_boundary_draft_ready" if entries else status,
        "provider_count": len(entries),
        "mock_adapter_allowed": bool(entries),
        "real_provider_adapter_allowed": False,
        "external_service_calls_allowed": False,
        "plaintext_key_allowed": False,
        "writes_artifacts": False,
        "allowed_modes": ["local_mock_only"] if entries else [],
        "blocked_modes": [
            "real_provider_call",
            "production_vector_store",
            "graphrag_sync",
            "zep_sync",
        ],
    }


def _decision(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    if status == "ready_for_opt_in_config_draft":
        return {
            "status": "opt_in_config_draft_ready_real_provider_still_blocked",
            "recommendation": "配置草案已生成；下一步只定义本地 provider contract 与 adapter 边界。",
            "next_slice": "Graph Memory Provider Spike Local Provider Contract / Adapter Boundary",
            "config_entry_count": summary["config_entry_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 human signoff schema draft，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Opt-in Config Draft",
        "config_entry_count": summary["config_entry_count"],
    }


def _draft_materials(status: str, entries: list[dict[str, Any]]) -> list[str]:
    if status != "ready_for_opt_in_config_draft":
        return []
    materials = [
        f"配置草案：{entry['service_target']} / {entry['provider_id']}"
        for entry in entries
    ]
    materials.append("所有配置项仅为草案，不保存到本地文件。")
    return _dedupe(materials)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_opt_in_config_draft":
        return []
    return [
        "人工确认 config draft 没有写入配置文件。",
        "人工确认草案不要求明文 Key。",
        "人工确认真实 provider 仍需另开显式 opt-in spike。",
    ]


def _no_go_conditions(schema: dict[str, Any], entries: list[dict[str, Any]]) -> list[str]:
    items = list(schema.get("no_go_conditions") or [])
    for entry in entries:
        items.append(
            f"{entry['service_target']} config draft 未保存，不能启用真实 provider。"
        )
    items.extend(
        [
            "不能把 config draft 当成真实 provider 配置。",
            "不能保存明文 Key、签收值或最终启用结论。",
            "不能把配置草案写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(schema: dict[str, Any], entries: list[dict[str, Any]]) -> list[str]:
    warnings = list(schema.get("warnings") or [])
    if not entries:
        warnings.append("没有可生成 opt-in config draft 的 human signoff schema。")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    config_draft: dict[str, Any],
    adapter_boundary: dict[str, Any],
    decision: dict[str, Any],
    entries: list[dict[str, Any]],
    mappings: list[dict[str, Any]],
    schema: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "config_draft": config_draft,
        "adapter_boundary": adapter_boundary,
        "decision": decision,
        "config_entries": entries,
        "field_mappings": mappings,
        "source_human_signoff_schema": {
            "version": schema.get("version"),
            "status": schema.get("status"),
            "schema_draft": schema.get("schema_draft"),
        },
        "contract": {
            "writes_artifacts": False,
            "config_saved": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_opt_in_config_draft":
        return [
            "人工阅读 config draft，确认字段映射和本地 adapter 边界。",
            "进入 local provider contract / adapter boundary，只定义接口，不接真实服务。",
        ]
    return [
        "保持 config draft 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 human signoff schema draft 就绪后再生成配置草案。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

"""Graph Memory Provider Spike Opt-in Human Signoff Schema Draft MVP.

This read-only draft turns the final readiness summary into a human signoff
schema. It does not save signoffs, write project artifacts, create provider
configs, read keys, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_opt_in_final_readiness_summary import (
    GraphMemoryProviderSpikeOptInFinalReadinessSummaryRequestError,
    get_graph_memory_provider_spike_opt_in_final_readiness_summary,
)

VERSION = "graph-memory-provider-spike-opt-in-human-signoff-schema-draft-mvp"


class GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftRequestError(ValueError):
    """Invalid graph-memory provider opt-in human signoff schema draft request."""


def get_graph_memory_provider_spike_opt_in_human_signoff_schema_draft(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return deterministic read-only human signoff schema draft."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        final = get_graph_memory_provider_spike_opt_in_final_readiness_summary(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeOptInFinalReadinessSummaryRequestError as exc:
        raise GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftRequestError(
            str(exc)
        ) from exc

    source_status = str(final.get("status") or "deferred")
    schema_sections = _schema_sections(final)
    schema_fields = _schema_fields(schema_sections)
    status = _status(source_status, schema_fields)
    summary = _summary(sid, source_status, status, final, schema_sections, schema_fields)
    schema_draft = _schema_draft(status, summary)
    decision = _decision(status, summary)
    schema_materials = _schema_materials(status, schema_sections)
    no_go_conditions = _no_go_conditions(final, schema_sections)
    manifest = _manifest(
        generated_at,
        summary,
        schema_draft,
        decision,
        schema_sections,
        schema_fields,
        final,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_opt_in_human_signoff_schema_draft",
        "status": status,
        "story_slug": sid,
        "source_kind": final.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "schema_draft": schema_draft,
        "decision": decision,
        "schema_sections": schema_sections,
        "schema_fields": schema_fields,
        "validation_rules": _validation_rules(status),
        "schema_materials": schema_materials,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(final, schema_fields),
        "boundaries": [
            "只读生成 human signoff schema draft，不保存签名、签收值或最终结论。",
            "签收 schema 草案只能定义人工字段和校验规则，不能创建真实 provider 配置。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftRequestError(
            "invalid slug"
        )
    return sid


def _status(source_status: str, fields: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_opt_in_final_readiness_summary" and fields:
        return "ready_for_human_signoff_schema_draft"
    if source_status in {"needs_more_evidence", "blocked"}:
        return source_status
    return "deferred"


def _schema_sections(final: dict[str, Any]) -> list[dict[str, Any]]:
    if final.get("status") != "ready_for_opt_in_final_readiness_summary":
        return []

    sections: list[dict[str, Any]] = []
    for row in final.get("readiness_rows") or []:
        fields = [_schema_field(row, field) for field in row.get("unresolved_signoff_fields") or []]
        sections.append(
            {
                "id": f"human-signoff-section-{row.get('provider_id') or 'unknown'}",
                "provider_id": str(row.get("provider_id") or "unknown"),
                "provider_label": str(row.get("provider_label") or "unknown"),
                "service_target": str(row.get("service_target") or "unknown"),
                "source_final_readiness_row_id": str(row.get("id") or ""),
                "source_decision_ledger_row_id": str(
                    row.get("source_decision_ledger_row_id") or ""
                ),
                "fixture_id": str(row.get("fixture_id") or ""),
                "eval_id": str(row.get("eval_id") or ""),
                "schema_fields": fields,
                "required_field_count": sum(1 for field in fields if field["required"]),
                "save_allowed": False,
                "signoff_saved": False,
                "real_provider_config_allowed": False,
                "section_notes": _section_notes(row, fields),
            }
        )
    return sections


def _schema_field(row: dict[str, Any], field: dict[str, Any]) -> dict[str, Any]:
    provider_id = str(row.get("provider_id") or field.get("provider_id") or "unknown")
    field_name = str(field.get("field") or field.get("id") or "unknown")
    return {
        "id": f"human-signoff-{provider_id}-{field_name}",
        "provider_id": provider_id,
        "service_target": str(row.get("service_target") or field.get("service_target") or "unknown"),
        "field": field_name,
        "label": str(field.get("label") or field_name),
        "value": field.get("value"),
        "type": "human_text",
        "required": bool(field.get("required", True)),
        "saved": False,
        "input_storage": "not_saved",
        "source_final_readiness_field_id": str(field.get("id") or ""),
        "source_final_readiness_row_id": str(row.get("id") or ""),
        "source_decision_ledger_row_id": str(
            field.get("source_decision_ledger_row_id")
            or row.get("source_decision_ledger_row_id")
            or ""
        ),
        "validation_rule": {
            "type": "required_non_empty_text",
            "min_length": 1,
            "max_length": 2000,
            "rejects_plaintext_keys": True,
        },
        "review_prompt": f"人工确认：{str(field.get('label') or field_name)}",
    }


def _schema_fields(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [field for section in sections for field in section["schema_fields"]]


def _section_notes(row: dict[str, Any], fields: list[dict[str, Any]]) -> list[str]:
    notes = [
        "本节只定义人工签收字段，不保存输入值。",
        "真实 provider 配置仍禁止。",
    ]
    if fields:
        notes.append(f"{len(fields)} 个字段需要人工确认。")
    notes.extend(row.get("readiness_notes") or [])
    return _dedupe(notes)


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    final: dict[str, Any],
    sections: list[dict[str, Any]],
    fields: list[dict[str, Any]],
) -> dict[str, Any]:
    final_summary = final.get("summary") or {}
    return {
        "story_slug": story_slug,
        "source_final_readiness_status": source_status,
        "source_final_readiness_summary_status": str(
            (final.get("final_readiness_summary") or {}).get("status") or "unknown"
        ),
        "status": status,
        "provider_count": len(sections),
        "schema_section_count": len(sections),
        "schema_field_count": len(fields),
        "required_field_count": sum(1 for field in fields if field["required"]),
        "unresolved_signoff_field_count": int(
            final_summary.get("unresolved_signoff_field_count") or len(fields)
        ),
        "writes_artifacts": False,
        "signoff_saved": False,
        "approval_saved": False,
        "final_decision_saved": False,
        "external_services_required": False,
        "provider_calls": False,
        "real_provider_ready": False,
        "real_provider_config_allowed": False,
        "uses_graphrag": False,
        "uses_zep": False,
        "uses_vector_store": False,
        "uses_reranker": False,
        "uses_embedding_provider": False,
        "plaintext_key_returned": False,
    }


def _schema_draft(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    if status == "ready_for_human_signoff_schema_draft":
        return {
            "id": "graph_memory_provider_spike_opt_in_human_signoff_schema_draft",
            "status": "human_signoff_schema_draft_ready",
            "ready": True,
            "schema_version": "draft-v1",
            "save_allowed": False,
            "signoff_saved": False,
            "real_provider_config_allowed": False,
            "field_count": summary["schema_field_count"],
            "required_field_count": summary["required_field_count"],
            "reason": "签收 schema 草案已可读；真实 provider 仍禁止配置。",
        }
    return {
        "id": "graph_memory_provider_spike_opt_in_human_signoff_schema_draft",
        "status": status,
        "ready": False,
        "schema_version": "draft-v1",
        "save_allowed": False,
        "signoff_saved": False,
        "real_provider_config_allowed": False,
        "field_count": summary["schema_field_count"],
        "required_field_count": summary["required_field_count"],
        "reason": "final readiness summary 尚不足以生成签收 schema 草案。",
    }


def _decision(status: str, summary: dict[str, Any]) -> dict[str, Any]:
    if status == "ready_for_human_signoff_schema_draft":
        return {
            "status": "human_signoff_schema_draft_ready_real_provider_still_blocked",
            "recommendation": "签收 schema 草案已生成；真实 provider 仍需显式 opt-in spike。",
            "next_slice": "Graph Memory Provider Spike Opt-in Config Draft",
            "schema_field_count": summary["schema_field_count"],
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 final readiness summary，不接真实 provider。",
        "next_slice": "Graph Memory Provider Spike Opt-in Human Signoff Schema Draft",
        "schema_field_count": summary["schema_field_count"],
    }


def _validation_rules(status: str) -> list[dict[str, Any]]:
    if status != "ready_for_human_signoff_schema_draft":
        return []
    return [
        {
            "id": "required-non-empty-text",
            "type": "required_non_empty_text",
            "description": "必填字段必须由人工填写非空文本。",
            "rejects_plaintext_keys": True,
        },
        {
            "id": "no-auto-provider-config",
            "type": "manual_gate_only",
            "description": "schema 通过不代表允许创建真实 provider 配置。",
            "real_provider_config_allowed": False,
        },
    ]


def _schema_materials(status: str, sections: list[dict[str, Any]]) -> list[str]:
    if status != "ready_for_human_signoff_schema_draft":
        return []
    materials: list[str] = []
    for section in sections:
        materials.append(
            f"签收 schema 草案：{section['service_target']} / {section['provider_id']}"
        )
        materials.append(f"必填字段：{section['required_field_count']} 项")
    materials.append("所有签收字段仅定义 schema，不保存输入值。")
    return _dedupe(materials)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_human_signoff_schema_draft":
        return []
    return [
        "人工确认 schema draft 只定义字段，不保存签收结果。",
        "人工确认每个 provider 的风险签收、回滚确认和成本确认字段齐全。",
        "人工确认真实 provider 仍需另开显式 opt-in spike。",
    ]


def _no_go_conditions(
    final: dict[str, Any],
    sections: list[dict[str, Any]],
) -> list[str]:
    items = list(final.get("no_go_conditions") or [])
    for section in sections:
        items.append(
            f"{section['service_target']} signoff schema 仍未保存人工签收，不能启用真实 provider。"
        )
    items.extend(
        [
            "不能把 schema draft 当成真实签收记录。",
            "不能保存签名、风险签收、回滚确认或最终结论。",
            "不能要求真实付费 Key 或外部账号才能生成 schema draft。",
            "不能把 schema draft 写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(final: dict[str, Any], fields: list[dict[str, Any]]) -> list[str]:
    warnings = list(final.get("warnings") or [])
    if not fields:
        warnings.append("没有可生成 human signoff schema draft 的 final readiness summary。")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    schema_draft: dict[str, Any],
    decision: dict[str, Any],
    sections: list[dict[str, Any]],
    fields: list[dict[str, Any]],
    final: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "schema_draft": schema_draft,
        "decision": decision,
        "schema_sections": sections,
        "schema_fields": fields,
        "source_final_readiness_summary": {
            "version": final.get("version"),
            "status": final.get("status"),
            "final_readiness_summary": final.get("final_readiness_summary"),
        },
        "contract": {
            "writes_artifacts": False,
            "signoff_saved": False,
            "approval_saved": False,
            "final_decision_saved": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_ready": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_human_signoff_schema_draft":
        return [
            "人工阅读 signoff schema draft，确认字段定义是否覆盖风险签收、成本、隐私和回滚。",
            "若需要保存签收，只能另开显式 opt-in 写入切片，不能由本草案自动保存。",
        ]
    if status == "blocked":
        return [
            "先修复 final readiness blockers，再重新生成 human signoff schema draft。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 human signoff schema draft 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 final readiness summary 就绪后再生成 schema draft。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

"""Graph Memory Provider Spike Mock Result Report MVP.

This read-only report fills the dry-run result template with deterministic
mock replay evidence. It does not persist manual results, create provider
configs, read keys, write artifacts, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_offline_shadow_replay_report import (
    GraphMemoryOfflineShadowReplayReportRequestError,
    get_graph_memory_offline_shadow_replay_report,
)
from living_novel_engine.service.graph_memory_provider_spike_dry_run_result_template import (
    GraphMemoryProviderSpikeDryRunResultTemplateRequestError,
    get_graph_memory_provider_spike_dry_run_result_template,
)

VERSION = "graph-memory-provider-spike-mock-result-report-mvp"


class GraphMemoryProviderSpikeMockResultReportRequestError(ValueError):
    """Invalid graph-memory mock result report request, mapped to HTTP 400."""


def get_graph_memory_provider_spike_mock_result_report(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only filled mock result report."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        template = get_graph_memory_provider_spike_dry_run_result_template(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
        replay_report = get_graph_memory_offline_shadow_replay_report(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except (
        GraphMemoryProviderSpikeDryRunResultTemplateRequestError,
        GraphMemoryOfflineShadowReplayReportRequestError,
    ) as exc:
        raise GraphMemoryProviderSpikeMockResultReportRequestError(str(exc)) from exc

    source_status = str(template.get("status") or "deferred")
    records = _mock_result_records(template, replay_report)
    status = _status(source_status, records)
    summary = _summary(sid, source_status, status, records, template, replay_report)
    report_gate = _report_gate(status, records)
    decision = _decision(status, records)
    no_go_conditions = _no_go_conditions(template, replay_report)
    manifest = _manifest(
        generated_at,
        summary,
        report_gate,
        decision,
        records,
        template,
        replay_report,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_mock_result_report",
        "status": status,
        "story_slug": sid,
        "source_kind": template.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "report_gate": report_gate,
        "decision": decision,
        "mock_result_records": records,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(template, replay_report, records),
        "boundaries": [
            "只读生成 provider spike mock result report，不保存人工结果，不写项目 artifact。",
            "报告只用既有 mock replay 证据填充模板，不自动连接外部服务或执行真实 provider 调用。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeMockResultReportRequestError("invalid slug")
    return sid


def _status(source_status: str, records: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_manual_result_recording" and records:
        return "ready_for_manual_review"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _mock_result_records(
    template: dict[str, Any],
    replay_report: dict[str, Any],
) -> list[dict[str, Any]]:
    if template.get("status") != "ready_for_manual_result_recording":
        return []
    cases_by_provider: dict[str, list[dict[str, Any]]] = {}
    for case in replay_report.get("case_results") or []:
        cases_by_provider.setdefault(str(case.get("provider_id") or "unknown"), []).append(
            case
        )

    records: list[dict[str, Any]] = []
    for provider in template.get("provider_result_templates") or []:
        if provider.get("status") != "manual_result_template_ready":
            continue
        provider_id = str(provider.get("provider_id") or "unknown")
        source_case = (cases_by_provider.get(provider_id) or [{}])[0]
        field_values = _field_values(provider, source_case)
        manual_decision = _manual_decision(source_case)
        records.append(
            {
                "id": f"mock-result-{provider_id}-{source_case.get('eval_id') or provider.get('fixture_id')}",
                "status": "mock_filled_result_ready",
                "provider_id": provider_id,
                "provider_label": str(provider.get("provider_label") or provider_id),
                "service_target": str(provider.get("service_target") or provider_id),
                "fixture_id": str(provider.get("fixture_id") or ""),
                "source_case_id": str(source_case.get("source_case_id") or ""),
                "eval_id": str(source_case.get("eval_id") or ""),
                "template_field_count": len(provider.get("result_fields") or []),
                "field_values": field_values,
                "manual_decision": manual_decision,
                "gain_summary": _gain_summary(provider, source_case),
                "risk_summary": _risk_summary(provider, source_case),
                "review_summary": _review_summary(provider, source_case, manual_decision),
                "pause_or_upgrade_decision": _decision_detail(manual_decision),
                "evidence_refs": _evidence_refs(provider, source_case),
                "no_go_conditions": list(provider.get("no_go_conditions") or []),
                "recommendation": "人工复核 mock result 后，再决定是否另开真实 opt-in spike。",
            }
        )
    return records


def _field_values(
    provider: dict[str, Any],
    source_case: dict[str, Any],
) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for field in provider.get("result_fields") or []:
        field_id = str(field.get("id") or "")
        values.append(
            {
                "field_id": field_id,
                "label": str(field.get("label") or field_id),
                "value": _value_for_field(field_id, provider, source_case),
                "source": "mock_replay_report",
            }
        )
    return values


def _value_for_field(
    field_id: str,
    provider: dict[str, Any],
    source_case: dict[str, Any],
) -> Any:
    provider_label = str(provider.get("provider_label") or provider.get("provider_id") or "")
    if field_id == "baseline_retrieval_summary":
        return str(source_case.get("baseline_chain") or "BM25 + canon ledger + entity aliases")
    if field_id == "provider_candidate_summary":
        return str(
            (source_case.get("mock_delta") or {}).get("candidate_summary")
            or f"{provider_label} mock 结果仅用于人工复核。"
        )
    if field_id == "relationship_gain":
        return "候选收益：关系链可能改善，需人工核对实体误连。"
    if field_id == "causal_chain_gain":
        return "候选收益：因果链可能改善，需人工核对伏笔前后文。"
    if field_id == "state_tracking_gain":
        return "候选收益：状态链可能改善，需人工核对 state_snapshot 真源。"
    if field_id == "false_positive_risk":
        return str(source_case.get("risk_assessment") or "需要人工复核误召回风险。")
    if field_id == "privacy_scope_confirmed":
        return "是：mock report 不上传文本、不读取密钥。"
    if field_id == "cost_guardrail_confirmed":
        return "是：mock report 不要求真实付费 Key 或外部账号。"
    if field_id == "rollback_verified":
        return "是：失败时继续使用本地 BM25 + canon ledger + aliases。"
    if field_id == "manual_decision":
        return _manual_decision(source_case)
    if field_id == "evidence_refs":
        return _evidence_refs(provider, source_case)
    return "待人工填写。"


def _manual_decision(source_case: dict[str, Any]) -> str:
    if source_case.get("status") == "mock_candidate_gain":
        return "collect_more_evidence"
    return "pause_no_stable_gain"


def _gain_summary(provider: dict[str, Any], source_case: dict[str, Any]) -> str:
    return str(
        source_case.get("gain_assessment")
        or f"{provider.get('provider_label') or '候选 provider'} 需要继续补 mock 证据。"
    )


def _risk_summary(provider: dict[str, Any], source_case: dict[str, Any]) -> str:
    return str(
        source_case.get("risk_assessment")
        or f"{provider.get('provider_label') or '候选 provider'} 仍需人工复核风险。"
    )


def _review_summary(
    provider: dict[str, Any],
    source_case: dict[str, Any],
    manual_decision: str,
) -> str:
    label = str(provider.get("provider_label") or provider.get("provider_id") or "候选")
    eval_id = str(source_case.get("eval_id") or "当前 fixture")
    return (
        f"{label} / {eval_id} 已生成 mock 填充样例；当前结论为 {manual_decision}，"
        "不能据此自动创建真实 provider 配置。"
    )


def _decision_detail(manual_decision: str) -> dict[str, str]:
    labels = {
        "collect_more_evidence": "继续收集证据",
        "pause_no_stable_gain": "暂停：收益不稳定",
        "upgrade_manual_opt_in_spike": "另开真实 opt-in spike",
    }
    return {
        "id": manual_decision,
        "label": labels.get(manual_decision, manual_decision),
        "description": "mock result 只能辅助人工复核，不能自动启用真实 provider。",
    }


def _evidence_refs(provider: dict[str, Any], source_case: dict[str, Any]) -> list[str]:
    refs = [str(item) for item in provider.get("evidence_refs") or []]
    for key in ("source_case_id", "eval_id"):
        value = str(source_case.get(key) or "")
        if value:
            refs.append(value)
    return _dedupe(refs)


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    records: list[dict[str, Any]],
    template: dict[str, Any],
    replay_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_result_template_status": source_status,
        "source_mock_replay_status": str(replay_report.get("status") or "deferred"),
        "status": status,
        "provider_result_count": len(template.get("provider_result_templates") or []),
        "filled_record_count": len(records),
        "candidate_gain_count": len(
            [item for item in records if item.get("manual_decision") == "collect_more_evidence"]
        ),
        "manual_review_required_count": len(records),
        "writes_artifacts": False,
        "result_write_allowed": False,
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


def _report_gate(status: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    if status == "ready_for_manual_review" and records:
        return {
            "id": "graph_memory_provider_spike_mock_result_report_gate",
            "status": "mock_result_report_ready",
            "passed": True,
            "reason": "结果模板已用 mock replay 证据填充，可进入人工复核。",
            "filled_record_count": len(records),
        }
    return {
        "id": "graph_memory_provider_spike_mock_result_report_gate",
        "status": status,
        "passed": False,
        "reason": "结果模板或 mock replay 证据不足，暂不生成填充样例。",
        "filled_record_count": len(records),
    }


def _decision(status: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    if status == "ready_for_manual_review":
        return {
            "status": "mock_result_review_required_no_real_config",
            "recommendation": "人工复核填充样例；真实 provider 配置仍需另行显式确认。",
            "filled_record_count": len(records),
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 result template 或 mock replay 证据，不接真实 provider。",
        "filled_record_count": len(records),
    }


def _no_go_conditions(
    template: dict[str, Any],
    replay_report: dict[str, Any],
) -> list[str]:
    items = list(template.get("no_go_conditions") or [])
    items.extend(replay_report.get("no_go_conditions") or [])
    items.extend(
        [
            "不能把 mock result report 当成真实 provider 配置许可。",
            "不能要求真实付费 Key 或外部账号才能生成 mock result report。",
            "不能把 mock result 写回 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        ]
    )
    return _dedupe(items)


def _warnings(
    template: dict[str, Any],
    replay_report: dict[str, Any],
    records: list[dict[str, Any]],
) -> list[str]:
    warnings = list(template.get("warnings") or [])
    warnings.extend(replay_report.get("warnings") or [])
    if not records:
        warnings.append("没有可填充的 mock result record，先补 result template 或 replay report。")
    return _dedupe(warnings)


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_manual_review":
        return []
    return [
        "人工复核每条 mock result 是否对应真实长篇痛点。",
        "人工复核收益是否超过误召回、隐私、成本和回滚复杂度。",
        "人工确认 mock result 不能直接升级为真实 provider 配置。",
    ]


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    report_gate: dict[str, Any],
    decision: dict[str, Any],
    records: list[dict[str, Any]],
    template: dict[str, Any],
    replay_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "report_gate": report_gate,
        "decision": decision,
        "mock_result_records": records,
        "source_result_template": {
            "version": template.get("version"),
            "status": template.get("status"),
            "template": template.get("template"),
        },
        "source_mock_replay_report": {
            "version": replay_report.get("version"),
            "status": replay_report.get("status"),
            "report_gate": replay_report.get("report_gate"),
        },
        "contract": {
            "writes_artifacts": False,
            "result_write_allowed": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_manual_review":
        return [
            "人工复核 mock result report，确认收益、风险和 no-go。",
            "若仍有稳定收益，再另开真实 provider opt-in spike 的人工审批切片。",
        ]
    if status == "blocked":
        return [
            "先补齐 result template blockers，再重新生成 mock result report。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 mock result report 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 result template 和 mock replay report 就绪后再生成填充样例。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

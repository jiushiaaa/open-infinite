"""Graph Memory Provider Spike Dry-run Result Template MVP.

This read-only report turns the manual provider spike runbook into a result
recording template. It does not persist dry-run results, create provider
configs, read keys, write artifacts, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_runbook import (
    GraphMemoryProviderSpikeRunbookRequestError,
    get_graph_memory_provider_spike_runbook,
)

VERSION = "graph-memory-provider-spike-dry-run-result-template-mvp"


class GraphMemoryProviderSpikeDryRunResultTemplateRequestError(ValueError):
    """Invalid graph-memory result template request, mapped to HTTP 400."""


def get_graph_memory_provider_spike_dry_run_result_template(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only manual dry-run result template."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        runbook = get_graph_memory_provider_spike_runbook(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeRunbookRequestError as exc:
        raise GraphMemoryProviderSpikeDryRunResultTemplateRequestError(str(exc)) from exc

    source_status = str(runbook.get("status") or "deferred")
    provider_templates = _provider_result_templates(runbook)
    status = _status(source_status, provider_templates)
    summary = _summary(sid, source_status, status, provider_templates)
    template = _template(status, provider_templates)
    decision = _decision(status, provider_templates)
    no_go_conditions = _no_go_conditions(runbook, provider_templates)
    manifest = _manifest(
        generated_at,
        summary,
        template,
        decision,
        provider_templates,
        runbook,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_dry_run_result_template",
        "status": status,
        "story_slug": sid,
        "source_kind": runbook.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "template": template,
        "decision": decision,
        "provider_result_templates": provider_templates,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(runbook, provider_templates),
        "boundaries": [
            "只读生成 provider spike dry-run 结果记录模板，不保存结果，不写项目 artifact。",
            "模板只指导人工记录，不自动连接外部服务或执行真实 provider 调用。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeDryRunResultTemplateRequestError("invalid slug")
    return sid


def _status(source_status: str, provider_templates: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_manual_dry_run" and provider_templates:
        if any(row["status"] == "blocked" for row in provider_templates):
            return "blocked"
        return "ready_for_manual_result_recording"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _provider_result_templates(runbook: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for provider in runbook.get("provider_runbooks") or []:
        blockers = list(provider.get("blockers") or [])
        status = (
            "manual_result_template_ready"
            if provider.get("status") == "manual_dry_run_ready" and not blockers
            else "blocked"
        )
        rows.append(
            {
                "provider_id": str(provider.get("provider_id") or "unknown"),
                "provider_label": str(provider.get("provider_label") or "unknown"),
                "service_target": str(provider.get("service_target") or "unknown"),
                "status": status,
                "fixture_id": str(provider.get("fixture_id") or ""),
                "source_runbook_status": str(provider.get("status") or "deferred"),
                "source_step_count": len(provider.get("steps") or []),
                "source_case_ids": list(provider.get("source_case_ids") or []),
                "result_fields": [] if blockers else _result_fields(provider),
                "comparison_axes": [] if blockers else _comparison_axes(provider),
                "acceptance_record": [] if blockers else _acceptance_record(provider),
                "pause_or_upgrade_decisions": (
                    [] if blockers else _pause_or_upgrade_decisions(provider)
                ),
                "rollback_confirmation": [] if blockers else _rollback_confirmation(provider),
                "evidence_refs": _evidence_refs(provider),
                "blockers": blockers,
                "no_go_conditions": list(provider.get("no_go_conditions") or []),
                "recommendation": _provider_recommendation(status),
            }
        )
    return rows


def _result_fields(provider: dict[str, Any]) -> list[dict[str, Any]]:
    provider_label = str(provider.get("provider_label") or "候选 provider")
    return [
        _field(
            "baseline_retrieval_summary",
            "本地基线摘要",
            "记录 BM25 + canon ledger + entity aliases 的原始召回结果。",
            "textarea",
        ),
        _field(
            "provider_candidate_summary",
            f"{provider_label} 候选结果摘要",
            "记录 dry-run 候选层给出的关系、因果或状态链补充。",
            "textarea",
        ),
        _field(
            "relationship_gain",
            "关系链收益",
            "说明人物、势力、道具关系是否比本地基线更完整。",
            "score_with_note",
        ),
        _field(
            "causal_chain_gain",
            "因果链收益",
            "说明伏笔、事件前因后果是否被更稳定召回。",
            "score_with_note",
        ),
        _field(
            "state_tracking_gain",
            "状态追踪收益",
            "说明资源、伤势、位置、阵营等状态是否更准确。",
            "score_with_note",
        ),
        _field(
            "false_positive_risk",
            "误召回风险",
            "记录候选层是否引入错误关系、幻觉实体或过期事实。",
            "risk_level",
        ),
        _field(
            "privacy_scope_confirmed",
            "隐私范围确认",
            "确认未上传 holdout_private、明文密钥或不可删除用户文本。",
            "boolean_with_note",
        ),
        _field(
            "cost_guardrail_confirmed",
            "成本边界确认",
            "确认 dry-run 未要求真实付费 Key、外部账号或生产调用。",
            "boolean_with_note",
        ),
        _field(
            "rollback_verified",
            "回滚演练确认",
            "确认关闭候选层后仍能回退到本地检索链路。",
            "boolean_with_note",
        ),
        _field(
            "manual_decision",
            "人工结论",
            "只能选择暂停、继续收集证据或另开真实 opt-in spike。",
            "enum",
            options=[
                "pause_no_go_hit",
                "pause_no_stable_gain",
                "collect_more_evidence",
                "upgrade_manual_opt_in_spike",
            ],
        ),
        _field(
            "evidence_refs",
            "证据引用",
            "填写 fixture id、case id、runbook step id 或人工截图/记录编号。",
            "string_list",
        ),
    ]


def _field(
    field_id: str,
    label: str,
    description: str,
    input_kind: str,
    *,
    options: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": field_id,
        "label": label,
        "description": description,
        "input_kind": input_kind,
        "required": True,
        "options": options or [],
    }


def _comparison_axes(provider: dict[str, Any]) -> list[dict[str, str]]:
    provider_label = str(provider.get("provider_label") or "候选 provider")
    return [
        {
            "id": "baseline_vs_candidate",
            "label": "本地基线 vs 候选层",
            "description": f"比较本地检索与 {provider_label} dry-run 输出的可解释差异。",
        },
        {
            "id": "gain_vs_risk",
            "label": "收益 vs 风险",
            "description": "收益必须覆盖误召回、隐私、成本和回滚复杂度。",
        },
        {
            "id": "manual_acceptance",
            "label": "人工验收",
            "description": "只有人工确认后，才能另开真实 provider opt-in spike。",
        },
    ]


def _acceptance_record(provider: dict[str, Any]) -> list[str]:
    items = list(provider.get("acceptance_checks") or [])
    items.extend(
        [
            "结果记录必须包含本地基线和候选层摘要。",
            "结果记录必须引用 fixture id 和 source case ids。",
            "结果记录必须说明暂停或升级判定，不能默认为接入真实 provider。",
        ]
    )
    return _dedupe(items)


def _pause_or_upgrade_decisions(provider: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "id": "pause_no_go_hit",
            "label": "暂停：命中 no-go",
            "description": "出现真实付费 Key、外部账号、不可删除上传或明文密钥需求时立即暂停。",
        },
        {
            "id": "pause_no_stable_gain",
            "label": "暂停：收益不稳定",
            "description": "候选层没有稳定优于 BM25 + canon ledger + aliases 时暂停。",
        },
        {
            "id": "collect_more_evidence",
            "label": "继续收集证据",
            "description": "样本不足或人工结论不一致时，回到失败样本/fixture 链路补证据。",
        },
        {
            "id": "upgrade_manual_opt_in_spike",
            "label": "另开真实 opt-in spike",
            "description": "只有 no-go 未命中、收益明确、人工确认后才能另开真实 provider spike。",
        },
    ]


def _rollback_confirmation(provider: dict[str, Any]) -> list[str]:
    items = list(provider.get("rollback_steps") or [])
    items.append("确认本次只是结果模板，不产生可回滚项目 artifact。")
    return _dedupe(items)


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    provider_templates: list[dict[str, Any]],
) -> dict[str, Any]:
    ready_count = sum(
        1 for item in provider_templates if item["status"] == "manual_result_template_ready"
    )
    blocked_count = sum(1 for item in provider_templates if item["status"] == "blocked")
    field_count = sum(len(item.get("result_fields") or []) for item in provider_templates)
    return {
        "story_slug": story_slug,
        "source_runbook_status": source_status,
        "status": status,
        "provider_template_count": len(provider_templates),
        "ready_provider_count": ready_count,
        "blocked_provider_count": blocked_count,
        "required_result_field_count": field_count,
        "writes_artifacts": False,
        "external_services_required": False,
        "provider_calls": False,
        "real_provider_config_allowed": False,
        "result_write_allowed": False,
        "uses_graphrag": False,
        "uses_zep": False,
        "uses_vector_store": False,
        "uses_reranker": False,
        "uses_embedding_provider": False,
        "plaintext_key_returned": False,
    }


def _template(
    status: str,
    provider_templates: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": "graph_memory_provider_spike_dry_run_result_template",
        "title": "Graph Memory Provider Spike 人工 dry-run 结果记录模板",
        "status": status,
        "manual_only": True,
        "result_write_allowed": False,
        "real_provider_config_allowed": False,
        "provider_count": len(provider_templates),
        "required_result_field_count": sum(
            len(item.get("result_fields") or []) for item in provider_templates
        ),
        "objective": "把人工 dry-run 后的对比、验收、暂停和升级判定固定为可复核记录字段。",
    }


def _decision(
    status: str,
    provider_templates: list[dict[str, Any]],
) -> dict[str, Any]:
    if status == "ready_for_manual_result_recording":
        return {
            "status": "result_template_ready_no_real_config",
            "recommendation": "可以人工使用结果模板记录 dry-run；真实 provider 配置仍需另行显式确认。",
            "provider_count": len(provider_templates),
        }
    if status == "blocked":
        return {
            "status": "blocked_before_result_recording",
            "recommendation": "先补齐 runbook blockers，不记录 dry-run 结果模板。",
            "provider_count": len(provider_templates),
        }
    return {
        "status": "deferred",
        "recommendation": "继续补 runbook 证据，不记录结果模板，不创建真实 provider 配置。",
        "provider_count": len(provider_templates),
    }


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_manual_result_recording":
        return []
    return [
        "人工执行 runbook 后，再填写结果模板；模板本身不保存项目 artifact。",
        "每个 provider 必须同时记录本地基线、候选输出、收益、风险和证据引用。",
        "人工结论只能是暂停、继续收集证据或另开真实 opt-in spike，不能自动接入 provider。",
    ]


def _no_go_conditions(
    runbook: dict[str, Any],
    provider_templates: list[dict[str, Any]],
) -> list[str]:
    items = list(runbook.get("no_go_conditions") or [])
    for row in provider_templates:
        items.extend(row.get("no_go_conditions") or [])
        for decision in row.get("pause_or_upgrade_decisions") or []:
            if decision["id"].startswith("pause_"):
                items.append(decision["description"])
    items.extend(
        [
            "不能把结果模板当成真实 provider 配置许可。",
            "不能要求真实付费 Key 或外部账号才能填写结果模板。",
            "不能在结果模板阶段上传 holdout_private 或明文密钥。",
        ]
    )
    return _dedupe(items)


def _warnings(
    runbook: dict[str, Any],
    provider_templates: list[dict[str, Any]],
) -> list[str]:
    warnings = list(runbook.get("warnings") or [])
    if not provider_templates:
        warnings.append("没有可生成结果模板的 provider runbook，结果记录暂缓。")
    for row in provider_templates:
        for blocker in row.get("blockers") or []:
            warnings.append(f"{row['provider_label']} result template blocked：{blocker}")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    template: dict[str, Any],
    decision: dict[str, Any],
    provider_templates: list[dict[str, Any]],
    runbook: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "template": template,
        "decision": decision,
        "provider_result_templates": provider_templates,
        "source_runbook": {
            "version": runbook.get("version"),
            "status": runbook.get("status"),
            "runbook": runbook.get("runbook"),
        },
        "contract": {
            "writes_artifacts": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_config_allowed": False,
            "result_write_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_manual_result_recording":
        return [
            "人工执行 runbook 后，按结果模板记录证据、收益、风险和结论。",
            "若 no-go 未命中且收益明确，再另开真实 provider opt-in spike。",
        ]
    if status == "blocked":
        return [
            "先补齐 runbook blockers，再重新生成结果模板。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    if status == "needs_more_evidence":
        return [
            "先补 runbook 所需证据和人工验收项。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 dry-run 结果模板暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 runbook 就绪后再生成结果模板。",
    ]


def _evidence_refs(provider: dict[str, Any]) -> list[str]:
    refs = [str(item) for item in provider.get("evidence_refs") or []]
    fixture_id = str(provider.get("fixture_id") or "")
    if fixture_id:
        refs.insert(0, fixture_id)
    return _dedupe(refs)


def _provider_recommendation(status: str) -> str:
    if status == "manual_result_template_ready":
        return "可以人工填写 dry-run 结果模板；真实配置仍需另行显式确认。"
    return "先补齐 runbook blockers。"


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

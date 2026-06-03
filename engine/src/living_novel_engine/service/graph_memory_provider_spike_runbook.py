"""Graph Memory Provider Spike Runbook MVP.

This read-only report turns the provider spike readiness gate into a manual
opt-in dry-run SOP. It does not create provider configs, read keys, write
artifacts, or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_readiness_gate import (
    GraphMemoryProviderSpikeReadinessGateRequestError,
    get_graph_memory_provider_spike_readiness_gate,
)

VERSION = "graph-memory-provider-spike-runbook-mvp"


class GraphMemoryProviderSpikeRunbookRequestError(ValueError):
    """Invalid graph-memory provider runbook request, mapped to HTTP 400."""


def get_graph_memory_provider_spike_runbook(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only manual provider spike runbook."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        readiness = get_graph_memory_provider_spike_readiness_gate(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeReadinessGateRequestError as exc:
        raise GraphMemoryProviderSpikeRunbookRequestError(str(exc)) from exc

    source_status = str(readiness.get("status") or "deferred")
    provider_runbooks = _provider_runbooks(readiness)
    status = _status(source_status, provider_runbooks)
    summary = _summary(sid, source_status, status, provider_runbooks)
    runbook = _runbook(status, provider_runbooks)
    decision = _decision(status, provider_runbooks)
    no_go_conditions = _no_go_conditions(readiness, provider_runbooks)
    manifest = _manifest(
        generated_at,
        summary,
        runbook,
        decision,
        provider_runbooks,
        readiness,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_runbook",
        "status": status,
        "story_slug": sid,
        "source_kind": readiness.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "runbook": runbook,
        "decision": decision,
        "provider_runbooks": provider_runbooks,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(readiness, provider_runbooks),
        "boundaries": [
            "只读生成 provider spike runbook，不创建 provider 配置，不写项目 artifact。",
            "runbook 只指导人工 dry-run，不自动连接外部服务或执行真实 provider 调用。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeRunbookRequestError("invalid slug")
    return sid


def _status(source_status: str, provider_runbooks: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_manual_opt_in_review" and provider_runbooks:
        if any(row["status"] == "blocked" for row in provider_runbooks):
            return "blocked"
        return "ready_for_manual_dry_run"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    if source_status == "blocked":
        return "blocked"
    return "deferred"


def _provider_runbooks(readiness: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for provider in readiness.get("provider_readiness") or []:
        blockers = list(provider.get("blockers") or [])
        status = "blocked" if blockers else "manual_dry_run_ready"
        steps = [] if blockers else _steps(provider)
        rows.append(
            {
                "provider_id": str(provider.get("provider_id") or "unknown"),
                "provider_label": str(provider.get("provider_label") or "unknown"),
                "service_target": str(provider.get("service_target") or "unknown"),
                "status": status,
                "fixture_id": str(provider.get("fixture_id") or ""),
                "source_readiness_status": str(provider.get("status") or "deferred"),
                "source_case_ids": list(provider.get("source_case_ids") or []),
                "steps": steps,
                "acceptance_checks": _acceptance_checks(provider),
                "rollback_steps": _rollback_steps(provider),
                "pause_conditions": _pause_conditions(provider),
                "evidence_refs": _evidence_refs(provider),
                "blockers": blockers,
                "no_go_conditions": list(provider.get("no_go_conditions") or []),
                "recommendation": _provider_recommendation(status),
            }
        )
    return rows


def _steps(provider: dict[str, Any]) -> list[dict[str, Any]]:
    provider_label = str(provider.get("provider_label") or "候选 provider")
    fixture_id = str(provider.get("fixture_id") or "fixture")
    return [
        {
            "id": "prepare",
            "phase": "prepare",
            "title": "锁定 dry-run 输入",
            "description": f"只使用 readiness gate 中的 {fixture_id}，不补充真实账号或明文 Key。",
            "expected_evidence": ["fixture_id", "source_case_ids", "manual_review_items"],
        },
        {
            "id": "dry_run",
            "phase": "dry_run",
            "title": "人工执行离线 dry-run",
            "description": f"按 {provider_label} fixture 对照本地 BM25/ledger/aliases 输出，不调用真实 provider。",
            "expected_evidence": ["baseline_chain", "expected_provider_output", "failure_fallback"],
        },
        {
            "id": "compare",
            "phase": "compare",
            "title": "对比候选收益",
            "description": "人工记录候选 provider 是否改善关系、因果或状态链召回。",
            "expected_evidence": ["candidate_gain", "missed_entities", "false_positive_risk"],
        },
        {
            "id": "review",
            "phase": "review",
            "title": "复核成本、隐私和 no-go",
            "description": "逐项确认成本上限、上传范围、删除策略、真实付费 Key 禁止条件。",
            "expected_evidence": ["cost_guardrails", "privacy_guardrails", "no_go_conditions"],
        },
        {
            "id": "rollback",
            "phase": "rollback",
            "title": "演练回滚",
            "description": "确认关闭候选层后仍能回退到本地 BM25 + canon ledger + entity aliases。",
            "expected_evidence": ["rollback_steps", "local_retrieval_fallback"],
        },
        {
            "id": "stop",
            "phase": "stop",
            "title": "暂停或升级决策",
            "description": "若任何 no-go 命中则暂停；只有人工确认后才另开真实 opt-in spike。",
            "expected_evidence": ["manual_decision", "pause_conditions", "next_owner"],
        },
    ]


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    provider_runbooks: list[dict[str, Any]],
) -> dict[str, Any]:
    ready_count = sum(
        1 for item in provider_runbooks if item["status"] == "manual_dry_run_ready"
    )
    blocked_count = sum(1 for item in provider_runbooks if item["status"] == "blocked")
    step_count = sum(len(item.get("steps") or []) for item in provider_runbooks)
    return {
        "story_slug": story_slug,
        "source_readiness_gate_status": source_status,
        "status": status,
        "provider_runbook_count": len(provider_runbooks),
        "ready_provider_count": ready_count,
        "blocked_provider_count": blocked_count,
        "total_step_count": step_count,
        "writes_artifacts": False,
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


def _runbook(status: str, provider_runbooks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": "graph_memory_provider_spike_runbook",
        "title": "Graph Memory Provider Spike 人工 dry-run SOP",
        "status": status,
        "manual_only": True,
        "real_provider_config_allowed": False,
        "provider_count": len(provider_runbooks),
        "step_count": sum(len(item.get("steps") or []) for item in provider_runbooks),
        "objective": "把 readiness gate 转成可人工复核、可暂停、可回滚的 dry-run 步骤。",
    }


def _decision(status: str, provider_runbooks: list[dict[str, Any]]) -> dict[str, Any]:
    if status == "ready_for_manual_dry_run":
        return {
            "status": "manual_runbook_ready_no_real_config",
            "recommendation": "可以人工执行 dry-run SOP；真实 provider 配置仍需另行显式确认。",
            "provider_count": len(provider_runbooks),
        }
    if status == "blocked":
        return {
            "status": "blocked_before_manual_dry_run",
            "recommendation": "先补齐 readiness blockers，不执行 dry-run SOP。",
            "provider_count": len(provider_runbooks),
        }
    return {
        "status": "deferred",
        "recommendation": "继续补本地证据，不执行 dry-run SOP，不创建真实 provider 配置。",
        "provider_count": len(provider_runbooks),
    }


def _acceptance_checks(provider: dict[str, Any]) -> list[str]:
    items = list(provider.get("manual_review_items") or [])
    items.extend(
        [
            "dry-run 结果必须能回溯到 fixture source cases。",
            "候选收益必须超过本地 BM25 + canon ledger + aliases 的当前输出。",
            "人工确认真实配置仍为禁止状态。",
        ]
    )
    return _dedupe(items)


def _rollback_steps(provider: dict[str, Any]) -> list[str]:
    return _dedupe(
        [
            f"停止 {provider.get('provider_label') or 'provider'} 候选层 dry-run。",
            "保留本地 BM25 + canon ledger + entity aliases 作为唯一运行链路。",
            "删除人工 dry-run 临时记录中的明文账号、Key 或上传草稿。",
            "复跑 readiness gate，确认 real_provider_config_allowed 仍为 false。",
        ]
    )


def _pause_conditions(provider: dict[str, Any]) -> list[str]:
    items = list(provider.get("no_go_conditions") or [])
    items.extend(
        [
            "需要真实付费 Key、外部账号或云端上传才能继续。",
            "需要上传 holdout_private、明文密钥或不可删除的用户文本。",
            "dry-run 无法证明相对本地检索的稳定收益。",
        ]
    )
    return _dedupe(items)


def _evidence_refs(provider: dict[str, Any]) -> list[str]:
    refs = [str(item) for item in provider.get("source_case_ids") or []]
    fixture_id = str(provider.get("fixture_id") or "")
    if fixture_id:
        refs.insert(0, fixture_id)
    return _dedupe(refs)


def _provider_recommendation(status: str) -> str:
    if status == "manual_dry_run_ready":
        return "可以人工执行 dry-run SOP；真实配置仍需另行显式确认。"
    return "先补齐 readiness blockers。"


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_manual_dry_run":
        return []
    return [
        "人工按 provider runbook 逐步执行 dry-run，记录证据引用。",
        "人工确认 no-go、成本、隐私、回滚和暂停条件。",
        "人工确认真实 provider 配置仍需另开 opt-in spike，不能由 runbook 自动创建。",
    ]


def _no_go_conditions(
    readiness: dict[str, Any],
    provider_runbooks: list[dict[str, Any]],
) -> list[str]:
    items = list(readiness.get("no_go_conditions") or [])
    for row in provider_runbooks:
        items.extend(row.get("no_go_conditions") or [])
        items.extend(row.get("pause_conditions") or [])
    items.extend(
        [
            "不能把 runbook 当成真实 provider 配置许可。",
            "不能要求真实付费 Key 或外部账号才能完成 runbook。",
            "不能在 runbook 阶段上传 holdout_private 或明文密钥。",
        ]
    )
    return _dedupe(items)


def _warnings(
    readiness: dict[str, Any],
    provider_runbooks: list[dict[str, Any]],
) -> list[str]:
    warnings = list(readiness.get("warnings") or [])
    if not provider_runbooks:
        warnings.append("没有可生成 runbook 的 provider readiness row，runbook 暂缓。")
    for row in provider_runbooks:
        for blocker in row.get("blockers") or []:
            warnings.append(f"{row['provider_label']} runbook blocked：{blocker}")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    runbook: dict[str, Any],
    decision: dict[str, Any],
    provider_runbooks: list[dict[str, Any]],
    readiness: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "runbook": runbook,
        "decision": decision,
        "provider_runbooks": provider_runbooks,
        "source_readiness_gate": {
            "version": readiness.get("version"),
            "status": readiness.get("status"),
            "readiness_gate": readiness.get("readiness_gate"),
        },
        "contract": {
            "writes_artifacts": False,
            "external_services_required": False,
            "provider_calls": False,
            "real_provider_config_allowed": False,
            "plaintext_key_returned": False,
        },
    }


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_manual_dry_run":
        return [
            "人工执行 runbook dry-run，并记录每一步证据。",
            "若 no-go 未命中且收益明确，再另开真实 provider opt-in spike。",
        ]
    if status == "blocked":
        return [
            "先补齐 readiness gate blockers，再重新生成 runbook。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    if status == "needs_more_evidence":
        return [
            "先补 readiness gate 所需 fixture、manual acceptance 和 no-go 条件。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 provider spike runbook 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 readiness gate 就绪后再生成 runbook。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

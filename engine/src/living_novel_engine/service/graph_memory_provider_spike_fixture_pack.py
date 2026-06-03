"""Graph Memory Provider Spike Fixture Pack MVP.

This read-only report packages deterministic dry-run fixtures for a future
explicit provider spike. It does not create provider configs, read keys, write
artifacts, or call external services.
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

VERSION = "graph-memory-provider-spike-fixture-pack-mvp"


class GraphMemoryProviderSpikeFixturePackRequestError(ValueError):
    """Invalid graph-memory provider fixture-pack request, mapped to HTTP 400."""


def get_graph_memory_provider_spike_fixture_pack(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only provider spike fixture pack."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        replay_report = get_graph_memory_offline_shadow_replay_report(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryOfflineShadowReplayReportRequestError as exc:
        raise GraphMemoryProviderSpikeFixturePackRequestError(str(exc)) from exc

    source_status = str(replay_report.get("status") or "deferred")
    status = _status(source_status)
    provider_fixture_packs = _provider_fixture_packs(status, sid, replay_report)
    fixture_gate = _fixture_gate(status, provider_fixture_packs)
    decision = _decision(status, provider_fixture_packs)
    summary = _summary(sid, source_status, status, provider_fixture_packs)
    manifest = _manifest(
        generated_at,
        summary,
        fixture_gate,
        decision,
        provider_fixture_packs,
        replay_report,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_fixture_pack",
        "status": status,
        "story_slug": sid,
        "source_kind": replay_report.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "fixture_gate": fixture_gate,
        "decision": decision,
        "provider_fixture_packs": provider_fixture_packs,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": _no_go_conditions(replay_report),
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(replay_report, provider_fixture_packs),
        "boundaries": [
            "只读生成 provider spike fixture pack，不创建 provider 配置，不写项目 artifact。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeFixturePackRequestError("invalid slug")
    return sid


def _status(source_status: str) -> str:
    if source_status == "ready_for_review":
        return "ready_for_fixture_pack"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    return "deferred"


def _provider_fixture_packs(
    status: str,
    story_slug: str,
    replay_report: dict[str, Any],
) -> list[dict[str, Any]]:
    if status != "ready_for_fixture_pack":
        return []

    cases_by_provider: dict[str, list[dict[str, Any]]] = {}
    for item in replay_report.get("case_results") or []:
        if item.get("status") == "deferred":
            continue
        provider_id = str(item.get("provider_id") or "unknown")
        cases_by_provider.setdefault(provider_id, []).append(item)

    packs: list[dict[str, Any]] = []
    for result in replay_report.get("provider_results") or []:
        provider_id = str(result.get("provider_id") or "unknown")
        provider_cases = cases_by_provider.get(provider_id, [])
        if not provider_cases:
            continue
        packs.append(
            {
                "id": f"provider-spike-fixture-{provider_id}",
                "provider_id": provider_id,
                "provider_label": str(result.get("provider_label") or provider_id),
                "service_target": str(result.get("service_target") or provider_id),
                "status": "dry_run_fixture_ready",
                "opt_in_required": True,
                "fixture": _fixture(story_slug, result, provider_cases, replay_report),
                "cost_guardrails": _cost_guardrails(provider_id),
                "privacy_guardrails": _privacy_guardrails(provider_id),
                "rollback_checklist": _rollback_checklist(result, provider_cases),
                "manual_acceptance_checklist": _manual_acceptance_checklist(
                    provider_id, provider_cases
                ),
                "no_go_conditions": _pack_no_go_conditions(replay_report, provider_cases),
            }
        )
    return packs


def _fixture(
    story_slug: str,
    provider_result: dict[str, Any],
    provider_cases: list[dict[str, Any]],
    replay_report: dict[str, Any],
) -> dict[str, Any]:
    provider_id = str(provider_result.get("provider_id") or "unknown")
    return {
        "id": f"single-project-fixture-{story_slug}-{provider_id}",
        "dry_run_only": True,
        "scope": "single_provider_single_project_single_fixture",
        "project_slug": story_slug,
        "provider_id": provider_id,
        "provider_label": str(provider_result.get("provider_label") or provider_id),
        "service_target": str(provider_result.get("service_target") or provider_id),
        "source_report_status": str(replay_report.get("status") or "deferred"),
        "sample_case_count": len(provider_cases),
        "source_case_ids": [str(item.get("source_case_id") or item.get("id") or "") for item in provider_cases],
        "cases": [_fixture_case(item) for item in provider_cases],
        "baseline_chain": "BM25 + canon ledger + entity aliases",
        "expected_output": "只允许生成 dry-run 对照结果和人工复核记录，不允许写回本地真源。",
    }


def _fixture_case(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "eval_id": str(item.get("eval_id") or ""),
        "query": str(item.get("query") or ""),
        "display_name": str(item.get("display_name") or item.get("eval_id") or ""),
        "baseline_chain": str(item.get("baseline_chain") or "BM25 + canon ledger + entity aliases"),
        "mock_delta": item.get("mock_delta") or {},
        "gain_assessment": str(item.get("gain_assessment") or ""),
        "risk_assessment": str(item.get("risk_assessment") or ""),
        "manual_review_focus": list(
            (item.get("manual_review_result") or {}).get("review_focus") or []
        ),
        "failure_fallback": str(
            (item.get("failure_mode") or {}).get("fallback") or "keep_local_baseline"
        ),
    }


def _cost_guardrails(provider_id: str) -> list[str]:
    return [
        f"{provider_id} spike 必须设置单次 dry-run 调用预算和总预算上限。",
        "必须能在人工复核前停止，不得后台循环调用。",
        "不得把 mock fixture pack 视为真实成本测算；真实成本另行人工确认。",
    ]


def _privacy_guardrails(provider_id: str) -> list[str]:
    return [
        f"{provider_id} spike 前必须列出会离开本机的章节片段、实体、关系和查询文本。",
        "不得上传 holdout_private、明文 Key、用户真实身份或未授权受保护文本。",
        "必须定义删除、重建和本地真源优先策略。",
    ]


def _rollback_checklist(
    provider_result: dict[str, Any],
    provider_cases: list[dict[str, Any]],
) -> list[str]:
    items = [
        str(provider_result.get("rollback_strategy") or "关闭 provider 并回退本地检索链路。"),
        "关闭 provider 后继续使用 BM25 + canon ledger + entity aliases。",
        "不得覆盖 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
    ]
    for case in provider_cases:
        for item in (case.get("failure_mode") or {}).get("rollback_checklist") or []:
            text = str(item)
            if text and text not in items:
                items.append(text)
    return items


def _manual_acceptance_checklist(
    provider_id: str,
    provider_cases: list[dict[str, Any]],
) -> list[str]:
    return [
        f"人工确认 {provider_id} fixture 中每个 query 的候选收益真实对应长篇痛点。",
        "人工确认候选结果没有正史冲突、同名实体误连或过度解释。",
        f"人工确认 {len(provider_cases)} 个 case 的收益足以进入真实 opt-in spike。",
    ]


def _pack_no_go_conditions(
    replay_report: dict[str, Any],
    provider_cases: list[dict[str, Any]],
) -> list[str]:
    conditions: list[str] = []
    for item in list(replay_report.get("no_go_conditions") or []):
        if item not in conditions:
            conditions.append(str(item))
    for case in provider_cases:
        for item in case.get("no_go_conditions") or []:
            text = str(item)
            if text and text not in conditions:
                conditions.append(text)
    for item in [
        "不能把 fixture pack 当成真实 provider 配置。",
        "不能要求真实付费 Key 或外部账号才能完成 fixture pack。",
        "不能在 fixture pack 阶段上传 holdout_private 或明文密钥。",
    ]:
        if item not in conditions:
            conditions.append(item)
    return conditions


def _fixture_gate(status: str, packs: list[dict[str, Any]]) -> dict[str, Any]:
    if status == "ready_for_fixture_pack" and packs:
        return {
            "id": "graph_memory_provider_spike_fixture_pack_gate",
            "status": "fixture_pack_ready",
            "passed": True,
            "reason": "离线 replay report 已形成人工复核候选，可整理 provider spike dry-run 前置包。",
            "provider_fixture_count": len(packs),
            "selected_fixture_count": len(packs),
        }
    if status == "needs_more_evidence":
        return {
            "id": "graph_memory_provider_spike_fixture_pack_gate",
            "status": "collect_more_evidence",
            "passed": False,
            "reason": "离线 replay report 证据不足，先补 replay case 与人工复核结果。",
            "provider_fixture_count": len(packs),
            "selected_fixture_count": len(packs),
        }
    return {
        "id": "graph_memory_provider_spike_fixture_pack_gate",
        "status": "deferred",
        "passed": False,
        "reason": "当前项目未达到 provider fixture pack 触发条件。",
        "provider_fixture_count": len(packs),
        "selected_fixture_count": len(packs),
    }


def _decision(status: str, packs: list[dict[str, Any]]) -> dict[str, Any]:
    if status == "ready_for_fixture_pack" and packs:
        return {
            "status": "manual_review_before_real_provider_config",
            "recommendation": "先人工复核 fixture pack，再决定是否创建真实 provider 配置。",
            "provider_fixture_count": len(packs),
            "selected_fixture_count": len(packs),
        }
    return {
        "status": "deferred",
        "recommendation": "继续补本地证据，不创建真实 provider 配置。",
        "provider_fixture_count": 0,
        "selected_fixture_count": 0,
    }


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    packs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "story_slug": story_slug,
        "source_replay_report_status": source_status,
        "status": status,
        "provider_fixture_count": len(packs),
        "selected_fixture_count": len(packs),
        "manual_review_required_count": len(packs),
        "writes_artifacts": False,
        "external_services_required": False,
        "provider_calls": False,
        "uses_graphrag": False,
        "uses_zep": False,
        "uses_vector_store": False,
        "uses_reranker": False,
        "uses_embedding_provider": False,
        "plaintext_key_returned": False,
    }


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    fixture_gate: dict[str, Any],
    decision: dict[str, Any],
    packs: list[dict[str, Any]],
    replay_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "fixture_gate": fixture_gate,
        "decision": decision,
        "provider_fixture_packs": packs,
        "source_replay_report": {
            "version": replay_report.get("version"),
            "status": replay_report.get("status"),
            "report_gate": replay_report.get("report_gate"),
        },
        "contract": {
            "writes_artifacts": False,
            "external_services_required": False,
            "provider_calls": False,
            "plaintext_key_returned": False,
        },
    }


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_fixture_pack":
        return []
    return [
        "人工复核 fixture pack 是否只包含单 provider、单项目、单 fixture 的 dry-run 输入。",
        "人工复核成本、隐私、回滚和 no-go 是否足够进入真实 opt-in spike。",
        "人工复核是否仍能继续用本地 BM25 + canon ledger + entity aliases 解决。",
    ]


def _no_go_conditions(replay_report: dict[str, Any]) -> list[str]:
    return _pack_no_go_conditions(replay_report, [])


def _warnings(
    replay_report: dict[str, Any],
    packs: list[dict[str, Any]],
) -> list[str]:
    warnings = list(replay_report.get("warnings") or [])
    if not packs:
        warnings.append("没有可整理的 provider fixture pack，先完成 offline replay report。")
    return warnings


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_fixture_pack":
        return [
            "人工复核 fixture pack 后，再决定是否进入真实 provider opt-in spike。",
            "真实 spike 前继续确认成本上限、隐私说明、删除策略和回滚验收清单。",
        ]
    if status == "needs_more_evidence":
        return [
            "先补 offline replay report 的 case result 和人工复核结论。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 provider fixture pack 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 offline replay report 就绪后再生成 dry-run fixture pack。",
    ]

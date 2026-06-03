"""Graph Memory Provider Spike Readiness Gate MVP.

This read-only report turns provider spike fixture packs into a manual opt-in
readiness gate. It does not create provider configs, read keys, write artifacts,
or call external services.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_provider_spike_fixture_pack import (
    GraphMemoryProviderSpikeFixturePackRequestError,
    get_graph_memory_provider_spike_fixture_pack,
)

VERSION = "graph-memory-provider-spike-readiness-gate-mvp"


class GraphMemoryProviderSpikeReadinessGateRequestError(ValueError):
    """Invalid graph-memory provider readiness-gate request, mapped to HTTP 400."""


def get_graph_memory_provider_spike_readiness_gate(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a deterministic read-only provider spike readiness gate."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        fixture_pack = get_graph_memory_provider_spike_fixture_pack(
            sid,
            projects_dir=projects_dir,
            now=now,
        )
    except GraphMemoryProviderSpikeFixturePackRequestError as exc:
        raise GraphMemoryProviderSpikeReadinessGateRequestError(str(exc)) from exc

    source_status = str(fixture_pack.get("status") or "deferred")
    provider_readiness = _provider_readiness(fixture_pack)
    status = _status(source_status, provider_readiness)
    summary = _summary(sid, source_status, status, provider_readiness)
    readiness_gate = _readiness_gate(status, provider_readiness)
    decision = _decision(status, provider_readiness)
    no_go_conditions = _no_go_conditions(fixture_pack, provider_readiness)
    manifest = _manifest(
        generated_at,
        summary,
        readiness_gate,
        decision,
        provider_readiness,
        fixture_pack,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_provider_spike_readiness_gate",
        "status": status,
        "story_slug": sid,
        "source_kind": fixture_pack.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "readiness_gate": readiness_gate,
        "decision": decision,
        "provider_readiness": provider_readiness,
        "manual_review_checklist": _manual_review_checklist(status),
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(fixture_pack, provider_readiness),
        "boundaries": [
            "只读生成 provider spike readiness gate，不创建 provider 配置，不写项目 artifact。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能另开显式 opt-in spike。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemoryProviderSpikeReadinessGateRequestError("invalid slug")
    return sid


def _status(source_status: str, provider_readiness: list[dict[str, Any]]) -> str:
    if source_status == "ready_for_fixture_pack" and provider_readiness:
        if any(item["status"] == "blocked" for item in provider_readiness):
            return "blocked"
        return "ready_for_manual_opt_in_review"
    if source_status == "needs_more_evidence":
        return "needs_more_evidence"
    return "deferred"


def _provider_readiness(fixture_pack: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pack in fixture_pack.get("provider_fixture_packs") or []:
        checks = _readiness_checks(pack)
        blockers = [
            str(check["label"])
            for check in checks
            if check["status"] == "blocked"
        ]
        status = "blocked" if blockers else "manual_review_ready"
        fixture = pack.get("fixture") or {}
        rows.append(
            {
                "provider_id": str(pack.get("provider_id") or "unknown"),
                "provider_label": str(pack.get("provider_label") or "unknown"),
                "service_target": str(pack.get("service_target") or "unknown"),
                "status": status,
                "fixture_id": str(fixture.get("id") or ""),
                "source_fixture_pack_status": str(pack.get("status") or "deferred"),
                "sample_case_count": int(fixture.get("sample_case_count") or 0),
                "source_case_ids": list(fixture.get("source_case_ids") or []),
                "readiness_checks": checks,
                "manual_review_items": _dedupe(
                    list(pack.get("manual_acceptance_checklist") or [])
                    + list(pack.get("cost_guardrails") or [])
                    + list(pack.get("privacy_guardrails") or [])
                ),
                "blockers": blockers,
                "no_go_conditions": list(pack.get("no_go_conditions") or []),
                "recommendation": _provider_recommendation(status),
            }
        )
    return rows


def _readiness_checks(pack: dict[str, Any]) -> list[dict[str, Any]]:
    fixture = pack.get("fixture") or {}
    checks = [
        _check(
            "fixture_scope",
            "单 provider、单项目、单 fixture dry-run 输入",
            bool(fixture.get("dry_run_only"))
            and fixture.get("scope") == "single_provider_single_project_single_fixture"
            and fixture.get("source_report_status") == "ready_for_review",
            "passed",
        ),
        _check(
            "fixture_cases",
            "至少包含一个可复核 case",
            int(fixture.get("sample_case_count") or 0) > 0,
            "passed",
        ),
        _check(
            "cost_guardrails",
            "成本上限和停止条件需人工复核",
            bool(pack.get("cost_guardrails")),
            "manual_review_required",
        ),
        _check(
            "privacy_guardrails",
            "隐私、上传范围和删除策略需人工复核",
            bool(pack.get("privacy_guardrails")),
            "manual_review_required",
        ),
        _check(
            "rollback_plan",
            "关闭 provider 后能回退本地检索链路",
            bool(pack.get("rollback_checklist")),
            "manual_review_required",
        ),
        _check(
            "manual_acceptance",
            "人工验收项已列出",
            bool(pack.get("manual_acceptance_checklist")),
            "manual_review_required",
        ),
        _check(
            "no_go_review",
            "no-go 条件已列出并需人工确认",
            bool(pack.get("no_go_conditions")),
            "manual_review_required",
        ),
    ]
    return checks


def _check(
    check_id: str,
    label: str,
    passed: bool,
    passed_status: str,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "status": passed_status if passed else "blocked",
        "passed": passed,
    }


def _summary(
    story_slug: str,
    source_status: str,
    status: str,
    provider_readiness: list[dict[str, Any]],
) -> dict[str, Any]:
    ready_count = sum(1 for item in provider_readiness if item["status"] == "manual_review_ready")
    blocked_count = sum(1 for item in provider_readiness if item["status"] == "blocked")
    return {
        "story_slug": story_slug,
        "source_fixture_pack_status": source_status,
        "status": status,
        "provider_fixture_count": len(provider_readiness),
        "ready_for_manual_review_count": ready_count,
        "blocked_provider_count": blocked_count,
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


def _readiness_gate(
    status: str,
    provider_readiness: list[dict[str, Any]],
) -> dict[str, Any]:
    if status == "ready_for_manual_opt_in_review":
        return {
            "id": "graph_memory_provider_spike_readiness_gate",
            "status": "ready_for_manual_opt_in_review",
            "passed": True,
            "real_provider_config_allowed": False,
            "reason": "fixture pack 已满足人工 opt-in review 前置条件，但仍不能自动创建真实 provider 配置。",
            "selected_provider_count": len(provider_readiness),
        }
    if status == "blocked":
        return {
            "id": "graph_memory_provider_spike_readiness_gate",
            "status": "blocked",
            "passed": False,
            "real_provider_config_allowed": False,
            "reason": "至少一个 provider fixture 缺少 scope、case、成本、隐私、回滚或 no-go 前置项。",
            "selected_provider_count": len(provider_readiness),
        }
    if status == "needs_more_evidence":
        return {
            "id": "graph_memory_provider_spike_readiness_gate",
            "status": "collect_more_evidence",
            "passed": False,
            "real_provider_config_allowed": False,
            "reason": "fixture pack 证据不足，先补 replay report 与 dry-run 前置包。",
            "selected_provider_count": len(provider_readiness),
        }
    return {
        "id": "graph_memory_provider_spike_readiness_gate",
        "status": "deferred",
        "passed": False,
        "real_provider_config_allowed": False,
        "reason": "当前项目未达到 provider spike readiness gate 触发条件。",
        "selected_provider_count": len(provider_readiness),
    }


def _decision(status: str, provider_readiness: list[dict[str, Any]]) -> dict[str, Any]:
    if status == "ready_for_manual_opt_in_review":
        return {
            "status": "manual_review_ready_no_real_config",
            "recommendation": "可以进入人工 opt-in review，但仍需另行显式确认真实 provider 配置。",
            "provider_count": len(provider_readiness),
        }
    if status == "blocked":
        return {
            "status": "blocked_before_real_provider_config",
            "recommendation": "先补齐 blocked readiness check，不创建真实 provider 配置。",
            "provider_count": len(provider_readiness),
        }
    return {
        "status": "deferred",
        "recommendation": "继续补本地证据，不创建真实 provider 配置。",
        "provider_count": len(provider_readiness),
    }


def _provider_recommendation(status: str) -> str:
    if status == "manual_review_ready":
        return "进入人工 opt-in review；真实配置仍需另行显式确认。"
    return "先补齐 blocked readiness check。"


def _manual_review_checklist(status: str) -> list[str]:
    if status != "ready_for_manual_opt_in_review":
        return []
    return [
        "人工确认是否仍能继续用本地 BM25 + canon ledger + entity aliases 解决。",
        "人工确认每个 provider fixture 的成本、隐私、回滚和 no-go 条件。",
        "人工确认真实 provider spike 只允许显式 opt-in，且另行配置预算和删除策略。",
    ]


def _no_go_conditions(
    fixture_pack: dict[str, Any],
    provider_readiness: list[dict[str, Any]],
) -> list[str]:
    items = list(fixture_pack.get("no_go_conditions") or [])
    for row in provider_readiness:
        items.extend(row.get("no_go_conditions") or [])
    items.extend(
        [
            "不能把 readiness gate 当成真实 provider 配置许可。",
            "不能要求真实付费 Key 或外部账号才能完成 readiness gate。",
            "不能在 readiness gate 阶段上传 holdout_private 或明文密钥。",
        ]
    )
    return _dedupe(items)


def _warnings(
    fixture_pack: dict[str, Any],
    provider_readiness: list[dict[str, Any]],
) -> list[str]:
    warnings = list(fixture_pack.get("warnings") or [])
    if not provider_readiness:
        warnings.append("没有可评估的 provider fixture pack，readiness gate 暂缓。")
    for row in provider_readiness:
        for blocker in row.get("blockers") or []:
            warnings.append(f"{row['provider_label']} blocked：{blocker}")
    return _dedupe(warnings)


def _manifest(
    generated_at: str,
    summary: dict[str, Any],
    readiness_gate: dict[str, Any],
    decision: dict[str, Any],
    provider_readiness: list[dict[str, Any]],
    fixture_pack: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": summary["status"],
        "summary": summary,
        "readiness_gate": readiness_gate,
        "decision": decision,
        "provider_readiness": provider_readiness,
        "source_fixture_pack": {
            "version": fixture_pack.get("version"),
            "status": fixture_pack.get("status"),
            "fixture_gate": fixture_pack.get("fixture_gate"),
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
    if status == "ready_for_manual_opt_in_review":
        return [
            "人工复核 readiness gate 后，再决定是否进入真实 provider opt-in spike。",
            "真实 spike 前继续确认预算上限、隐私说明、删除策略和回滚验收清单。",
        ]
    if status == "blocked":
        return [
            "先补齐 blocked readiness check，再重新生成 readiness gate。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    if status == "needs_more_evidence":
        return [
            "先补 fixture pack 的 dry-run 输入、manual acceptance 和 no-go 条件。",
            "继续保持 GraphRAG、Zep、向量库、reranker 为触发式增强。",
        ]
    return [
        "保持 provider spike readiness gate 暂缓，不创建外部账号、不写配置、不接重型服务。",
        "等 fixture pack 就绪后再生成 readiness gate。",
    ]


def _dedupe(items: list[Any]) -> list[str]:
    result: list[str] = []
    for item in items:
        text = str(item)
        if text and text not in result:
            result.append(text)
    return result

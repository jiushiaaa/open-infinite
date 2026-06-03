"""Graph Memory Spike Design Pack MVP.

This report turns local GraphRAG / Zep trigger evidence into a deterministic
spike design pack. It is intentionally read-only: no external memory services,
providers, vector stores, rerankers, or artifact writes.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.graph_memory_trigger_evidence import (
    GraphMemoryTriggerEvidenceRequestError,
    get_graph_memory_trigger_evidence,
)

VERSION = "graph-memory-spike-design-pack-mvp"


class GraphMemorySpikeDesignPackRequestError(ValueError):
    """Invalid graph-memory spike design pack request, mapped to HTTP 400."""


def get_graph_memory_spike_design_pack(
    slug: str,
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a read-only spike design pack from local trigger evidence."""

    sid = _safe_slug(slug)
    generated_at = (now or datetime.now()).isoformat(timespec="seconds")
    try:
        evidence = get_graph_memory_trigger_evidence(sid, projects_dir=projects_dir, now=now)
    except GraphMemoryTriggerEvidenceRequestError as exc:
        raise GraphMemorySpikeDesignPackRequestError(str(exc)) from exc

    status = _status(evidence)
    layer_plans = _layer_plans(status, evidence)
    experiment_inputs = _experiment_inputs(evidence)
    acceptance_gates = _acceptance_gates(layer_plans, evidence)
    no_go_conditions = _no_go_conditions()
    rollback_plan = _rollback_plan()
    design_gate = _design_gate(status, evidence, layer_plans)
    summary = _summary(
        evidence,
        layer_plans,
        experiment_inputs,
        acceptance_gates,
        no_go_conditions,
    )
    manifest = _manifest(
        generated_at,
        status,
        evidence,
        summary,
        design_gate,
        layer_plans,
        experiment_inputs,
        acceptance_gates,
        no_go_conditions,
        rollback_plan,
    )
    content_json = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"

    return {
        "version": VERSION,
        "mode": "read_only_graph_memory_spike_design_pack",
        "status": status,
        "story_slug": sid,
        "source_kind": evidence.get("source_kind") or "unknown",
        "generated_at": generated_at,
        "summary": summary,
        "design_gate": design_gate,
        "layer_plans": layer_plans,
        "experiment_inputs": experiment_inputs,
        "acceptance_gates": acceptance_gates,
        "rollback_plan": rollback_plan,
        "no_go_conditions": no_go_conditions,
        "manifest": manifest,
        "content_json": content_json,
        "warnings": _warnings(evidence, layer_plans),
        "boundaries": [
            "只读整理 GraphRAG、Zep、Temporal Memory spike 设计，不写项目 artifact。",
            "不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。",
            "不替换 BM25、canon ledger、entity aliases、retrieval_context 或 run_scene 默认行为。",
            "不读取、不返回、不记录明文 Key；真实付费服务只能在用户明确确认后另开 opt-in spike。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise GraphMemorySpikeDesignPackRequestError("invalid slug")
    return sid


def _status(evidence: dict[str, Any]) -> str:
    evidence_status = str(evidence.get("status") or "")
    if evidence_status == "triggered":
        return "ready_for_spike"
    if evidence_status == "monitor":
        return "needs_more_evidence"
    return "deferred"


def _layer_plans(status: str, evidence: dict[str, Any]) -> list[dict[str, Any]]:
    plans: list[dict[str, Any]] = []
    for layer in evidence.get("candidate_layers") or []:
        layer_id = str(layer.get("id") or "unknown")
        candidate = layer.get("status") == "candidate"
        plan_status = "candidate" if status == "ready_for_spike" and candidate else "deferred"
        if status == "needs_more_evidence" and candidate:
            plan_status = "monitor"
        plans.append(
            {
                "id": layer_id,
                "label": str(layer.get("label") or layer_id),
                "status": plan_status,
                "source_status": str(layer.get("status") or "unknown"),
                "reason": str(layer.get("reason") or ""),
                "design_focus": _design_focus(layer_id),
                "trial_inputs": _trial_inputs(layer_id),
                "acceptance_gate_ids": _layer_gate_ids(layer_id),
                "risks": _layer_risks(layer_id),
                "rollback_strategy": _layer_rollback(layer_id),
            }
        )
    return plans


def _design_focus(layer_id: str) -> str:
    return {
        "graphrag": "验证实体关系、伏笔因果和离散事实查询是否比 BM25 + ledger 更稳定。",
        "zep": "验证现成长期记忆服务能否补足本地账本/别名基础缺口。",
        "temporal_memory": "验证时间、资源和状态链能否解释跨章节状态漂移。",
    }.get(layer_id, "保留为观察层，不进入默认实现。")


def _trial_inputs(layer_id: str) -> list[str]:
    common = ["source_raw", "canon_ledger", "entity_aliases", "retrieval_eval_records"]
    if layer_id == "temporal_memory":
        return common + ["state_snapshot", "runtime_memory_context"]
    if layer_id == "zep":
        return common + ["graph_memory_trigger_evidence", "foundation_gap_summary"]
    return common + ["retrieval_probe", "relation_causal_state_signals"]


def _layer_gate_ids(layer_id: str) -> list[str]:
    if layer_id == "graphrag":
        return ["contract_safety", "retrieval_gain", "relation_traceability"]
    if layer_id == "zep":
        return ["contract_safety", "zep_foundation_gap_reduction"]
    if layer_id == "temporal_memory":
        return ["contract_safety", "temporal_state_traceability"]
    return ["contract_safety"]


def _layer_risks(layer_id: str) -> list[str]:
    return {
        "graphrag": ["图构建噪声把错误关系固化", "检索链路变重后难以定位召回问题"],
        "zep": ["外部服务账号和网络状态影响本地可复现性", "长期记忆写入策略可能污染事实层"],
        "temporal_memory": ["状态粒度过细会挤占 prompt budget", "时间线解释可能和现有 state_snapshot 冲突"],
    }.get(layer_id, ["证据不足时不进入 spike"])


def _layer_rollback(layer_id: str) -> str:
    return {
        "graphrag": "保留 BM25 + canon ledger + entity aliases 为默认召回，GraphRAG 只做 opt-in shadow report。",
        "zep": "Zep 只读 shadow compare 失败时直接丢弃外部结果，不写回本地账本。",
        "temporal_memory": "Temporal Memory 只输出对照报告，不覆盖 state_snapshot 或 runtime_memory_context。",
    }.get(layer_id, "保持现有文件型记忆默认链路。")


def _experiment_inputs(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    summary = evidence.get("summary") or {}
    records = evidence.get("records") or []
    return [
        {
            "id": "source_raw",
            "label": "长篇原文与章节切片",
            "status": "required",
            "detail": f"{int(summary.get('chapter_count') or 0)} 章输入，用于构建 shadow corpus。",
        },
        {
            "id": "canon_ledger",
            "label": "正史账本",
            "status": "required",
            "detail": (
                f"{summary.get('canon_ledger_status')}/"
                f"{int(summary.get('canon_ledger_count') or 0)} 条，作为事实基准。"
            ),
        },
        {
            "id": "entity_aliases",
            "label": "实体别名",
            "status": "required",
            "detail": (
                f"{summary.get('entity_alias_status')}/"
                f"{int(summary.get('entity_alias_count') or 0)} 条，用于统一实体口径。"
            ),
        },
        {
            "id": "retrieval_eval_records",
            "label": "检索评测样本",
            "status": "required" if records else "missing",
            "detail": f"{len(records)} 条跨项目 eval records，优先用于 shadow compare。",
        },
        {
            "id": "relation_causal_state_signals",
            "label": "关系/因果/状态信号",
            "status": "required" if summary.get("relation_or_state_pressure") else "optional",
            "detail": (
                f"关系 {summary.get('relation_signal_count')}，因果 {summary.get('causal_signal_count')}，"
                f"状态 {summary.get('state_signal_count')}。"
            ),
        },
    ]


def _acceptance_gates(
    layer_plans: list[dict[str, Any]], evidence: dict[str, Any]
) -> list[dict[str, Any]]:
    candidate_ids = {layer["id"] for layer in layer_plans if layer["status"] == "candidate"}
    summary = evidence.get("summary") or {}
    return [
        {
            "id": "contract_safety",
            "label": "契约安全",
            "status": "required",
            "target": "不得修改 run_scene 默认行为，不覆盖 canon_ledger.jsonl 或 state_snapshot.json。",
        },
        {
            "id": "retrieval_gain",
            "label": "召回收益",
            "status": "required" if "graphrag" in candidate_ids else "optional",
            "target": "shadow compare 中词面缺口样本命中率必须高于 BM25 基线，且可解释命中来源。",
        },
        {
            "id": "relation_traceability",
            "label": "关系可追溯",
            "status": "required" if summary.get("relation_signal_count") else "optional",
            "target": "人物/势力/道具关系必须能回溯到 source_raw 或 canon ledger 证据。",
        },
        {
            "id": "zep_foundation_gap_reduction",
            "label": "Zep 基础缺口收益",
            "status": "required" if "zep" in candidate_ids else "deferred",
            "target": "只在本地账本/别名基础缺口明确时比较 Zep；失败时不得写回本地事实层。",
        },
        {
            "id": "temporal_state_traceability",
            "label": "时间/状态可解释",
            "status": "required" if "temporal_memory" in candidate_ids else "optional",
            "target": "状态链解释必须和 state_snapshot、runtime memory 不冲突。",
        },
    ]


def _no_go_conditions() -> list[str]:
    return [
        "必须依赖真实付费 Key 或外部账号才能完成最小验证。",
        "需要替换 run_scene 默认行为或默认 runner。",
        "需要覆盖 canon_ledger.jsonl、state_snapshot.json 或 retrieval_context.json。",
        "无法用本地样本复现收益，只能靠主观体验判断。",
        "任一 shadow report 泄漏路径、密钥、原文私有 holdout 或外部服务错误细节。",
    ]


def _rollback_plan() -> list[dict[str, str]]:
    return [
        {
            "id": "shadow_only",
            "label": "只读 shadow",
            "action": "所有 spike 输出先写成临时报告或 HTTP 响应，不进入默认检索链路。",
        },
        {
            "id": "default_retrieval_fallback",
            "label": "默认召回回退",
            "action": "任一异常时继续使用 BM25 + canon ledger + entity aliases。",
        },
        {
            "id": "artifact_contract_guard",
            "label": "产物契约保护",
            "action": "不覆盖既有 run artifact；若需要持久化，另开 additive artifact 评审。",
        },
    ]


def _design_gate(
    status: str,
    evidence: dict[str, Any],
    layer_plans: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_count = sum(1 for layer in layer_plans if layer["status"] == "candidate")
    status_map = {
        "ready_for_spike": "design_pack_ready",
        "needs_more_evidence": "collect_more_evidence",
        "deferred": "deferred",
    }
    return {
        "id": "graph_memory_spike_design_ready",
        "status": status_map[status],
        "passed": status == "ready_for_spike" and candidate_count > 0,
        "reason": _gate_reason(status, evidence, candidate_count),
        "evidence_status": str(evidence.get("status") or "unknown"),
        "candidate_layer_count": candidate_count,
    }


def _gate_reason(status: str, evidence: dict[str, Any], candidate_count: int) -> str:
    if status == "ready_for_spike" and candidate_count > 0:
        return "触发证据已足够，先写只读 spike 设计包，不接生产服务。"
    if status == "needs_more_evidence":
        return "已有趋势压力，但还需要更多样本或修复本地记忆层。"
    return "当前证据不足，继续使用现有文件型记忆与 BM25 检索。"


def _summary(
    evidence: dict[str, Any],
    layer_plans: list[dict[str, Any]],
    experiment_inputs: list[dict[str, Any]],
    acceptance_gates: list[dict[str, Any]],
    no_go_conditions: list[str],
) -> dict[str, Any]:
    evidence_summary = evidence.get("summary") or {}
    return {
        "story_slug": evidence.get("story_slug") or "",
        "source_kind": evidence.get("source_kind") or "unknown",
        "evidence_status": evidence.get("status") or "unknown",
        "graph_memory_status": evidence_summary.get("graph_memory_status") or "unknown",
        "trigger_gate_status": (evidence.get("trigger_gate") or {}).get("status") or "unknown",
        "candidate_layer_count": sum(
            1 for layer in layer_plans if layer["status"] == "candidate"
        ),
        "monitor_layer_count": sum(1 for layer in layer_plans if layer["status"] == "monitor"),
        "experiment_input_count": len(experiment_inputs),
        "acceptance_gate_count": len(acceptance_gates),
        "no_go_condition_count": len(no_go_conditions),
        "trend_record_count": int(evidence_summary.get("trend_record_count") or 0),
        "trend_lexical_gap_count": int(evidence_summary.get("trend_lexical_gap_count") or 0),
        "relation_signal_count": int(evidence_summary.get("relation_signal_count") or 0),
        "causal_signal_count": int(evidence_summary.get("causal_signal_count") or 0),
        "state_signal_count": int(evidence_summary.get("state_signal_count") or 0),
        "writes_artifacts": False,
        "external_services_required": False,
        "uses_graphrag": False,
        "uses_zep": False,
        "uses_vector_store": False,
        "uses_reranker": False,
        "plaintext_key_returned": False,
    }


def _manifest(
    generated_at: str,
    status: str,
    evidence: dict[str, Any],
    summary: dict[str, Any],
    design_gate: dict[str, Any],
    layer_plans: list[dict[str, Any]],
    experiment_inputs: list[dict[str, Any]],
    acceptance_gates: list[dict[str, Any]],
    no_go_conditions: list[str],
    rollback_plan: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "generated_at": generated_at,
        "status": status,
        "summary": summary,
        "design_gate": design_gate,
        "layer_plans": layer_plans,
        "experiment_inputs": experiment_inputs,
        "acceptance_gates": acceptance_gates,
        "no_go_conditions": no_go_conditions,
        "rollback_plan": rollback_plan,
        "source_evidence": {
            "version": evidence.get("version"),
            "status": evidence.get("status"),
            "trigger_gate": evidence.get("trigger_gate"),
            "records": evidence.get("records") or [],
        },
    }


def _warnings(evidence: dict[str, Any], layer_plans: list[dict[str, Any]]) -> list[str]:
    warnings = [str(item) for item in evidence.get("warnings") or []]
    if not any(layer["status"] == "candidate" for layer in layer_plans):
        warnings.append("当前没有候选层进入 spike 设计。")
    return warnings[:8]


def _next_steps(status: str) -> list[str]:
    if status == "ready_for_spike":
        return [
            "先做 shadow compare，不进入默认 retrieval/run_scene。",
            "以本地 eval records 和关系/因果/状态信号定义验收门槛。",
            "只有设计包通过后，再拆真实 provider 或外部服务 opt-in spike。",
        ]
    if status == "needs_more_evidence":
        return [
            "继续积累 retrieval failure samples 和跨项目趋势快照。",
            "补齐 canon ledger、entity aliases 与状态投影后再评估设计包。",
        ]
    return [
        "继续使用 BM25、canon ledger、entity aliases 与 runtime memory。",
        "等真实长篇样本持续暴露关系/因果/状态缺口后再生成 spike 设计。",
    ]

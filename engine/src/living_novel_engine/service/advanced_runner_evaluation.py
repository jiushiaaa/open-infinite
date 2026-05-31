"""v0.9.4 Advanced Runner Evaluation trigger report.

This module only reads existing run artifacts and decides whether a later
LangGraph / OASIS / CAMEL spike is justified. It does not connect those
frameworks and does not mutate runner outputs.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_VERSION = "v0.9.4"


def evaluate_advanced_runner_trigger(
    run_id: str, *, outputs_dir: Path | None = None
) -> dict[str, Any]:
    """Return a deterministic trigger report for advanced runner evaluation."""
    rid = _validate_identifier(run_id)
    run_dir = _outputs_root(outputs_dir) / rid
    if not run_dir.is_dir():
        raise FileNotFoundError(f"run 不存在: {rid}")

    state_report = _read_optional_json(run_dir / "runner_state_execution_report.json")
    emergence = _read_optional_json(run_dir / "emergence_nodes.json")
    trace_metrics = _trace_metrics(run_dir)
    state_metrics = _state_execution_metrics(state_report)
    emergence_metrics = _emergence_metrics(emergence)
    reasons = _trigger_reasons(state_metrics, trace_metrics, emergence_metrics)
    status = _status(reasons, state_report, trace_metrics)

    return {
        "version": _VERSION,
        "run_id": rid,
        "status": status,
        "summary": _summary(status),
        "metrics": {
            **state_metrics,
            **trace_metrics,
            **emergence_metrics,
        },
        "trigger": {
            "should_evaluate": status == "triggered",
            "reasons": reasons,
            "thresholds": {
                "state_execution_backlog": 6,
                "trace_warning_count": 2,
                "private_complexity_items": 6,
            },
        },
        "next_steps": _next_steps(status),
        "boundaries": [
            "不接 LangGraph / OASIS / CAMEL。",
            "不改 run_scene 默认行为。",
            "不改 chapter.md / events.json / state_snapshot.json / multi_agent_trace.json / causal_diff.json 契约。",
        ],
        "source_artifacts": [
            "runner_state_execution_report.json",
            "multi_agent_trace.json",
            "emergence_nodes.json",
        ],
    }


def evaluate_advanced_runner_probes(
    run_id: str, *, outputs_dir: Path | None = None
) -> dict[str, Any]:
    """Collect deterministic failure samples before any advanced runner spike."""
    trigger = evaluate_advanced_runner_trigger(run_id, outputs_dir=outputs_dir)
    metrics = trigger["metrics"]
    probes = [
        probe
        for probe in (
            _state_execution_probe(metrics),
            _trace_warning_probe(metrics),
            _emergence_probe(metrics),
        )
        if probe is not None
    ]
    failure_samples = [probe for probe in probes if not probe["hit"]]
    status = (
        "insufficient_data"
        if not probes
        else "weak"
        if failure_samples
        else "pass"
    )
    return {
        "version": _VERSION,
        "run_id": trigger["run_id"],
        "status": status,
        "summary": _probe_summary(status),
        "metrics": {
            "sample_count": len(probes),
            "hit_count": len(probes) - len(failure_samples),
            "failure_count": len(failure_samples),
        },
        "probes": probes,
        "failure_samples": failure_samples,
        "next_steps": _probe_next_steps(status),
        "boundaries": trigger["boundaries"],
        "source_artifacts": trigger["source_artifacts"],
    }


def _validate_identifier(value: str | None) -> str:
    ident = (value or "").strip()
    if not ident or ".." in ident or not _SAFE_ID_RE.match(ident):
        raise ValueError("invalid run_id")
    return ident


def _outputs_root(outputs_dir: Path | None) -> Path:
    if outputs_dir is not None:
        return outputs_dir
    from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir

    return default_outputs_dir()


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return {"status": "damaged"}
    return data if isinstance(data, dict) else {"status": "damaged"}


def _branch_dirs(run_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in run_dir.iterdir()
        if path.is_dir()
        and (path.name.startswith("branch_") or path.name in {"linear", "baseline"})
    )


def _state_execution_metrics(report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    return {
        "state_execution_status": _artifact_status(report),
        "state_execution_candidate_count": _int(summary.get("candidate_count")),
        "state_execution_executable_count": _int(summary.get("executable_count")),
        "state_execution_review_required_count": _int(
            summary.get("review_required_count")
        ),
        "state_execution_blocked_count": _int(summary.get("blocked_count")),
        "state_execution_high_risk_count": _int(summary.get("high_risk_count")),
    }


def _trace_metrics(run_dir: Path) -> dict[str, Any]:
    trace_count = 0
    turn_plan_count = 0
    private_count = 0
    misunderstanding_count = 0
    warning_count = 0
    repaired_count = 0
    hard_fail_count = 0
    for branch in _branch_dirs(run_dir):
        trace = _read_optional_json(branch / "multi_agent_trace.json")
        if not trace:
            continue
        trace_count += 1
        turn_plan_count += _list_len(trace.get("turn_plans"))
        private_count += _list_len(trace.get("private_knowledge"))
        misunderstanding_count += _list_len(trace.get("misunderstandings"))
        meta = trace.get("generation_meta") if isinstance(trace.get("generation_meta"), dict) else {}
        warnings = meta.get("validator_warnings")
        warning_count += _list_len(warnings)
        validation_status = str(meta.get("validation_status") or "")
        if validation_status == "repaired":
            repaired_count += 1
        if validation_status == "hard_fail":
            hard_fail_count += 1
    return {
        "multi_agent_trace_count": trace_count,
        "turn_plan_count": turn_plan_count,
        "private_knowledge_count": private_count,
        "misunderstanding_count": misunderstanding_count,
        "trace_warning_count": warning_count,
        "trace_repaired_count": repaired_count,
        "trace_hard_fail_count": hard_fail_count,
    }


def _emergence_metrics(report: dict[str, Any]) -> dict[str, Any]:
    nodes = report.get("nodes") if isinstance(report.get("nodes"), list) else []
    high_value = [
        node
        for node in nodes
        if isinstance(node, dict) and node.get("status") == "high_value"
    ]
    return {
        "emergence_status": _artifact_status(report),
        "emergence_node_count": len(nodes),
        "high_value_emergence_count": len(high_value),
    }


def _trigger_reasons(
    state: dict[str, Any],
    trace: dict[str, Any],
    emergence: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    candidate_count = state["state_execution_candidate_count"]
    unresolved = (
        state["state_execution_review_required_count"]
        + state["state_execution_blocked_count"]
    )
    executable = state["state_execution_executable_count"]
    if candidate_count >= 6 and unresolved > executable:
        reasons.append("state_execution_backlog")
    if state["state_execution_high_risk_count"] > 0:
        reasons.append("high_risk_actions")
    if trace["trace_warning_count"] >= 2 or trace["trace_repaired_count"] > 0:
        reasons.append("trace_repair_warnings")
    private_complexity = (
        trace["private_knowledge_count"] + trace["misunderstanding_count"]
    )
    if private_complexity >= 6:
        reasons.append("private_state_complexity")
    if emergence["high_value_emergence_count"] > 0:
        reasons.append("high_value_emergence")
    if trace["trace_hard_fail_count"] > 0:
        reasons.append("trace_hard_fail")
    return reasons


def _status(
    reasons: list[str],
    state_report: dict[str, Any],
    trace_metrics: dict[str, Any],
) -> str:
    if reasons:
        return "triggered"
    if not state_report and trace_metrics["multi_agent_trace_count"] == 0:
        return "insufficient_data"
    return "not_triggered"


def _summary(status: str) -> str:
    if status == "triggered":
        return "当前 run 暴露复杂 runner 评估信号，先做 spike 设计，不直接替换现有 runner。"
    if status == "insufficient_data":
        return "当前 run 缺少状态执行或多 Agent trace 证据，尚不能判断是否需要高级 runner。"
    return "继续使用当前 SceneRunner、multi_agent_trace 与状态执行 overlay；暂不触发高级 runner 重依赖。"


def _next_steps(status: str) -> list[str]:
    if status == "triggered":
        return [
            "先复核高风险动作、review/blocked 状态候选和 trace warning 是否来自规则质量问题。",
            "若自研 runner 无法表达多轮共识、裁判、反思/重试，再评估 LangGraph 局部 runner。",
            "若真实需求是群体仿真环境，再评估 OASIS / CAMEL；仍保持现有 artifact 契约不变。",
        ]
    if status == "insufficient_data":
        return [
            "先补 runner_state_execution_report.json 或 multi_agent_trace.json 证据。",
            "不要在缺少证据时直接接 LangGraph / OASIS / CAMEL。",
        ]
    return [
        "继续使用当前 SceneRunner 与状态执行 overlay。",
        "只有复杂状态流转或群体仿真失败样例增加时，再进入 advanced runner spike。",
    ]


def _state_execution_probe(metrics: dict[str, Any]) -> dict[str, Any] | None:
    if metrics["state_execution_status"] == "missing":
        return None
    unresolved = (
        metrics["state_execution_review_required_count"]
        + metrics["state_execution_blocked_count"]
    )
    executable = metrics["state_execution_executable_count"]
    backlog = (
        metrics["state_execution_candidate_count"] >= 6 and unresolved > executable
    )
    high_risk = metrics["state_execution_high_risk_count"] > 0
    hit = not backlog and not high_risk
    reason = ""
    if backlog:
        reason = "state_execution_backlog"
    elif high_risk:
        reason = "high_risk_actions"
    return {
        "probe_id": "state_execution_backlog",
        "subject": "状态执行候选",
        "hit": hit,
        "reason": reason,
        "observed": {
            "candidate_count": metrics["state_execution_candidate_count"],
            "executable_count": executable,
            "review_required_count": metrics["state_execution_review_required_count"],
            "blocked_count": metrics["state_execution_blocked_count"],
            "high_risk_count": metrics["state_execution_high_risk_count"],
        },
    }


def _trace_warning_probe(metrics: dict[str, Any]) -> dict[str, Any] | None:
    if metrics["multi_agent_trace_count"] == 0:
        return None
    hit = (
        metrics["trace_warning_count"] < 2
        and metrics["trace_repaired_count"] == 0
        and metrics["trace_hard_fail_count"] == 0
    )
    return {
        "probe_id": "trace_repair_warnings",
        "subject": "多 Agent trace 质量",
        "hit": hit,
        "reason": "" if hit else "trace_repair_warnings",
        "observed": {
            "trace_count": metrics["multi_agent_trace_count"],
            "turn_plan_count": metrics["turn_plan_count"],
            "warning_count": metrics["trace_warning_count"],
            "repaired_count": metrics["trace_repaired_count"],
            "hard_fail_count": metrics["trace_hard_fail_count"],
            "private_complexity": (
                metrics["private_knowledge_count"]
                + metrics["misunderstanding_count"]
            ),
        },
    }


def _emergence_probe(metrics: dict[str, Any]) -> dict[str, Any] | None:
    if metrics["emergence_status"] == "missing":
        return None
    hit = metrics["high_value_emergence_count"] == 0
    return {
        "probe_id": "high_value_emergence",
        "subject": "涌现节点复杂度",
        "hit": hit,
        "reason": "" if hit else "high_value_emergence",
        "observed": {
            "node_count": metrics["emergence_node_count"],
            "high_value_count": metrics["high_value_emergence_count"],
        },
    }


def _probe_summary(status: str) -> str:
    if status == "weak":
        return "代表性 runner probe 已收集到复杂状态或 trace 失败样例，先复核自研 runner 能否修复。"
    if status == "insufficient_data":
        return "代表性 runner probe 样本不足，尚不能判断是否需要高级 runner。"
    return "代表性 runner probe 暂未暴露高级 runner 缺口，继续使用当前自研 runner。"


def _probe_next_steps(status: str) -> list[str]:
    if status == "weak":
        return [
            "先按失败样例修复状态执行候选、trace warning 或高价值涌现解释。",
            "若修复后仍需要多轮裁判、反思/重试或共识流，再评估 LangGraph。",
            "若失败样例来自群体仿真环境需求，再评估 OASIS / CAMEL。",
        ]
    if status == "insufficient_data":
        return [
            "先生成 runner_state_execution_report.json、multi_agent_trace.json 或 emergence_nodes.json。",
            "不要在样本不足时直接引入 LangGraph / OASIS / CAMEL。",
        ]
    return [
        "继续使用当前 SceneRunner、multi_agent_trace 与状态执行 overlay。",
        "积累真实复杂 run 失败样例后再复跑 advanced runner probes。",
    ]


def _artifact_status(payload: dict[str, Any]) -> str:
    if not payload:
        return "missing"
    if payload.get("status") == "damaged":
        return "damaged"
    return "ready"


def _list_len(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def _int(value: Any) -> int:
    try:
        return max(0, int(value or 0)) if isinstance(value, (int, float, str)) else 0
    except (TypeError, ValueError):
        return 0

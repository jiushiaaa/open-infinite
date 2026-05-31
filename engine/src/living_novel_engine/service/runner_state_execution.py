"""v0.8.10-A Runner State Execution Spike service.

This module only performs an opt-in dry-run evaluation. It reads existing run
artifacts and writes a new additive report; it never mutates branch
``state_snapshot.json`` files and does not alter ``run_scene`` defaults.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_REPORT_NAME = "runner_state_execution_report.json"
_VERSION = "v0.8.10-a"


class RunnerStateExecutionRequestError(ValueError):
    """非法入参或损坏报告 —— 映射为 HTTP 400。"""


class RunnerStateExecutionConflict(RuntimeError):
    """当前 run 缺少必要 artifact，暂不能评估 —— 映射为 HTTP 409。"""


def _validate_identifier(value: str | None, label: str) -> str:
    ident = (value or "").strip()
    if not ident:
        raise RunnerStateExecutionRequestError(f"缺少 {label}")
    if ".." in ident or not _SAFE_ID_RE.match(ident):
        raise RunnerStateExecutionRequestError(f"invalid {label}")
    return ident


def _outputs_root(outputs_dir: Path | None) -> Path:
    if outputs_dir is not None:
        return outputs_dir
    from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir

    return default_outputs_dir()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise RunnerStateExecutionRequestError(f"{label} 损坏: {path.name}") from exc
    if not isinstance(data, dict):
        raise RunnerStateExecutionRequestError(f"{label} 不是对象: {path.name}")
    return data


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _read_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, OSError) as exc:
        raise RunnerStateExecutionRequestError(f"{label} 损坏: {path.name}") from exc
    if not isinstance(data, dict):
        raise RunnerStateExecutionRequestError(f"{label} 不是对象: {path.name}")
    return data


def _branch_dirs(run_dir: Path) -> list[Path]:
    return sorted(
        p
        for p in run_dir.iterdir()
        if p.is_dir() and (p.name.startswith("branch_") or p.name in {"linear", "baseline"})
    )


def _snapshots_by_branch(run_dir: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for branch in _branch_dirs(run_dir):
        snap = _read_optional_json(branch / "state_snapshot.json")
        if snap:
            out[branch.name] = snap
    return out


def _registry_by_type(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    actions = registry.get("actions") or []
    return {
        str(action.get("action_type") or ""): action
        for action in actions
        if isinstance(action, dict) and action.get("action_type")
    }


def _status_from_score(score: float) -> str:
    if score >= 0.65:
        return "high_value"
    if score < 0.35:
        return "archive"
    return "candidate"


def _branch_hint(step: dict[str, Any], snapshots: dict[str, dict[str, Any]]) -> str:
    axis = str(step.get("branch_axis_id") or "")
    if axis in snapshots:
        return axis
    if axis.startswith("branch_") and axis in snapshots:
        return axis
    return next(iter(snapshots), "")


def _character_state(
    snapshot: dict[str, Any], character_id: str
) -> dict[str, Any]:
    chars = snapshot.get("characters") if isinstance(snapshot, dict) else {}
    if isinstance(chars, dict):
        state = chars.get(character_id)
        if isinstance(state, dict):
            return state
    return {}


def _proposed_deltas(
    step: dict[str, Any],
    *,
    snapshot: dict[str, Any],
    status: str,
) -> list[dict[str, Any]]:
    if status == "blocked":
        return []
    character_id = str(step.get("character_id") or "")
    label = str(step.get("action_label") or step.get("action_type") or "动作")
    action_type = str(step.get("action_type") or "")
    char_state = _character_state(snapshot, character_id)

    if action_type == "verify_information":
        return [
            {
                "character_id": character_id,
                "field": "characters.emotion",
                "old_value": char_state.get("emotion", ""),
                "new_value": "警觉（待查证）",
                "reason": "信息型动作只能成为角色可查证的认知变化。",
            }
        ]
    if action_type == "inspect_resource":
        resources = list(char_state.get("resources") or [])
        return [
            {
                "character_id": character_id,
                "field": "characters.resources",
                "old_value": resources,
                "new_value": resources + [f"外来资源待检：{label}"],
                "reason": "资源注入必须先进入待检状态，不能直接生效。",
            }
        ]
    if action_type == "choose_under_pressure":
        return [
            {
                "character_id": character_id,
                "field": "scene_flags.pending_pressure_actions",
                "old_value": [],
                "new_value": [label],
                "reason": "强制行动降级为处境压力，保留角色自主选择。",
            }
        ]
    return [
        {
            "character_id": character_id,
            "field": "scene_flags.rejected_or_translated_rules",
            "old_value": [],
            "new_value": [label],
            "reason": "规则改写只能拒绝或转译，不能静默污染原世界线。",
        }
    ]


def _candidate_from_step(
    step: dict[str, Any],
    *,
    index: int,
    plan: dict[str, Any],
    registry_entry: dict[str, Any],
    snapshots: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    risk = str(step.get("risk") or registry_entry.get("risk") or "low")
    lineage = str(plan.get("lineage_type") or "")
    failure = str(step.get("failure_reason") or "")
    blockers: list[str] = []
    warnings: list[str] = []

    if lineage == "alternate_novel":
        blockers.append("故事合约冲突：Alternate Novel 不应写回原世界线状态。")
    if risk == "high":
        blockers.append("高风险动作需人工确认，Spike 阶段不执行。")
    if failure:
        warnings.append(failure)

    gate_status = "blocked" if blockers else "review_required" if warnings or risk == "medium" else "executable"
    branch_id = _branch_hint(step, snapshots)
    snapshot = snapshots.get(branch_id, {})
    deltas = _proposed_deltas(step, snapshot=snapshot, status=gate_status)
    source_step = str(step.get("action_id") or f"step_{index:03d}")

    return {
        "candidate_id": f"exec_{index:03d}_{source_step}",
        "source_step_id": source_step,
        "branch_axis_id": step.get("branch_axis_id", ""),
        "branch_id": branch_id,
        "character_id": step.get("character_id", ""),
        "character_name": step.get("character_name", ""),
        "action_type": step.get("action_type", ""),
        "action_label": step.get("action_label", ""),
        "risk": risk,
        "visibility": step.get("visibility", ""),
        "gate_status": gate_status,
        "state_deltas": deltas,
        "blockers": blockers,
        "warnings": warnings,
        "evidence": list(step.get("effects") or [])[:4],
        "source_artifacts": [
            "act_director_plan.json",
            "dynamic_action_registry.yaml",
        ],
    }


def _emergence_summary(run_dir: Path) -> dict[str, Any]:
    report = _read_optional_json(run_dir / "emergence_nodes.json")
    nodes = report.get("nodes") if isinstance(report.get("nodes"), list) else []
    high_value = [
        node for node in nodes
        if isinstance(node, dict) and node.get("status") == "high_value"
    ]
    return {
        "status": "ready" if report else "missing",
        "node_count": len(nodes),
        "high_value_count": len(high_value),
        "recommended_status": _status_from_score(
            max([float(n.get("score") or 0.0) for n in nodes if isinstance(n, dict)] or [0.0])
        ),
    }


def evaluate_runner_state_execution(
    run_id: str, *, outputs_dir: Path | None = None
) -> dict[str, Any]:
    """生成 v0.8.10-A dry-run 状态执行评估报告。"""

    rid = _validate_identifier(run_id, "run_id")
    run_dir = _outputs_root(outputs_dir) / rid
    if not run_dir.is_dir():
        raise FileNotFoundError(f"run 不存在: {rid}")

    plan_path = run_dir / "act_director_plan.json"
    registry_path = run_dir / "dynamic_action_registry.yaml"
    if not plan_path.exists() or not registry_path.exists():
        raise RunnerStateExecutionConflict(
            "缺少动作计划或动作注册表，无法进行状态执行评估。"
        )

    plan = _read_json(plan_path, "动作计划")
    registry = _read_yaml(registry_path, "动作注册表")
    registry_by_type = _registry_by_type(registry)
    snapshots = _snapshots_by_branch(run_dir)
    steps = [s for s in (plan.get("steps") or []) if isinstance(s, dict)]
    candidates = [
        _candidate_from_step(
            step,
            index=index,
            plan=plan,
            registry_entry=registry_by_type.get(str(step.get("action_type") or ""), {}),
            snapshots=snapshots,
        )
        for index, step in enumerate(steps, start=1)
    ]
    executable = sum(1 for c in candidates if c["gate_status"] == "executable")
    review = sum(1 for c in candidates if c["gate_status"] == "review_required")
    blocked = sum(1 for c in candidates if c["gate_status"] == "blocked")
    high_risk = sum(1 for c in candidates if c["risk"] == "high")
    payload = {
        "version": _VERSION,
        "kind": "runner_state_execution_spike",
        "mode": "dry_run",
        "run_id": rid,
        "story_slug": plan.get("story_slug", ""),
        "source_artifacts": [
            "act_director_plan.json",
            "dynamic_action_registry.yaml",
            "emergence_nodes.json",
        ],
        "summary": {
            "candidate_count": len(candidates),
            "executable_count": executable,
            "review_required_count": review,
            "blocked_count": blocked,
            "high_risk_count": high_risk,
            "applied_count": 0,
        },
        "safety": {
            "default_run_scene_unchanged": True,
            "writes_state_snapshot": False,
            "writes_branch_artifacts": False,
            "apply_mode": "dry_run_only",
            "required_before_mvp": [
                "人工确认 high/medium 风险动作",
                "定义 state_delta 白名单与回滚策略",
                "补运行后一致性审计写回",
            ],
        },
        "candidates": candidates,
        "emergence_summary": _emergence_summary(run_dir),
        "warnings": list(plan.get("warnings") or []) + list(registry.get("warnings") or []),
        "created_at": datetime.now().isoformat(),
    }
    (run_dir / _REPORT_NAME).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload


def get_runner_state_execution_report(
    run_id: str, *, outputs_dir: Path | None = None
) -> dict[str, Any]:
    rid = _validate_identifier(run_id, "run_id")
    path = _outputs_root(outputs_dir) / rid / _REPORT_NAME
    if not path.exists():
        raise FileNotFoundError(f"状态执行评估报告不存在: {rid}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise RunnerStateExecutionRequestError(
            f"状态执行评估报告损坏: {rid}"
        ) from exc
    if not isinstance(data, dict):
        raise RunnerStateExecutionRequestError(f"状态执行评估报告不是对象: {rid}")
    return data

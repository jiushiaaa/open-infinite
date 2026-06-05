"""Read-only dossier for worldline continuation and checkpoint replay pages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.project_health import resolve_story_path
from living_novel_engine.service.worldline_state import get_worldline_state

VERSION = "worldline-dossier-v1"


class WorldlineDossierRequestError(ValueError):
    """Invalid worldline dossier request."""


def get_worldline_dossier(
    story_slug: str,
    *,
    worldline_id: str = "main",
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
) -> dict[str, Any]:
    """Collect the state, tasks, checkpoints, and continuation hints for a worldline."""

    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")
    story_path, source_kind = resolve_story_path(sid, projects_dir)
    state = get_worldline_state(sid, worldline_id=wid, projects_dir=projects_dir)
    tasks = _read_tasks(story_path, wid)
    checkpoints = _read_checkpoints(
        sid,
        wid,
        outputs_dir or default_outputs_dir(),
    )
    return {
        "version": VERSION,
        "story_slug": sid,
        "source_kind": source_kind,
        "worldline_id": wid,
        "worldline_state": state,
        "tianming_audit": _tianming_audit(state),
        "task_count": len(tasks),
        "tasks": tasks,
        "checkpoint_count": len(checkpoints),
        "checkpoints": checkpoints,
        "next_actions": _next_actions(state, tasks, checkpoints),
        "boundaries": [
            "世界线档案只读聚合现有状态、任务和检查点，不覆盖根天命书。",
            "继续运行时后续沙盘轮次会读取 source_intervention、tianming_snapshot、causal_debt、branch_state 与 consequence_state。",
            "检查点回放只还原自演证据，恢复或继续仍由用户显式触发。",
        ],
    }


def _read_tasks(story_path: Path, worldline_id: str) -> list[dict[str, Any]]:
    tasks_dir = story_path / "worldlines" / worldline_id / "autopilot_tasks"
    if not tasks_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(tasks_dir.glob("*.json")):
        task = _read_json(path)
        if task:
            rows.append(task)
    rows.sort(
        key=lambda item: str(item.get("updated_at") or item.get("created_at") or ""),
        reverse=True,
    )
    return rows


def _read_checkpoints(
    story_slug: str,
    worldline_id: str,
    root: Path,
) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for report_path in sorted(root.glob("*/autopilot_report.json")):
        report = _read_json(report_path)
        if not report:
            continue
        if report.get("story_slug") != story_slug or report.get("worldline_id") != worldline_id:
            continue
        run_id = str(report.get("run_id") or report_path.parent.name)
        created_at = str(report.get("created_at") or "")
        for checkpoint in report.get("checkpoints") or []:
            if not isinstance(checkpoint, dict):
                continue
            rows.append(_checkpoint_row(run_id, created_at, checkpoint))
    rows.sort(
        key=lambda item: (
            str(item.get("created_at") or ""),
            int(item.get("round_index") or 0),
        ),
        reverse=True,
    )
    return rows


def _checkpoint_row(
    run_id: str,
    created_at: str,
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    consequence = (
        checkpoint.get("consequence_state")
        if isinstance(checkpoint.get("consequence_state"), dict)
        else {}
    )
    return {
        "run_id": run_id,
        "created_at": created_at,
        "checkpoint_id": checkpoint.get("checkpoint_id") or "",
        "round_index": checkpoint.get("round_index") or 0,
        "sandbox_run_id": checkpoint.get("sandbox_run_id") or "",
        "major_event": checkpoint.get("major_event") or "",
        "stage": checkpoint.get("stage") or "",
        "anchor_pressure": checkpoint.get("anchor_pressure") or "",
        "causal_debt": checkpoint.get("causal_debt") or "",
        "consequence_state": {
            "status": consequence.get("status") or "none",
            "summary": consequence.get("summary") or "",
            "domains": consequence.get("domains") or {},
            "next_round_hint": consequence.get("next_round_hint") or "",
        },
        "who_remembered_what": checkpoint.get("who_remembered_what") or [],
        "next_story_possibilities": checkpoint.get("next_story_possibilities") or [],
    }


def _next_actions(
    state: dict[str, Any],
    tasks: list[dict[str, Any]],
    checkpoints: list[dict[str, Any]],
) -> list[dict[str, str]]:
    worldline_id = str(state.get("current_worldline") or "")
    hint = (
        state.get("continuation_inputs")
        if isinstance(state.get("continuation_inputs"), dict)
        else {}
    )
    actions = [
        {
            "action": "continue_sandbox",
            "label": "继续下一轮沙盘",
            "reason": str(hint.get("major_event_hint") or "沿当前世界线读取干预约束、因果债和具象代偿继续运行。"),
            "worldline_id": worldline_id,
        }
    ]
    if tasks:
        actions.append(
            {
                "action": "resume_or_pause_autopilot",
                "label": "管理世界自演任务",
                "reason": "可查看最近任务状态，必要时暂停、恢复或从检查点继续判断。",
                "worldline_id": worldline_id,
            }
        )
    if checkpoints:
        first = checkpoints[0]
        actions.append(
            {
                "action": "replay_checkpoint",
                "label": "回放最新检查点",
                "reason": str(first.get("stage") or "回看世界状态变化证据。"),
                "run_id": str(first.get("run_id") or ""),
                "checkpoint_id": str(first.get("checkpoint_id") or ""),
            }
        )
    return actions


def _tianming_audit(state: dict[str, Any]) -> dict[str, Any]:
    snapshot = (
        state.get("tianming_snapshot")
        if isinstance(state.get("tianming_snapshot"), dict)
        else {}
    )
    if snapshot:
        return {
            "status": snapshot.get("status") or "snapshot_present",
            "audit_status": snapshot.get("audit_status") or "pending_confirmation",
            "requires_confirmation": bool(snapshot.get("requires_confirmation", False)),
            "root_tianming_mutated": bool(snapshot.get("root_tianming_mutated", False)),
            "artifact": snapshot.get("artifact") or "",
        }
    return {
        "status": "root_tianming_active",
        "audit_status": "no_branch_snapshot",
        "requires_confirmation": False,
        "root_tianming_mutated": False,
        "artifact": "",
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorldlineDossierRequestError(f"{path.name} 无法解析：{exc}") from exc
    return raw if isinstance(raw, dict) else {}


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise WorldlineDossierRequestError(f"{label} 无效")
    return checked

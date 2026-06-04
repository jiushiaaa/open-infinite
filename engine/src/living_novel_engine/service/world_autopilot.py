"""World Sandbox Loop v6: local world autopilot."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.world_sandbox import run_sandbox_round

VERSION = "world-autopilot-v1"
ARTIFACT = "autopilot_report.json"


class WorldAutopilotRequestError(ValueError):
    """Invalid world autopilot request."""


def run_world_autopilot(
    story_slug: str,
    *,
    seed_event: str,
    objective_type: str = "rounds",
    stop_event: str = "",
    time_limit: str = "",
    round_limit: int = 3,
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
    worldline_id: str = "main",
) -> dict[str, Any]:
    """Run multiple sandbox rounds and write an autopilot report."""

    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")
    event = " ".join(str(seed_event or "").split())
    if not event:
        raise WorldAutopilotRequestError("缺少 seed_event（世界自演起点事件）")
    objective = _objective(objective_type)
    target_event = " ".join(str(stop_event or "").split())
    target_time = " ".join(str(time_limit or "").split())
    limit = max(1, min(10, int(round_limit or 1)))
    root = outputs_dir or default_outputs_dir()
    run_id = _new_run_id()
    run_dir = root / run_id
    checkpoints_dir = run_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    sandbox_runs: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    current_event = event
    stop_reason = "round_limit_reached"
    for round_index in range(1, limit + 1):
        sandbox = run_sandbox_round(
            sid,
            major_event=current_event,
            projects_dir=projects_dir,
            outputs_dir=root,
            worldline_id=wid,
        )
        sandbox_runs.append(
            {
                "round_index": round_index,
                "sandbox_run_id": sandbox["run_id"],
                "major_event": current_event,
                "character_action_count": sandbox["summary"]["character_action_count"],
            }
        )
        checkpoint = _checkpoint(round_index, sandbox, objective, current_event)
        checkpoints.append(checkpoint)
        (checkpoints_dir / f"checkpoint_{round_index:03d}.json").write_text(
            json.dumps(checkpoint, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        if objective == "anchor_change" and _anchor_changed(current_event, sandbox):
            stop_reason = "anchor_change_detected"
            break
        if objective == "event" and _event_reached(current_event, sandbox, target_event):
            stop_reason = "target_event_reached"
            break
        if objective == "time" and _time_limit_reached(round_index, target_time):
            stop_reason = "time_limit_reached"
            break
        current_event = _next_event(sandbox, round_index)

    objective_payload = {
        "type": objective,
        "round_limit": limit,
        "seed_event": event,
    }
    if objective == "event":
        objective_payload["stop_event"] = target_event
    if objective == "time":
        objective_payload["time_limit"] = target_time

    report = {
        "version": VERSION,
        "artifact": ARTIFACT,
        "run_id": run_id,
        "story_slug": sid,
        "worldline_id": wid,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "objective": objective_payload,
        "rounds_completed": len(checkpoints),
        "stop_reason": stop_reason,
        "sandbox_runs": sandbox_runs,
        "checkpoints": checkpoints,
        "final_world_stage": _final_stage(checkpoints),
        "artifacts": {
            "autopilot_report": ARTIFACT,
            "checkpoints_dir": "checkpoints",
        },
        "boundaries": [
            "世界自演复用 sandbox round 和主观记忆链，不调用外部 provider。",
            "不改 run_scene 默认行为，不覆盖既有章节或世界线 artifact。",
            "每轮自动生成检查点，用户可醒来后查看世界阶段变化。",
        ],
        "next_steps": [
            "多视角活体小说可读取 checkpoints 生成角色个人卷和事件多视角。",
            "后续可把事件和时间目标扩展为可视化时间轴与命中证据。",
        ],
    }
    (run_dir / ARTIFACT).write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def _checkpoint(
    round_index: int,
    sandbox: dict[str, Any],
    objective: str,
    event: str,
) -> dict[str, Any]:
    round_record = sandbox["rounds"][0]
    delta = round_record["world_state_delta"]
    return {
        "round_index": round_index,
        "sandbox_run_id": sandbox["run_id"],
        "major_event": event,
        "objective_type": objective,
        "stage": f"第 {round_index} 轮后，{delta.get('trigger', '世界')} 已改变。",
        "anchor_pressure": delta.get("anchor_pressure"),
        "causal_debt": delta.get("causal_debt"),
        "character_action_count": len(round_record.get("character_actions", [])),
        "next_story_possibilities": round_record.get("next_story_possibilities", []),
    }


def _anchor_changed(event: str, sandbox: dict[str, Any]) -> bool:
    if any(token in event for token in ("死亡", "失去主锚点", "失锚", "锚点变化")):
        return True
    delta = sandbox["rounds"][0].get("world_state_delta", {})
    return str(delta.get("anchor_pressure") or "") in {"剧烈上升", "失锚"}


def _event_reached(event: str, sandbox: dict[str, Any], target: str) -> bool:
    if not target:
        return False
    if target in event:
        return True
    possibilities = sandbox["rounds"][0].get("next_story_possibilities", [])
    return any(
        target in str(item.get("title") or "") or target in str(item.get("brief") or "")
        for item in possibilities
    )


def _time_limit_reached(round_index: int, target: str) -> bool:
    if not target:
        return False
    return round_index >= 2


def _next_event(sandbox: dict[str, Any], round_index: int) -> str:
    possibilities = sandbox["rounds"][0].get("next_story_possibilities", [])
    if possibilities:
        brief = possibilities[0].get("brief") or possibilities[0].get("title")
        if brief:
            return f"第 {round_index + 1} 轮：{brief}"
    return f"第 {round_index + 1} 轮：世界继续消化上一轮选择。"


def _final_stage(checkpoints: list[dict[str, Any]]) -> dict[str, str]:
    if not checkpoints:
        return {"stage": "未启动", "summary": "世界尚未自演。"}
    last = checkpoints[-1]
    return {
        "stage": str(last.get("stage") or "世界已推进"),
        "summary": f"已完成 {len(checkpoints)} 个检查点，最新因果债：{last.get('causal_debt')}",
    }


def _objective(value: str) -> str:
    raw = str(value or "rounds").strip()
    if raw in {"rounds", "event", "time", "anchor_change"}:
        return raw
    return "rounds"


def _new_run_id() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"autopilot_{ts}_{uuid.uuid4().hex[:6]}"


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise WorldAutopilotRequestError(f"{label} 无效")
    return checked

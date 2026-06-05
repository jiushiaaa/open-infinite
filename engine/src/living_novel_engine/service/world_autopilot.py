"""World Sandbox Loop v6: local world autopilot."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.project_health import resolve_story_path
from living_novel_engine.service.world_sandbox import run_sandbox_round

VERSION = "world-autopilot-v1"
ARTIFACT = "autopilot_report.json"
READABLE_ENTRY_VERSION = "world-autopilot-readable-entry-v1"


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
    resume_from_run_id: str = "",
    resume_from_checkpoint: str = "",
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
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    run_dir = root / run_id
    checkpoints_dir = run_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    recovery_source = _load_recovery_source(
        resume_from_run_id,
        resume_from_checkpoint,
        outputs_dir=root,
    )
    if recovery_source:
        current_event = _resume_event(recovery_source)
    else:
        current_event = event

    sandbox_runs: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    stop_reason = "round_limit_reached"
    status = "completed"
    failure: dict[str, Any] | None = None
    stop_condition: dict[str, Any] = {
        "type": objective,
        "matched": False,
        "evidence": "达到轮数上限。",
        "round_index": 0,
    }
    for round_index in range(1, limit + 1):
        try:
            sandbox = run_sandbox_round(
                sid,
                major_event=current_event,
                projects_dir=projects_dir,
                outputs_dir=root,
                worldline_id=wid,
            )
        except Exception as exc:
            if not checkpoints and isinstance(
                exc,
                (FileNotFoundError, WorldAutopilotRequestError),
            ):
                raise
            status = "failed"
            stop_reason = "autopilot_failed"
            failure = {
                "message": str(exc),
                "failed_round": round_index,
                "latest_checkpoint": (
                    checkpoints[-1].get("checkpoint_id") if checkpoints else ""
                ),
                "recoverable": bool(checkpoints),
            }
            stop_condition = {
                "type": objective,
                "matched": False,
                "evidence": f"第 {round_index} 轮中断：{exc}",
                "round_index": round_index,
            }
            break
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
            stop_condition = _stop_condition(
                objective,
                True,
                checkpoint,
                "锚点压力或事件描述已出现失锚/锚点变化。",
            )
            break
        if objective == "causal_debt" and _causal_debt_burst(
            current_event,
            sandbox,
            checkpoint,
        ):
            stop_reason = "causal_debt_burst_detected"
            stop_condition = _stop_condition(
                objective,
                True,
                checkpoint,
                f"因果债已爆发：{checkpoint.get('causal_debt')}",
            )
            break
        if objective == "awakening" and _awakening_detected(sandbox):
            stop_reason = "character_awareness_detected"
            stop_condition = _stop_condition(
                objective,
                True,
                checkpoint,
                "至少一名角色进入 L5 觉醒。",
            )
            break
        if objective == "event" and _event_reached(current_event, sandbox, target_event):
            stop_reason = "target_event_reached"
            stop_condition = _stop_condition(
                objective,
                True,
                checkpoint,
                f"目标事件已出现：{target_event}",
            )
            break
        if objective == "time" and _time_limit_reached(round_index, target_time):
            stop_reason = "time_limit_reached"
            stop_condition = _stop_condition(
                objective,
                True,
                checkpoint,
                f"世界内时间推进到：{target_time}",
            )
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

    recovery = _recovery_payload(
        checkpoints,
        recovery_source=recovery_source,
        latest_report_run_id=run_id,
    )
    progress = {
        "current_round": len(checkpoints),
        "target_round": limit,
        "percent": _progress_percent(len(checkpoints), limit, status),
    }
    report = {
        "version": VERSION,
        "artifact": ARTIFACT,
        "status": status,
        "run_id": run_id,
        "story_slug": sid,
        "worldline_id": wid,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "objective": objective_payload,
        "rounds_completed": len(checkpoints),
        "stop_reason": stop_reason,
        "stop_condition": stop_condition,
        "task": {
            "task_id": task_id,
            "status": status,
            "can_pause": True,
            "can_resume": True,
            "checkpoint_replay": True,
        },
        "progress": progress,
        "sandbox_runs": sandbox_runs,
        "checkpoints": checkpoints,
        "final_world_stage": _final_stage(checkpoints),
        "overnight_report": _overnight_report(checkpoints, recovery),
        "recovery": recovery,
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
    report["readable_entry"] = _readable_entry(report)
    if failure is not None:
        report["failure"] = failure
    (run_dir / ARTIFACT).write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    task_payload = {
        "version": VERSION,
        "task_id": task_id,
        "status": status,
        "story_slug": sid,
        "worldline_id": wid,
        "latest_report_run_id": run_id,
        "created_at": report["created_at"],
        "updated_at": report["created_at"],
        "progress": progress,
        "request": {
            "seed_event": event,
            "objective_type": objective,
            "stop_event": target_event,
            "time_limit": target_time,
            "round_limit": limit,
            "worldline_id": wid,
        },
        "resume_from_checkpoint": recovery.get("resume_from_checkpoint") or "",
        "recovery": recovery,
    }
    if failure is not None:
        task_payload["failure"] = failure
    if recovery_source:
        task_payload["recovered_from"] = recovery_source
    _write_task(
        sid,
        wid,
        task_id,
        task_payload,
        projects_dir=projects_dir,
    )
    return report


def get_world_autopilot_task(
    story_slug: str,
    task_id: str,
    *,
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
    worldline_id: str = "main",
) -> dict[str, Any]:
    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")
    tid = _checked_id(task_id, "task_id")
    return _read_task(sid, wid, tid, projects_dir=projects_dir)


def pause_world_autopilot_task(
    story_slug: str,
    task_id: str,
    *,
    projects_dir: Path | None = None,
    worldline_id: str = "main",
) -> dict[str, Any]:
    task = get_world_autopilot_task(
        story_slug,
        task_id,
        projects_dir=projects_dir,
        worldline_id=worldline_id,
    )
    task["status"] = "paused"
    task["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _write_task(
        story_slug,
        worldline_id,
        task_id,
        task,
        projects_dir=projects_dir,
    )
    return task


def resume_world_autopilot_task(
    story_slug: str,
    task_id: str,
    *,
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
    worldline_id: str = "main",
) -> dict[str, Any]:
    task = get_world_autopilot_task(
        story_slug,
        task_id,
        projects_dir=projects_dir,
        outputs_dir=outputs_dir,
        worldline_id=worldline_id,
    )
    if task.get("status") == "failed" and task.get("resume_from_checkpoint"):
        request = task.get("request") if isinstance(task.get("request"), dict) else {}
        progress = task.get("progress") if isinstance(task.get("progress"), dict) else {}
        target_round = int(progress.get("target_round") or request.get("round_limit") or 1)
        current_round = int(progress.get("current_round") or 0)
        remaining_rounds = max(1, target_round - current_round)
        report = run_world_autopilot(
            story_slug,
            seed_event=str(request.get("seed_event") or "从检查点继续世界自演。"),
            objective_type=str(request.get("objective_type") or "rounds"),
            stop_event=str(request.get("stop_event") or ""),
            time_limit=str(request.get("time_limit") or ""),
            round_limit=remaining_rounds,
            projects_dir=projects_dir,
            outputs_dir=outputs_dir,
            worldline_id=worldline_id,
            resume_from_run_id=str(task.get("latest_report_run_id") or ""),
            resume_from_checkpoint=str(task.get("resume_from_checkpoint") or ""),
        )
        task["status"] = report.get("status", "completed")
        task["updated_at"] = datetime.now().isoformat(timespec="seconds")
        task["latest_report_run_id"] = report["run_id"]
        task["progress"] = report.get("progress", {})
        task["recovered_from"] = report.get("recovery", {}).get("resumed_from", {})
        task["recovery_child_task_id"] = report.get("task", {}).get("task_id", "")
        task.pop("failure", None)
        _write_task(
            story_slug,
            worldline_id,
            task_id,
            task,
            projects_dir=projects_dir,
        )
        return task
    task["status"] = (
        "running" if task.get("status") == "paused" else task.get("status", "running")
    )
    task["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _write_task(
        story_slug,
        worldline_id,
        task_id,
        task,
        projects_dir=projects_dir,
    )
    return task


def replay_world_autopilot_checkpoint(
    run_id: str,
    *,
    checkpoint_id: str,
    outputs_dir: Path | None = None,
) -> dict[str, Any]:
    rid = _checked_id(run_id, "run_id")
    cid = _checked_id(checkpoint_id, "checkpoint_id")
    filename = cid if cid.endswith(".json") else f"{cid}.json"
    root = outputs_dir or default_outputs_dir()
    path = root / rid / "checkpoints" / filename
    if not path.exists():
        raise FileNotFoundError(f"检查点不存在: {cid}")
    checkpoint = _read_json(path)
    report = _read_autopilot_report(rid, root=root)
    return {
        "version": VERSION,
        "run_id": rid,
        "checkpoint_id": cid,
        "checkpoint": checkpoint,
        "replay": {
            "sandbox_run_id": checkpoint.get("sandbox_run_id") or "",
            "major_event": checkpoint.get("major_event") or "",
            "can_resume_from_here": True,
            "resume_hint": f"可从 {checkpoint.get('checkpoint_id') or cid} 继续世界自演。",
        },
        "readable_entry": _readable_entry(report, focus_checkpoint_id=cid),
    }


def get_world_autopilot_readable_entry(
    run_id: str,
    *,
    outputs_dir: Path | None = None,
) -> dict[str, Any]:
    """Return the wake-up reading entry for a world autopilot report."""

    rid = _checked_id(run_id, "run_id")
    root = outputs_dir or default_outputs_dir()
    report = _read_autopilot_report(rid, root=root)
    cached = report.get("readable_entry")
    if isinstance(cached, dict) and cached.get("version") == READABLE_ENTRY_VERSION:
        return cached
    return _readable_entry(report)


def _checkpoint(
    round_index: int,
    sandbox: dict[str, Any],
    objective: str,
    event: str,
) -> dict[str, Any]:
    round_record = sandbox["rounds"][0]
    delta = round_record["world_state_delta"]
    state = sandbox.get("worldline_state") if isinstance(sandbox.get("worldline_state"), dict) else {}
    consequence = (
        state.get("consequence_state")
        if isinstance(state.get("consequence_state"), dict)
        else {}
    )
    scene_beats = _scene_beats(
        round_index=round_index,
        event=event,
        sandbox=sandbox,
        round_record=round_record,
        delta=delta,
        consequence=consequence,
    )
    chapter_seed = _chapter_seed(scene_beats)
    return {
        "checkpoint_id": f"checkpoint_{round_index:03d}",
        "round_index": round_index,
        "sandbox_run_id": sandbox["run_id"],
        "major_event": event,
        "objective_type": objective,
        "stage": f"第 {round_index} 轮后，{delta.get('trigger', '世界')} 已改变。",
        "anchor_pressure": delta.get("anchor_pressure"),
        "causal_debt": delta.get("causal_debt"),
        "consequence_state": (
            {
                "status": consequence.get("status") or "active",
                "summary": consequence.get("summary") or "",
                "domains": consequence.get("domains") or {},
                "next_round_hint": consequence.get("next_round_hint") or "",
            }
            if consequence
            else {"status": "none", "summary": "", "domains": {}}
        ),
        "character_action_count": len(round_record.get("character_actions", [])),
        "next_story_possibilities": round_record.get("next_story_possibilities", []),
        "who_remembered_what": [
            {
                "character_id": action.get("character_id"),
                "remembered": action.get("memory_seed", {}).get("inferred", [""])[0]
                if isinstance(action.get("memory_seed"), dict)
                else "",
            }
            for action in round_record.get("character_actions", [])
            if isinstance(action, dict)
        ],
        "scene_beats": scene_beats,
        "chapter_seed": chapter_seed,
    }


def _scene_beats(
    *,
    round_index: int,
    event: str,
    sandbox: dict[str, Any],
    round_record: dict[str, Any],
    delta: dict[str, Any],
    consequence: dict[str, Any],
) -> list[dict[str, Any]]:
    actions = [
        action
        for action in round_record.get("character_actions", [])
        if isinstance(action, dict)
    ]
    first = actions[0] if actions else {}
    second = actions[1] if len(actions) > 1 else {}
    first_name = str(first.get("character_name") or "主锚点")
    second_name = str(second.get("character_name") or "另一名角色")
    visible_action = _action_fragment(
        first.get("visible_action") or first.get("action") or "没有公开行动",
        first_name,
    )
    true_intent = _trim(first.get("true_intent") or first.get("stance") or "仍在权衡", 80)
    risk = _trim(first.get("risk") or "误判会把私人选择推成公共后果", 80)
    consequence_text = _trim(
        consequence.get("summary")
        or delta.get("causal_debt")
        or "因果债尚未具象，但世界已经开始记账",
        90,
    )
    possibility = _first_possibility(round_record)
    event_text = _strip_terminal_punctuation(_trim(event, 48))
    scene_hook = (
        f"第 {round_index} 轮，{event_text}。{first_name}{visible_action}，"
        f"却把真正意图压在心底。"
    )
    character_miscalculation = (
        f"{first_name}以为{true_intent}足以保住主动；{second_name}却只能按自己掌握的半截消息判断，"
        f"把沉默、试探或迟疑读成新的威胁。"
    )
    materialized_consequence = (
        f"世界没有替任何人解释，它把代价落成可见压力：{consequence_text}。"
    )
    conflict_escalation = (
        f"{risk}；锚点压力为{delta.get('anchor_pressure') or '未明'}，"
        f"因果债为{delta.get('causal_debt') or '未明'}，私人误会被推向下一场公开冲突。"
    )
    chapter_handoff = possibility or (
        f"下一章应从{first_name}是否继续隐瞒，以及{second_name}是否误信这半截真相写起。"
    )
    return [
        {
            "beat_type": "opening_hook",
            "label": "开场钩子",
            "body": scene_hook,
            "focus_character_id": first.get("character_id") or "",
            "evidence_refs": [f"outputs/{sandbox.get('run_id')}/sandbox_rounds.jsonl"],
        },
        {
            "beat_type": "miscalculation",
            "label": "人物误判",
            "body": character_miscalculation,
            "focus_character_id": second.get("character_id") or first.get("character_id") or "",
            "evidence_refs": [f"outputs/{sandbox.get('run_id')}/subjective_memory_delta.json"],
        },
        {
            "beat_type": "materialized_consequence",
            "label": "代偿显形",
            "body": materialized_consequence,
            "focus_character_id": "",
            "evidence_refs": ["worldline_state.json#consequence_state"],
        },
        {
            "beat_type": "conflict_escalation",
            "label": "冲突升级",
            "body": conflict_escalation,
            "focus_character_id": first.get("character_id") or "",
            "evidence_refs": [f"outputs/{sandbox.get('run_id')}/sandbox_summary.json"],
        },
        {
            "beat_type": "handoff",
            "label": "下一章悬念",
            "body": chapter_handoff,
            "focus_character_id": first.get("character_id") or "",
            "evidence_refs": [f"outputs/{sandbox.get('run_id')}/sandbox_rounds.jsonl#next_story_possibilities"],
        },
    ]


def _chapter_seed(scene_beats: list[dict[str, Any]]) -> dict[str, str]:
    by_type = {str(beat.get("beat_type")): str(beat.get("body") or "") for beat in scene_beats}
    return {
        "opening_hook": by_type.get("opening_hook", ""),
        "viewpoint_misread": by_type.get("miscalculation", ""),
        "consequence_pressure": by_type.get("materialized_consequence", ""),
        "conflict_turn": by_type.get("conflict_escalation", ""),
        "next_chapter_hook": by_type.get("handoff", ""),
    }


def _narrative_timeline(checkpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    for checkpoint in checkpoints:
        seed = checkpoint.get("chapter_seed") if isinstance(checkpoint.get("chapter_seed"), dict) else {}
        timeline.append(
            {
                "round_index": checkpoint.get("round_index"),
                "checkpoint_id": checkpoint.get("checkpoint_id"),
                "sandbox_run_id": checkpoint.get("sandbox_run_id"),
                "scene_hook": seed.get("opening_hook") or "",
                "character_miscalculation": seed.get("viewpoint_misread") or "",
                "materialized_consequence": seed.get("consequence_pressure") or "",
                "conflict_escalation": seed.get("conflict_turn") or "",
                "chapter_handoff": seed.get("next_chapter_hook") or "",
                "evidence_refs": [
                    f"outputs/{checkpoint.get('sandbox_run_id')}/sandbox_rounds.jsonl",
                    f"outputs/{checkpoint.get('sandbox_run_id')}/subjective_memory_delta.json",
                    "worldline_state.json#consequence_state",
                ],
            }
        )
    return timeline


def _first_possibility(round_record: dict[str, Any]) -> str:
    possibilities = round_record.get("next_story_possibilities", [])
    for item in possibilities if isinstance(possibilities, list) else []:
        if not isinstance(item, dict):
            continue
        text = str(item.get("brief") or item.get("title") or "").strip()
        if text:
            return _trim(text, 100)
    return ""


def _trim(value: Any, limit: int = 80) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _action_fragment(value: Any, character_name: str) -> str:
    text = _strip_terminal_punctuation(_trim(value, 80))
    name = str(character_name or "").strip()
    if name and text.startswith(name):
        text = text[len(name) :].lstrip("，,。 ")
    if not text:
        return "没有公开行动"
    if text.startswith(("在", "向", "把", "将", "以", "用", "假意", "选择", "故意")):
        return text
    return f"选择{text}"


def _strip_terminal_punctuation(value: str) -> str:
    return str(value or "").rstrip("。.!！?？；;，, ")


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


def _causal_debt_burst(
    event: str,
    sandbox: dict[str, Any],
    checkpoint: dict[str, Any],
) -> bool:
    if any(token in event for token in ("因果债爆发", "因果债失控", "代偿爆发")):
        return True
    delta = sandbox["rounds"][0].get("world_state_delta", {})
    debt = str(delta.get("causal_debt") or checkpoint.get("causal_debt") or "")
    return any(token in debt for token in ("高", "爆发", "失控", "high", "critical"))


def _awakening_detected(sandbox: dict[str, Any]) -> bool:
    actions = sandbox["rounds"][0].get("character_actions", [])
    return any(
        isinstance(action, dict)
        and isinstance(action.get("awareness"), dict)
        and action["awareness"].get("level") == "L5"
        for action in actions
    )


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


def _readable_entry(
    report: dict[str, Any],
    *,
    focus_checkpoint_id: str = "",
) -> dict[str, Any]:
    checkpoints = [
        item
        for item in report.get("checkpoints", [])
        if isinstance(item, dict)
    ]
    latest = _pick_checkpoint(checkpoints, focus_checkpoint_id)
    story_slug = str(report.get("story_slug") or "")
    worldline_id = str(report.get("worldline_id") or "main")
    run_id = str(report.get("run_id") or "")
    checkpoint_id = str(latest.get("checkpoint_id") or "")
    protagonist = _protagonist_from_checkpoint(latest)
    routes = _readable_routes(
        story_slug=story_slug,
        worldline_id=worldline_id,
        run_id=run_id,
        checkpoint_id=checkpoint_id,
    )
    overnight = (
        report.get("overnight_report")
        if isinstance(report.get("overnight_report"), dict)
        else {}
    )
    consequence = (
        latest.get("consequence_state")
        if isinstance(latest.get("consequence_state"), dict)
        else {}
    )
    timeline = (
        overnight.get("narrative_timeline")
        if isinstance(overnight.get("narrative_timeline"), list)
        else []
    )
    return {
        "version": READABLE_ENTRY_VERSION,
        "story_slug": story_slug,
        "worldline_id": worldline_id,
        "run_id": run_id,
        "latest_checkpoint": {
            "checkpoint_id": checkpoint_id,
            "round_index": latest.get("round_index") or 0,
            "stage": latest.get("stage") or "世界尚未留下检查点。",
            "major_event": latest.get("major_event") or "",
            "sandbox_run_id": latest.get("sandbox_run_id") or "",
        },
        "protagonist": protagonist,
        "routes": routes,
        "primary_actions": _readable_actions(
            routes=routes,
            latest=latest,
            protagonist=protagonist,
        ),
        "state_change_explanation": {
            "headline": overnight.get("what_happened")
            or report.get("final_world_stage", {}).get("summary")
            or "世界自演已结束。",
            "why_world_changed": overnight.get("why_world_changed")
            or _why_world_changed(latest),
            "stop_evidence": (
                report.get("stop_condition", {}).get("evidence")
                if isinstance(report.get("stop_condition"), dict)
                else ""
            ),
            "narrative_thread": _narrative_thread(timeline, latest),
        },
        "memory_readout": {
            "summary": _memory_summary(latest),
            "who_remembered_what": latest.get("who_remembered_what") or [],
        },
        "causal_debt_readout": {
            "summary": consequence.get("summary")
            or latest.get("causal_debt")
            or "因果债尚未显形，但世界已经记账。",
            "level": latest.get("causal_debt") or "",
            "next_round_hint": consequence.get("next_round_hint") or "",
            "domains": consequence.get("domains") or {},
        },
        "context_bridge": [
            "从结果页先回放最近关键检查点，确认世界状态为何改变。",
            "再进入角色个人卷，看主角记住了什么、误读了什么。",
            "随后切到事件多视角，比较同一事件在不同角色心中的偏差。",
            "最后回到连续阅读，沿下一章悬念继续读下去。",
        ],
        "boundaries": [
            "readable_entry 只派生自 autopilot_report 与检查点，不改旧 artifact 契约。",
            "连续阅读、角色个人卷和事件多视角入口可在资料未完备时先作为世界内部卷宗落点。",
        ],
    }


def _pick_checkpoint(
    checkpoints: list[dict[str, Any]],
    focus_checkpoint_id: str,
) -> dict[str, Any]:
    if focus_checkpoint_id:
        for checkpoint in checkpoints:
            if checkpoint.get("checkpoint_id") == focus_checkpoint_id:
                return checkpoint
    return checkpoints[-1] if checkpoints else {}


def _readable_routes(
    *,
    story_slug: str,
    worldline_id: str,
    run_id: str,
    checkpoint_id: str,
) -> dict[str, str]:
    base = (
        f"#/world/{story_slug}/worldlines/{worldline_id}"
        if story_slug and worldline_id
        else "#/"
    )
    return {
        "worldline_dossier": base,
        "latest_checkpoint": (
            f"{base}/checkpoints/{run_id}/{checkpoint_id}"
            if run_id and checkpoint_id
            else base
        ),
        "protagonist_volume": f"{base}/reading/character_volume",
        "event_multi_perspective": f"{base}/reading/event_multi_perspective",
        "continuous_reading": f"{base}/reading/continuous_reading",
    }


def _readable_actions(
    *,
    routes: dict[str, str],
    latest: dict[str, Any],
    protagonist: dict[str, str],
) -> list[dict[str, Any]]:
    stage = str(latest.get("stage") or "最近检查点")
    character_label = protagonist.get("character_name") or protagonist.get("character_id") or "主角"
    return [
        {
            "id": "latest_checkpoint",
            "label": "先看最近关键检查点",
            "route": routes["latest_checkpoint"],
            "reason": stage,
            "status": "ready" if latest else "partial",
        },
        {
            "id": "protagonist_volume",
            "label": f"读{character_label}个人卷",
            "route": routes["protagonist_volume"],
            "reason": _memory_summary(latest),
            "status": "ready",
        },
        {
            "id": "event_multi_perspective",
            "label": "比较关键事件多视角",
            "route": routes["event_multi_perspective"],
            "reason": "同一轮事件会带着各自的信息差、误判和隐瞒进入卷宗。",
            "status": "ready",
        },
        {
            "id": "continuous_reading",
            "label": "继续下一段正文",
            "route": routes["continuous_reading"],
            "reason": _next_chapter_reason(latest),
            "status": "ready",
        },
    ]


def _protagonist_from_checkpoint(checkpoint: dict[str, Any]) -> dict[str, str]:
    memories = checkpoint.get("who_remembered_what") or []
    for item in memories if isinstance(memories, list) else []:
        if not isinstance(item, dict):
            continue
        character_id = str(item.get("character_id") or "").strip()
        if character_id:
            return {
                "character_id": character_id,
                "character_name": character_id,
            }
    for beat in checkpoint.get("scene_beats") or []:
        if not isinstance(beat, dict):
            continue
        character_id = str(beat.get("focus_character_id") or "").strip()
        if character_id:
            return {
                "character_id": character_id,
                "character_name": character_id,
            }
    return {"character_id": "", "character_name": "主角"}


def _why_world_changed(checkpoint: dict[str, Any]) -> str:
    if not checkpoint:
        return "世界尚未推进。"
    consequence = (
        checkpoint.get("consequence_state")
        if isinstance(checkpoint.get("consequence_state"), dict)
        else {}
    )
    summary = str(consequence.get("summary") or "").strip()
    return (
        f"锚点压力 {checkpoint.get('anchor_pressure') or '未明'}，"
        f"因果债 {checkpoint.get('causal_debt') or '未明'}。"
        + (f"具象代偿：{summary}" if summary else "")
    )


def _memory_summary(checkpoint: dict[str, Any]) -> str:
    memories = [
        item
        for item in checkpoint.get("who_remembered_what", [])
        if isinstance(item, dict)
    ]
    if not memories:
        return "本轮尚未留下明确主观记忆。"
    first = memories[0]
    who = first.get("character_id") or "角色"
    remembered = first.get("remembered") or "记住了本轮变化"
    suffix = f"；另有 {len(memories) - 1} 人留下记忆" if len(memories) > 1 else ""
    return f"{who}记住：{remembered}{suffix}。"


def _next_chapter_reason(checkpoint: dict[str, Any]) -> str:
    seed = (
        checkpoint.get("chapter_seed")
        if isinstance(checkpoint.get("chapter_seed"), dict)
        else {}
    )
    return (
        seed.get("next_chapter_hook")
        or seed.get("opening_hook")
        or "从最近检查点留下的误会、代偿和因果债继续读。"
    )


def _narrative_thread(
    timeline: list[Any],
    latest: dict[str, Any],
) -> list[dict[str, Any]]:
    if timeline:
        return [
            {
                "round_index": item.get("round_index"),
                "checkpoint_id": item.get("checkpoint_id"),
                "scene_hook": item.get("scene_hook") or "",
                "turn": item.get("character_miscalculation") or "",
                "consequence": item.get("materialized_consequence") or "",
                "handoff": item.get("chapter_handoff") or "",
            }
            for item in timeline
            if isinstance(item, dict)
        ]
    if not latest:
        return []
    return [
        {
            "round_index": latest.get("round_index"),
            "checkpoint_id": latest.get("checkpoint_id"),
            "scene_hook": latest.get("major_event") or "",
            "turn": _memory_summary(latest),
            "consequence": _why_world_changed(latest),
            "handoff": _next_chapter_reason(latest),
        }
    ]


def _objective(value: str) -> str:
    raw = str(value or "rounds").strip()
    if raw in {
        "rounds",
        "event",
        "time",
        "anchor_change",
        "causal_debt",
        "awakening",
        "lost_anchor",
    }:
        return raw
    return "rounds"


def _overnight_report(
    checkpoints: list[dict[str, Any]],
    recovery: dict[str, Any] | None = None,
) -> dict[str, Any]:
    recovery = recovery or {}
    if not checkpoints:
        return {
            "what_happened": "世界自演未推进。",
            "who_remembered_what": [],
            "why_world_changed": "无检查点。",
            "where_to_continue": [],
            "timeline": [],
            "narrative_timeline": [],
            "memory_changes": [],
            "checkpoint_recovery": recovery,
        }
    last = checkpoints[-1]
    consequence = (
        last.get("consequence_state")
        if isinstance(last.get("consequence_state"), dict)
        else {}
    )
    consequence_summary = str(consequence.get("summary") or "").strip()
    return {
        "what_happened": f"世界推进到{last.get('stage')}，共留下 {len(checkpoints)} 个检查点。",
        "who_remembered_what": [
            item
            for checkpoint in checkpoints
            for item in checkpoint.get("who_remembered_what", [])
            if isinstance(item, dict)
        ],
        "why_world_changed": (
            f"锚点压力 {last.get('anchor_pressure')}，因果债 {last.get('causal_debt')}。"
            + (f"具象代偿：{consequence_summary}" if consequence_summary else "")
        ),
        "where_to_continue": [
            {
                "checkpoint_id": checkpoint.get("checkpoint_id"),
                "sandbox_run_id": checkpoint.get("sandbox_run_id"),
                "label": checkpoint.get("stage"),
            }
            for checkpoint in checkpoints
        ],
        "timeline": [
            {
                "round_index": checkpoint.get("round_index"),
                "checkpoint_id": checkpoint.get("checkpoint_id"),
                "major_event": checkpoint.get("major_event"),
                "stage": checkpoint.get("stage"),
                "causal_debt": checkpoint.get("causal_debt"),
                "remembered_count": len(checkpoint.get("who_remembered_what", [])),
            }
            for checkpoint in checkpoints
        ],
        "narrative_timeline": _narrative_timeline(checkpoints),
        "memory_changes": [
            item
            for checkpoint in checkpoints
            for item in checkpoint.get("who_remembered_what", [])
            if isinstance(item, dict)
        ],
        "checkpoint_recovery": recovery,
    }


def _stop_condition(
    objective: str,
    matched: bool,
    checkpoint: dict[str, Any],
    evidence: str,
) -> dict[str, Any]:
    return {
        "type": objective,
        "matched": matched,
        "evidence": evidence,
        "round_index": checkpoint.get("round_index", 0),
        "checkpoint_id": checkpoint.get("checkpoint_id", ""),
    }


def _progress_percent(current_round: int, target_round: int, status: str) -> int:
    if status == "completed" and current_round >= target_round:
        return 100
    return int((current_round / max(1, target_round)) * 100)


def _recovery_payload(
    checkpoints: list[dict[str, Any]],
    *,
    recovery_source: dict[str, Any] | None,
    latest_report_run_id: str,
) -> dict[str, Any]:
    latest = checkpoints[-1] if checkpoints else {}
    checkpoint_id = str(latest.get("checkpoint_id") or "")
    payload: dict[str, Any] = {
        "can_resume": bool(checkpoint_id),
        "resume_from_checkpoint": checkpoint_id,
        "latest_report_run_id": latest_report_run_id,
        "resume_endpoint": "",
    }
    if checkpoint_id:
        payload["resume_endpoint"] = (
            "POST /api/stories/<slug>/worldlines/<worldline_id>/"
            "world-autopilot/tasks/<task_id>/resume"
        )
    if recovery_source:
        payload["resumed_from"] = recovery_source
    return payload


def _load_recovery_source(
    run_id: str,
    checkpoint_id: str,
    *,
    outputs_dir: Path,
) -> dict[str, Any] | None:
    if not run_id and not checkpoint_id:
        return None
    rid = _checked_id(run_id, "resume_from_run_id")
    cid = _checked_id(checkpoint_id, "resume_from_checkpoint")
    path = outputs_dir / rid / "checkpoints" / f"{cid}.json"
    if not path.exists():
        raise FileNotFoundError(f"恢复检查点不存在: {cid}")
    checkpoint = _read_json(path)
    return {
        "run_id": rid,
        "checkpoint_id": cid,
        "round_index": checkpoint.get("round_index"),
        "major_event": checkpoint.get("major_event") or "",
        "stage": checkpoint.get("stage") or "",
        "causal_debt": checkpoint.get("causal_debt") or "",
    }


def _resume_event(recovery_source: dict[str, Any]) -> str:
    checkpoint_id = recovery_source.get("checkpoint_id") or "最近检查点"
    stage = recovery_source.get("stage") or recovery_source.get("major_event") or "世界继续推进"
    return f"从 {checkpoint_id} 继续：{stage}"


def _task_path(
    story_slug: str,
    worldline_id: str,
    task_id: str,
    *,
    projects_dir: Path | None,
) -> Path:
    story_path, _source_kind = resolve_story_path(
        _checked_id(story_slug, "story_slug"),
        projects_dir,
    )
    return (
        story_path
        / "worldlines"
        / _checked_id(worldline_id, "worldline_id")
        / "autopilot_tasks"
        / f"{_checked_id(task_id, 'task_id')}.json"
    )


def _write_task(
    story_slug: str,
    worldline_id: str,
    task_id: str,
    task: dict[str, Any],
    *,
    projects_dir: Path | None,
) -> None:
    path = _task_path(
        story_slug,
        worldline_id,
        task_id,
        projects_dir=projects_dir,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_task(
    story_slug: str,
    worldline_id: str,
    task_id: str,
    *,
    projects_dir: Path | None,
) -> dict[str, Any]:
    path = _task_path(
        story_slug,
        worldline_id,
        task_id,
        projects_dir=projects_dir,
    )
    if not path.exists():
        raise FileNotFoundError(f"世界自演任务不存在: {task_id}")
    return _read_json(path)


def _read_autopilot_report(run_id: str, *, root: Path) -> dict[str, Any]:
    rid = _checked_id(run_id, "run_id")
    path = root / rid / ARTIFACT
    if not path.exists():
        raise FileNotFoundError(f"世界自演报告不存在: {rid}")
    return _read_json(path)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorldAutopilotRequestError(f"{path.name} 无法解析：{exc}") from exc
    return raw if isinstance(raw, dict) else {}


def _new_run_id() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"autopilot_{ts}_{uuid.uuid4().hex[:6]}"


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise WorldAutopilotRequestError(f"{label} 无效")
    return checked

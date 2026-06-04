"""World Sandbox Loop v7: character lens novel briefs."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.world_sandbox import (
    get_character_subjective_memory,
    get_sandbox_run,
    run_sandbox_round,
)

VERSION = "character-lens-novel-v1"
ARTIFACT = "character_lens_briefs.json"


class CharacterLensRequestError(ValueError):
    """Invalid character lens request."""


def generate_character_lens_briefs(
    story_slug: str,
    *,
    source_event: str,
    character_id: str = "",
    source_run_id: str = "",
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
    worldline_id: str = "main",
) -> dict[str, Any]:
    """Generate readable multi-lens briefs from one sandbox event."""

    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")
    event = " ".join(str(source_event or "").split())
    if not event:
        raise CharacterLensRequestError("缺少 source_event（多视角事件）")
    root = outputs_dir or default_outputs_dir()

    if source_run_id:
        sandbox = get_sandbox_run(_checked_id(source_run_id, "source_run_id"), outputs_dir=root)
    else:
        sandbox = run_sandbox_round(
            sid,
            major_event=event,
            projects_dir=projects_dir,
            outputs_dir=root,
            worldline_id=wid,
        )
    round_record = sandbox["rounds"][0]
    actions = [
        action
        for action in round_record.get("character_actions", [])
        if isinstance(action, dict)
    ]
    if not actions:
        raise CharacterLensRequestError("沙盘轮次缺少角色行动，无法生成多视角")

    selected_character_id = _select_character_id(character_id, actions)
    selected_action = _find_action(selected_character_id, actions)
    memories = _read_memories_for_actions(
        sid,
        actions,
        projects_dir=projects_dir,
        worldline_id=str(sandbox.get("worldline_id") or wid),
    )
    selected_memory = _latest_memory(memories.get(selected_character_id))
    run_id = _new_run_id()
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    briefs = _briefs(
        event=event,
        sandbox=sandbox,
        round_record=round_record,
        actions=actions,
        selected_action=selected_action,
        selected_memory=selected_memory,
        memories=memories,
    )
    report = {
        "version": VERSION,
        "artifact": ARTIFACT,
        "run_id": run_id,
        "story_slug": sid,
        "worldline_id": str(sandbox.get("worldline_id") or wid),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source": {
            "source_event": event,
            "sandbox_run_id": sandbox["run_id"],
            "source_round_index": round_record.get("round_index"),
        },
        "brief_count": len(briefs),
        "briefs": briefs,
        "artifacts": {
            "character_lens_briefs": ARTIFACT,
        },
        "boundaries": [
            "多视角 brief 读取沙盘轮次和主观记忆链，不调用外部 provider。",
            "不改 run_scene 默认行为，不覆盖既有章节或世界线 artifact。",
            "角色个人卷来自 subjective_memory.jsonl，而不是全局正史摘要改写。",
        ],
        "next_steps": [
            "作者采纳台可把某个 lens brief 标记为采纳、部分采纳或另开分支。",
            "后续可把 brief 扩展为完整章节正文与多角色镜头切换。",
        ],
    }
    (run_dir / ARTIFACT).write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def _briefs(
    *,
    event: str,
    sandbox: dict[str, Any],
    round_record: dict[str, Any],
    actions: list[dict[str, Any]],
    selected_action: dict[str, Any],
    selected_memory: dict[str, Any],
    memories: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    delta = round_record.get("world_state_delta", {})
    first_action = actions[0]
    perspectives = [_perspective(action, memories) for action in actions]
    character_name = str(selected_action.get("character_name") or "角色")
    belief = str(selected_memory.get("new_belief") or selected_action.get("intent") or "")
    return [
        {
            "lens_type": "world_chronicle",
            "title": "世界正史卷",
            "body": (
                f"正史记下：{event}。此事令锚点压力{delta.get('anchor_pressure')}，"
                f"因果债转为{delta.get('causal_debt')}。"
            ),
            "evidence": {
                "source": "sandbox_round",
                "sandbox_run_id": sandbox["run_id"],
            },
        },
        {
            "lens_type": "anchor_volume",
            "title": "主锚点卷",
            "character_id": first_action.get("character_id"),
            "character_name": first_action.get("character_name"),
            "body": (
                f"{first_action.get('character_name')}的选择牵动本轮主线："
                f"{first_action.get('action')} 世界并未静止，而是要求锚点继续承压。"
            ),
            "evidence": {
                "source": "sandbox_round",
                "anchor_pressure": delta.get("anchor_pressure"),
            },
        },
        {
            "lens_type": "character_volume",
            "title": f"{character_name}个人卷",
            "character_id": selected_action.get("character_id"),
            "character_name": character_name,
            "body": (
                f"{character_name}眼中的事件并非正史摘要。"
                f"{belief} 这份判断来自他看到的“{_join(selected_memory.get('saw'))}”"
                f"和亲手做下的“{_join(selected_memory.get('did'))}”。"
            ),
            "evidence": {
                "source": "subjective_memory",
                "source_run_id": selected_memory.get("source_run_id"),
                "source_round_index": selected_memory.get("source_round_index"),
            },
        },
        {
            "lens_type": "faction_volume",
            "title": "势力卷",
            "body": (
                f"苍澜派、归云斋与暗线势力不再共享同一解释。"
                f"{character_name}的行动把“{event}”推入关系、资源和秘密的再分配。"
            ),
            "evidence": {
                "source": "world_state_delta",
                "resource_changes": delta.get("resource_changes", []),
                "secret_changes": delta.get("secret_changes", []),
            },
        },
        {
            "lens_type": "event_multi_perspective",
            "title": "事件多视角",
            "body": "同一事件在不同角色眼中分裂成多条叙事镜头。",
            "perspectives": perspectives,
            "evidence": {
                "source": "sandbox_round_and_subjective_memory",
                "character_count": len(perspectives),
            },
        },
    ]


def _perspective(
    action: dict[str, Any],
    memories: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    cid = str(action.get("character_id") or "")
    memory = _latest_memory(memories.get(cid))
    belief = str(memory.get("new_belief") or action.get("intent") or "形成新的判断")
    return {
        "character_id": cid,
        "character_name": action.get("character_name"),
        "stance": action.get("stance"),
        "voice": f"{action.get('character_name')}记住的是：{belief}",
        "evidence": {
            "source": "subjective_memory" if memory else "sandbox_action",
            "source_run_id": memory.get("source_run_id"),
        },
    }


def _read_memories_for_actions(
    story_slug: str,
    actions: list[dict[str, Any]],
    *,
    projects_dir: Path | None,
    worldline_id: str,
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for action in actions:
        cid = _checked_id(str(action.get("character_id") or ""), "character_id")
        report = get_character_subjective_memory(
            story_slug,
            cid,
            projects_dir=projects_dir,
            worldline_id=worldline_id,
        )
        result[cid] = [
            row for row in report.get("entries", []) if isinstance(row, dict)
        ]
    return result


def _select_character_id(value: str, actions: list[dict[str, Any]]) -> str:
    if value:
        checked = _checked_id(value, "character_id")
        if any(action.get("character_id") == checked for action in actions):
            return checked
    return str(actions[0].get("character_id") or "")


def _find_action(character_id: str, actions: list[dict[str, Any]]) -> dict[str, Any]:
    for action in actions:
        if action.get("character_id") == character_id:
            return action
    return actions[0]


def _latest_memory(entries: list[dict[str, Any]] | None) -> dict[str, Any]:
    rows = entries or []
    return rows[-1] if rows else {}


def _join(value: object) -> str:
    if isinstance(value, list):
        return "；".join(str(item) for item in value if str(item))
    text = str(value or "").strip()
    return text or "尚未记录"


def _new_run_id() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"lens_{ts}_{uuid.uuid4().hex[:6]}"


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise CharacterLensRequestError(f"{label} 无效")
    return checked

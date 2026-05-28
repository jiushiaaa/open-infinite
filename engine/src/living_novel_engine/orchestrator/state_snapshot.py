from __future__ import annotations

import copy
from typing import Any

from living_novel_engine.models import CharacterAgent, OpenThread, StoryWorld
from living_novel_engine.models.events import SimulationResult
from living_novel_engine.orchestrator.worldline_brancher import BranchSpec


def build_state_snapshot(
    world: StoryWorld,
    characters_before: list[CharacterAgent],
    char_map_after: dict[str, CharacterAgent],
    scene_state: dict[str, Any],
    spec: BranchSpec,
    result: SimulationResult,
) -> dict[str, Any]:
    """分支结束时的完整状态快照。"""
    before_map = {c.id: c for c in characters_before}
    character_snapshots: dict[str, dict[str, Any]] = {}
    relationship_changes: list[dict[str, str]] = []

    for cid, char in char_map_after.items():
        prev = before_map.get(cid)
        character_snapshots[cid] = {
            "name": char.name,
            "location": char.current_state.location or scene_state.get("location", ""),
            "emotion": char.current_state.emotion,
            "resources": list(char.current_state.resources),
            "narrative_role": char.narrative_role,
        }
        if prev:
            if prev.current_state.emotion != char.current_state.emotion:
                character_snapshots[cid]["emotion_changed_from"] = prev.current_state.emotion
            if prev.current_state.location != char.current_state.location:
                character_snapshots[cid]["location_changed_from"] = prev.current_state.location

    for cid, char in char_map_after.items():
        prev = before_map.get(cid)
        if not prev:
            continue
        for other_id, rel in char.relationships.items():
            old_rel = prev.relationships.get(other_id)
            if old_rel != rel:
                relationship_changes.append(
                    {
                        "from": cid,
                        "to": other_id,
                        "was": old_rel or "",
                        "now": rel,
                    }
                )

    open_threads = _project_open_threads(world.open_threads, scene_state, spec)

    hook = _next_chapter_hook(spec, scene_state, result)

    return {
        "worldline_id": result.worldline_id,
        "branch_theme": spec.theme,
        "branch_seed": spec.branch_seed,
        "termination_reason": result.termination_reason,
        "characters": character_snapshots,
        "relationship_changes": relationship_changes,
        "open_threads": open_threads,
        "next_chapter_hook": hook,
        "scene_flags": {
            k: v
            for k, v in scene_state.items()
            if k not in ("location", "time")
        },
        "time": scene_state.get("time", ""),
        "location": scene_state.get("location", ""),
    }


def _project_open_threads(
    threads: list[OpenThread],
    scene_state: dict[str, Any],
    spec: BranchSpec,
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for t in threads:
        status = t.status
        note = ""
        if t.id == "thread_jade_slip" and scene_state.get("jade_slip_used"):
            status = "resolved"
            note = "传讯玉简已碎，单向传音已发出"
        elif t.id == "thread_soul_bell" and scene_state.get("lin_wan_zhou_departed"):
            status = "escalated"
            note = "林晚舟携铃外出，离身风险上升"
        elif t.id == "thread_bamboo_array" and scene_state.get("bamboo_grove_triggered"):
            status = "escalated"
            note = "竹林阵纹已激活"
        elif t.id == "thread_wake_powder" and scene_state.get("investigating"):
            status = "touched"
            note = "调查线可能引向药庐"
        if spec.branch_seed == "believe" and t.id == "thread_jade_slip":
            note = note or "相信干预后或暂缓使用玉简"
        if spec.branch_seed == "reject" and t.id == "thread_seclusion_order":
            note = note or "反弹后林凡擅离风险增加"
        out.append(
            {
                "id": t.id,
                "title": t.title,
                "status": status,
                "note": note,
            }
        )
    return out


def _next_chapter_hook(
    spec: BranchSpec,
    scene_state: dict[str, Any],
    result: SimulationResult,
) -> str:
    if spec.branch_seed == "believe":
        if scene_state.get("jade_slip_used"):
            return "传讯已至，林晚舟会否改道？墨青烟在竹林等候的空寂里，谁先到一步？"
        return "她选择相信那道低语，却在廊下停步——竹林里的铃音，究竟在召唤谁？"
    if spec.branch_seed == "doubt":
        if scene_state.get("investigating"):
            return "她未赴约，却提灯入暗巷查探；林凡的呼吸与墨青烟的死士，谁会被先发现？"
        return "半信半疑的她折返听雨轩，窗纸后的影子，比雨夜更冷。"
    if scene_state.get("lin_wan_zhou_departed"):
        return "她仍踏入雨幕，退魂铃在远处震鸣——这一去，是生路还是魂散？"
    return "她拒绝无名低语，反手扣住林凡手腕：今夜，你必须说清楚。"

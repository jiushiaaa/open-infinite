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
        resources = list(char.current_state.resources)
        if cid == "lin_fan" and scene_state.get("jade_slip_used"):
            if not any("已碎" in r for r in resources):
                resources = [r for r in resources if "传讯玉简" not in r]
                resources.append("传讯玉简（已碎）")
        character_snapshots[cid] = {
            "name": char.name,
            "location": char.current_state.location or scene_state.get("location", ""),
            "emotion": char.current_state.emotion,
            "resources": resources,
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
    """由 scene_flags 优先生成钩子，避免与快照矛盾的 Phase 0 固定文案。"""
    seed = spec.branch_seed

    if scene_state.get("bamboo_grove_triggered"):
        if seed == "reject":
            return "石亭阵纹亮如骨烛——她终究还是赴了约，墨青烟在雨幕尽头等她。"
        if seed == "doubt":
            return "竹林深处，调查得来的线索与阵纹同亮，下一招是杀局还是局中局？"
        return "城外竹林铃音与阵纹同鸣，墨青烟的身影已在石亭显现。"

    if scene_state.get("investigating"):
        if seed == "believe":
            return "她暂缓赴约，先查退魂铃与城主府异动——那只乱葬岗伸来的手，会先于墨青烟现身吗？"
        if seed == "doubt":
            return "暗巷灯影摇曳，她与林凡步步逼近某个不该被揭开的答案。"
        return "城内调查未歇，雨夜里还有谁在看她的一举一动？"

    if scene_state.get("lin_wan_zhou_departed"):
        if seed == "reject":
            return "她仍踏入雨幕赴约，退魂铃在远处震鸣——这一去，是生路还是魂散？"
        return "她提灯出城，赴约之路步步逼近城外竹林。"

    if seed == "reject":
        return "她拒听低语，却仍将赴约——林凡能否在最后一步拦住她？"
    if seed == "linear":
        hook = _hook_from_events(result)
        if hook:
            return hook
        return "雨夜未歇，下一章的杀机藏在谁袖中？"

    return _hook_from_events(result) or "更漏声里，真相与杀局只隔一扇窗。"


def _hook_from_events(result: SimulationResult) -> str:
    """从最后一两条推演事件摘一句悬念（无则空）。"""
    events = getattr(result, "accepted_events", None) or []
    for evt in reversed(events[-4:]):
        payload = getattr(evt, "payload", None) or {}
        content = str(payload.get("content", "")).strip()
        if len(content) >= 12:
            return content[:72] + ("……" if len(content) > 72 else "")
    return ""

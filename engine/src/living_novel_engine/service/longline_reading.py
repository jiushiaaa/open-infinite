"""Read-only longline reading packet for cross-event worldline understanding."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.dossier_reading import get_dossier_reading

VERSION = "longline-reading-v1"


class LonglineReadingRequestError(ValueError):
    """Invalid longline reading request."""


def get_longline_reading(
    story_slug: str,
    *,
    worldline_id: str = "main",
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
) -> dict[str, Any]:
    """Compose a longline dossier from existing reading, volume, and worldline packets."""

    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")
    root = outputs_dir or default_outputs_dir()
    dossier = get_dossier_reading(
        sid,
        worldline_id=wid,
        projects_dir=projects_dir,
        outputs_dir=root,
    )
    timeline_entries = _timeline_entries(sid, wid, dossier)
    longline_threads = _longline_threads(dossier)
    evidence_refs = _evidence_refs(dossier, timeline_entries)
    status = "ready" if timeline_entries else "empty"
    if timeline_entries and dossier.get("status") != "ready":
        status = "partial"

    return {
        "version": VERSION,
        "story_slug": sid,
        "source_kind": dossier.get("source_kind") or "",
        "worldline_id": wid,
        "status": status,
        "default_axis": "cause",
        "title": f"{wid} 的长线卷",
        "subtitle": "把事件、误会、角色记忆、势力代偿和作者下一章串成一条可继续阅读的世界长线。",
        "source_runs": dossier.get("source_runs") or {},
        "current_tension": _current_tension(dossier),
        "reading_progress": _reading_progress(timeline_entries, longline_threads),
        "event_index": _event_index(timeline_entries, longline_threads),
        "misbelief_recovery": _misbelief_recovery(sid, wid, dossier, timeline_entries),
        "timeline_entries": timeline_entries,
        "longline_threads": longline_threads,
        "open_threads": _open_threads(sid, wid, longline_threads),
        "evidence_panel": {
            "default_open": False,
            "label": "长线证据链",
            "description": "默认先读世界如何持续变化；展开后再核对正文场景、角色卷、势力卷、事件多视角和确认入卷来源。",
            "ref_count": len(evidence_refs),
            "refs": evidence_refs,
        },
        "next_actions": _next_actions(sid, wid, dossier),
        "boundaries": [
            "长线卷只读聚合 dossier-reading、worldline_dossier、连续阅读场景和多视角卷宗，不新增持久 artifact。",
            "当前版本先承接最近一条世界线的长线阅读；后续可扩展为跨章节回收和用户阅读进度持久化。",
            "缺少单个来源时降级为 partial 或 empty，不改变 run_scene 默认行为。",
        ],
    }


def _timeline_entries(
    story_slug: str,
    worldline_id: str,
    dossier: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    continuous = (
        dossier.get("continuous_reading")
        if isinstance(dossier.get("continuous_reading"), dict)
        else {}
    )
    sections = (
        continuous.get("reading_sections")
        if isinstance(continuous.get("reading_sections"), list)
        else []
    )
    for index, section in enumerate(sections):
        if not isinstance(section, dict):
            continue
        rows.append(
            {
                "id": str(section.get("id") or f"scene_{index + 1}"),
                "sequence": len(rows) + 1,
                "phase": "scene",
                "label": "连续正文",
                "title": str(section.get("title") or f"场景 {index + 1}"),
                "body": str(section.get("body") or "").strip(),
                "source": "continuous_reading",
                "route": f"#/world/{story_slug}/worldlines/{worldline_id}/reading/continuous_reading",
                "evidence_refs": _as_str_list(section.get("evidence_refs")),
                "affected_characters": _names_from_text(str(section.get("body") or "")),
                "affected_factions": [],
                "consequence_hint": str(section.get("conflict_turn") or section.get("cognitive_bias") or ""),
            }
        )

    volume_tabs = dossier.get("volume_tabs") if isinstance(dossier.get("volume_tabs"), list) else []
    for tab in volume_tabs:
        if not isinstance(tab, dict):
            continue
        route = _volume_route(story_slug, worldline_id, tab)
        rows.append(
            {
                "id": f"volume_{tab.get('id') or len(rows) + 1}",
                "sequence": len(rows) + 1,
                "phase": "volume",
                "label": str(tab.get("label") or "卷宗"),
                "title": str(tab.get("title") or tab.get("label") or "世界卷宗"),
                "body": _first_paragraph(str(tab.get("body_md") or "")),
                "source": str(tab.get("id") or "volume_tab"),
                "route": route,
                "evidence_refs": _as_str_list(tab.get("evidence_refs")),
                "affected_characters": [str(tab.get("character_name") or "")] if tab.get("character_name") else [],
                "affected_factions": [str(tab.get("faction_name") or "")] if tab.get("faction_name") else [],
                "consequence_hint": str(tab.get("cognitive_bias") or ""),
            }
        )

    confirmed = (
        dossier.get("confirmed_chapter")
        if isinstance(dossier.get("confirmed_chapter"), dict)
        else {}
    )
    if confirmed:
        rows.append(
            {
                "id": "confirmed_chapter",
                "sequence": len(rows) + 1,
                "phase": "confirmation",
                "label": "作者确认",
                "title": str(confirmed.get("chapter_title") or "确认入卷"),
                "body": str(confirmed.get("author_note") or _first_paragraph(str(confirmed.get("body_md") or ""))),
                "source": "confirmed_chapter",
                "route": f"#/world/{story_slug}/worldlines/{worldline_id}/reading/confirmed_chapter",
                "evidence_refs": _as_str_list(list((confirmed.get("evidence_chain") or {}).values())),
                "affected_characters": [],
                "affected_factions": [],
                "consequence_hint": _continuation_hint(confirmed),
            }
        )

    worldline_dossier = (
        dossier.get("worldline_dossier")
        if isinstance(dossier.get("worldline_dossier"), dict)
        else {}
    )
    checkpoints = (
        worldline_dossier.get("checkpoints")
        if isinstance(worldline_dossier.get("checkpoints"), list)
        else []
    )
    for checkpoint in reversed(checkpoints):
        if not isinstance(checkpoint, dict):
            continue
        rows.append(
            {
                "id": str(checkpoint.get("checkpoint_id") or f"checkpoint_{len(rows) + 1}"),
                "sequence": len(rows) + 1,
                "phase": "checkpoint",
                "label": "检查点",
                "title": str(checkpoint.get("stage") or "世界自演检查点"),
                "body": str(checkpoint.get("major_event") or ""),
                "source": "worldline_checkpoint",
                "route": (
                    f"#/world/{story_slug}/worldlines/{worldline_id}/checkpoints/"
                    f"{checkpoint.get('run_id') or ''}/{checkpoint.get('checkpoint_id') or ''}"
                ),
                "evidence_refs": [str(checkpoint.get("sandbox_run_id") or "")],
                "affected_characters": [
                    str(item.get("character_id") or "")
                    for item in checkpoint.get("who_remembered_what") or []
                    if isinstance(item, dict) and item.get("character_id")
                ],
                "affected_factions": [],
                "consequence_hint": str(
                    (checkpoint.get("consequence_state") or {}).get("summary") or checkpoint.get("causal_debt") or ""
                ),
            }
        )
    return rows


def _reading_progress(
    timeline_entries: list[dict[str, Any]],
    threads: list[dict[str, Any]],
) -> dict[str, Any]:
    total = len(timeline_entries)
    active = timeline_entries[0] if timeline_entries else {}
    next_entry = timeline_entries[1] if len(timeline_entries) > 1 else {}
    active_threads = [thread for thread in threads if thread.get("status") == "active"]
    return {
        "label": "长线阅读进度",
        "current_sequence": int(active.get("sequence") or 0),
        "total_entries": total,
        "percent": round((1 / total) * 100) if total else 0,
        "current_entry_id": str(active.get("id") or ""),
        "current_title": str(active.get("title") or "等待长线节点"),
        "next_entry_id": str(next_entry.get("id") or ""),
        "next_title": str(next_entry.get("title") or "等待下一段发酵"),
        "active_thread_count": len(active_threads),
        "unresolved_thread_count": len([thread for thread in threads if thread.get("status") != "closed"]),
        "summary": (
            f"已整理 {total} 个长线节点，{len(active_threads)} 条发酵线正在显形。"
            if total
            else "还没有可追踪的长线节点。"
        ),
    }


def _event_index(
    timeline_entries: list[dict[str, Any]],
    threads: list[dict[str, Any]],
) -> dict[str, Any]:
    open_thread_ids = [str(thread.get("id") or "") for thread in threads if thread.get("status") != "closed"]
    items: list[dict[str, Any]] = []
    for entry in timeline_entries:
        if not isinstance(entry, dict):
            continue
        thread_ids = _thread_ids_for_entry(entry, open_thread_ids)
        items.append(
            {
                "id": f"event_{entry.get('sequence') or len(items) + 1}",
                "label": str(entry.get("label") or "长线事件"),
                "title": str(entry.get("title") or "未命名事件"),
                "summary": _compact_text(str(entry.get("body") or entry.get("consequence_hint") or "")),
                "phase": str(entry.get("phase") or ""),
                "route": str(entry.get("route") or ""),
                "entry_ids": [str(entry.get("id") or "")],
                "thread_ids": thread_ids,
                "evidence_count": len(_as_str_list(entry.get("evidence_refs"))),
                "unresolved_count": len(thread_ids),
            }
        )
    return {
        "label": "多事件索引",
        "description": "把长线卷拆成可扫读的事件目录，先定位事件，再回到正文、角色卷或证据链。",
        "event_count": len(items),
        "items": items,
    }


def _misbelief_recovery(
    story_slug: str,
    worldline_id: str,
    dossier: dict[str, Any],
    timeline_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    biases = dossier.get("perspective_biases") if isinstance(dossier.get("perspective_biases"), list) else []
    usable_biases = [item for item in biases if isinstance(item, dict)]
    first_event = timeline_entries[0] if timeline_entries else {}
    items: list[dict[str, Any]] = []
    for index, bias in enumerate(usable_biases):
        misunderstanding = str(
            bias.get("cognitive_bias")
            or bias.get("description")
            or bias.get("bias")
            or "角色仍在用不完整信息解释同一事件。"
        )
        source = str(bias.get("source") or bias.get("volume") or first_event.get("source") or "longline")
        origin_title = str(
            bias.get("scene_title")
            or bias.get("title")
            or first_event.get("title")
            or "长线起点"
        )
        affected = _as_str_list(bias.get("affected_characters")) or _as_str_list(
            bias.get("characters")
        )
        if not affected:
            affected = _names_from_text(misunderstanding + " " + str(first_event.get("body") or ""))
        evidence = _as_str_list(bias.get("evidence_refs")) or _as_str_list(first_event.get("evidence_refs"))
        items.append(
            {
                "id": str(bias.get("id") or f"misbelief_{index + 1}"),
                "status": "unresolved",
                "misunderstanding": misunderstanding,
                "origin_event_title": origin_title,
                "source": source,
                "affected_characters": affected or ["待确认角色"],
                "evidence_refs": evidence,
                "recovery_steps": [
                    "先回到事件现场，确认哪句话或哪次沉默制造了误读。",
                    "再进入角色个人卷，查看该角色把误会写成了什么主观记忆。",
                    "最后送到作者台，把误会回收为下一章的对话、行动或代偿结果。",
                ],
                "next_route": f"#/world/{story_slug}/worldlines/{worldline_id}/reading",
                "author_prompt": f"下一章需要让角色面对这个误会：{misunderstanding}",
            }
        )
    return {
        "label": "误会回收台",
        "description": "把已经显形的误会整理成可回收的写作任务：先确认误读来源，再看谁记住了它，最后决定下一章怎样兑现或反转。",
        "misbelief_count": len(items),
        "items": items,
        "fallback_action": {
            "label": "回卷宗阅读",
            "route": f"#/world/{story_slug}/worldlines/{worldline_id}/reading",
            "reason": "从误会图谱回到连续正文和卷宗证据。",
        },
    }


def _open_threads(
    story_slug: str,
    worldline_id: str,
    threads: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    routes = {
        "misbelief": f"#/world/{story_slug}/worldlines/{worldline_id}/reading",
        "character_memory": f"#/world/{story_slug}/worldlines/{worldline_id}/reading/character_volume",
        "faction_pressure": f"#/world/{story_slug}/worldlines/{worldline_id}/reading/faction_volume",
        "event_chain": f"#/world/{story_slug}/worldlines/{worldline_id}/events/main/perspectives",
        "author_continuation": f"#/world/{story_slug}/author",
    }
    reasons = {
        "misbelief": "回到误会图谱，追踪哪句话被角色误读。",
        "character_memory": "进入角色卷，查看误会如何写进主观记忆。",
        "faction_pressure": "进入势力卷，查看事件如何变成资源和立场压力。",
        "event_chain": "拆开事件现场，核对同一事件的多视角差异。",
        "author_continuation": "送到作者台，把长线张力写进下一章。",
    }
    result: list[dict[str, Any]] = []
    for thread in threads:
        if not isinstance(thread, dict) or thread.get("status") == "closed":
            continue
        tid = str(thread.get("id") or "")
        result.append(
            {
                "id": tid,
                "label": str(thread.get("label") or tid),
                "status": str(thread.get("status") or "pending"),
                "summary": str(thread.get("summary") or ""),
                "source_count": int(thread.get("source_count") or 0),
                "next_route": routes.get(tid, f"#/world/{story_slug}/worldlines/{worldline_id}/longline"),
                "reason": reasons.get(tid, "继续追踪这条长线。"),
            }
        )
    return result


def _longline_threads(dossier: dict[str, Any]) -> list[dict[str, Any]]:
    biases = dossier.get("perspective_biases") if isinstance(dossier.get("perspective_biases"), list) else []
    volume_tabs = dossier.get("volume_tabs") if isinstance(dossier.get("volume_tabs"), list) else []
    worldline = dossier.get("worldline_dossier") if isinstance(dossier.get("worldline_dossier"), dict) else {}
    state = worldline.get("worldline_state") if isinstance(worldline.get("worldline_state"), dict) else {}
    consequence = (
        state.get("consequence_state")
        if isinstance(state.get("consequence_state"), dict)
        else {}
    )
    character_tab = _first_volume(volume_tabs, "character_volume")
    faction_tab = _first_volume(volume_tabs, "faction_volume")
    event_tab = _first_volume(volume_tabs, "event_multi_perspective")
    continuous = dossier.get("continuous_reading") if isinstance(dossier.get("continuous_reading"), dict) else {}
    confirmed = dossier.get("confirmed_chapter") if isinstance(dossier.get("confirmed_chapter"), dict) else {}
    return [
        {
            "id": "misbelief",
            "label": "误会长线",
            "status": "active" if biases else "pending",
            "summary": _join_first(
                [str(item.get("cognitive_bias") or "") for item in biases if isinstance(item, dict)],
                fallback="角色和正史之间的误会等待更多事件显形。",
            ),
            "source_count": len(biases),
        },
        {
            "id": "character_memory",
            "label": "角色记忆长线",
            "status": "active" if character_tab else "pending",
            "summary": str(character_tab.get("cognitive_bias") or _first_paragraph(str(character_tab.get("body_md") or "")) or "角色个人卷尚未形成。"),
            "source_count": 1 if character_tab else 0,
        },
        {
            "id": "faction_pressure",
            "label": "势力压力长线",
            "status": "active" if faction_tab or consequence else "pending",
            "summary": str(
                consequence.get("summary")
                or faction_tab.get("cognitive_bias")
                or _first_paragraph(str(faction_tab.get("body_md") or ""))
                or "势力代偿尚未显形。"
            ),
            "source_count": len(consequence.get("domains") or {}) or (1 if faction_tab else 0),
        },
        {
            "id": "event_chain",
            "label": "事件裂缝长线",
            "status": "active" if event_tab else "pending",
            "summary": str(event_tab.get("cognitive_bias") or _first_paragraph(str(event_tab.get("body_md") or "")) or "事件多视角尚未生成。"),
            "source_count": len(event_tab.get("novel_scene_plan") or []) if event_tab else 0,
        },
        {
            "id": "author_continuation",
            "label": "作者承接长线",
            "status": "active" if continuous or confirmed else "pending",
            "summary": str(
                continuous.get("next_chapter_hook")
                or confirmed.get("author_note")
                or "作者确认入卷后会出现下一章承接。"
            ),
            "source_count": 1 if continuous or confirmed else 0,
        },
    ]


def _current_tension(dossier: dict[str, Any]) -> dict[str, str]:
    continuous = dossier.get("continuous_reading") if isinstance(dossier.get("continuous_reading"), dict) else {}
    biases = dossier.get("perspective_biases") if isinstance(dossier.get("perspective_biases"), list) else []
    first_bias = next((item for item in biases if isinstance(item, dict) and item.get("cognitive_bias")), {})
    return {
        "summary": str(
            continuous.get("next_chapter_hook")
            or first_bias.get("cognitive_bias")
            or dossier.get("title")
            or "这条世界线等待下一轮事件继续发酵。"
        ),
        "primary_misbelief": str(first_bias.get("cognitive_bias") or ""),
        "next_chapter_hook": str(continuous.get("next_chapter_hook") or ""),
    }


def _next_actions(story_slug: str, worldline_id: str, dossier: dict[str, Any]) -> list[dict[str, str]]:
    character_tab = _first_volume(dossier.get("volume_tabs") or [], "character_volume")
    faction_tab = _first_volume(dossier.get("volume_tabs") or [], "faction_volume")
    character_id = str(character_tab.get("character_id") or "zhao_xuan")
    faction_id = str(faction_tab.get("faction_id") or faction_tab.get("faction_name") or "苍澜派")
    return [
        {
            "id": "reading",
            "label": "回卷宗阅读",
            "route": f"#/world/{story_slug}/worldlines/{worldline_id}/reading",
            "reason": "回到连续正文和全部卷宗。",
        },
        {
            "id": "event_perspective",
            "label": "看事件详情",
            "route": f"#/world/{story_slug}/worldlines/{worldline_id}/events/main/perspectives",
            "reason": "把当前长线拆回同一事件的多视角现场。",
        },
        {
            "id": "character_volume",
            "label": "追角色个人卷",
            "route": f"#/world/{story_slug}/worldlines/{worldline_id}/characters/{character_id}",
            "reason": "查看误会如何进入角色主观记忆。",
        },
        {
            "id": "faction_volume",
            "label": "追势力卷",
            "route": f"#/world/{story_slug}/worldlines/{worldline_id}/factions/{faction_id}",
            "reason": "查看事件如何变成势力姿态和资源压力。",
        },
        {
            "id": "author",
            "label": "送到作者台",
            "route": f"#/world/{story_slug}/author",
            "reason": "把长线张力整理成下一章材料。",
        },
    ]


def _volume_route(story_slug: str, worldline_id: str, tab: dict[str, Any]) -> str:
    tid = str(tab.get("id") or "")
    if tid == "character_volume" and tab.get("character_id"):
        return f"#/world/{story_slug}/worldlines/{worldline_id}/characters/{tab.get('character_id')}"
    if tid == "faction_volume":
        faction = str(tab.get("faction_id") or tab.get("faction_name") or "苍澜派")
        return f"#/world/{story_slug}/worldlines/{worldline_id}/factions/{faction}"
    if tid == "event_multi_perspective":
        return f"#/world/{story_slug}/worldlines/{worldline_id}/events/main/perspectives"
    return f"#/world/{story_slug}/worldlines/{worldline_id}/reading/{tid}"


def _evidence_refs(dossier: dict[str, Any], timeline_entries: list[dict[str, Any]]) -> list[str]:
    refs: list[str] = []
    panel = dossier.get("evidence_panel") if isinstance(dossier.get("evidence_panel"), dict) else {}
    refs.extend(_as_str_list(panel.get("refs")))
    for entry in timeline_entries:
        refs.extend(_as_str_list(entry.get("evidence_refs")))
    seen: set[str] = set()
    result: list[str] = []
    for ref in refs:
        if ref and ref not in seen:
            result.append(ref)
            seen.add(ref)
    return result


def _first_volume(volumes: Any, volume_type: str) -> dict[str, Any]:
    if not isinstance(volumes, list):
        return {}
    for volume in volumes:
        if isinstance(volume, dict) and volume.get("id") == volume_type:
            return volume
    return {}


def _join_first(values: list[str], *, fallback: str) -> str:
    clean = [value.strip() for value in values if value.strip()]
    return "；".join(clean[:3]) if clean else fallback


def _first_paragraph(markdown: str) -> str:
    for part in markdown.replace("\r\n", "\n").split("\n\n"):
        text = part.strip().lstrip("#").strip()
        if text:
            return text
    return ""


def _compact_text(text: str, limit: int = 96) -> str:
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def _thread_ids_for_entry(entry: dict[str, Any], fallback_ids: list[str]) -> list[str]:
    phase = str(entry.get("phase") or "")
    source = str(entry.get("source") or "")
    result: list[str] = []
    if phase == "scene":
        result.extend(["misbelief", "author_continuation"])
    if source == "character_volume":
        result.append("character_memory")
    if source == "faction_volume":
        result.append("faction_pressure")
    if source == "event_multi_perspective" or phase == "checkpoint":
        result.append("event_chain")
    if phase == "confirmation":
        result.append("author_continuation")
    clean = [item for item in result if item in fallback_ids]
    return clean or fallback_ids[:2]


def _names_from_text(text: str) -> list[str]:
    names = []
    for name in ("赵轩", "沈冰月", "韩无归"):
        if name in text:
            names.append(name)
    return names


def _continuation_hint(confirmed: dict[str, Any]) -> str:
    effect = confirmed.get("continuation_effect") if isinstance(confirmed.get("continuation_effect"), dict) else {}
    if effect.get("next_sandbox_entry"):
        return str(effect.get("next_sandbox_entry"))
    return str(confirmed.get("author_note") or "")


def _as_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item or "").strip()]
    return [str(value)] if str(value or "").strip() else []


def _checked_id(value: str, label: str) -> str:
    checked = safe_id(str(value or ""))
    if checked is None:
        raise LonglineReadingRequestError(f"{label} 无效")
    return checked

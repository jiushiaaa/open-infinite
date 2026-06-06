"""Read-only event perspective packet for a worldline event page."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.dossier_reading import get_dossier_reading

VERSION = "event-perspective-v1"


class EventPerspectiveRequestError(ValueError):
    """Invalid event perspective request."""


def get_event_perspective(
    story_slug: str,
    *,
    worldline_id: str = "main",
    event_id: str = "main",
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
) -> dict[str, Any]:
    """Compose an event detail page from existing reading and lens artifacts."""

    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")
    eid = _checked_id(event_id, "event_id")
    root = outputs_dir or default_outputs_dir()
    dossier = get_dossier_reading(
        sid,
        worldline_id=wid,
        projects_dir=projects_dir,
        outputs_dir=root,
    )
    event_volume = _event_volume(dossier)
    scene_beats = _scene_beats(event_volume, dossier)
    evidence_refs = _evidence_refs(event_volume, scene_beats, dossier)
    title = _title(dossier, event_volume, scene_beats)
    status = "ready" if event_volume and scene_beats else "partial"
    if not event_volume and not scene_beats:
        status = "empty"

    return {
        "version": VERSION,
        "story_slug": sid,
        "worldline_id": wid,
        "event_id": eid,
        "status": status,
        "title": title,
        "subtitle": "同一事件如何在正史、角色记忆、势力秩序和作者下一章之间分裂。",
        "source_runs": {
            **(dossier.get("source_runs") or {}),
            "sandbox_run_id": _sandbox_run_id(event_volume, dossier),
        },
        "event_volume": event_volume,
        "scene_beats": scene_beats,
        "information_gap": _information_gap(event_volume, dossier),
        "perspective_biases": _perspective_biases(dossier),
        "evidence_panel": {
            "default_open": False,
            "label": "事件证据链",
            "description": "先读事件，再展开证据核对沙盘轮次、主观记忆、世界线代偿和卷宗来源。",
            "ref_count": len(evidence_refs),
            "refs": evidence_refs,
        },
        "next_actions": _next_actions(sid, wid, dossier),
        "boundaries": [
            "事件详情页只读聚合 dossier-reading 与 character_lens_volumes，不新增持久 artifact。",
            "事件 id 先以 main 承接当前世界线最近事件；后续可扩展为多事件索引。",
            "缺少单个来源时降级为空态或 partial，不改变 run_scene 默认行为。",
        ],
    }


def _checked_id(value: str, label: str) -> str:
    checked = safe_id(str(value or ""))
    if checked is None:
        raise EventPerspectiveRequestError(f"{label} 无效")
    return checked


def _event_volume(dossier: dict[str, Any]) -> dict[str, Any]:
    tabs = dossier.get("volume_tabs") if isinstance(dossier.get("volume_tabs"), list) else []
    for tab in tabs:
        if isinstance(tab, dict) and tab.get("id") == "event_multi_perspective":
            return tab
    return {}


def _scene_beats(event_volume: dict[str, Any], dossier: dict[str, Any]) -> list[dict[str, Any]]:
    beats = event_volume.get("novel_scene_plan")
    if not isinstance(beats, list) or not beats:
        continuous = dossier.get("continuous_reading") if isinstance(dossier.get("continuous_reading"), dict) else {}
        beats = continuous.get("reading_sections")
    rows: list[dict[str, Any]] = []
    for index, beat in enumerate(beats if isinstance(beats, list) else []):
        if not isinstance(beat, dict):
            continue
        rows.append(
            {
                "id": str(beat.get("id") or beat.get("beat_type") or f"beat_{index + 1}"),
                "beat_type": str(beat.get("beat_type") or beat.get("source_beat_type") or "event_beat"),
                "title": str(beat.get("title") or f"事件片段 {index + 1}"),
                "body": str(beat.get("body") or "").strip(),
                "viewpoint": str(beat.get("viewpoint") or beat.get("narrative_role") or "事件视角"),
                "cognitive_bias": str(beat.get("cognitive_bias") or ""),
                "evidence_refs": _as_str_list(beat.get("evidence_refs")),
            }
        )
    return rows


def _evidence_refs(
    event_volume: dict[str, Any],
    scene_beats: list[dict[str, Any]],
    dossier: dict[str, Any],
) -> list[str]:
    refs: list[str] = []
    refs.extend(_as_str_list(event_volume.get("evidence_refs")))
    for beat in scene_beats:
        refs.extend(_as_str_list(beat.get("evidence_refs")))
    evidence_panel = dossier.get("evidence_panel") if isinstance(dossier.get("evidence_panel"), dict) else {}
    refs.extend(_as_str_list(evidence_panel.get("refs")))
    seen: set[str] = set()
    result: list[str] = []
    for ref in refs:
        if ref and ref not in seen:
            result.append(ref)
            seen.add(ref)
    return result


def _title(
    dossier: dict[str, Any],
    event_volume: dict[str, Any],
    scene_beats: list[dict[str, Any]],
) -> str:
    body = str(event_volume.get("body_md") or "").strip()
    if "“" in body and "”" in body:
        quoted = body.split("“", 1)[1].split("”", 1)[0].strip()
        if quoted:
            return quoted
    source = dossier.get("continuous_reading")
    if isinstance(source, dict):
        hook = str(source.get("next_chapter_hook") or "").strip()
        if hook:
            return hook
    label = str(event_volume.get("title") or "").strip()
    if label:
        return label
    if scene_beats:
        return str(scene_beats[0].get("title") or "事件多视角")
    return "事件多视角"


def _sandbox_run_id(event_volume: dict[str, Any], dossier: dict[str, Any]) -> str:
    chain = event_volume.get("evidence_chain") if isinstance(event_volume.get("evidence_chain"), dict) else {}
    if chain.get("sandbox_round_id"):
        return str(chain.get("sandbox_round_id"))
    source = dossier.get("source_runs") if isinstance(dossier.get("source_runs"), dict) else {}
    return str(source.get("lens_run_id") or "")


def _information_gap(event_volume: dict[str, Any], dossier: dict[str, Any]) -> dict[str, Any]:
    gap = event_volume.get("information_gap")
    if isinstance(gap, dict):
        return {
            "canon_vs_character": str(gap.get("canon_vs_character") or ""),
            "misbeliefs": str(gap.get("misbeliefs") or ""),
            "unknown_canon_facts": str(gap.get("unknown_canon_facts") or ""),
        }
    biases = _perspective_biases(dossier)
    first = biases[0] if biases else {}
    return {
        "canon_vs_character": first.get("cognitive_bias") or "正史与角色主观视角尚未形成明确差异。",
        "misbeliefs": "",
        "unknown_canon_facts": "",
    }


def _perspective_biases(dossier: dict[str, Any]) -> list[dict[str, str]]:
    rows = dossier.get("perspective_biases") if isinstance(dossier.get("perspective_biases"), list) else []
    result: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        result.append(
            {
                "id": str(row.get("id") or f"bias_{len(result) + 1}"),
                "label": str(row.get("label") or "事件视角"),
                "source": str(row.get("source") or ""),
                "cognitive_bias": str(row.get("cognitive_bias") or ""),
            }
        )
    return result


def _next_actions(story_slug: str, worldline_id: str, dossier: dict[str, Any]) -> list[dict[str, str]]:
    character_tab = next(
        (
            tab
            for tab in dossier.get("volume_tabs", [])
            if isinstance(tab, dict) and tab.get("id") == "character_volume" and tab.get("character_id")
        ),
        {},
    )
    character_id = str(character_tab.get("character_id") or "zhao_xuan")
    return [
        {
            "id": "reading",
            "label": "回卷宗阅读",
            "route": f"#/world/{story_slug}/worldlines/{worldline_id}/reading/event_multi_perspective",
            "reason": "回到连续正文和全部卷宗目录。",
        },
        {
            "id": "character_volume",
            "label": "看角色个人卷",
            "route": f"#/world/{story_slug}/worldlines/{worldline_id}/characters/{character_id}",
            "reason": "查看这一事件如何写入角色主观记忆。",
        },
        {
            "id": "worldline",
            "label": "查世界线代偿",
            "route": f"#/world/{story_slug}/worldlines/{worldline_id}",
            "reason": "核对因果债、检查点和后续承接。",
        },
        {
            "id": "longline",
            "label": "追长线卷",
            "route": f"#/world/{story_slug}/worldlines/{worldline_id}/longline",
            "reason": "查看这件事如何继续影响误会、记忆、势力和下一章。",
        },
        {
            "id": "author",
            "label": "送到作者台",
            "route": f"#/world/{story_slug}/author",
            "reason": "把事件张力转成下一章材料。",
        },
    ]


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item or "").strip()]

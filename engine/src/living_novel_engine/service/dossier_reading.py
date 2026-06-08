"""Read-only productized dossier reading packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.project_health import resolve_story_path
from living_novel_engine.service.worldline_dossier import get_worldline_dossier

VERSION = "dossier-reading-v1"


class DossierReadingRequestError(ValueError):
    """Invalid dossier reading request."""


def get_dossier_reading(
    story_slug: str,
    *,
    worldline_id: str = "main",
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
) -> dict[str, Any]:
    """Compose existing S8/S9 artifacts into a novel-first dossier reading packet."""

    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")
    _story_path, source_kind = resolve_story_path(sid, projects_dir)
    root = outputs_dir or default_outputs_dir()

    draft_run_id, draft = _latest_artifact_run(
        root,
        "next_chapter_draft.json",
        story_slug=sid,
        worldline_id=wid,
    )
    confirmation_run_id, confirmation = _latest_artifact_run(
        root,
        "confirmed_chapter_entry.json",
        story_slug=sid,
        worldline_id=wid,
    )
    adoption_run_id = confirmation_run_id or draft_run_id
    run_dir = root / adoption_run_id if adoption_run_id else None

    confirmed = _confirmed_chapter(run_dir, confirmation)
    reading_trail = _read_named_json(run_dir, "confirmed_chapter_reading_trail.json")
    continuous = _continuous_reading(run_dir, draft)
    lens_run_id = _source_lens_run_id(continuous, reading_trail)
    lens_payload = _read_named_json(root / lens_run_id if lens_run_id else None, "character_lens_volumes.json")
    volume_tabs = _volume_tabs(lens_payload, lens_run_id)
    continuous = _continuous_with_inline_evidence(continuous, volume_tabs)
    evidence_refs = _evidence_refs(
        continuous=continuous,
        confirmed=confirmed,
        reading_trail=reading_trail,
        volume_tabs=volume_tabs,
    )
    status = "ready" if continuous and len(volume_tabs) >= 3 else "partial"
    if not continuous and not confirmed and not volume_tabs:
        status = "empty"

    return {
        "version": VERSION,
        "story_slug": sid,
        "source_kind": source_kind,
        "worldline_id": wid,
        "status": status,
        "default_mode": "novel",
        "default_tab": "continuous_reading" if continuous else "confirmed_chapter",
        "title": _title(continuous, confirmed, volume_tabs),
        "source_runs": {
            "adoption_run_id": adoption_run_id,
            "draft_run_id": draft_run_id,
            "confirmation_run_id": confirmation_run_id,
            "lens_run_id": lens_run_id,
        },
        "continuous_reading": continuous,
        "confirmed_chapter": confirmed,
        "reading_trail": reading_trail,
        "volume_tabs": volume_tabs,
        "perspective_biases": _perspective_biases(continuous, volume_tabs),
        "evidence_panel": {
            "default_open": False,
            "label": "证据链",
            "description": "默认不打断正文阅读；展开后核对沙盘轮次、主观记忆、确认稿和跨卷宗引用。",
            "ref_count": len(evidence_refs),
            "refs": evidence_refs,
        },
        "inline_evidence_anchor_panel": _inline_evidence_anchor_panel(continuous),
        "worldline_dossier": _safe_worldline_dossier(
            sid,
            wid,
            projects_dir=projects_dir,
            outputs_dir=root,
        ),
        "boundaries": [
            "卷宗阅读页只读聚合 continuous_reading_chapter、confirmed_chapter、reading_trail、character_lens_volumes 与 worldline_dossier。",
            "不覆盖既有 artifact，不改变 run_scene 默认行为。",
            "证据链默认折叠，正文阅读态优先。缺少单个来源时降级为 partial 或 empty。",
        ],
    }


def _latest_artifact_run(
    root: Path,
    artifact: str,
    *,
    story_slug: str,
    worldline_id: str,
) -> tuple[str, dict[str, Any]]:
    if not root.exists():
        return "", {}
    candidates: list[tuple[float, str, dict[str, Any]]] = []
    for path in root.glob(f"*/{artifact}"):
        payload = _read_json(path)
        if not payload:
            continue
        if payload.get("story_slug") != story_slug:
            continue
        if str(payload.get("worldline_id") or "main") != worldline_id:
            continue
        candidates.append((path.stat().st_mtime, path.parent.name, payload))
    if not candidates:
        return "", {}
    candidates.sort(reverse=True, key=lambda item: item[0])
    return candidates[0][1], candidates[0][2]


def _continuous_reading(
    run_dir: Path | None,
    draft: dict[str, Any],
) -> dict[str, Any]:
    payload = (
        draft.get("continuous_reading_chapter")
        if isinstance(draft.get("continuous_reading_chapter"), dict)
        else {}
    )
    if not payload and run_dir:
        payload = _read_named_json(run_dir, "continuous_reading_chapter.json")
    if not payload:
        return {}
    return payload


def _confirmed_chapter(
    run_dir: Path | None,
    confirmation: dict[str, Any],
) -> dict[str, Any]:
    if not confirmation:
        return {}
    body_md = ""
    if run_dir:
        try:
            body_md = (run_dir / "confirmed_chapter.md").read_text(encoding="utf-8")
        except OSError:
            body_md = ""
    return {
        "artifact": confirmation.get("artifact") or "confirmed_chapter_entry.json",
        "markdown_artifact": "confirmed_chapter.md",
        "chapter_title": confirmation.get("chapter_title") or "",
        "body_md": body_md or str(confirmation.get("chapter_text") or ""),
        "edited": bool(confirmation.get("edited")),
        "author_note": confirmation.get("author_note") or "",
        "continuation_effect": confirmation.get("continuation_effect") or {},
        "evidence_chain": confirmation.get("evidence_chain") or {},
    }


def _continuous_with_inline_evidence(
    continuous: dict[str, Any],
    volume_tabs: list[dict[str, Any]],
) -> dict[str, Any]:
    sections = (
        continuous.get("reading_sections")
        if isinstance(continuous.get("reading_sections"), list)
        else []
    )
    if not continuous or not sections:
        return continuous
    next_continuous = dict(continuous)
    next_sections: list[dict[str, Any]] = []
    available_tabs = {str(tab.get("id") or "") for tab in volume_tabs}
    for section in sections:
        if not isinstance(section, dict):
            continue
        next_section = dict(section)
        refs = _section_evidence_refs(next_section)
        next_section["inline_evidence_anchors"] = _inline_evidence_anchors_for_section(
            section=next_section,
            refs=refs,
            available_tabs=available_tabs,
        )
        next_sections.append(next_section)
    next_continuous["reading_sections"] = next_sections
    return next_continuous


def _inline_evidence_anchors_for_section(
    *,
    section: dict[str, Any],
    refs: list[str],
    available_tabs: set[str],
) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    section_id = str(section.get("id") or "")
    title = str(section.get("title") or "当前段落")
    ref_text = " ".join(refs)
    viewpoint = str(section.get("viewpoint") or "")

    def add(
        *,
        kind: str,
        label: str,
        heading: str,
        detail: str,
        target: dict[str, str],
        evidence_ref: str,
    ) -> None:
        if any(item.get("kind") == kind for item in anchors):
            return
        anchors.append(
            {
                "id": f"{section_id}-{kind}" if section_id else kind,
                "kind": kind,
                "label": label,
                "title": heading,
                "detail": detail,
                "source_section_id": section_id,
                "source_section_title": title,
                "evidence_ref": evidence_ref,
                "target": target,
            }
        )

    if (
        "character_volume" in ref_text
        or "subjective_memory" in ref_text
        or "角色" in viewpoint
    ) and "character_volume" in available_tabs:
        add(
            kind="character_memory",
            label="角色记忆",
            heading="跳到角色个人卷",
            detail="看这一段被谁记住、误读或隐瞒。",
            target={"type": "tab", "tab": "character_volume"},
            evidence_ref=_first_ref(refs, ("character_volume", "subjective_memory")),
        )
    if "world_chronicle" in ref_text or "worldline_state" in ref_text or "世界" in viewpoint:
        add(
            kind="world_state",
            label="世界状态",
            heading="查看世界线变化",
            detail="核对世界承认了什么，以及状态怎样继续发酵。",
            target={"type": "worldline", "section": "world_state"},
            evidence_ref=_first_ref(refs, ("worldline_state", "world_chronicle")),
        )
    if "consequence_state" in ref_text or "materialized_consequences" in ref_text:
        add(
            kind="causal_debt",
            label="因果债",
            heading="追因果代偿",
            detail="看这段正文背后的债务、代偿和下一轮压力。",
            target={"type": "worldline", "section": "consequence_state"},
            evidence_ref=_first_ref(refs, ("consequence_state", "materialized_consequences")),
        )
    if "event_multi_perspective" in ref_text or "事件" in viewpoint:
        add(
            kind="event_perspective",
            label="事件视角",
            heading="打开事件多视角",
            detail="从同一事件的不同误读里核对这段冲突。",
            target={"type": "event_perspective", "event_id": "main"},
            evidence_ref=_first_ref(refs, ("event_multi_perspective",)),
        )
    if (
        "author_adoption" in ref_text
        or "next_chapter_brief" in ref_text
        or "draft_revision_pack" in ref_text
    ):
        add(
            kind="author_adoption",
            label="作者证据",
            heading="送到作者采纳台",
            detail="查看这段如何变成下一章 brief、Reviewer 或确认入卷材料。",
            target={"type": "author", "section": "adoption_evidence"},
            evidence_ref=_first_ref(
                refs,
                ("author_adoption", "next_chapter_brief", "draft_revision_pack"),
            ),
        )
    return anchors


def _inline_evidence_anchor_panel(continuous: dict[str, Any]) -> dict[str, Any]:
    sections = (
        continuous.get("reading_sections")
        if isinstance(continuous.get("reading_sections"), list)
        else []
    )
    anchors = [
        anchor
        for section in sections
        if isinstance(section, dict)
        for anchor in section.get("inline_evidence_anchors", [])
        if isinstance(anchor, dict)
    ]
    return {
        "label": "正文内证据锚点",
        "description": (
            "读到关键段落时，可跳到角色记忆、世界状态、因果债、"
            "事件视角或作者采纳证据；默认仍先读正文。"
        ),
        "anchor_count": len(anchors),
        "kinds": sorted({str(anchor.get("kind") or "") for anchor in anchors if anchor.get("kind")}),
    }


def _section_evidence_refs(section: dict[str, Any]) -> list[str]:
    mode = section.get("evidence_mode") if isinstance(section.get("evidence_mode"), dict) else {}
    refs = (
        mode.get("refs")
        if isinstance(mode.get("refs"), list) and mode.get("refs")
        else section.get("evidence_refs")
    )
    return [str(ref) for ref in refs or [] if str(ref)]


def _first_ref(refs: list[str], needles: tuple[str, ...]) -> str:
    for ref in refs:
        if any(needle in ref for needle in needles):
            return ref
    return refs[0] if refs else ""


def _volume_tabs(payload: dict[str, Any], lens_run_id: str) -> list[dict[str, Any]]:
    volumes = payload.get("volumes") if isinstance(payload.get("volumes"), list) else []
    tabs: list[dict[str, Any]] = []
    order = {
        "world_chronicle": 0,
        "anchor_volume": 1,
        "character_volume": 2,
        "faction_volume": 3,
        "event_multi_perspective": 4,
    }
    for volume in volumes:
        if not isinstance(volume, dict):
            continue
        volume_type = str(volume.get("volume_type") or "")
        if volume_type not in order:
            continue
        artifact = (
            f"outputs/{lens_run_id}/character_lens_volumes.json#{volume_type}"
            if lens_run_id
            else f"character_lens_volumes.json#{volume_type}"
        )
        tabs.append(
            {
                "id": volume_type,
                "label": _volume_label(volume_type),
                "title": volume.get("title") or _volume_label(volume_type),
                "body_md": _volume_body(volume),
                "character_id": volume.get("character_id") or "",
                "character_name": volume.get("character_name") or "",
                "cognitive_bias": _volume_bias(volume_type, volume),
                "evidence_refs": _volume_evidence_refs(volume, artifact),
                "evidence_chain": volume.get("evidence_chain") or {},
                "information_gap": volume.get("information_gap") or {},
                "novel_scene_plan": volume.get("novel_scene_plan") or [],
                "artifact": artifact,
                "default_open": False,
            }
        )
    tabs.sort(key=lambda item: order.get(str(item.get("id")), 99))
    return tabs


def _volume_body(volume: dict[str, Any]) -> str:
    prose = str(volume.get("prose") or "").strip()
    title = str(volume.get("title") or "").strip()
    if not prose:
        return ""
    if title:
        return f"## {title}\n\n{prose}"
    return prose


def _volume_bias(volume_type: str, volume: dict[str, Any]) -> str:
    if volume_type == "world_chronicle":
        return "正史卷只记录外显后果，压低个人辩解，因此会遮蔽角色的自保理由。"
    if volume_type == "anchor_volume":
        return "主锚点卷把压力集中到核心角色身上，容易把旁支代价读成背景噪音。"
    if volume_type == "character_volume":
        name = str(volume.get("character_name") or "角色")
        return f"{name}只相信自己看见和记住的部分，容易把别人的沉默误读成背叛或试探。"
    if volume_type == "faction_volume":
        return "势力卷只关心资源、解释权和公开姿态，容易把个人的真实意图压成阵营利益。"
    return "事件多视角保留多人的误读，同一动作会被不同角色解释成算计、退让或隐瞒。"


def _perspective_biases(
    continuous: dict[str, Any],
    volume_tabs: list[dict[str, Any]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    sections = (
        continuous.get("reading_sections")
        if isinstance(continuous.get("reading_sections"), list)
        else []
    )
    for section in sections:
        if not isinstance(section, dict):
            continue
        bias = str(section.get("cognitive_bias") or "").strip()
        if not bias:
            continue
        rows.append(
            {
                "id": str(section.get("id") or f"section_{len(rows) + 1}"),
                "label": str(section.get("viewpoint") or section.get("title") or "正文视角"),
                "cognitive_bias": bias,
                "source": "continuous_reading",
            }
        )
    for tab in volume_tabs:
        rows.append(
            {
                "id": str(tab.get("id") or ""),
                "label": str(tab.get("label") or ""),
                "cognitive_bias": str(tab.get("cognitive_bias") or ""),
                "source": "volume_tab",
            }
        )
    return rows


def _evidence_refs(
    *,
    continuous: dict[str, Any],
    confirmed: dict[str, Any],
    reading_trail: dict[str, Any],
    volume_tabs: list[dict[str, Any]],
) -> list[str]:
    refs: list[str] = []
    sections = (
        continuous.get("reading_sections")
        if isinstance(continuous.get("reading_sections"), list)
        else []
    )
    for section in sections:
        if isinstance(section, dict):
            refs.extend(str(ref) for ref in section.get("evidence_refs") or [] if ref)
    refs.extend(str(ref) for ref in confirmed.get("evidence_chain", {}).values() if isinstance(ref, str) and ref)
    trail_sections = (
        reading_trail.get("sections")
        if isinstance(reading_trail.get("sections"), list)
        else []
    )
    for section in trail_sections:
        if isinstance(section, dict):
            refs.extend(str(ref) for ref in section.get("evidence_refs") or [] if ref)
    for tab in volume_tabs:
        refs.extend(str(ref) for ref in tab.get("evidence_refs") or [] if ref)
    return sorted(set(refs))


def _source_lens_run_id(
    continuous: dict[str, Any],
    reading_trail: dict[str, Any],
) -> str:
    s8 = continuous.get("s8_source") if isinstance(continuous.get("s8_source"), dict) else {}
    lens_run_id = str(s8.get("lens_run_id") or reading_trail.get("source_lens_run_id") or "")
    return safe_id(lens_run_id.strip()) or ""


def _safe_worldline_dossier(
    story_slug: str,
    worldline_id: str,
    *,
    projects_dir: Path | None,
    outputs_dir: Path,
) -> dict[str, Any]:
    try:
        dossier = get_worldline_dossier(
            story_slug,
            worldline_id=worldline_id,
            projects_dir=projects_dir,
            outputs_dir=outputs_dir,
        )
    except Exception:
        return {}
    return {
        "version": dossier.get("version") or "",
        "worldline_id": dossier.get("worldline_id") or worldline_id,
        "checkpoint_count": dossier.get("checkpoint_count") or 0,
        "task_count": dossier.get("task_count") or 0,
        "next_actions": dossier.get("next_actions") or [],
        "worldline_state": dossier.get("worldline_state") or {},
    }


def _title(
    continuous: dict[str, Any],
    confirmed: dict[str, Any],
    volume_tabs: list[dict[str, Any]],
) -> str:
    return (
        str(continuous.get("chapter_title") or "")
        or str(confirmed.get("chapter_title") or "")
        or (str(volume_tabs[0].get("title") or "") if volume_tabs else "")
        or "世界内部卷宗"
    )


def _read_named_json(run_dir: Path | None, artifact: str) -> dict[str, Any]:
    if not run_dir:
        return {}
    return _read_json(run_dir / artifact)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DossierReadingRequestError(f"{path.name} 无法解析：{exc}") from exc
    return payload if isinstance(payload, dict) else {}


def _volume_label(volume_type: str) -> str:
    return {
        "world_chronicle": "世界正史卷",
        "anchor_volume": "主锚点卷",
        "character_volume": "角色个人卷",
        "faction_volume": "势力卷",
        "event_multi_perspective": "事件多视角",
    }.get(volume_type, volume_type)


def _volume_evidence_refs(volume: dict[str, Any], artifact: str) -> list[str]:
    refs = [artifact]
    chain = volume.get("evidence_chain") if isinstance(volume.get("evidence_chain"), dict) else {}
    for value in chain.values():
        if isinstance(value, str) and value:
            refs.append(value)
        elif isinstance(value, list):
            refs.extend(str(item) for item in value if item)
    return sorted(set(refs))


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise DossierReadingRequestError(f"{label} 无效")
    return checked

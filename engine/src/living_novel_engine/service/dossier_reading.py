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

    continuous = _continuous_reading(run_dir, draft)
    confirmed = _confirmed_chapter(run_dir, confirmation)
    reading_trail = _read_named_json(run_dir, "confirmed_chapter_reading_trail.json")
    lens_run_id = _source_lens_run_id(continuous, reading_trail)
    lens_payload = _read_named_json(root / lens_run_id if lens_run_id else None, "character_lens_volumes.json")
    volume_tabs = _volume_tabs(lens_payload, lens_run_id)
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


def _volume_tabs(payload: dict[str, Any], lens_run_id: str) -> list[dict[str, Any]]:
    volumes = payload.get("volumes") if isinstance(payload.get("volumes"), list) else []
    tabs: list[dict[str, Any]] = []
    order = {
        "world_chronicle": 0,
        "anchor_volume": 1,
        "character_volume": 2,
        "event_multi_perspective": 3,
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

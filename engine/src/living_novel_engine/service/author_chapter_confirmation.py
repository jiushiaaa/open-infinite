"""Confirm an edited author chapter draft as a worldline continuation entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.project_health import resolve_story_path
from living_novel_engine.service.worldline_state import (
    apply_confirmed_chapter_to_worldline_state,
)

VERSION = "author-chapter-confirmation-v1"
ARTIFACT = "confirmed_chapter_entry.json"
MARKDOWN_ARTIFACT = "confirmed_chapter.md"
READING_TRAIL_ARTIFACT = "confirmed_chapter_reading_trail.json"


class AuthorChapterConfirmationRequestError(ValueError):
    """Invalid author chapter confirmation request."""


def confirm_author_chapter_entry(
    story_slug: str,
    *,
    adoption_run_id: str,
    edited_chapter_text: str = "",
    author_note: str = "",
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
) -> dict[str, Any]:
    """Confirm a generated or edited chapter draft as the next worldline entry."""

    sid = _checked_id(story_slug, "story_slug")
    rid = _checked_id(adoption_run_id, "adoption_run_id")
    story_path, source_kind = resolve_story_path(sid, projects_dir)
    root = outputs_dir or default_outputs_dir()
    run_dir = root / rid
    record_path = run_dir / "author_adoption_record.json"
    brief_path = run_dir / "next_chapter_brief.json"
    draft_path = run_dir / "next_chapter_draft.json"
    if not record_path.exists() or not brief_path.exists():
        raise FileNotFoundError(f"作者采纳记录或下一章 brief 不存在: {rid}")
    if not draft_path.exists():
        raise FileNotFoundError(f"下一章草稿不存在，请先生成草稿: {rid}")
    record = _read_json(record_path)
    brief = _read_json(brief_path)
    draft = _read_json(draft_path)
    if record.get("story_slug") != sid or draft.get("story_slug") != sid:
        raise AuthorChapterConfirmationRequestError("adoption_run_id 不属于当前故事")
    worldline_id = _checked_id(str(record.get("worldline_id") or "main"), "worldline_id")
    draft_text = str(draft.get("chapter_text") or "")
    chapter_text = _chapter_text(edited_chapter_text, draft_text)
    edited = bool(_strip_text(edited_chapter_text)) and _strip_text(chapter_text) != _strip_text(
        draft_text
    )
    note = _clean(author_note)
    title = str(draft.get("chapter_title") or _chapter_title(brief))
    accepted_rewrites = _accepted_local_rewrites(run_dir)
    next_sandbox_entry = _next_sandbox_entry(
        brief=brief,
        title=title,
        author_note=note,
        chapter_text=chapter_text,
        accepted_rewrites=accepted_rewrites,
    )
    worldline_state = apply_confirmed_chapter_to_worldline_state(
        story_path=story_path,
        worldline_id=worldline_id,
        source_adoption_run_id=rid,
        chapter_title=title,
        chapter_text=chapter_text,
        author_note=note,
        edited=edited,
        artifact=ARTIFACT,
        markdown_artifact=MARKDOWN_ARTIFACT,
        next_sandbox_entry=next_sandbox_entry,
        accepted_rewrite_ids=accepted_rewrites.get("applied_rewrite_ids")
        if accepted_rewrites
        else [],
        accepted_rewrites_artifact=accepted_rewrites.get("artifact", "")
        if accepted_rewrites
        else "",
    )
    reading_trail = _reading_trail(
        record=record,
        worldline_state=worldline_state,
        outputs_root=root,
    )
    now = datetime.now().isoformat(timespec="seconds")
    report = {
        "version": VERSION,
        "artifact": ARTIFACT,
        "story_slug": sid,
        "source_kind": source_kind,
        "worldline_id": worldline_id,
        "source_adoption_run_id": rid,
        "created_at": now,
        "edited": edited,
        "chapter_title": title,
        "chapter_text": chapter_text,
        "author_note": note,
        "evidence_chain": {
            "adoption_record": "author_adoption_record.json",
            "next_chapter_brief": "next_chapter_brief.json",
            "next_chapter_draft": "next_chapter_draft.json",
            "worldline_state_artifact": worldline_state.get("artifact") or "",
            "sandbox_inputs": brief.get("sandbox_inputs") or {},
            "materialized_consequences": brief.get("materialized_consequences") or [],
            "reading_trail": READING_TRAIL_ARTIFACT,
            "accepted_local_rewrites": accepted_rewrites.get("artifact", "")
            if accepted_rewrites
            else "",
        },
        "accepted_local_rewrites": accepted_rewrites,
        "continuation_effect": {
            "affects_future_sandbox": True,
            "worldline_state_artifact": worldline_state.get("artifact") or "",
            "next_sandbox_entry": next_sandbox_entry,
        },
        "reading_trail": reading_trail,
        "reviewer_checklist": _reviewer_checklist(
            chapter_text,
            brief,
            worldline_state,
            reading_trail,
        ),
        "artifacts": {
            "confirmed_chapter_entry": ARTIFACT,
            "confirmed_chapter_markdown": MARKDOWN_ARTIFACT,
            "confirmed_chapter_reading_trail": READING_TRAIL_ARTIFACT,
        },
        "boundaries": [
            "正式入卷只写入作者采纳 run 目录和 worldline_state，不覆盖正史 chapter.md。",
            "确认结果会成为后续沙盘的读取入口，但不改 run_scene 默认行为。",
            "确认动作不调用外部模型；真实文本质量由生成草稿 smoke 或人工编辑验收。",
        ],
    }
    (run_dir / ARTIFACT).write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / MARKDOWN_ARTIFACT).write_text(_markdown(report), encoding="utf-8")
    (run_dir / READING_TRAIL_ARTIFACT).write_text(
        json.dumps(reading_trail, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def _accepted_local_rewrites(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "accepted_local_rewrites.json"
    if not path.exists():
        return {}
    payload = _read_json(path)
    ids = payload.get("applied_rewrite_ids")
    rewrites = payload.get("applied_rewrites")
    return {
        "artifact": str(payload.get("artifact") or "accepted_local_rewrites.json"),
        "markdown_artifact": str(payload.get("markdown_artifact") or ""),
        "applied_rewrite_ids": [str(item) for item in ids] if isinstance(ids, list) else [],
        "applied_rewrite_count": len(ids) if isinstance(ids, list) else 0,
        "applied_rewrites": rewrites if isinstance(rewrites, list) else [],
        "author_note": str(payload.get("author_note") or ""),
        "feeds": payload.get("feeds") if isinstance(payload.get("feeds"), list) else [],
    }


def _chapter_text(edited: str, draft_text: str) -> str:
    text = str(edited or "").strip() or str(draft_text or "").strip()
    if len(_strip_text(text)) < 120:
        raise AuthorChapterConfirmationRequestError("确认章节正文过短，无法正式入卷")
    if len(text) > 20000:
        raise AuthorChapterConfirmationRequestError("确认章节正文过长，请先拆分章节")
    return text


def _next_sandbox_entry(
    *,
    brief: dict[str, Any],
    title: str,
    author_note: str,
    chapter_text: str,
    accepted_rewrites: dict[str, Any] | None = None,
) -> dict[str, str]:
    sandbox_inputs = brief.get("sandbox_inputs") if isinstance(brief.get("sandbox_inputs"), dict) else {}
    seed = author_note or str(sandbox_inputs.get("major_event") or title)
    entry = {
        "major_event": f"作者确认章节：{seed}",
        "worldline_id": str(sandbox_inputs.get("worldline_id") or brief.get("worldline_id") or "main"),
        "confirmed_chapter_artifact": ARTIFACT,
        "confirmed_chapter_markdown": MARKDOWN_ARTIFACT,
        "chapter_summary": _trim(chapter_text, 140),
    }
    if accepted_rewrites:
        ids = accepted_rewrites.get("applied_rewrite_ids")
        entry["accepted_local_rewrites"] = str(accepted_rewrites.get("artifact") or "")
        entry["accepted_rewrite_ids"] = "、".join(str(item) for item in ids if item) if isinstance(ids, list) else ""
    return entry


def _reviewer_checklist(
    chapter_text: str,
    brief: dict[str, Any],
    worldline_state: dict[str, Any],
    reading_trail: dict[str, Any],
) -> list[dict[str, Any]]:
    checks = [
        {
            "item": "确认章节保留可读正文",
            "passed": len(_strip_text(chapter_text)) >= 120,
        },
        {
            "item": "保留角色信息差或误判",
            "passed": any(
                word in chapter_text
                for word in ("误判", "信息差", "隐瞒", "怀疑", "没有说明", "没有拆穿")
            ),
        },
        {
            "item": "延续世界内因果或代偿",
            "passed": bool(brief.get("materialized_consequences"))
            or any(word in chapter_text for word in ("因果债", "代偿", "世界线", "归云斋")),
        },
        {
            "item": "写入后续沙盘读取入口",
            "passed": bool(worldline_state.get("confirmed_chapter_entry"))
            and (
                worldline_state.get("confirmed_chapter_entry")
                if isinstance(worldline_state.get("confirmed_chapter_entry"), dict)
                else {}
            ).get("affects_future_sandbox")
            is True,
        },
        {
            "item": "不覆盖正史 chapter.md",
            "passed": True,
        },
    ]
    if reading_trail.get("status") == "ready":
        checks.append(
            {
                "item": "可回读世界正史卷、角色个人卷和事件多视角",
                "passed": _has_cross_volume_sections(reading_trail),
            }
        )
    return checks


def _reading_trail(
    *,
    record: dict[str, Any],
    worldline_state: dict[str, Any],
    outputs_root: Path,
) -> dict[str, Any]:
    adoption_entry = (
        record.get("adoption_entry") if isinstance(record.get("adoption_entry"), dict) else {}
    )
    source_lens_run_id = str(adoption_entry.get("source_run_id") or "").strip()
    source_lens_run_id = safe_id(source_lens_run_id) or ""
    sections = [
        {
            "id": "confirmed_chapter",
            "label": "确认正文",
            "artifact": MARKDOWN_ARTIFACT,
            "reason": "作者最终确认的正文，从这里回看世界为什么会写成这一章。",
            "evidence_refs": [ARTIFACT, MARKDOWN_ARTIFACT],
        },
        {
            "id": "worldline_state",
            "label": "世界线状态",
            "artifact": str(worldline_state.get("artifact") or ""),
            "reason": "确认章节已绑定的世界线、后续沙盘入口和分支状态。",
            "evidence_refs": [str(worldline_state.get("artifact") or "")],
        },
        {
            "id": "author_adoption",
            "label": "作者采纳记录",
            "artifact": "author_adoption_record.json",
            "reason": "原大纲、沙盘涌现剧情和采纳方式的对照。",
            "evidence_refs": ["author_adoption_record.json", "next_chapter_brief.json"],
        },
    ]
    lens_payload = _read_lens_volumes(outputs_root, source_lens_run_id)
    source = lens_payload.get("source") if isinstance(lens_payload.get("source"), dict) else {}
    volumes = lens_payload.get("volumes") if isinstance(lens_payload.get("volumes"), list) else []
    for volume_type, label in (
        ("world_chronicle", "世界正史卷"),
        ("character_volume", "角色个人卷"),
        ("event_multi_perspective", "事件多视角"),
    ):
        volume = _find_volume(volumes, volume_type)
        if not volume:
            continue
        artifact = f"outputs/{source_lens_run_id}/character_lens_volumes.json#{volume_type}"
        section = {
            "id": volume_type,
            "label": label,
            "title": str(volume.get("title") or label),
            "artifact": artifact,
            "reason": _volume_reason(volume_type),
            "evidence_refs": _volume_evidence_refs(
                volume=volume,
                artifact=artifact,
                sandbox_run_id=str(source.get("sandbox_run_id") or ""),
            ),
        }
        if volume_type == "character_volume":
            section["character_id"] = str(volume.get("character_id") or "")
            section["character_name"] = str(volume.get("character_name") or "")
            event_nodes = volume.get("event_nodes") if isinstance(volume.get("event_nodes"), list) else []
            section["event_node_count"] = len(event_nodes)
        sections.append(section)
    status = "ready" if _has_cross_volume_sections({"sections": sections}) else "partial"
    return {
        "version": VERSION,
        "artifact": READING_TRAIL_ARTIFACT,
        "status": status,
        "source_lens_run_id": source_lens_run_id,
        "source_sandbox_run_id": str(source.get("sandbox_run_id") or ""),
        "sections": sections,
        "next_reader_actions": [
            "先读确认正文，再回看世界线状态确认下一轮如何继续。",
            "回到世界正史卷看客观后果，再读角色个人卷看信息差。",
            "从事件多视角核对同一事件在不同角色眼中的裂缝。",
        ],
        "boundaries": [
            "跨卷宗阅读链只引用现有作者采纳、多视角和世界线 artifact。",
            "缺少来源 lens run 时降级为 partial，不阻断确认入卷。",
        ],
    }


def _chapter_title(brief: dict[str, Any]) -> str:
    conflict = str(brief.get("conflict_focus") or "")
    if "因果债" in conflict:
        return "下一章 因果债入卷"
    if "隐瞒" in conflict or "误判" in conflict:
        return "下一章 风鸣铃后的确认"
    return "下一章 作者确认的世界线"


def _read_lens_volumes(outputs_root: Path, lens_run_id: str) -> dict[str, Any]:
    if not lens_run_id:
        return {}
    path = outputs_root / lens_run_id / "character_lens_volumes.json"
    if not path.exists():
        return {}
    return _read_json(path)


def _find_volume(volumes: list[Any], volume_type: str) -> dict[str, Any]:
    for volume in volumes:
        if isinstance(volume, dict) and volume.get("volume_type") == volume_type:
            return volume
    return {}


def _has_cross_volume_sections(reading_trail: dict[str, Any]) -> bool:
    sections = (
        reading_trail.get("sections")
        if isinstance(reading_trail.get("sections"), list)
        else []
    )
    section_ids = {section.get("id") for section in sections if isinstance(section, dict)}
    return {"world_chronicle", "character_volume", "event_multi_perspective"} <= section_ids


def _volume_reason(volume_type: str) -> str:
    if volume_type == "world_chronicle":
        return "用正史卷确认这一章对应的客观世界后果。"
    if volume_type == "character_volume":
        return "用角色个人卷确认这一章保留了主观记忆、误会和连续事件节点。"
    return "用事件多视角确认同一事件在不同角色眼中的信息差。"


def _volume_evidence_refs(
    *,
    volume: dict[str, Any],
    artifact: str,
    sandbox_run_id: str,
) -> list[str]:
    refs = [artifact]
    if sandbox_run_id:
        refs.append(f"outputs/{sandbox_run_id}/sandbox_rounds.jsonl")
    evidence_chain = (
        volume.get("evidence_chain")
        if isinstance(volume.get("evidence_chain"), dict)
        else {}
    )
    subjective_refs = evidence_chain.get("subjective_memory_refs")
    if isinstance(subjective_refs, list) and subjective_refs:
        refs.append("subjective_memory.jsonl")
    consequence_refs = evidence_chain.get("consequence_state_refs")
    if isinstance(consequence_refs, list) and consequence_refs:
        refs.append("worldline_state.json#consequence_state")
    return list(dict.fromkeys(ref for ref in refs if ref))


def _markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {report['chapter_title']}",
            "",
            report["chapter_text"],
            "",
            "## 入卷证据",
            "",
            f"- 作者采纳：{report['evidence_chain']['adoption_record']}",
            f"- 下一章 brief：{report['evidence_chain']['next_chapter_brief']}",
            f"- 草稿：{report['evidence_chain']['next_chapter_draft']}",
            f"- 世界线状态：{report['evidence_chain']['worldline_state_artifact']}",
            f"- 跨卷宗阅读链：{report['evidence_chain']['reading_trail']}",
            "",
            "## 下一轮沙盘入口",
            "",
            report["continuation_effect"]["next_sandbox_entry"]["major_event"],
            "",
            "## 跨卷宗阅读",
            "",
            "\n".join(
                f"- {section['label']}：{section['artifact']}"
                for section in report["reading_trail"]["sections"]
            ),
            "",
            "## Reviewer 检查",
            "",
            "\n".join(
                f"- {'通过' if row['passed'] else '待补'}：{row['item']}"
                for row in report["reviewer_checklist"]
            ),
            "",
        ]
    )


def _read_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthorChapterConfirmationRequestError(f"{path.name} 无法解析：{exc}") from exc
    return raw if isinstance(raw, dict) else {}


def _clean(value: object) -> str:
    return " ".join(str(value or "").split())


def _strip_text(value: object) -> str:
    return "".join(str(value or "").split())


def _trim(value: object, limit: int) -> str:
    clean = _clean(value)
    return clean if len(clean) <= limit else clean[:limit] + "..."


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise AuthorChapterConfirmationRequestError(f"{label} 无效")
    return checked

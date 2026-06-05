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
    next_sandbox_entry = _next_sandbox_entry(
        brief=brief,
        title=title,
        author_note=note,
        chapter_text=chapter_text,
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
        },
        "continuation_effect": {
            "affects_future_sandbox": True,
            "worldline_state_artifact": worldline_state.get("artifact") or "",
            "next_sandbox_entry": next_sandbox_entry,
        },
        "reviewer_checklist": _reviewer_checklist(
            chapter_text,
            brief,
            worldline_state,
        ),
        "artifacts": {
            "confirmed_chapter_entry": ARTIFACT,
            "confirmed_chapter_markdown": MARKDOWN_ARTIFACT,
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
    return report


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
) -> dict[str, str]:
    sandbox_inputs = brief.get("sandbox_inputs") if isinstance(brief.get("sandbox_inputs"), dict) else {}
    seed = author_note or str(sandbox_inputs.get("major_event") or title)
    return {
        "major_event": f"作者确认章节：{seed}",
        "worldline_id": str(sandbox_inputs.get("worldline_id") or brief.get("worldline_id") or "main"),
        "confirmed_chapter_artifact": ARTIFACT,
        "confirmed_chapter_markdown": MARKDOWN_ARTIFACT,
        "chapter_summary": _trim(chapter_text, 140),
    }


def _reviewer_checklist(
    chapter_text: str,
    brief: dict[str, Any],
    worldline_state: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
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


def _chapter_title(brief: dict[str, Any]) -> str:
    conflict = str(brief.get("conflict_focus") or "")
    if "因果债" in conflict:
        return "下一章 因果债入卷"
    if "隐瞒" in conflict or "误判" in conflict:
        return "下一章 风鸣铃后的确认"
    return "下一章 作者确认的世界线"


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
            "",
            "## 下一轮沙盘入口",
            "",
            report["continuation_effect"]["next_sandbox_entry"]["major_event"],
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

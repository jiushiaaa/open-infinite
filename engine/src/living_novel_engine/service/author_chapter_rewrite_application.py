"""Apply selected reviewer local rewrites to an author chapter draft."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.project_health import resolve_story_path

VERSION = "author-chapter-rewrite-application-v1"
ARTIFACT = "accepted_local_rewrites.json"
MARKDOWN_ARTIFACT = "next_chapter_draft_revised.md"


class AuthorChapterRewriteApplicationRequestError(ValueError):
    """Invalid author chapter rewrite application request."""


def apply_author_chapter_rewrites(
    story_slug: str,
    *,
    adoption_run_id: str,
    rewrite_ids: list[str] | None = None,
    author_note: str = "",
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
) -> dict[str, Any]:
    """Append selected reviewer rewrites to a revised draft artifact."""

    sid = _checked_id(story_slug, "story_slug")
    rid = _checked_id(adoption_run_id, "adoption_run_id")
    resolve_story_path(sid, projects_dir)
    root = outputs_dir or default_outputs_dir()
    run_dir = root / rid
    draft_path = run_dir / "next_chapter_draft.json"
    revision_path = run_dir / "draft_revision_pack.json"
    if not draft_path.exists():
        raise FileNotFoundError(f"下一章草稿不存在，请先生成草稿: {rid}")
    if not revision_path.exists():
        raise FileNotFoundError(f"Reviewer 局部修订包不存在: {rid}")

    draft = _read_json(draft_path)
    revision_pack = _read_json(revision_path)
    if draft.get("story_slug") != sid:
        raise AuthorChapterRewriteApplicationRequestError("adoption_run_id 不属于当前故事")

    localized = revision_pack.get("localized_rewrites")
    if not isinstance(localized, list) or not localized:
        raise AuthorChapterRewriteApplicationRequestError("当前草稿没有可采纳的局部重写建议")

    requested_ids = _checked_rewrite_ids(rewrite_ids, localized)
    by_id = {
        str(item.get("id") or ""): item for item in localized if isinstance(item, dict)
    }
    missing = [item_id for item_id in requested_ids if item_id not in by_id]
    if missing:
        raise AuthorChapterRewriteApplicationRequestError(
            f"未找到局部重写建议: {', '.join(missing)}"
        )

    applied_rewrites = [_rewrite_application_row(by_id[item_id]) for item_id in requested_ids]
    revised_chapter_text = _revised_chapter_text(
        str(draft.get("chapter_text") or ""),
        applied_rewrites,
    )
    now = datetime.now().isoformat(timespec="seconds")
    note = _clean(author_note)
    report = {
        "version": VERSION,
        "artifact": ARTIFACT,
        "markdown_artifact": MARKDOWN_ARTIFACT,
        "story_slug": sid,
        "worldline_id": str(draft.get("worldline_id") or "main"),
        "source_adoption_run_id": rid,
        "created_at": now,
        "author_note": note,
        "applied_rewrite_ids": requested_ids,
        "applied_rewrites": applied_rewrites,
        "revised_chapter_text": revised_chapter_text,
        "evidence_chain": {
            "next_chapter_draft": "next_chapter_draft.json",
            "draft_revision_pack": "draft_revision_pack.json",
            "localized_rewrites": [item["id"] for item in applied_rewrites],
        },
        "feeds": [
            "next_chapter_draft",
            "author_adoption_desk",
            "chapter_confirmation",
            "future_sandbox_entry",
        ],
        "does_not_overwrite": [
            "chapter_text",
            "next_chapter_draft.md",
            "confirmed_chapter.md",
            "chapter.md",
        ],
        "boundaries": [
            "局部重写采纳只追加修订稿和采纳记录，不覆盖原草稿正文。",
            "确认入卷会读取 accepted_local_rewrites.json，但仍由作者显式确认。",
        ],
    }
    (run_dir / ARTIFACT).write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / MARKDOWN_ARTIFACT).write_text(_markdown(report), encoding="utf-8")

    draft["accepted_local_rewrites"] = {
        "artifact": ARTIFACT,
        "markdown_artifact": MARKDOWN_ARTIFACT,
        "applied_rewrite_ids": requested_ids,
        "applied_rewrite_count": len(requested_ids),
        "author_note": note,
        "updated_at": now,
        "feeds": report["feeds"],
        "does_not_overwrite": report["does_not_overwrite"],
    }
    draft["chapter_text_with_accepted_rewrites"] = revised_chapter_text
    artifacts = draft.get("artifacts") if isinstance(draft.get("artifacts"), dict) else {}
    artifacts.update(
        {
            "accepted_local_rewrites": ARTIFACT,
            "next_chapter_draft_revised": MARKDOWN_ARTIFACT,
        }
    )
    draft["artifacts"] = artifacts
    draft_path.write_text(
        json.dumps(draft, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def _checked_rewrite_ids(
    rewrite_ids: list[str] | None,
    localized_rewrites: list[Any],
) -> list[str]:
    if rewrite_ids is None:
        rewrite_ids = [
            str(item.get("id") or "")
            for item in localized_rewrites
            if isinstance(item, dict) and str(item.get("id") or "")
        ]
    checked = [_checked_id(str(item), "rewrite_id") for item in rewrite_ids]
    unique: list[str] = []
    for item in checked:
        if item not in unique:
            unique.append(item)
    if not unique:
        raise AuthorChapterRewriteApplicationRequestError("请至少选择一条局部重写建议")
    return unique


def _rewrite_application_row(item: dict[str, Any]) -> dict[str, Any]:
    original_problem = _clean(str(item.get("original_problem") or item.get("issue") or ""))
    revision_intent = _clean(
        str(item.get("revision_intent") or item.get("rewrite_instruction") or "")
    )
    suggested_rewrite = _clean(
        str(item.get("suggested_rewrite") or item.get("suggested_revision") or "")
    )
    if not original_problem or not revision_intent or not suggested_rewrite:
        raise AuthorChapterRewriteApplicationRequestError(
            f"局部重写建议缺少可采纳字段: {item.get('id') or ''}"
        )
    return {
        "id": str(item.get("id") or ""),
        "priority": str(item.get("priority") or "medium"),
        "target_text": _clean(str(item.get("target_text") or "")),
        "original_problem": original_problem,
        "revision_intent": revision_intent,
        "suggested_rewrite": suggested_rewrite,
        "impact_on_characters": [
            str(value)
            for value in (
                item.get("impact_on_characters")
                if isinstance(item.get("impact_on_characters"), list)
                else []
            )
        ],
        "impact_on_world_state": _clean(str(item.get("impact_on_world_state") or "")),
        "adoption_direction": _clean(str(item.get("adoption_direction") or "")),
        "evidence_refs": [
            str(value)
            for value in (
                item.get("evidence_refs") if isinstance(item.get("evidence_refs"), list) else []
            )
        ],
    }


def _revised_chapter_text(chapter_text: str, applied_rewrites: list[dict[str, Any]]) -> str:
    body = chapter_text.strip()
    rows = ["## 已采纳的 Reviewer 局部重写"]
    for item in applied_rewrites:
        characters = "、".join(item["impact_on_characters"]) or "未标明"
        rows.extend(
            [
                "",
                f"### {item['id']}",
                f"原问题：{item['original_problem']}",
                f"修改意图：{item['revision_intent']}",
                f"建议改写：{item['suggested_rewrite']}",
                f"影响角色：{characters}",
                f"影响世界状态：{item['impact_on_world_state'] or '不改写世界状态，仅作为下一章写作提示。'}",
            ]
        )
        if item["adoption_direction"]:
            rows.append(f"采纳方向：{item['adoption_direction']}")
    return f"{body}\n\n" + "\n".join(rows)


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# 已采纳的 Reviewer 局部重写",
        "",
        f"- 采纳数量：{len(report['applied_rewrites'])}",
        f"- 反哺草稿：{MARKDOWN_ARTIFACT}",
        f"- 作者备注：{report.get('author_note') or '未填写'}",
        "",
        report["revised_chapter_text"],
        "",
    ]
    return "\n".join(lines)


def _checked_id(value: str, field_name: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise AuthorChapterRewriteApplicationRequestError(f"invalid {field_name}")
    return checked


def _clean(text: str) -> str:
    return " ".join(str(text or "").strip().split())


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}

"""Long novel ingestion report helpers (v0.8.0).

报告是导入阶段的 additive artifact：供产品 UI 和后续分层记忆使用，
不参与 runner prompt，也不改变既有 source/canon/summaries 契约。
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from statistics import mean

from living_novel_engine.import_novel.splitter import SplitChapter

REPORT_VERSION = "v0.8.6"
DEFAULT_PLAYABLE_LIMIT = 20
SHORT_CHAPTER_CHAR_LIMIT = 20
PREVIEW_CHAR_LIMIT = 160

_FILENAME_CHAPTER_RE = re.compile(r"(?:chapter|chap|ch)[_\-\s]*(\d+)", re.IGNORECASE)


def build_import_report(
    *,
    slug: str,
    chapters: list[SplitChapter],
    source_filenames: list[str] | None = None,
    source_type: str = "manual",
    source_name: str = "",
    long_mode: bool = False,
    warnings: list[str] | None = None,
) -> dict:
    """构造长篇导入报告。

    source_filenames 与 chapters 同序；缺失时只用 normalized chapter index。
    """
    source_filenames = source_filenames or [
        f"chapter_{ch.index:03d}.md" for ch in chapters
    ]
    total_characters = sum(len(ch.content) for ch in chapters)
    duplicate_titles = _duplicate_titles(chapters)
    garbled_chapters = [
        ch.index for ch in chapters if _looks_garbled(ch.content)
    ]
    short_chapters = [
        ch.index for ch in chapters if len(ch.content.strip()) < SHORT_CHAPTER_CHAR_LIMIT
    ]
    missing_numbers = _missing_chapter_numbers(source_filenames)
    playable_limit = min(DEFAULT_PLAYABLE_LIMIT, len(chapters))

    quality_risks = _quality_risks(
        duplicate_titles=duplicate_titles,
        garbled_chapters=garbled_chapters,
        missing_numbers=missing_numbers,
        short_chapters=short_chapters,
    )
    risk_warnings = [risk["message"] for risk in quality_risks]
    all_warnings = list(warnings or []) + risk_warnings

    chapter_reports = []
    for ch, filename in zip(chapters, source_filenames, strict=False):
        content = ch.content.strip()
        chapter_reports.append({
            "index": ch.index,
            "title": ch.title,
            "source_filename": filename,
            "characters": len(ch.content),
            "preview": _preview_text(content),
            "detected_chapter_number": _detect_chapter_number(filename),
            "source_raw_path": f"source_raw/chapter_{ch.index:03d}.md",
            "source_path": f"source/chapter_{ch.index:03d}.md",
        })

    return {
        "version": REPORT_VERSION,
        "slug": slug,
        "created_at": datetime.now().isoformat(),
        "long_mode": bool(long_mode),
        "source": {
            "type": source_type or "manual",
            "name": source_name or "",
            "file_count": len(source_filenames),
            "filenames": list(source_filenames[:50]),
        },
        "total_chapters": len(chapters),
        "total_characters": total_characters,
        "chapter_stats": _chapter_stats(chapters),
        "playable_chapter_limit": playable_limit,
        "partial_ready": len(chapters) > playable_limit,
        "source_raw_dir": "source_raw",
        "source_dir": "source",
        "risks": {
            "garbled_chapters": garbled_chapters,
            "duplicate_titles": duplicate_titles,
            "missing_chapter_numbers": missing_numbers,
            "short_chapters": short_chapters,
        },
        "quality_risks": quality_risks,
        "parsing_warnings": list(warnings or []),
        "recommended_actions": _recommended_actions(
            total_chapters=len(chapters),
            quality_risks=quality_risks,
            partial_ready=len(chapters) > playable_limit,
        ),
        "warnings": all_warnings,
        "chapters": chapter_reports,
    }


def summarize_import_report(report: dict) -> dict:
    """API 返回的紧凑摘要，避免把每章明细塞进 job result。"""
    return {
        "version": report.get("version", REPORT_VERSION),
        "status": report.get("status", "ready"),
        "source": report.get("source", {"type": "unknown"}),
        "total_chapters": int(report.get("total_chapters") or 0),
        "total_characters": int(report.get("total_characters") or 0),
        "chapter_stats": report.get("chapter_stats", {}),
        "playable_chapter_limit": int(report.get("playable_chapter_limit") or 0),
        "partial_ready": bool(report.get("partial_ready", False)),
        "risks": report.get("risks", {}),
        "quality_risks": report.get("quality_risks", []),
        "recommended_actions": report.get("recommended_actions", []),
        "warnings": report.get("warnings", []),
    }


def chapter_previews_from_report(report: dict, *, limit: int = 8) -> list[dict]:
    """Return compact chapter previews from a full import report."""
    previews: list[dict] = []
    chapters = report.get("chapters", [])
    if not isinstance(chapters, list):
        return previews
    for raw in chapters[:limit]:
        if not isinstance(raw, dict):
            continue
        previews.append({
            "index": raw.get("index"),
            "title": raw.get("title", ""),
            "characters": raw.get("characters", 0),
            "preview": raw.get("preview", ""),
            "source_path": raw.get("source_path", ""),
            "source_filename": raw.get("source_filename", ""),
        })
    return previews


def _duplicate_titles(chapters: list[SplitChapter]) -> list[str]:
    counts = Counter(ch.title.strip() for ch in chapters if ch.title.strip())
    return sorted(title for title, count in counts.items() if count > 1)


def _chapter_stats(chapters: list[SplitChapter]) -> dict:
    lengths = [len(ch.content) for ch in chapters]
    if not lengths:
        return {
            "min_characters": 0,
            "max_characters": 0,
            "average_characters": 0,
            "short_chapters": [],
        }
    return {
        "min_characters": min(lengths),
        "max_characters": max(lengths),
        "average_characters": round(mean(lengths), 1),
        "short_chapters": [
            ch.index
            for ch in chapters
            if len(ch.content.strip()) < SHORT_CHAPTER_CHAR_LIMIT
        ],
    }


def _preview_text(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= PREVIEW_CHAR_LIMIT:
        return compact
    return compact[:PREVIEW_CHAR_LIMIT].rstrip() + "..."


def _looks_garbled(text: str) -> bool:
    if "\ufffd" in text or "���" in text:
        return True
    question_marks = text.count("?")
    return question_marks >= 4 and question_marks / max(1, len(text)) > 0.01


def _detect_chapter_number(filename: str) -> int | None:
    match = _FILENAME_CHAPTER_RE.search(filename)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _missing_chapter_numbers(source_filenames: list[str]) -> list[int]:
    numbers = sorted(
        n for n in (_detect_chapter_number(name) for name in source_filenames)
        if n is not None
    )
    if len(numbers) < 2:
        return []
    expected = set(range(numbers[0], numbers[-1] + 1))
    return sorted(expected - set(numbers))


def _quality_risks(
    *,
    duplicate_titles: list[str],
    garbled_chapters: list[int],
    missing_numbers: list[int],
    short_chapters: list[int],
) -> list[dict]:
    risks: list[dict] = []
    if garbled_chapters:
        risks.append({
            "code": "garbled_text",
            "level": "high",
            "message": f"疑似乱码章节：{', '.join(map(str, garbled_chapters))}",
            "chapters": garbled_chapters,
        })
    if duplicate_titles:
        risks.append({
            "code": "duplicate_titles",
            "level": "medium",
            "message": f"疑似重复章名：{', '.join(duplicate_titles)}",
            "titles": duplicate_titles,
        })
    if missing_numbers:
        risks.append({
            "code": "missing_chapter_numbers",
            "level": "medium",
            "message": f"疑似缺章编号：{', '.join(map(str, missing_numbers))}",
            "missing_numbers": missing_numbers,
        })
    if short_chapters:
        risks.append({
            "code": "short_chapters",
            "level": "low",
            "message": f"疑似过短章节：{', '.join(map(str, short_chapters))}",
            "chapters": short_chapters,
        })
    return risks


def _recommended_actions(
    *,
    total_chapters: int,
    quality_risks: list[dict],
    partial_ready: bool,
) -> list[dict]:
    actions = [
        {
            "kind": "review_chapters",
            "label": "核对章节列表",
            "description": "先确认章节顺序、章名和正文片段是否符合原文。",
        },
        {
            "kind": "open_anchor",
            "label": "检查世界锚定",
            "description": "重点查看角色、人设边界、世界规则和开放伏笔。",
        },
    ]
    if quality_risks:
        actions.insert(
            0,
            {
                "kind": "fix_import_risks",
                "label": "处理导入风险",
                "description": "优先修正乱码、缺章、重复章名或过短章节后再继续运行。",
            },
        )
    if partial_ready:
        actions.append({
            "kind": "start_with_playable_range",
            "label": "先从前 20 章体验",
            "description": "长篇项目已可先进入锚定，后续章节管理将在后续版本收束。",
        })
    if total_chapters < 6:
        actions.append({
            "kind": "add_more_chapters",
            "label": "补充更多上下文",
            "description": "章节较少时建议补充到 6 章以上，以提升角色与伏笔抽取质量。",
        })
    return actions

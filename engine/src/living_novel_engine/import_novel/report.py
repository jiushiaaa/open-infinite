"""Long novel ingestion report helpers (v0.8.0).

报告是导入阶段的 additive artifact：供产品 UI 和后续分层记忆使用，
不参与 runner prompt，也不改变既有 source/canon/summaries 契约。
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime

from living_novel_engine.import_novel.splitter import SplitChapter

REPORT_VERSION = "v0.8.0"
DEFAULT_PLAYABLE_LIMIT = 20

_FILENAME_CHAPTER_RE = re.compile(r"(?:chapter|chap|ch)[_\-\s]*(\d+)", re.IGNORECASE)


def build_import_report(
    *,
    slug: str,
    chapters: list[SplitChapter],
    source_filenames: list[str] | None = None,
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
    missing_numbers = _missing_chapter_numbers(source_filenames)
    playable_limit = min(DEFAULT_PLAYABLE_LIMIT, len(chapters))

    risk_warnings = _risk_warnings(
        duplicate_titles=duplicate_titles,
        garbled_chapters=garbled_chapters,
        missing_numbers=missing_numbers,
    )
    all_warnings = list(warnings or []) + risk_warnings

    chapter_reports = []
    for ch, filename in zip(chapters, source_filenames, strict=False):
        chapter_reports.append({
            "index": ch.index,
            "title": ch.title,
            "source_filename": filename,
            "characters": len(ch.content),
            "detected_chapter_number": _detect_chapter_number(filename),
            "source_raw_path": f"source_raw/chapter_{ch.index:03d}.md",
            "source_path": f"source/chapter_{ch.index:03d}.md",
        })

    return {
        "version": REPORT_VERSION,
        "slug": slug,
        "created_at": datetime.now().isoformat(),
        "long_mode": bool(long_mode),
        "total_chapters": len(chapters),
        "total_characters": total_characters,
        "playable_chapter_limit": playable_limit,
        "partial_ready": len(chapters) > playable_limit,
        "source_raw_dir": "source_raw",
        "source_dir": "source",
        "risks": {
            "garbled_chapters": garbled_chapters,
            "duplicate_titles": duplicate_titles,
            "missing_chapter_numbers": missing_numbers,
        },
        "warnings": all_warnings,
        "chapters": chapter_reports,
    }


def summarize_import_report(report: dict) -> dict:
    """API 返回的紧凑摘要，避免把每章明细塞进 job result。"""
    return {
        "version": report.get("version", REPORT_VERSION),
        "total_chapters": int(report.get("total_chapters") or 0),
        "total_characters": int(report.get("total_characters") or 0),
        "playable_chapter_limit": int(report.get("playable_chapter_limit") or 0),
        "partial_ready": bool(report.get("partial_ready", False)),
        "risks": report.get("risks", {}),
        "warnings": report.get("warnings", []),
    }


def _duplicate_titles(chapters: list[SplitChapter]) -> list[str]:
    counts = Counter(ch.title.strip() for ch in chapters if ch.title.strip())
    return sorted(title for title, count in counts.items() if count > 1)


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


def _risk_warnings(
    *,
    duplicate_titles: list[str],
    garbled_chapters: list[int],
    missing_numbers: list[int],
) -> list[str]:
    warnings: list[str] = []
    if garbled_chapters:
        warnings.append(f"疑似乱码章节：{', '.join(map(str, garbled_chapters))}")
    if duplicate_titles:
        warnings.append(f"疑似重复章名：{', '.join(duplicate_titles)}")
    if missing_numbers:
        warnings.append(f"疑似缺章编号：{', '.join(map(str, missing_numbers))}")
    return warnings

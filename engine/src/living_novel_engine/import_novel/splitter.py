"""Chapter Splitter — 拆分用户输入为独立章节文件。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SplitChapter:
    index: int
    title: str
    content: str


CHAPTER_PATTERNS = [
    re.compile(
        r"^(第[一二三四五六七八九十百千万零〇\d]+[章节回])[\s:：]*(.*)$",
        re.MULTILINE,
    ),
    re.compile(r"^(Chapter\s+\d+)[\s:：]*(.*)$", re.MULTILINE | re.IGNORECASE),
]


def split_from_directory(path: Path, *, max_chapters: int = 10) -> list[SplitChapter]:
    """从目录中读取章节文件（按文件名排序）。"""
    if not path.is_dir():
        raise ValueError(f"路径不是目录: {path}")

    files = sorted(
        f
        for f in path.iterdir()
        if f.is_file() and f.suffix.lower() in (".txt", ".md")
    )
    if not files:
        raise ValueError(f"目录中未找到 .txt/.md 文件: {path}")
    if len(files) > max_chapters:
        raise ValueError(
            f"章节数 {len(files)} 超过上限 {max_chapters}，请使用 --max-chapters 或减少文件"
        )

    chapters: list[SplitChapter] = []
    for i, fp in enumerate(files):
        text = fp.read_text(encoding="utf-8")
        title = _extract_title(text, fallback=fp.stem)
        chapters.append(SplitChapter(index=i + 1, title=title, content=text))
    return chapters


def split_from_file(path: Path, *, max_chapters: int = 10) -> list[SplitChapter]:
    """从合并文本中按章节标记拆分。"""
    if not path.is_file():
        raise ValueError(f"路径不是文件: {path}")

    text = path.read_text(encoding="utf-8")

    for pattern in CHAPTER_PATTERNS:
        matches = list(pattern.finditer(text))
        if len(matches) >= 2:
            return _split_by_matches(text, matches, max_chapters=max_chapters)

    raise ValueError(
        f"无法识别章节标记（需要至少 2 个匹配）。"
        f"支持格式：第X章 / Chapter N。请改用目录模式（每文件一章）。"
    )


def split_chapters(path: Path, *, max_chapters: int = 10) -> list[SplitChapter]:
    """自动判断路径是目录还是文件，执行拆分。"""
    if path.is_dir():
        return split_from_directory(path, max_chapters=max_chapters)
    elif path.is_file():
        return split_from_file(path, max_chapters=max_chapters)
    else:
        raise ValueError(f"路径不存在: {path}")


def _split_by_matches(
    text: str, matches: list[re.Match], *, max_chapters: int
) -> list[SplitChapter]:
    chapters: list[SplitChapter] = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[start:end].strip()
        title_part = match.group(2).strip() if match.group(2) else match.group(1)
        title = f"{match.group(1)} {title_part}".strip() if title_part != match.group(1) else match.group(1)
        chapters.append(SplitChapter(index=i + 1, title=title, content=chunk))

    if len(chapters) > max_chapters:
        raise ValueError(
            f"章节数 {len(chapters)} 超过上限 {max_chapters}，请用 --max-chapters 调整"
        )
    if len(chapters) < 2:
        raise ValueError("拆分后章节数不足 2，请检查输入格式")
    return chapters


def _extract_title(text: str, fallback: str) -> str:
    """从章节文本首行尝试提取标题。"""
    first_line = text.strip().split("\n", 1)[0].strip()
    first_line = first_line.lstrip("#").strip()
    if first_line:
        return first_line
    return fallback

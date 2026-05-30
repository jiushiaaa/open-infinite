"""console-free 导入小说服务（v0.7 第五刀：导入小说 Web 入口）。

复用现有 import_novel 流水线（splitter / extractor / writer / validator），
不复制导入逻辑。供 HTTP API（POST /api/import-novel）与 CLI 共用。

流程：校验 slug/章节 → 构造 SplitChapter → mock/llm 抽取 → write_project → validate。
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from living_novel_engine.import_novel.mock_extractor import ExtractionResult, mock_extract
from living_novel_engine.import_novel.report import (
    build_import_report,
    summarize_import_report,
)
from living_novel_engine.import_novel.splitter import SplitChapter, _extract_title
from living_novel_engine.import_novel.validator import validate_project
from living_novel_engine.import_novel.writer import _default_projects_dir, write_project
from living_novel_engine.llm.client import LLMClient, LLMSettings

MIN_CHAPTERS = 3
MAX_CHAPTERS = 10
LONG_MAX_CHAPTERS = 200
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class ImportRequestError(ValueError):
    """入参非法（坏 slug、章节不足/过多、内容为空）——映射为 HTTP 400。"""


class ProjectExistsError(Exception):
    """同名项目已存在且未允许覆盖——映射为 HTTP 409。"""


@dataclass
class ImportServiceResult:
    story_slug: str
    display_name: str
    character_count: int
    chapter_count: int
    anchor_chapter_index: int
    warnings: list[str] = field(default_factory=list)
    extraction_mode: str = "mock"
    import_report: dict = field(default_factory=dict)


def _collect_chapter_items(chapters: list[dict]) -> list[tuple[str, str]]:
    """校验并收集 [{filename, content}]，按 filename 排序。"""
    items: list[tuple[str, str]] = []
    for i, ch in enumerate(chapters):
        if not isinstance(ch, dict):
            raise ImportRequestError(f"chapters[{i}] 不是对象")
        content = str(ch.get("content") or "").strip()
        if not content:
            raise ImportRequestError(f"chapters[{i}] 内容为空")
        filename = str(ch.get("filename") or f"chapter_{i + 1:03d}.md")
        items.append((filename, content))

    return sorted(items, key=lambda x: x[0])


def _build_split_chapters(items: list[tuple[str, str]]) -> list[SplitChapter]:
    """从 [(filename, content)] 构造 SplitChapter（镜像目录导入）。"""
    split: list[SplitChapter] = []
    for i, (filename, content) in enumerate(items):
        stem = Path(filename).stem
        title = _extract_title(content, fallback=stem)
        split.append(SplitChapter(index=i + 1, title=title, content=content))
    return split


def _extract(
    split: list[SplitChapter],
    *,
    name: str,
    genre: str,
    mock: bool,
    anchor_idx: int,
) -> tuple[ExtractionResult, str]:
    """选择 mock / llm 抽取；无 API Key 时自动退化 mock。返回 (result, mode)。"""
    settings = LLMSettings.from_env()
    env_mock = os.environ.get("LNE_MOCK", "").lower() in ("1", "true", "yes")
    use_mock = mock or env_mock or not settings.llm_api_key

    if use_mock:
        return (
            mock_extract(
                split, story_name=name, genre=genre, anchor_chapter_index=anchor_idx
            ),
            "mock",
        )

    llm = LLMClient(settings=settings, mock=False)
    if not llm.available:
        # 无可用 LLM：安全退化为 mock，而不是抛错（端到端可用）。
        return (
            mock_extract(
                split, story_name=name, genre=genre, anchor_chapter_index=anchor_idx
            ),
            "mock",
        )

    from living_novel_engine.import_novel.llm_extractor import llm_extract

    return (
        llm_extract(
            split, llm, story_name=name, genre=genre, anchor_chapter_index=anchor_idx
        ),
        "llm",
    )


def import_novel_from_payload(
    *,
    name: str,
    chapters: list[dict],
    genre: str = "xianxia",
    mock: bool = False,
    force: bool = False,
    long_mode: bool = False,
    projects_dir: Path | None = None,
) -> ImportServiceResult:
    """导入 3-10 章文本为可干预项目，复用 import_novel 流水线。

    抛出：
    - ImportRequestError：坏 slug / 章节数越界 / 内容为空（HTTP 400）
    - ProjectExistsError：同名项目存在且 force=False（HTTP 409）
    """
    name = (name or "").strip()
    if not _SLUG_RE.match(name):
        raise ImportRequestError("项目名须为英文小写字母+数字+连字符，如 my-story")

    if not isinstance(chapters, list):
        raise ImportRequestError("chapters 须为数组")
    if len(chapters) < MIN_CHAPTERS:
        raise ImportRequestError(f"至少需要 {MIN_CHAPTERS} 章，当前 {len(chapters)} 章")
    max_chapters = LONG_MAX_CHAPTERS if long_mode else MAX_CHAPTERS
    if len(chapters) > max_chapters:
        limit_label = f"{max_chapters} 章"
        suffix = "（v0.8 长篇导入）" if long_mode else "（v0.2 级小闭环）"
        raise ImportRequestError(
            f"最多 {limit_label}，当前 {len(chapters)} 章{suffix}"
        )

    items = _collect_chapter_items(chapters)
    split = _build_split_chapters(items)
    source_filenames = [filename for filename, _content in items]
    anchor_idx = len(split) - 1

    pdir = projects_dir or _default_projects_dir()
    if (pdir / name).exists() and not force:
        raise ProjectExistsError(f"项目 '{name}' 已存在，如需覆盖请开启覆盖选项")

    extraction, mode = _extract(
        split, name=name, genre=genre, mock=mock, anchor_idx=anchor_idx
    )
    import_report = build_import_report(
        slug=name,
        chapters=split,
        source_filenames=source_filenames,
        long_mode=long_mode,
        warnings=list(extraction.warnings),
    )

    project_dir = write_project(
        name,
        split,
        extraction,
        anchor_chapter_index=anchor_idx,
        projects_dir=pdir,
        allow_overwrite=force,
        genre=genre,
        import_report=import_report,
    )

    vr = validate_project(project_dir)
    warnings = list(import_report.get("warnings", [])) + list(vr.warnings)
    warnings.extend(f"校验未通过：{e}" for e in vr.errors)

    world = extraction.world_yaml
    display_name = world.get("display_name") or world.get("title") or name
    character_count = len(extraction.characters_yaml.get("characters", []) or [])

    return ImportServiceResult(
        story_slug=name,
        display_name=display_name,
        character_count=character_count,
        chapter_count=len(split),
        anchor_chapter_index=anchor_idx,
        warnings=warnings,
        extraction_mode=mode,
        import_report=summarize_import_report(import_report),
    )

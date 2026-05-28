"""Unified story loader — 统一从 projects/ 或 samples/ 加载 StoryBundle。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import yaml

from living_novel_engine.models import CharacterAgent, StoryWorld
from living_novel_engine.models.world import Location, OpenThread
from living_novel_engine.samples.loader import SampleBundle, _samples_dir


def _projects_dir() -> Path:
    import os

    env = os.environ.get("LNE_PROJECTS_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2] / "projects"


class StoryBundle(SampleBundle):
    """扩展 SampleBundle，增加 source_kind 和 project_dir 标记。"""

    source_kind: Literal["builtin", "imported"] = "builtin"
    project_dir: Path | None = None

    def __init__(
        self,
        *,
        source_kind: Literal["builtin", "imported"] = "builtin",
        project_dir: Path | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        object.__setattr__(self, "source_kind", source_kind)
        object.__setattr__(self, "project_dir", project_dir)

    def intervention_chapter(self) -> int:
        """imported 项目首次 intervene 时用于检索的当前章节号。"""
        return intervention_chapter_from_project(self.project_dir)


def intervention_chapter_from_project(project_dir: Path | None) -> int:
    """从 import_meta.json 推导首次干预的检索章节号。

    优先 anchor_chapter_index + 1（index 为 0-based），
    其次 chapter_count，最后回退 1。
    """
    if project_dir is None:
        return 1
    meta_path = project_dir / "import_meta.json"
    if not meta_path.exists():
        return 1
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 1
    if not isinstance(meta, dict):
        return 1
    anchor_idx = meta.get("anchor_chapter_index")
    if isinstance(anchor_idx, int) and anchor_idx >= 0:
        return anchor_idx + 1
    chapter_count = meta.get("chapter_count")
    if isinstance(chapter_count, int) and chapter_count >= 1:
        return chapter_count
    return 1


def load_story(slug: str) -> StoryBundle:
    """先查 projects/<slug>，再查 samples/<slug>。找到即加载。"""
    projects = _projects_dir()
    project_path = projects / slug
    if project_path.exists() and (project_path / "world.yaml").exists():
        return _load_from_project(slug, project_path)

    samples = _samples_dir()
    sample_path = samples / slug
    if sample_path.exists() and (sample_path / "world.yaml").exists():
        return _load_from_sample(slug, sample_path)

    raise FileNotFoundError(
        f"故事不存在: {slug}（已查找 projects/ 和 samples/）"
    )


def list_stories() -> list[tuple[str, str]]:
    """返回 (slug, source_kind) 列表。projects 优先于同名 sample。"""
    seen: dict[str, str] = {}
    projects = _projects_dir()
    if projects.exists():
        for d in sorted(projects.iterdir()):
            if d.is_dir() and (d / "world.yaml").exists():
                seen[d.name] = "imported"
    samples = _samples_dir()
    if samples.exists():
        for d in sorted(samples.iterdir()):
            if d.is_dir() and (d / "world.yaml").exists() and d.name not in seen:
                seen[d.name] = "builtin"
    return [(slug, kind) for slug, kind in sorted(seen.items())]


def _load_from_project(slug: str, path: Path) -> StoryBundle:
    with open(path / "world.yaml", encoding="utf-8") as f:
        world_data = yaml.safe_load(f)

    with open(path / "characters.yaml", encoding="utf-8") as f:
        chars_data = yaml.safe_load(f)

    ot_path = path / "open_threads.yaml"
    if ot_path.exists():
        with open(ot_path, encoding="utf-8") as f:
            threads_data = yaml.safe_load(f) or []
    else:
        threads_data = world_data.get("open_threads", [])

    canon_path = path / "canon_chapter.md"
    canon_chapter = canon_path.read_text(encoding="utf-8") if canon_path.exists() else ""
    prologue_path = path / "prologue.md"
    prologue = prologue_path.read_text(encoding="utf-8") if prologue_path.exists() else ""
    opening_path = path / "canon_opening.md"
    canon_opening = opening_path.read_text(encoding="utf-8") if opening_path.exists() else ""

    locations = [Location(**loc) for loc in world_data.get("locations", [])]
    open_threads = [
        OpenThread(**t) if isinstance(t, dict) else OpenThread(id=str(i), title=str(t))
        for i, t in enumerate(threads_data or [])
    ]

    display_name = world_data.get("display_name") or world_data.get("title", slug)
    world = StoryWorld(
        id=world_data.get("id", slug),
        title=world_data.get("title", display_name),
        display_name=display_name,
        canonical_place_name=world_data.get("canonical_place_name", ""),
        source_type=world_data.get("source_type", "imported"),
        rules=world_data.get("rules", []),
        locations=locations,
        factions=world_data.get("factions", []),
        timeline=world_data.get("timeline", []),
        open_threads=open_threads,
        worldline_policy=world_data.get("worldline_policy", "branch_on_major_intervention"),
        divergence_point=world_data.get("divergence_point", ""),
        scene_description=world_data.get("scene_description", ""),
        canon_chapter_path=str(canon_path),
    )

    characters = [CharacterAgent(**c) for c in chars_data.get("characters", [])]
    return StoryBundle(
        source_kind="imported",
        project_dir=path,
        slug=slug,
        world=world,
        characters=characters,
        canon_chapter=canon_chapter,
        prologue=prologue,
        canon_opening=canon_opening,
    )


def _load_from_sample(slug: str, path: Path) -> StoryBundle:
    """加载内置样例并包装为 StoryBundle。"""
    from living_novel_engine.samples import load_sample

    sample = load_sample(slug)
    return StoryBundle(
        source_kind="builtin",
        slug=sample.slug,
        world=sample.world,
        characters=sample.characters,
        canon_chapter=sample.canon_chapter,
        prologue=sample.prologue,
        canon_opening=sample.canon_opening,
    )

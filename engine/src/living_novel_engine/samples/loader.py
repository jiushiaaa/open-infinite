from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from living_novel_engine.models import CharacterAgent, OpenThread, StoryWorld
from living_novel_engine.models.world import Location


def _engine_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _samples_dir() -> Path:
    return _engine_root() / "samples"


@dataclass
class SampleBundle:
    slug: str
    world: StoryWorld
    characters: list[CharacterAgent]
    canon_chapter: str
    prologue: str = ""
    canon_opening: str = ""

    @property
    def display_name(self) -> str:
        return self.world.display_name or self.world.title

    def character_map(self) -> dict[str, CharacterAgent]:
        return {c.id: c for c in self.characters}

    def canon_context_for_narrator(self, *, max_chars: int = 3500) -> str:
        """合并前情、开篇与干预章，供叙事与 mock 承接。"""
        parts: list[str] = []
        if self.prologue:
            parts.append(f"【前情提要】\n{self.prologue.strip()}")
        if self.canon_opening:
            parts.append(f"【第一章节选】\n{self.canon_opening.strip()}")
        if self.canon_chapter:
            parts.append(f"【干预节点章节】\n{self.canon_chapter.strip()}")
        text = "\n\n".join(parts)
        if len(text) > max_chars:
            return text[-max_chars:]
        return text


def list_samples() -> list[str]:
    root = _samples_dir()
    if not root.exists():
        return []
    return sorted(
        p.name
        for p in root.iterdir()
        if p.is_dir() and (p / "world.yaml").exists()
    )


def load_sample(slug: str) -> SampleBundle:
    sample_dir = _samples_dir() / slug
    if not sample_dir.exists():
        raise FileNotFoundError(f"样例不存在: {slug}（请使用英文 slug，如 tianhuang-night）")

    with open(sample_dir / "world.yaml", encoding="utf-8") as f:
        world_data = yaml.safe_load(f)

    with open(sample_dir / "characters.yaml", encoding="utf-8") as f:
        chars_data = yaml.safe_load(f)

    open_threads_path = sample_dir / "open_threads.yaml"
    if open_threads_path.exists():
        with open(open_threads_path, encoding="utf-8") as f:
            threads_data = yaml.safe_load(f) or []
    else:
        threads_data = world_data.get("open_threads", [])

    canon_path = sample_dir / "canon_chapter.md"
    canon_chapter = canon_path.read_text(encoding="utf-8") if canon_path.exists() else ""
    prologue_path = sample_dir / "prologue.md"
    prologue = prologue_path.read_text(encoding="utf-8") if prologue_path.exists() else ""
    opening_path = sample_dir / "canon_opening.md"
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
        canonical_place_name=world_data.get("canonical_place_name", "天荒城"),
        source_type=world_data.get("source_type", "builtin_sample"),
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
    return SampleBundle(
        slug=slug,
        world=world,
        characters=characters,
        canon_chapter=canon_chapter,
        prologue=prologue,
        canon_opening=canon_opening,
    )

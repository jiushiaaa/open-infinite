"""Project Writer — 将抽取结果写入 projects/<slug>/ 目录。"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

import yaml

from living_novel_engine.import_novel.mock_extractor import ExtractionResult
from living_novel_engine.import_novel.splitter import SplitChapter


def _default_projects_dir() -> Path:
    import os

    env = os.environ.get("LNE_PROJECTS_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3] / "projects"


def write_project(
    slug: str,
    chapters: list[SplitChapter],
    extraction: ExtractionResult,
    *,
    anchor_chapter_index: int | None = None,
    projects_dir: Path | None = None,
    allow_overwrite: bool = True,
    genre: str = "xianxia",
) -> Path:
    """将导入结果写入 projects/<slug>/ 目录并返回项目路径。

    allow_overwrite=False 时，若目标目录已存在则抛出 FileExistsError。
    """
    if projects_dir is None:
        projects_dir = _default_projects_dir()

    project_dir = projects_dir / slug
    if project_dir.exists():
        if not allow_overwrite:
            raise FileExistsError(f"项目已存在: {project_dir}")
        shutil.rmtree(project_dir)
    project_dir.mkdir(parents=True, exist_ok=True)

    # source/
    source_dir = project_dir / "source"
    source_dir.mkdir(exist_ok=True)
    for ch in chapters:
        fname = f"chapter_{ch.index:03d}.md"
        (source_dir / fname).write_text(ch.content, encoding="utf-8")

    # world.yaml
    _write_yaml(project_dir / "world.yaml", extraction.world_yaml)

    # characters.yaml
    _write_yaml(project_dir / "characters.yaml", extraction.characters_yaml)

    # open_threads.yaml
    if extraction.open_threads:
        _write_yaml(project_dir / "open_threads.yaml", extraction.open_threads)

    # canon_chapter.md
    if anchor_chapter_index is None:
        anchor_chapter_index = len(chapters) - 1
    anchor = chapters[anchor_chapter_index]
    (project_dir / "canon_chapter.md").write_text(anchor.content, encoding="utf-8")

    # prologue.md — 前几章摘要
    if len(chapters) > 1:
        prologue_parts: list[str] = []
        for ch in chapters[:anchor_chapter_index]:
            preview = ch.content[:400]
            prologue_parts.append(f"【{ch.title}】\n{preview}")
        prologue_text = "\n\n".join(prologue_parts)
        (project_dir / "prologue.md").write_text(prologue_text, encoding="utf-8")

    # canon_opening.md
    if chapters:
        opening = chapters[0].content[:800]
        (project_dir / "canon_opening.md").write_text(opening, encoding="utf-8")

    # anchor_proposal.yaml
    _write_yaml(project_dir / "anchor_proposal.yaml", extraction.anchor_proposal)

    # --- v0.2.2: story_contract.yaml ---
    _write_story_contract(project_dir, extraction)

    # --- v0.2.2: canon/facts.jsonl ---
    _write_facts(project_dir, chapters, extraction)

    # --- v0.2.2: summaries/ ---
    _write_summaries(project_dir, chapters, extraction)

    # import_meta.json
    meta = {
        "slug": slug,
        "imported_at": datetime.now().isoformat(),
        "source_type": "imported",
        "chapter_count": len(chapters),
        "anchor_chapter_index": anchor_chapter_index,
        "anchor_chapter_title": anchor.title,
        "extraction_mode": "mock" if "mock" in str(extraction.warnings) else "llm",
        "genre": genre,
        "warnings": extraction.warnings,
    }
    (project_dir / "import_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return project_dir


def _write_story_contract(project_dir: Path, extraction: ExtractionResult) -> None:
    """生成 story_contract.yaml — 集中化叙事合约。"""
    world = extraction.world_yaml
    characters = extraction.characters_yaml.get("characters", [])

    character_boundaries: dict[str, list[str]] = {}
    for char in characters:
        char_id = char.get("id", "")
        persona = char.get("persona", {})
        boundaries = persona.get("boundaries", [])
        if char_id and boundaries:
            character_boundaries[char_id] = boundaries

    contract = {
        "world_rules": world.get("rules", []),
        "character_boundaries": character_boundaries,
        "power_system_limits": [
            "境界压制：低境界者无法以蛮力击败高两境以上修士",
            "凡人无法直接对抗修士，但可借信息差、阵法或外物破局",
        ],
        "forbidden_additions": [
            "重生",
            "系统",
            "穿越",
            "前世记忆",
            "无中生有的人物或势力",
        ],
        "unresolved_threads": [
            {"id": t["id"], "title": t["title"], "status": t.get("status", "open")}
            for t in extraction.open_threads
        ] if extraction.open_threads else [],
    }
    _write_yaml(project_dir / "story_contract.yaml", contract)


def _write_facts(
    project_dir: Path,
    chapters: list[SplitChapter],
    extraction: ExtractionResult,
) -> None:
    """生成 canon/facts.jsonl — 轻量事实日志。"""
    canon_dir = project_dir / "canon"
    canon_dir.mkdir(exist_ok=True)

    facts: list[dict] = []
    characters = extraction.characters_yaml.get("characters", [])

    fact_counter = 0
    for char in characters:
        char_id = char.get("id", "")
        char_name = char.get("name", char_id)
        rels = char.get("relationships", {})
        for rel_id, rel_desc in rels.items():
            fact_counter += 1
            facts.append({
                "id": f"fact_{fact_counter:03d}",
                "chapter": len(chapters),
                "type": "relationship",
                "subject": char_id,
                "object": rel_id,
                "text": f"{char_name}: {rel_desc}",
                "evidence": f"chapter_{len(chapters):03d}.md",
            })

        memories = char.get("memory", [])
        for mem in memories[:3]:
            fact_counter += 1
            facts.append({
                "id": f"fact_{fact_counter:03d}",
                "chapter": len(chapters),
                "type": "memory",
                "subject": char_id,
                "text": f"{char_name} - {mem}",
                "evidence": f"chapter_{len(chapters):03d}.md",
            })

    lines = [json.dumps(f, ensure_ascii=False) for f in facts]
    (canon_dir / "facts.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summaries(
    project_dir: Path,
    chapters: list[SplitChapter],
    extraction: ExtractionResult,
) -> None:
    """生成 summaries/chapter_xxx.yaml — 轻量章节摘要。"""
    summaries_dir = project_dir / "summaries"
    summaries_dir.mkdir(exist_ok=True)

    characters = extraction.characters_yaml.get("characters", [])
    char_names = [c.get("name", c.get("id", "")) for c in characters]

    for ch in chapters:
        first_line = ch.content.strip().split("\n")[0][:100]
        summary_data = {
            "chapter": ch.index,
            "title": ch.title,
            "summary": first_line,
            "key_events": [],
            "character_state_changes": [],
            "state_changes": [],
            "open_threads": [],
            "characters_present": char_names[:3],
            "evidence_refs": [],
        }
        fname = f"chapter_{ch.index:03d}.yaml"
        _write_yaml(summaries_dir / fname, summary_data)

    _write_volume_brief(summaries_dir, chapters, extraction)


def _write_volume_brief(
    summaries_dir: Path,
    chapters: list[SplitChapter],
    extraction: ExtractionResult,
) -> None:
    """生成 summaries/volume_001.yaml — 轻量卷摘要。"""
    if not chapters:
        return
    characters = extraction.characters_yaml.get("characters", [])
    char_names = [c.get("name", c.get("id", "")) for c in characters]
    threads = extraction.open_threads or []

    volume_data = {
        "volume": 1,
        "chapter_range": [chapters[0].index, chapters[-1].index],
        "summary": f"共 {len(chapters)} 章，{chapters[0].title} 至 {chapters[-1].title}",
        "main_conflicts": [t.get("title", "") for t in threads[:3]],
        "key_facts": [],
        "active_threads": [t.get("id", "") for t in threads],
        "character_arcs": char_names[:4],
    }
    _write_yaml(summaries_dir / "volume_001.yaml", volume_data)


def _write_yaml(path: Path, data: object) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        )

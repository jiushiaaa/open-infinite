"""Hierarchical memory writer (v0.8.1).

把 v0.2/v0.3 已有的 world、characters、summaries、facts 进一步镜像成
`memory/` 分层骨架。当前只负责可审计的本地 artifact，不让 runner 直接消费。
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import yaml

from living_novel_engine.entity_aliases import write_entity_aliases
from living_novel_engine.import_novel.consistency_audit import build_consistency_report
from living_novel_engine.import_novel.mock_extractor import ExtractionResult
from living_novel_engine.import_novel.splitter import SplitChapter

MEMORY_VERSION = "v0.8.1"
_VOLUME_SIZE = 20
_SAFE_FILE_RE = re.compile(r"[^a-zA-Z0-9_\-]+")


def write_hierarchical_memory(
    project_dir: Path,
    *,
    slug: str,
    chapters: list[SplitChapter],
    extraction: ExtractionResult,
    genre: str,
    import_report: dict | None = None,
) -> dict:
    """写入 `projects/<slug>/memory/` 并返回 manifest。"""
    memory_dir = project_dir / "memory"
    chapters_dir = memory_dir / "chapters"
    volumes_dir = memory_dir / "volumes"
    characters_dir = memory_dir / "character_states"
    for directory in (memory_dir, chapters_dir, volumes_dir, characters_dir):
        directory.mkdir(parents=True, exist_ok=True)

    _write_yaml(
        memory_dir / "master_setting.yaml",
        _build_master_setting(slug, extraction, genre),
    )
    chapter_count = _write_chapter_memories(chapters_dir, chapters, extraction)
    volume_count = _write_volume_memories(volumes_dir, chapters, extraction)
    character_count = _write_character_states(characters_dir, extraction)
    _write_yaml(memory_dir / "timeline.yaml", _build_timeline(chapters))
    _write_yaml(memory_dir / "plot_threads.yaml", _build_plot_threads(extraction))
    _write_yaml(memory_dir / "propagation_debts.yaml", {"debts": []})
    canon_records = _build_canon_ledger_records(chapters, extraction)
    canon_ledger_count = _write_canon_ledger(memory_dir, canon_records)
    entity_aliases = write_entity_aliases(
        memory_dir,
        story_slug=slug,
        extraction=extraction,
        canon_records=canon_records,
    )
    consistency_report = build_consistency_report(
        story_slug=slug,
        import_report=import_report,
        canon_ledger_count=canon_ledger_count,
        entity_alias_count=len(entity_aliases.get("entities", []) or []),
        open_threads=extraction.open_threads or [],
    )
    (memory_dir / "consistency_report.json").write_text(
        json.dumps(consistency_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    manifest = {
        "version": MEMORY_VERSION,
        "story_slug": slug,
        "created_at": datetime.now().isoformat(),
        "source": "import_novel",
        "import_report_path": "import_report.json" if import_report else "",
        "layers": {
            "contract": {"path": "memory/master_setting.yaml", "count": 1},
            "volumes": {"path": "memory/volumes", "count": volume_count},
            "chapters": {"path": "memory/chapters", "count": chapter_count},
            "character_states": {
                "path": "memory/character_states",
                "count": character_count,
            },
            "timeline": {"path": "memory/timeline.yaml", "count": len(chapters)},
            "plot_threads": {
                "path": "memory/plot_threads.yaml",
                "count": len(extraction.open_threads or []),
            },
            "propagation_debts": {
                "path": "memory/propagation_debts.yaml",
                "count": 0,
            },
            "canon_ledger": {
                "path": "memory/canon_ledger.jsonl",
                "count": canon_ledger_count,
            },
            "entity_aliases": {
                "path": "memory/entity_aliases.yaml",
                "count": len(entity_aliases.get("entities", []) or []),
            },
            "consistency_report": {
                "path": "memory/consistency_report.json",
                "count": consistency_report["summary"]["issue_count"],
            },
        },
    }
    (memory_dir / "memory_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def _build_master_setting(
    slug: str, extraction: ExtractionResult, genre: str
) -> dict:
    world = extraction.world_yaml
    return {
        "story_slug": slug,
        "display_name": world.get("display_name") or world.get("title") or slug,
        "genre": genre,
        "world_rules": world.get("rules", []),
        "locations": world.get("locations", []),
        "factions": world.get("factions", []),
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
        "source_refs": [
            "world.yaml",
            "characters.yaml",
            "story_contract.yaml",
        ],
    }


def _write_chapter_memories(
    chapters_dir: Path,
    chapters: list[SplitChapter],
    extraction: ExtractionResult,
) -> int:
    characters = extraction.characters_yaml.get("characters", []) or []
    char_names = [c.get("name", c.get("id", "")) for c in characters][:5]
    for ch in chapters:
        first_line = ch.content.strip().split("\n", 1)[0][:120]
        _write_yaml(
            chapters_dir / f"chapter_{ch.index:04d}.yaml",
            {
                "chapter": ch.index,
                "title": ch.title,
                "summary": first_line,
                "source_ref": f"source/chapter_{ch.index:03d}.md",
                "raw_ref": f"source_raw/chapter_{ch.index:03d}.md",
                "characters_present": char_names,
                "key_events": [],
                "state_changes": [],
                "open_threads": [],
            },
        )
    return len(chapters)


def _write_volume_memories(
    volumes_dir: Path,
    chapters: list[SplitChapter],
    extraction: ExtractionResult,
) -> int:
    if not chapters:
        return 0
    threads = extraction.open_threads or []
    count = 0
    for start in range(0, len(chapters), _VOLUME_SIZE):
        group = chapters[start : start + _VOLUME_SIZE]
        count += 1
        _write_yaml(
            volumes_dir / f"volume_{count:03d}.yaml",
            {
                "volume": count,
                "chapter_range": [group[0].index, group[-1].index],
                "summary": f"第 {group[0].index} 至 {group[-1].index} 章导入记忆",
                "main_conflicts": [t.get("title", "") for t in threads[:3]],
                "active_threads": [t.get("id", "") for t in threads],
                "source_refs": [
                    f"memory/chapters/chapter_{ch.index:04d}.yaml" for ch in group
                ],
            },
        )
    return count


def _write_character_states(
    characters_dir: Path, extraction: ExtractionResult
) -> int:
    characters = extraction.characters_yaml.get("characters", []) or []
    count = 0
    for idx, char in enumerate(characters, start=1):
        char_id = str(char.get("id") or f"character_{idx:03d}")
        filename = _safe_filename(char_id)
        _write_yaml(
            characters_dir / f"{filename}.yaml",
            {
                "character_id": char_id,
                "name": char.get("name", char_id),
                "narrative_role": char.get("narrative_role", ""),
                "persona": char.get("persona", {}),
                "current_state": char.get("current_state", {}),
                "relationships": char.get("relationships", {}),
                "memory": char.get("memory", []),
                "source_refs": ["characters.yaml", "canon/facts.jsonl"],
            },
        )
        count += 1
    return count


def _build_timeline(chapters: list[SplitChapter]) -> dict:
    return {
        "events": [
            {
                "chapter": ch.index,
                "title": ch.title,
                "source_ref": f"source/chapter_{ch.index:03d}.md",
                "raw_ref": f"source_raw/chapter_{ch.index:03d}.md",
            }
            for ch in chapters
        ]
    }


def _build_plot_threads(extraction: ExtractionResult) -> dict:
    return {
        "active_threads": [
            {
                "id": t.get("id", ""),
                "title": t.get("title", ""),
                "status": t.get("status", "open"),
                "source_refs": ["open_threads.yaml"],
            }
            for t in (extraction.open_threads or [])
        ]
    }


def _write_canon_ledger(memory_dir: Path, records: list[dict]) -> int:
    lines = [json.dumps(record, ensure_ascii=False) for record in records]
    (memory_dir / "canon_ledger.jsonl").write_text(
        "\n".join(lines) + ("\n" if lines else ""),
        encoding="utf-8",
    )
    return len(records)


def _build_canon_ledger_records(
    chapters: list[SplitChapter], extraction: ExtractionResult
) -> list[dict]:
    records: list[dict] = []
    counter = 0
    characters = extraction.characters_yaml.get("characters", []) or []
    character_ids = [str(c.get("id") or "") for c in characters if c.get("id")]

    for ch in chapters:
        counter += 1
        records.append(_ledger_record(
            counter=counter,
            record_type="event",
            chapter=ch.index,
            scene=1,
            entities=character_ids[:4],
            statement=f"{ch.title}：{ch.content.strip().splitlines()[0][:120]}",
            source_ref=f"source/chapter_{ch.index:03d}.md",
            confidence=0.68,
            valid_from=ch.index,
        ))

    last_chapter = chapters[-1].index if chapters else 1
    for char in characters:
        char_id = str(char.get("id") or "")
        name = str(char.get("name") or char_id)
        state = char.get("current_state", {}) or {}
        if char_id:
            counter += 1
            statement = (
                f"{name} 当前位于 {state.get('location', '未知地点')}，"
                f"情绪为 {state.get('emotion', '未知')}。"
            )
            records.append(_ledger_record(
                counter=counter,
                record_type="state",
                chapter=last_chapter,
                scene=1,
                entities=[char_id],
                statement=statement,
                source_ref="characters.yaml",
                confidence=0.72,
                valid_from=last_chapter,
            ))

        rels = char.get("relationships", {}) or {}
        for rel_id, rel_desc in rels.items():
            counter += 1
            records.append(_ledger_record(
                counter=counter,
                record_type="relationship",
                chapter=last_chapter,
                scene=1,
                entities=[char_id, str(rel_id)] if char_id else [str(rel_id)],
                statement=f"{name} 与 {rel_id}：{rel_desc}",
                source_ref="characters.yaml",
                confidence=0.75,
                valid_from=last_chapter,
            ))

    for thread in extraction.open_threads or []:
        counter += 1
        records.append(_ledger_record(
            counter=counter,
            record_type="foreshadowing",
            chapter=last_chapter,
            scene=1,
            entities=[],
            statement=str(thread.get("title") or thread.get("description") or ""),
            source_ref="open_threads.yaml",
            confidence=0.66,
            valid_from=last_chapter,
        ))

    return records


def _ledger_record(
    *,
    counter: int,
    record_type: str,
    chapter: int,
    scene: int,
    entities: list[str],
    statement: str,
    source_ref: str,
    confidence: float,
    valid_from: int,
) -> dict:
    return {
        "id": f"canon_{counter:06d}",
        "type": record_type,
        "chapter": int(chapter),
        "scene": int(scene),
        "entities": [e for e in entities if e],
        "statement": statement,
        "truth_status": "canon",
        "source_ref": source_ref,
        "confidence": round(float(confidence), 2),
        "valid_from": int(valid_from),
        "valid_until": None,
    }


def _safe_filename(value: str) -> str:
    clean = _SAFE_FILE_RE.sub("_", value).strip("_").lower()
    return clean or "character"


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

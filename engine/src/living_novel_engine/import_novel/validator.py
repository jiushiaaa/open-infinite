"""Project Validator — 校验 projects/<slug>/ 是否满足最低运行时要求。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from living_novel_engine.models import CharacterAgent, StoryWorld
from living_novel_engine.models.world import Location, OpenThread


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    world: StoryWorld | None = None
    characters: list[CharacterAgent] = field(default_factory=list)


def validate_project(project_dir: Path) -> ValidationResult:
    """校验项目目录结构与 YAML 字段完整性。"""
    errors: list[str] = []
    warnings: list[str] = []
    world: StoryWorld | None = None
    characters: list[CharacterAgent] = []

    if not project_dir.is_dir():
        return ValidationResult(valid=False, errors=[f"项目目录不存在: {project_dir}"])

    # --- world.yaml ---
    world_path = project_dir / "world.yaml"
    if not world_path.exists():
        errors.append("缺少 world.yaml")
    else:
        world = _validate_world(world_path, errors, warnings)

    # --- characters.yaml ---
    chars_path = project_dir / "characters.yaml"
    if not chars_path.exists():
        errors.append("缺少 characters.yaml")
    else:
        characters = _validate_characters(chars_path, errors, warnings)

    # --- canon_chapter.md ---
    canon_path = project_dir / "canon_chapter.md"
    if not canon_path.exists():
        errors.append("缺少 canon_chapter.md")
    elif canon_path.stat().st_size == 0:
        errors.append("canon_chapter.md 为空")

    # --- import_meta.json ---
    meta_path = project_dir / "import_meta.json"
    if not meta_path.exists():
        warnings.append("缺少 import_meta.json（非致命）")
    else:
        _validate_meta(meta_path, warnings)

    # --- source/ ---
    source_dir = project_dir / "source"
    if not source_dir.is_dir():
        warnings.append("缺少 source/ 目录（原文备份）")

    # --- v0.2.2: story_contract.yaml ---
    contract_path = project_dir / "story_contract.yaml"
    if not contract_path.exists():
        warnings.append("缺少 story_contract.yaml（建议重新导入或手动创建）")
    else:
        _validate_contract(contract_path, warnings)

    # --- v0.2.2: canon/facts.jsonl ---
    facts_path = project_dir / "canon" / "facts.jsonl"
    if not facts_path.exists():
        warnings.append("缺少 canon/facts.jsonl（建议重新导入）")
    elif facts_path.stat().st_size == 0:
        warnings.append("canon/facts.jsonl 为空")

    # --- v0.2.2: summaries/ ---
    summaries_dir = project_dir / "summaries"
    if not summaries_dir.is_dir():
        warnings.append("缺少 summaries/ 目录（建议重新导入）")
    else:
        yaml_files = list(summaries_dir.glob("chapter_*.yaml"))
        if not yaml_files:
            warnings.append("summaries/ 下无 chapter_*.yaml 文件")

    valid = len(errors) == 0
    return ValidationResult(
        valid=valid,
        errors=errors,
        warnings=warnings,
        world=world,
        characters=characters,
    )


def _validate_world(
    path: Path, errors: list[str], warnings: list[str]
) -> StoryWorld | None:
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        errors.append(f"world.yaml 解析失败: {e}")
        return None

    if not isinstance(data, dict):
        errors.append("world.yaml 根节点须为 dict")
        return None

    required_fields = ["id", "title", "rules", "locations"]
    for fld in required_fields:
        if fld not in data:
            errors.append(f"world.yaml 缺少必填字段: {fld}")

    if "rules" in data and len(data["rules"]) < 2:
        warnings.append("world.yaml rules 少于 2 条，建议补充")

    if "locations" in data and len(data["locations"]) < 1:
        warnings.append("world.yaml locations 为空")

    try:
        locations = [Location(**loc) for loc in data.get("locations", [])]
        open_threads: list[OpenThread] = []
        ot_path = path.parent / "open_threads.yaml"
        if ot_path.exists():
            with open(ot_path, encoding="utf-8") as f:
                ot_data = yaml.safe_load(f) or []
            open_threads = [
                OpenThread(**t) if isinstance(t, dict) else OpenThread(id=str(i), title=str(t))
                for i, t in enumerate(ot_data)
            ]

        world = StoryWorld(
            id=data.get("id", "unknown"),
            title=data.get("title", ""),
            display_name=data.get("display_name", data.get("title", "")),
            canonical_place_name=data.get("canonical_place_name", ""),
            source_type=data.get("source_type", "imported"),
            rules=data.get("rules", []),
            locations=locations,
            factions=data.get("factions", []),
            timeline=data.get("timeline", []),
            open_threads=open_threads,
            worldline_policy=data.get("worldline_policy", "branch_on_major_intervention"),
            divergence_point=data.get("divergence_point", ""),
            scene_description=data.get("scene_description", ""),
        )
        return world
    except Exception as e:
        errors.append(f"world.yaml 无法构造 StoryWorld: {e}")
        return None


def _validate_characters(
    path: Path, errors: list[str], warnings: list[str]
) -> list[CharacterAgent]:
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        errors.append(f"characters.yaml 解析失败: {e}")
        return []

    if not isinstance(data, dict) or "characters" not in data:
        errors.append("characters.yaml 须含 'characters' 列表")
        return []

    chars_data = data["characters"]
    if not isinstance(chars_data, list) or len(chars_data) == 0:
        errors.append("characters.yaml 中 characters 列表为空")
        return []

    characters: list[CharacterAgent] = []
    has_present = False
    seen_ids: set[str] = set()

    for i, cdata in enumerate(chars_data):
        if not isinstance(cdata, dict):
            errors.append(f"characters[{i}] 不是 dict")
            continue
        char_id = cdata.get("id", "")
        if not char_id:
            errors.append(f"characters[{i}] 缺少 id")
            continue
        if char_id in seen_ids:
            errors.append(f"characters 中存在重复 id: {char_id}")
        seen_ids.add(char_id)

        try:
            char = CharacterAgent(**cdata)
            characters.append(char)
            if char.present_in_scene:
                has_present = True
        except Exception as e:
            errors.append(f"characters[{i}] (id={char_id}) 构造失败: {e}")

    if not has_present:
        errors.append("至少需要 1 个 present_in_scene=true 的角色")

    return characters


def _validate_meta(path: Path, warnings: list[str]) -> None:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            warnings.append("import_meta.json 根节点不是 dict")
    except Exception as e:
        warnings.append(f"import_meta.json 解析失败: {e}")


def _validate_contract(path: Path, warnings: list[str]) -> None:
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        warnings.append(f"story_contract.yaml 解析失败: {e}")
        return

    if not isinstance(data, dict):
        warnings.append("story_contract.yaml 根节点须为 dict")
        return

    expected_keys = ["world_rules", "character_boundaries", "forbidden_additions"]
    for key in expected_keys:
        if key not in data:
            warnings.append(f"story_contract.yaml 缺少字段: {key}")

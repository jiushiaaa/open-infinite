"""console-free 世界锚定轻编辑写回（v0.7 第七刀）。

仅允许白名单字段写回项目 YAML，写前 parse 校验 + 备份，写后 validate_project。
不允许任意 YAML 写入；不改 chapter.md / outputs / worldline run。
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from living_novel_engine.import_novel.validator import validate_project
from living_novel_engine.import_novel.writer import _write_yaml
from living_novel_engine.service.project_health import (
    HealthReport,
    check_project_health,
    resolve_story_path,
)


class AnchorUpdateError(ValueError):
    """patch 非法 / 原 YAML 解析失败——映射为 HTTP 400。"""


class AnchorReadOnlyError(ValueError):
    """内置样例只读，不允许编辑——映射为 HTTP 400。"""


@dataclass
class AnchorUpdateResult:
    slug: str
    project_dir: Path
    backup_dir: Path | None
    health: HealthReport
    changed: list[str]


def _load_strict(path: Path) -> Any:
    """严格 parse YAML；失败抛 AnchorUpdateError（不写文件）。"""
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, UnicodeDecodeError, OSError) as exc:
        raise AnchorUpdateError(f"{path.name} 解析失败，已拒绝保存：{exc}")


def _apply_world(world: dict, patch: dict, changed: list[str]) -> None:
    wp = patch.get("world")
    if not isinstance(wp, dict):
        return
    if isinstance(wp.get("rules"), list):
        world["rules"] = [str(r) for r in wp["rules"] if str(r).strip()]
        changed.append("world.rules")
    if "scene_description" in wp and isinstance(wp["scene_description"], str):
        world["scene_description"] = wp["scene_description"]
        changed.append("world.scene_description")


def _apply_characters(chars_doc: dict, patch: dict, changed: list[str]) -> None:
    cp = patch.get("characters")
    if not isinstance(cp, list):
        return
    by_id = {c.get("id"): c for c in chars_doc.get("characters", []) if isinstance(c, dict)}
    for item in cp:
        if not isinstance(item, dict):
            continue
        target = by_id.get(item.get("id"))
        if target is None:
            continue
        persona = item.get("persona")
        if isinstance(persona, dict):
            tgt_persona = target.setdefault("persona", {})
            for fld in ("boundaries", "traits"):
                if isinstance(persona.get(fld), list):
                    tgt_persona[fld] = [str(x) for x in persona[fld] if str(x).strip()]
                    changed.append(f"characters[{item['id']}].persona.{fld}")
        state = item.get("current_state")
        if isinstance(state, dict):
            tgt_state = target.setdefault("current_state", {})
            for fld in ("location", "emotion"):
                if isinstance(state.get(fld), str):
                    tgt_state[fld] = state[fld]
                    changed.append(f"characters[{item['id']}].current_state.{fld}")


def _apply_threads(patch: dict, changed: list[str]) -> list[dict] | None:
    tp = patch.get("open_threads")
    if not isinstance(tp, list):
        return None
    out: list[dict] = []
    for i, t in enumerate(tp):
        if not isinstance(t, dict):
            continue
        out.append(
            {
                "id": str(t.get("id") or f"thread_{i + 1}"),
                "title": str(t.get("title") or ""),
                "description": str(t.get("description") or ""),
                "status": str(t.get("status") or "open"),
            }
        )
    changed.append("open_threads")
    return out


def _backup(project_dir: Path, names: list[str]) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_dir = project_dir / "backups" / ts
    backup_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        src = project_dir / name
        if src.exists():
            shutil.copy2(src, backup_dir / name)
    return backup_dir


def update_world_anchor(
    slug: str, patch: dict, projects_dir: Path | None = None
) -> AnchorUpdateResult:
    """白名单写回世界锚定字段。

    抛出：
    - AnchorUpdateError：patch 非 dict / 原 YAML 解析失败（HTTP 400）
    - AnchorReadOnlyError：内置样例只读（HTTP 400）
    - FileNotFoundError：故事不存在（HTTP 404）
    """
    if not isinstance(patch, dict):
        raise AnchorUpdateError("patch 须为对象")

    story_path, source_kind = resolve_story_path(slug, projects_dir)
    if source_kind == "builtin":
        raise AnchorReadOnlyError("内置样例只读，请先导入或创世为可编辑项目")

    # 写前严格 parse（任一损坏即 400，不写任何文件）。
    world = _load_strict(story_path / "world.yaml") or {}
    chars_doc = _load_strict(story_path / "characters.yaml") or {}
    _load_strict(story_path / "open_threads.yaml")  # 仅校验可解析
    _load_strict(story_path / "story_contract.yaml")  # 仅校验可解析

    if not isinstance(world, dict) or not isinstance(chars_doc, dict):
        raise AnchorUpdateError("world.yaml / characters.yaml 结构异常，已拒绝保存")

    changed: list[str] = []
    _apply_world(world, patch, changed)
    _apply_characters(chars_doc, patch, changed)
    new_threads = _apply_threads(patch, changed)

    if not changed:
        raise AnchorUpdateError("没有可写回的白名单字段")

    # 先备份再写。
    backup_dir = _backup(
        story_path, ["world.yaml", "characters.yaml", "open_threads.yaml"]
    )

    _write_yaml(story_path / "world.yaml", world)
    _write_yaml(story_path / "characters.yaml", chars_doc)
    if new_threads is not None:
        _write_yaml(story_path / "open_threads.yaml", new_threads)

    # 写后校验（即便有 hard error 也已保存，由 health.status 标注）。
    _ = validate_project(story_path)
    health = check_project_health(slug, projects_dir)

    return AnchorUpdateResult(
        slug=slug,
        project_dir=story_path,
        backup_dir=backup_dir,
        health=health,
        changed=changed,
    )

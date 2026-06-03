"""Cards Workspace MVP：从现有设定记忆派生只读卡片工作台。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from living_novel_engine.service.project_health import resolve_story_path

VERSION = "cards-workspace-mvp"


class CardsWorkspaceRequestError(ValueError):
    """Invalid cards workspace request."""


def get_cards_workspace(
    story_slug: str,
    *,
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    """Return world/character/style cards without writing artifacts."""

    story_path, source_kind = resolve_story_path(story_slug, projects_dir)
    memory_dir = story_path / "memory"
    master_status, raw_master = _read_yaml_status(memory_dir / "master_setting.yaml")
    master = raw_master if isinstance(raw_master, dict) else {}
    warnings: list[str] = []
    if master_status == "missing":
        warnings.append("MasterSetting 设定文件缺失，世界卡与风格卡已降级为空态。")
    elif master_status == "damaged":
        warnings.append("MasterSetting 设定文件无法解析，世界卡与风格卡已降级为空态。")

    can_edit_master = source_kind == "imported" and master_status == "ready"
    character_cards, character_warnings = _character_cards(story_path)
    warnings.extend(character_warnings)
    cards = [
        _world_card(master, master_status, can_edit_master),
        _style_card(master, master_status, can_edit_master),
        *character_cards,
    ]
    status = "attention" if warnings else "ready"
    editable_count = sum(1 for card in cards if card["editable_fields"])
    groups = [
        _group("world", "世界卡", cards),
        _group("character", "角色卡", cards),
        _group("style", "风格卡", cards),
    ]

    return {
        "version": VERSION,
        "mode": "read_only_cards_workspace",
        "status": status,
        "story_slug": story_slug,
        "source_kind": source_kind,
        "summary": {
            "card_count": len(cards),
            "world_card_count": 1,
            "character_card_count": len(character_cards),
            "style_card_count": 1,
            "editable_card_count": editable_count,
            "writes_artifacts": False,
            "external_services_required": False,
        },
        "groups": groups,
        "cards": cards,
        "warnings": warnings,
        "boundaries": [
            "只读派生自 master_setting、character_states 和 characters.yaml。",
            "不写 artifact、不生成新卡片文件、不调用外部模型。",
            "轻编辑继续复用 MasterSetting 白名单保存链路。",
        ],
        "next_steps": [
            "先把世界卡、角色卡、风格卡作为长期设定资产入口使用。",
            "如需真正版本化卡片，再做 opt-in 写入和审计，不默认扩成完整作者工作台。",
        ],
    }


def _world_card(
    master: dict[str, Any],
    master_status: str,
    can_edit: bool,
) -> dict[str, Any]:
    display_name = _text(master.get("display_name")) or "世界卡"
    genre = _text(master.get("genre")) or "题材未标注"
    status = "ready" if master_status == "ready" else "attention"
    return {
        "id": "world",
        "type": "world",
        "title": display_name,
        "subtitle": genre,
        "status": status,
        "status_label": "可用" if status == "ready" else "需补齐",
        "source_paths": ["memory/master_setting.yaml"],
        "editable_fields": (
            [
                "display_name",
                "genre",
                "world_rules",
                "power_system_limits",
                "forbidden_additions",
            ]
            if can_edit
            else []
        ),
        "fields": [
            _field("世界规则", _as_list(master.get("world_rules"))[:8]),
            _field("力量限制", _as_list(master.get("power_system_limits"))[:6]),
            _field("禁用设定", _as_list(master.get("forbidden_additions"))[:8]),
            _field("地点", _named_items(master.get("locations"))[:6]),
            _field("势力", _named_items(master.get("factions"))[:6]),
        ],
    }


def _style_card(
    master: dict[str, Any],
    master_status: str,
    can_edit: bool,
) -> dict[str, Any]:
    genre = _text(master.get("genre")) or "题材未标注"
    style_hints = _as_list(master.get("style_hints")) or _as_list(master.get("tone"))
    if not style_hints:
        style_hints = _default_style_hints(genre)
    status = "ready" if master_status == "ready" else "attention"
    return {
        "id": "style",
        "type": "style",
        "title": "风格卡",
        "subtitle": genre,
        "status": status,
        "status_label": "可用" if status == "ready" else "需补齐",
        "source_paths": ["memory/master_setting.yaml"],
        "editable_fields": ["genre", "forbidden_additions"] if can_edit else [],
        "fields": [
            _field("题材基调", [genre]),
            _field("叙事口径", style_hints[:6]),
            _field("避免", _as_list(master.get("forbidden_additions"))[:8]),
        ],
    }


def _character_cards(story_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    memory_cards, warnings = _character_cards_from_memory(
        story_path / "memory" / "character_states"
    )
    if memory_cards:
        return memory_cards[:12], warnings
    fallback_cards, fallback_warning = _character_cards_from_anchor(
        story_path / "characters.yaml"
    )
    warnings.extend(fallback_warning)
    return fallback_cards[:12], warnings


def _character_cards_from_memory(
    characters_dir: Path,
) -> tuple[list[dict[str, Any]], list[str]]:
    if not characters_dir.exists():
        return [], ["人物状态目录缺失，已尝试从 characters.yaml 降级生成角色卡。"]
    cards: list[dict[str, Any]] = []
    warnings: list[str] = []
    for path in sorted(characters_dir.glob("*.yaml")):
        status, raw = _read_yaml_status(path)
        if status != "ready" or not isinstance(raw, dict):
            warnings.append(f"人物状态无法解析：{path.name}")
            continue
        persona = raw.get("persona") if isinstance(raw.get("persona"), dict) else {}
        current_state = (
            raw.get("current_state")
            if isinstance(raw.get("current_state"), dict)
            else {}
        )
        name = _text(raw.get("name")) or path.stem
        character_id = _text(raw.get("character_id")) or path.stem
        cards.append(
            {
                "id": f"character:{character_id}",
                "type": "character",
                "title": name,
                "subtitle": _text(raw.get("narrative_role")) or "角色",
                "status": "ready",
                "status_label": "可用",
                "source_paths": [f"memory/character_states/{path.name}"],
                "editable_fields": [],
                "fields": [
                    _field("当前位置", [_text(current_state.get("location"))]),
                    _field("情绪状态", [_text(current_state.get("emotion"))]),
                    _field("边界", _as_list(persona.get("boundaries"))[:6]),
                    _field("资源", _as_list(current_state.get("resources"))[:6]),
                    _field("记忆", _as_list(raw.get("memory"))[:4]),
                ],
            }
        )
    return cards, warnings


def _character_cards_from_anchor(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    status, raw = _read_yaml_status(path)
    if status != "ready" or not isinstance(raw, dict):
        return [], ["characters.yaml 缺失或无法解析，角色卡为空。"]
    raw_characters = raw.get("characters") if isinstance(raw.get("characters"), list) else []
    cards: list[dict[str, Any]] = []
    for idx, item in enumerate(raw_characters):
        if not isinstance(item, dict):
            continue
        character_id = _text(item.get("id")) or f"character_{idx + 1}"
        name = _text(item.get("name")) or character_id
        cards.append(
            {
                "id": f"character:{character_id}",
                "type": "character",
                "title": name,
                "subtitle": _text(item.get("narrative_role")) or "角色",
                "status": "attention",
                "status_label": "仅锚定",
                "source_paths": ["characters.yaml"],
                "editable_fields": [],
                "fields": [
                    _field("人设", _as_list(item.get("persona"))[:6]),
                    _field("边界", _as_list(item.get("boundaries"))[:6]),
                    _field("出场", ["当前场景" if item.get("present_in_scene") else "未出场"]),
                ],
            }
        )
    return cards, []


def _group(group_id: str, label: str, cards: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [card["id"] for card in cards if card["type"] == group_id]
    return {"id": group_id, "label": label, "count": len(ids), "card_ids": ids}


def _field(label: str, items: list[str]) -> dict[str, Any]:
    cleaned = [item for item in items if item]
    return {
        "label": label,
        "items": cleaned,
        "status": "ready" if cleaned else "missing",
        "empty": f"暂无{label}",
    }


def _default_style_hints(genre: str) -> list[str]:
    if "玄幻" in genre or "仙" in genre or "xianxia" in genre.lower():
        return ["克制留白", "画面感", "因果清楚", "避免口号式解释"]
    if "悬疑" in genre:
        return ["信息分层", "线索递进", "保留误导", "避免提前解谜"]
    return ["克制", "画面感", "人物动机清楚", "避免平铺直叙"]


def _read_yaml_status(path: Path) -> tuple[str, Any]:
    if not path.exists():
        return "missing", None
    try:
        return "ready", yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return "damaged", None


def _text(value: object) -> str:
    return str(value).strip() if value is not None else ""


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [_stringify_item(item) for item in value if _stringify_item(item)]
    text = _text(value)
    return [text] if text else []


def _named_items(value: object) -> list[str]:
    items: list[str] = []
    if not isinstance(value, list):
        return _as_list(value)
    for item in value:
        if isinstance(item, dict):
            label = _text(item.get("name")) or _text(item.get("id"))
            desc = _text(item.get("description"))
            if label and desc:
                items.append(f"{label}：{desc}")
            elif label:
                items.append(label)
        else:
            text = _text(item)
            if text:
                items.append(text)
    return items


def _stringify_item(value: object) -> str:
    if isinstance(value, dict):
        return _text(value.get("name")) or _text(value.get("title")) or _text(value.get("id"))
    return _text(value)

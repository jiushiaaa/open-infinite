"""World Sandbox Loop v3: local Tianming book draft and confirmation."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.project_health import resolve_story_path

VERSION = "tianming-book-v1"
ARTIFACT = "tianming.json"


class TianmingRequestError(ValueError):
    """Invalid Tianming book request."""


def generate_tianming_book(
    story_slug: str,
    *,
    projects_dir: Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Generate a local deterministic Tianming draft for one story world."""

    sid = _checked_id(story_slug, "story_slug")
    story_path, source_kind = resolve_story_path(sid, projects_dir)
    path = story_path / ARTIFACT
    if path.exists() and not force:
        existing = _read_json(path)
        if existing.get("status") == "confirmed":
            return existing
    created_at = datetime.now().isoformat(timespec="seconds")
    world = _read_yaml(story_path / "world.yaml")
    characters = _read_yaml(story_path / "characters.yaml")
    threads = _read_yaml(story_path / "open_threads.yaml")
    book = _build_book(
        story_slug=sid,
        source_kind=source_kind,
        world=world,
        characters=characters,
        threads=threads,
        created_at=created_at,
    )
    path.write_text(json.dumps(book, ensure_ascii=False, indent=2), encoding="utf-8")
    return book


def get_tianming_book(
    story_slug: str,
    *,
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    """Read a generated Tianming book."""

    sid = _checked_id(story_slug, "story_slug")
    story_path, _source_kind = resolve_story_path(sid, projects_dir)
    path = story_path / ARTIFACT
    if not path.exists():
        raise FileNotFoundError(f"天命书不存在: {sid}")
    return _read_json(path)


def confirm_tianming_book(
    story_slug: str,
    *,
    confirm: bool,
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    """Lightweight confirmation: no large form, only explicit consent."""

    if not confirm:
        raise TianmingRequestError("确认《天命书》需要 confirm=True")
    sid = _checked_id(story_slug, "story_slug")
    story_path, _source_kind = resolve_story_path(sid, projects_dir)
    path = story_path / ARTIFACT
    if not path.exists():
        raise FileNotFoundError(f"天命书不存在: {sid}")
    book = _read_json(path)
    now = datetime.now().isoformat(timespec="seconds")
    book["status"] = "confirmed"
    book["requires_confirmation"] = False
    book["confirmed_at"] = now
    book["updated_at"] = now
    book["confirmation"] = {
        "method": "lightweight",
        "message": "作者确认当前天命书草案可作为沙盘轮次与干预编译的世界宪法输入。",
    }
    path.write_text(json.dumps(book, ensure_ascii=False, indent=2), encoding="utf-8")
    return book


def _build_book(
    *,
    story_slug: str,
    source_kind: str,
    world: dict[str, Any],
    characters: dict[str, Any],
    threads: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    character_rows = [
        item for item in characters.get("characters", []) if isinstance(item, dict)
    ]
    thread_rows = _thread_rows(threads)
    candidates = _replacement_candidates(character_rows)
    attractors = _narrative_attractors(world, character_rows, thread_rows)
    constraints = _genre_constraints(world)
    return {
        "version": VERSION,
        "artifact": ARTIFACT,
        "story_slug": story_slug,
        "source_kind": source_kind,
        "status": "draft",
        "requires_confirmation": True,
        "created_at": created_at,
        "updated_at": created_at,
        "confirmed_at": None,
        "narrative_attractors": attractors,
        "genre_constraints": constraints,
        "anchor_status": _anchor_status(character_rows, candidates),
        "contract_pressure": _contract_pressure(thread_rows, character_rows),
        "replacement_anchor_candidates": candidates,
        "ordinary_intervention_mutates_tianming": False,
        "mutation_policy": {
            "ordinary_intervention": "只能生成世界线 delta 或因果债，不能永久改写天命书。",
            "l4_l5_intervention": "必须经审计后写入世界线快照，不能直接覆盖原始天命书。",
        },
        "boundaries": [
            "本文件是本地 JSON 草案，不调用外部模型或 provider。",
            "确认只是轻量状态切换，不要求复杂表单。",
            "普通读者干预不能永久改写《天命书》。",
        ],
        "next_steps": [
            "确认后让干预编译器每次读取《天命书》。",
            "后续沙盘轮次可把 anchor_status 与 contract_pressure 作为世界压力输入。",
        ],
    }


def _narrative_attractors(
    world: dict[str, Any],
    characters: list[dict[str, Any]],
    threads: list[dict[str, Any]],
) -> list[dict[str, str]]:
    attractors: list[dict[str, str]] = []
    for idx, thread in enumerate(threads[:3], start=1):
        title = _text(thread.get("title")) or _text(thread.get("id")) or f"伏笔 {idx}"
        desc = _text(thread.get("description")) or "开放伏笔正在牵引角色行动。"
        attractors.append(
            {
                "id": f"attractor_{idx}",
                "title": title,
                "pull": desc,
                "source": "open_threads.yaml",
            }
        )
    for character in characters[:3]:
        name = _text(character.get("name")) or _text(character.get("id")) or "关键角色"
        desire = _first_text(
            (character.get("persona") or {}).get("desires")
            if isinstance(character.get("persona"), dict)
            else None,
            "追索自己的命运位置",
        )
        attractors.append(
            {
                "id": f"character_pull_{safe_id(_text(character.get('id'))) or len(attractors) + 1}",
                "title": f"{name}的欲望牵引",
                "pull": desire,
                "source": "characters.yaml",
            }
        )
    if not attractors:
        attractors.append(
            {
                "id": "attractor_world_continuity",
                "title": _text(world.get("title")) or "世界继续运行",
                "pull": "世界会推动角色选择，而不是等待作者逐句安排。",
                "source": "world.yaml",
            }
        )
    return attractors[:5]


def _genre_constraints(world: dict[str, Any]) -> list[dict[str, str]]:
    genre = _text(world.get("genre")) or _text(world.get("type")) or "东方奇幻"
    tone = _text(world.get("tone")) or "古风纸面、克制系统感"
    rules = world.get("rules") if isinstance(world.get("rules"), list) else []
    constraints = [
        {
            "id": "genre",
            "name": "题材约束",
            "rule": genre,
        },
        {
            "id": "tone",
            "name": "叙事气质",
            "rule": tone,
        },
    ]
    for idx, rule in enumerate(rules[:3], start=1):
        constraints.append(
            {
                "id": f"world_rule_{idx}",
                "name": "世界规则",
                "rule": _text(rule) or "世界规则待补全",
            }
        )
    return constraints


def _anchor_status(
    characters: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    protagonist = next(
        (
            c
            for c in characters
            if "protagonist" in _text(c.get("narrative_role")).lower()
        ),
        characters[0] if characters else {},
    )
    return {
        "status": "anchored" if protagonist else "needs_anchor",
        "current_anchor_character_id": safe_id(_text(protagonist.get("id"))) or None,
        "current_anchor_name": _text(protagonist.get("name")) or "",
        "candidate_count": len(candidates),
        "risk": "主锚点可运行，但世界需要候选承载者以支持反抗、失锚和代偿。",
    }


def _contract_pressure(
    threads: list[dict[str, Any]],
    characters: list[dict[str, Any]],
) -> dict[str, Any]:
    score = len(threads) + len(characters)
    level = "high" if score >= 8 else "medium" if score >= 4 else "low"
    return {
        "level": level,
        "score": score,
        "drivers": [
            f"{len(threads)} 条开放伏笔正在施压",
            f"{len(characters)} 名角色可自主行动",
            "普通干预只能增加因果债或生成世界线差异",
        ],
    }


def _replacement_candidates(characters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, character in enumerate(characters[:5], start=1):
        cid = safe_id(_text(character.get("id"))) or f"character_{idx}"
        name = _text(character.get("name")) or cid
        persona = character.get("persona") if isinstance(character.get("persona"), dict) else {}
        desire = _first_text(persona.get("desires"), "维持自身命运主动权")
        fear = _first_text(persona.get("fears"), "失去选择余地")
        role = _text(character.get("narrative_role")) or "character"
        rows.append(
            {
                "character_id": cid,
                "character_name": name,
                "current_role": role,
                "desire": desire,
                "risk": fear,
                "anchor_fit": max(1, 6 - idx),
                "reason": f"{name}有明确欲望“{desire}”，可在主锚点失效时承接世界压力。",
            }
        )
    return rows


def _thread_rows(raw: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("threads", "open_threads", "items"):
        rows = raw.get(key)
        if isinstance(rows, list):
            return [item for item in rows if isinstance(item, dict)]
    return []


def _read_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TianmingRequestError(f"{path.name} 无法解析：{exc}") from exc
    if not isinstance(raw, dict):
        raise TianmingRequestError(f"{path.name} 结构异常")
    return raw


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _first_text(value: object, fallback: str) -> str:
    if isinstance(value, list):
        for item in value:
            text = _text(item)
            if text:
                return text
    return _text(value) or fallback


def _text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return str(value.get("name") or value.get("title") or value.get("id") or "").strip()
    return str(value).strip()


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise TianmingRequestError(f"{label} 无效")
    return checked

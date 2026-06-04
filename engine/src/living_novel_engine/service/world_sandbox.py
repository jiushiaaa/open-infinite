"""World Sandbox Loop v1: local deterministic sandbox round service."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.service.project_health import resolve_story_path

VERSION = "world-sandbox-round-v1"
_ROUNDS_ARTIFACT = "sandbox_rounds.jsonl"
_SUBJECTIVE_MEMORY_DELTA_ARTIFACT = "subjective_memory_delta.json"


class WorldSandboxRequestError(ValueError):
    """Invalid world sandbox request."""


def run_sandbox_round(
    story_slug: str,
    *,
    major_event: str,
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
    worldline_id: str = "main",
) -> dict[str, Any]:
    """Run one deterministic sandbox round and write ``sandbox_rounds.jsonl``.

    The first slice intentionally does not call LLMs, external providers, or
    ``run_scene``. It proves the product loop can persist role-specific action
    chains and world deltas as additive local artifacts.
    """

    event = str(major_event or "").strip()
    if not event:
        raise WorldSandboxRequestError("major_event 不能为空")
    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")

    story_path, source_kind = resolve_story_path(sid, projects_dir)
    characters = _load_characters(story_path)
    if not characters:
        raise WorldSandboxRequestError("故事缺少可参与沙盘的角色")
    selected = _select_characters(characters)
    previous_memories = _load_latest_subjective_memories(story_path, wid, selected)
    created_at = datetime.now().isoformat(timespec="seconds")
    run_id = _new_run_id()
    root = outputs_dir or default_outputs_dir()
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    round_record = _build_round_record(
        story_slug=sid,
        source_kind=source_kind,
        worldline_id=wid,
        run_id=run_id,
        major_event=event,
        characters=selected,
        previous_memories=previous_memories,
        created_at=created_at,
    )
    _write_jsonl(run_dir / _ROUNDS_ARTIFACT, [round_record])
    memory_delta = _append_subjective_memory_delta(
        story_path=story_path,
        run_dir=run_dir,
        round_record=round_record,
    )
    meta = {
        "kind": "world_sandbox_round",
        "version": VERSION,
        "story_slug": sid,
        "source_kind": source_kind,
        "worldline_id": wid,
        "created_at": created_at,
        "artifacts": {
            "sandbox_rounds": _ROUNDS_ARTIFACT,
            "subjective_memory_delta": _SUBJECTIVE_MEMORY_DELTA_ARTIFACT,
        },
    }
    (run_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report = _build_report(
        run_id=run_id,
        story_slug=sid,
        source_kind=source_kind,
        worldline_id=wid,
        created_at=created_at,
        rounds=[round_record],
        subjective_memory_delta=memory_delta,
    )
    (run_dir / "sandbox_summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def get_sandbox_run(
    run_id: str,
    *,
    outputs_dir: Path | None = None,
) -> dict[str, Any]:
    """Read a sandbox run from local output artifacts."""

    rid = str(run_id or "").strip()
    if not rid:
        raise WorldSandboxRequestError("run_id 不能为空")
    root = outputs_dir or default_outputs_dir()
    run_dir = root / rid
    if not run_dir.is_dir():
        raise FileNotFoundError(f"沙盘运行不存在: {rid}")
    rounds_path = run_dir / _ROUNDS_ARTIFACT
    if not rounds_path.exists():
        raise FileNotFoundError(f"沙盘轮次不存在: {rid}")
    rounds = _read_jsonl(rounds_path)
    if not rounds:
        raise WorldSandboxRequestError("sandbox_rounds.jsonl 为空")
    meta = _read_json(run_dir / "meta.json")
    subjective_memory_delta = _read_optional_json(
        run_dir / _SUBJECTIVE_MEMORY_DELTA_ARTIFACT
    )
    return _build_report(
        run_id=rid,
        story_slug=str(meta.get("story_slug") or rounds[0].get("story_slug") or ""),
        source_kind=str(meta.get("source_kind") or rounds[0].get("source_kind") or ""),
        worldline_id=str(meta.get("worldline_id") or rounds[0].get("worldline_id") or ""),
        created_at=str(meta.get("created_at") or rounds[0].get("created_at") or ""),
        rounds=rounds,
        subjective_memory_delta=subjective_memory_delta,
    )


def get_character_subjective_memory(
    story_slug: str,
    character_id: str,
    *,
    projects_dir: Path | None = None,
    worldline_id: str = "main",
) -> dict[str, Any]:
    """Read one character's subjective memory chain for a worldline."""

    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")
    cid = _checked_id(character_id, "character_id")
    story_path, source_kind = resolve_story_path(sid, projects_dir)
    path = _subjective_memory_path(story_path, wid, cid)
    entries = _read_jsonl(path) if path.exists() else []
    return {
        "version": VERSION,
        "story_slug": sid,
        "source_kind": source_kind,
        "worldline_id": wid,
        "character_id": cid,
        "entry_count": len(entries),
        "artifact": str(path.relative_to(story_path)).replace("\\", "/"),
        "entries": entries,
        "next_steps": [
            "下一轮沙盘行动会读取本角色最后一条主观记忆。",
            "后续可把角色个人卷从这条主观记忆链渲染出来。",
        ],
    }


def _new_run_id() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"sandbox_{ts}_{uuid.uuid4().hex[:6]}"


def _load_characters(story_path: Path) -> list[dict[str, Any]]:
    status, raw = _read_yaml(story_path / "characters.yaml")
    if status != "ready" or not isinstance(raw, dict):
        return []
    characters = raw.get("characters")
    if not isinstance(characters, list):
        return []
    return [item for item in characters if isinstance(item, dict)]


def _select_characters(characters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    present = [c for c in characters if c.get("present_in_scene", True)]
    pool = present or characters
    return pool[: max(3, min(len(pool), 5))]


def _build_round_record(
    *,
    story_slug: str,
    source_kind: str,
    worldline_id: str,
    run_id: str,
    major_event: str,
    characters: list[dict[str, Any]],
    previous_memories: dict[str, dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    actions = [
        _character_action(
            character,
            idx,
            major_event,
            previous_memories=previous_memories,
        )
        for idx, character in enumerate(characters)
    ]
    return {
        "version": VERSION,
        "run_id": run_id,
        "story_slug": story_slug,
        "source_kind": source_kind,
        "worldline_id": worldline_id,
        "round_index": 1,
        "created_at": created_at,
        "major_event": major_event,
        "character_actions": actions,
        "conflicts": _conflicts(actions, major_event),
        "information_flow": _information_flow(actions, major_event),
        "world_state_delta": _world_state_delta(actions, major_event),
        "next_story_possibilities": _next_story_possibilities(actions, major_event),
        "boundaries": [
            "本轮只写 sandbox_rounds.jsonl 和 sandbox_summary.json。",
            "不调用 run_scene，不覆盖 chapter.md、events.json、state_snapshot.json。",
            "不调用外部模型、GraphRAG、Zep、向量库或 reranker。",
        ],
    }


def _character_action(
    character: dict[str, Any],
    index: int,
    major_event: str,
    *,
    previous_memories: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    character_id = _safe_character_id(character, index)
    name = _text(character.get("name")) or character_id
    role = _text(character.get("narrative_role")) or "角色"
    persona = character.get("persona") if isinstance(character.get("persona"), dict) else {}
    state = (
        character.get("current_state")
        if isinstance(character.get("current_state"), dict)
        else {}
    )
    desire = _first_text(persona.get("desires"), "保住自己在局势中的主动权")
    fear = _first_text(persona.get("fears"), "被他人抢先定义真相")
    memory = _first_text(character.get("memory"), "记得旧局势中仍有未解的伏笔")
    location = _text(state.get("location")) or "当前场景"
    emotion = _text(state.get("emotion")) or "警惕"
    posture = ["试探", "隐忍", "结盟", "封锁消息", "抢占叙事位置"][index % 5]
    target_hint = _event_hint(major_event)
    previous_memory = previous_memories.get(character_id) or {}
    previous_memory_ref = _previous_memory_reference(previous_memory)
    return {
        "character_id": character_id,
        "character_name": name,
        "narrative_role": role,
        "known_information": [
            f"听闻：{target_hint}",
            f"旧记忆：{memory}",
            previous_memory_ref,
        ],
        "previous_subjective_memory": previous_memory_ref,
        "intent": f"{name}想{desire}，同时避免{fear}。",
        "action": f"{name}在{location}{posture}，围绕“{target_hint}”调整下一步。",
        "reason": f"行动依据来自欲望“{desire}”、恐惧“{fear}”和记忆“{memory}”。",
        "stance": posture,
        "emotion_delta": f"{emotion} -> {emotion}中带有戒备",
        "relationship_delta": "开始重新评估同场角色的可靠性",
        "memory_seed": {
            "saw": [target_hint],
            "did": [posture],
            "inferred": [f"{name}认为这不是孤立事件，而是世界大势的开端。"],
        },
    }


def _append_subjective_memory_delta(
    *,
    story_path: Path,
    run_dir: Path,
    round_record: dict[str, Any],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    paths: list[str] = []
    for action in round_record.get("character_actions", []):
        if not isinstance(action, dict):
            continue
        character_id = _checked_id(str(action.get("character_id") or ""), "character_id")
        entry = _subjective_memory_entry(round_record, action)
        path = _subjective_memory_path(
            story_path,
            str(round_record.get("worldline_id") or "main"),
            character_id,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        entries.append(entry)
        paths.append(str(path.relative_to(story_path)).replace("\\", "/"))
    delta = {
        "version": VERSION,
        "artifact": _SUBJECTIVE_MEMORY_DELTA_ARTIFACT,
        "story_slug": round_record.get("story_slug"),
        "worldline_id": round_record.get("worldline_id"),
        "source_run_id": round_record.get("run_id"),
        "entry_count": len(entries),
        "entries": entries,
        "paths": paths,
    }
    (run_dir / _SUBJECTIVE_MEMORY_DELTA_ARTIFACT).write_text(
        json.dumps(delta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return delta


def _subjective_memory_entry(
    round_record: dict[str, Any],
    action: dict[str, Any],
) -> dict[str, Any]:
    seed = action.get("memory_seed") if isinstance(action.get("memory_seed"), dict) else {}
    saw = _list_text(seed.get("saw")) or _list_text(action.get("known_information"))
    did = _list_text(seed.get("did")) or [_text(action.get("action"))]
    inferred = _list_text(seed.get("inferred"))
    new_belief = inferred[0] if inferred else f"{action.get('character_name')}认为局势正在改写。"
    return {
        "version": VERSION,
        "source_run_id": round_record.get("run_id"),
        "source_round_index": round_record.get("round_index"),
        "source_major_event": round_record.get("major_event"),
        "created_at": round_record.get("created_at"),
        "story_slug": round_record.get("story_slug"),
        "worldline_id": round_record.get("worldline_id"),
        "character_id": action.get("character_id"),
        "character_name": action.get("character_name"),
        "saw": saw,
        "did": did,
        "new_belief": new_belief,
        "emotion_delta": action.get("emotion_delta") or "情绪波动被记录",
        "trust_delta": action.get("relationship_delta") or "信任关系开始重新排序",
        "anomaly_delta": "异常感上升：本轮事件被记为世界大势的扰动。",
        "previous_subjective_memory": action.get("previous_subjective_memory") or "",
        "source_action": action.get("action") or "",
    }


def _load_latest_subjective_memories(
    story_path: Path,
    worldline_id: str,
    characters: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for idx, character in enumerate(characters):
        cid = _safe_character_id(character, idx)
        path = _subjective_memory_path(story_path, worldline_id, cid)
        if not path.exists():
            continue
        rows = _read_jsonl(path)
        if rows:
            latest[cid] = rows[-1]
    return latest


def _subjective_memory_path(
    story_path: Path,
    worldline_id: str,
    character_id: str,
) -> Path:
    wid = _checked_id(worldline_id, "worldline_id")
    cid = _checked_id(character_id, "character_id")
    return (
        story_path
        / "worldlines"
        / wid
        / "characters"
        / cid
        / "subjective_memory.jsonl"
    )


def _previous_memory_reference(memory: dict[str, Any]) -> str:
    if not memory:
        return "主观记忆：暂无上一轮记录。"
    belief = _text(memory.get("new_belief")) or "上一轮判断尚未成形"
    emotion = _text(memory.get("emotion_delta")) or "情绪变化未记录"
    return f"主观记忆：{belief}；{emotion}"


def _conflicts(actions: list[dict[str, Any]], major_event: str) -> list[dict[str, Any]]:
    if len(actions) < 2:
        return []
    first = actions[0]
    second = actions[1]
    return [
        {
            "id": "conflict_1",
            "title": "消息封锁与主动试探冲突",
            "participants": [
                first["character_id"],
                second["character_id"],
            ],
            "cause": f"同一大事件“{_event_hint(major_event)}”被不同角色解释成不同机会。",
            "pressure": "中",
        }
    ]


def _information_flow(
    actions: list[dict[str, Any]], major_event: str
) -> list[dict[str, Any]]:
    return [
        {
            "from": "world_event",
            "to": action["character_id"],
            "content": _event_hint(major_event),
            "distortion": action["stance"],
        }
        for action in actions
    ]


def _world_state_delta(
    actions: list[dict[str, Any]], major_event: str
) -> dict[str, Any]:
    return {
        "status": "changed",
        "trigger": _event_hint(major_event),
        "relationship_changes": [
            {
                "source": action["character_id"],
                "change": action["relationship_delta"],
            }
            for action in actions
        ],
        "resource_changes": ["情报流动加快", "旧秩序稳定性下降"],
        "secret_changes": ["至少一名角色选择暂不公开自己的判断"],
        "anchor_pressure": "上升",
        "causal_debt": "低到中：世界开始要求角色为各自选择付出代价",
    }


def _next_story_possibilities(
    actions: list[dict[str, Any]], major_event: str
) -> list[dict[str, Any]]:
    names = [action["character_name"] for action in actions[:2]]
    joined = "、".join(names) if names else "关键角色"
    return [
        {
            "id": "possibility_1",
            "title": "暗线试探升级",
            "brief": f"{joined}围绕“{_event_hint(major_event)}”形成误判，下一轮会互相试探。",
        },
        {
            "id": "possibility_2",
            "title": "旧秩序松动",
            "brief": "世界状态开始偏移，新的联盟、谣言和因果债会自然长出。",
        },
    ]


def _build_report(
    *,
    run_id: str,
    story_slug: str,
    source_kind: str,
    worldline_id: str,
    created_at: str,
    rounds: list[dict[str, Any]],
    subjective_memory_delta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    actions = [
        action
        for round_record in rounds
        for action in round_record.get("character_actions", [])
        if isinstance(action, dict)
    ]
    return {
        "version": VERSION,
        "mode": "deterministic_world_sandbox_round",
        "run_id": run_id,
        "story_slug": story_slug,
        "source_kind": source_kind,
        "worldline_id": worldline_id,
        "created_at": created_at,
        "round_count": len(rounds),
        "summary": {
            "character_action_count": len(actions),
            "conflict_count": sum(len(r.get("conflicts", [])) for r in rounds),
            "information_flow_count": sum(
                len(r.get("information_flow", [])) for r in rounds
            ),
            "writes_artifacts": True,
            "subjective_memory_entries_written": int(
                (subjective_memory_delta or {}).get("entry_count") or 0
            ),
            "external_services_required": False,
            "run_scene_default_unchanged": True,
        },
        "artifacts": {
            "sandbox_rounds": _ROUNDS_ARTIFACT,
            "sandbox_summary": "sandbox_summary.json",
            "subjective_memory_delta": _SUBJECTIVE_MEMORY_DELTA_ARTIFACT,
        },
        "rounds": rounds,
        "subjective_memory_delta": subjective_memory_delta or {},
        "next_steps": [
            "下一刀让 UI 从主观记忆链渲染角色个人卷。",
            "再把《天命书》作为干预编译与沙盘轮次的世界宪法输入。",
        ],
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorldSandboxRequestError(f"sandbox_rounds.jsonl 无法解析：{exc}") from exc
    if not all(isinstance(row, dict) for row in rows):
        raise WorldSandboxRequestError("sandbox_rounds.jsonl 包含非对象记录")
    return rows


def _read_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorldSandboxRequestError(f"{path.name} 无法解析：{exc}") from exc
    return raw if isinstance(raw, dict) else {}


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return _read_json(path)


def _read_yaml(path: Path) -> tuple[str, Any]:
    if not path.exists():
        return "missing", None
    try:
        return "ready", yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return "damaged", None


def _event_hint(value: str) -> str:
    text = " ".join(str(value or "").split())
    return text[:80] or "未命名大事件"


def _first_text(value: object, fallback: str) -> str:
    if isinstance(value, list):
        for item in value:
            text = _text(item)
            if text:
                return text
    text = _text(value)
    return text or fallback


def _list_text(value: object) -> list[str]:
    if isinstance(value, list):
        return [_text(item) for item in value if _text(item)]
    text = _text(value)
    return [text] if text else []


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise WorldSandboxRequestError(f"{label} 无效")
    return checked


def _safe_character_id(character: dict[str, Any], index: int) -> str:
    raw = _text(character.get("id")) or _text(character.get("name"))
    return safe_id(raw) or f"character_{index + 1}"


def _text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return str(value.get("name") or value.get("title") or value.get("id") or "").strip()
    return str(value).strip()

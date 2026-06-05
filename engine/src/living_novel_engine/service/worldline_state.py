"""Persistent worldline state for the Unfinale sandbox loop."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.project_health import resolve_story_path

VERSION = "worldline-state-v1"
ARTIFACT = "worldline_state.json"


class WorldlineStateRequestError(ValueError):
    """Invalid worldline state request."""


def get_worldline_state(
    story_slug: str,
    *,
    worldline_id: str = "main",
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")
    story_path, source_kind = resolve_story_path(sid, projects_dir)
    state = load_worldline_state(story_path, wid)
    state.setdefault("story_slug", sid)
    state.setdefault("source_kind", source_kind)
    state.setdefault("current_worldline", wid)
    state.setdefault("artifact", f"worldlines/{wid}/{ARTIFACT}")
    return state


def load_worldline_state(story_path: Path, worldline_id: str) -> dict[str, Any]:
    wid = _checked_id(worldline_id, "worldline_id")
    path = _state_path(story_path, wid)
    if not path.exists():
        return _empty_state(wid)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorldlineStateRequestError(f"{ARTIFACT} 无法解析：{exc}") from exc
    if not isinstance(raw, dict):
        return _empty_state(wid)
    return raw


def apply_sandbox_worldline_state(
    *,
    story_path: Path,
    worldline_id: str,
    round_record: dict[str, Any],
    intervention_constraint: dict[str, Any],
) -> dict[str, Any]:
    wid = _checked_id(worldline_id, "worldline_id")
    previous = load_worldline_state(story_path, wid)
    now = datetime.now().isoformat(timespec="seconds")
    active = (
        intervention_constraint
        if isinstance(intervention_constraint, dict)
        and intervention_constraint.get("status") == "active"
        else previous.get("source_intervention")
        if isinstance(previous.get("source_intervention"), dict)
        else {}
    )
    actions = [
        action
        for action in round_record.get("character_actions", [])
        if isinstance(action, dict)
    ]
    delta = (
        round_record.get("world_state_delta")
        if isinstance(round_record.get("world_state_delta"), dict)
        else {}
    )
    prior_debt = previous.get("causal_debt") if isinstance(previous.get("causal_debt"), dict) else {}
    current_debt = active.get("causal_debt") if isinstance(active.get("causal_debt"), dict) else {}
    debt_score = max(
        int(prior_debt.get("score") or 0) + (1 if previous.get("current_worldline") else 0),
        int(current_debt.get("score") or 0),
        1 if actions else 0,
    )
    snapshot = _snapshot_state(active, previous)
    state = {
        "version": VERSION,
        "artifact": f"worldlines/{wid}/{ARTIFACT}",
        "current_worldline": wid,
        "status": "active",
        "updated_at": now,
        "last_sandbox_run_id": round_record.get("run_id") or "",
        "last_major_event": round_record.get("major_event") or "",
        "source_intervention": _source_intervention(active, previous),
        "tianming_snapshot": snapshot,
        "branch_state": {
            "continuation_status": "runnable",
            "projection_mode": _projection_mode(active, previous),
            "next_round_reads": [
                "source_intervention",
                "tianming_snapshot",
                "causal_debt",
                "branch_state",
                "consequence_state",
                "meme_contamination",
                "author_adoption",
            ],
        },
        "causal_debt": {
            "score": debt_score,
            "level": "high" if debt_score >= 7 else "medium" if debt_score >= 3 else "low",
            "pressure_order": ["current_anchor", "relationship_network", "factions", "environment"],
            "spread": _merge_lists(prior_debt.get("spread"), current_debt.get("spread"))
            or ["关系网承担第一波代偿", "势力和环境随后外溢"],
        },
        "anchor_status": _anchor_state(actions, delta, debt_score),
        "replacement_anchor_candidates": _replacement_candidates(actions),
        "meme_contamination": _meme_state(actions, previous),
        "compensation_effects": _compensation_effects(debt_score, actions),
        "consequence_state": _consequence_state(previous, round_record, debt_score, actions),
        "continuation_inputs": {
            "major_event_hint": _next_major_event(round_record, active),
            "worldline_id": wid,
        },
        "author_adoption": previous.get("author_adoption") or {},
        "next_chapter_brief": previous.get("next_chapter_brief") or {},
    }
    path = _state_path(story_path, wid)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def apply_author_adoption_to_worldline_state(
    *,
    story_path: Path,
    worldline_id: str,
    decision: str,
    source_run_id: str,
    next_chapter_brief: dict[str, Any],
    author_branch: dict[str, str] | None = None,
    source_worldline_id: str = "",
) -> dict[str, Any]:
    wid = _checked_id(worldline_id, "worldline_id")
    state = load_worldline_state(story_path, wid)
    now = datetime.now().isoformat(timespec="seconds")
    feed_forward = (
        next_chapter_brief.get("feed_forward")
        if isinstance(next_chapter_brief.get("feed_forward"), dict)
        else {}
    )
    sandbox_inputs = (
        feed_forward.get("sandbox_continuation_inputs")
        if isinstance(feed_forward.get("sandbox_continuation_inputs"), dict)
        else next_chapter_brief.get("sandbox_inputs")
        if isinstance(next_chapter_brief.get("sandbox_inputs"), dict)
        else {}
    )
    state.update(
        {
            "version": VERSION,
            "artifact": f"worldlines/{wid}/{ARTIFACT}",
            "current_worldline": wid,
            "status": "active",
            "updated_at": now,
            "author_adoption": {
                "latest_decision": decision,
                "source_run_id": source_run_id,
                "updated_at": now,
                "affects_future_sandbox": True,
            },
            "next_chapter_brief": {
                "source_run_id": source_run_id,
                "opening_scene": next_chapter_brief.get("opening_scene") or "",
                "major_event": sandbox_inputs.get("major_event") or "",
                "materialized_consequences": next_chapter_brief.get(
                    "materialized_consequences"
                )
                or [],
                "writing_plan": next_chapter_brief.get("writing_plan") or {},
                "feed_forward": feed_forward,
            },
            "continuation_inputs": {
                "major_event_hint": sandbox_inputs.get("major_event") or "",
                "worldline_id": wid,
                "source": "next_chapter_brief",
                "source_adoption_run_id": source_run_id,
            },
        }
    )
    state.setdefault("branch_state", {})["continuation_status"] = "runnable"
    state.setdefault("branch_state", {}).setdefault("next_round_reads", [])
    reads = state["branch_state"]["next_round_reads"]
    if isinstance(reads, list):
        for key in feed_forward.get("next_round_reads") or ["next_chapter_brief"]:
            if key not in reads:
                reads.append(key)
    branch = author_branch if isinstance(author_branch, dict) else {}
    if branch:
        state["author_branch"] = {
            "branch_id": branch.get("branch_id") or wid,
            "source_worldline_id": branch.get("source_worldline_id")
            or source_worldline_id
            or "",
            "status": branch.get("status") or "created",
            "root_canon_policy": branch.get("root_canon_policy")
            or "preserve_root_canon",
            "source_adoption_run_id": source_run_id,
        }
    path = _state_path(story_path, wid)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def apply_confirmed_chapter_to_worldline_state(
    *,
    story_path: Path,
    worldline_id: str,
    source_adoption_run_id: str,
    chapter_title: str,
    chapter_text: str,
    author_note: str,
    edited: bool,
    artifact: str,
    markdown_artifact: str,
    next_sandbox_entry: dict[str, str],
    accepted_rewrite_ids: list[str] | None = None,
    accepted_rewrites_artifact: str = "",
) -> dict[str, Any]:
    wid = _checked_id(worldline_id, "worldline_id")
    rid = _checked_id(source_adoption_run_id, "source_adoption_run_id")
    state = load_worldline_state(story_path, wid)
    now = datetime.now().isoformat(timespec="seconds")
    entry = {
        "source_adoption_run_id": rid,
        "artifact": artifact,
        "markdown_artifact": markdown_artifact,
        "title": chapter_title,
        "summary": _chapter_summary(chapter_text),
        "author_note": author_note,
        "edited": edited,
        "affects_future_sandbox": True,
        "updated_at": now,
        "next_sandbox_entry": next_sandbox_entry,
        "accepted_rewrite_ids": accepted_rewrite_ids or [],
        "accepted_rewrites_artifact": accepted_rewrites_artifact,
    }
    history = state.get("confirmed_chapter_entries")
    rows = [item for item in history if isinstance(item, dict)] if isinstance(history, list) else []
    rows.append(entry)
    state.update(
        {
            "version": VERSION,
            "artifact": f"worldlines/{wid}/{ARTIFACT}",
            "current_worldline": wid,
            "status": "active",
            "updated_at": now,
            "confirmed_chapter_entry": entry,
            "confirmed_chapter_entries": rows[-8:],
        }
    )
    state.setdefault("branch_state", {})["continuation_status"] = "runnable"
    state.setdefault("branch_state", {}).setdefault("next_round_reads", [])
    reads = state["branch_state"]["next_round_reads"]
    if isinstance(reads, list) and "confirmed_chapter_entry" not in reads:
        reads.append("confirmed_chapter_entry")
    state["continuation_inputs"] = {
        "major_event_hint": next_sandbox_entry.get("major_event") or "",
        "worldline_id": wid,
        "source": "confirmed_chapter_entry",
        "source_adoption_run_id": rid,
    }
    path = _state_path(story_path, wid)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def _empty_state(worldline_id: str) -> dict[str, Any]:
    return {
        "version": VERSION,
        "artifact": f"worldlines/{worldline_id}/{ARTIFACT}",
        "current_worldline": worldline_id,
        "status": "new",
    }


def _source_intervention(
    active: dict[str, Any],
    previous: dict[str, Any],
) -> dict[str, Any]:
    if active.get("status") == "active":
        return {
            "status": "active",
            "source": active.get("source") or "worldline_state",
            "content": active.get("content") or "",
            "target": active.get("target") or "",
            "projection_mode": active.get("projection_mode") or "immersive",
            "intervention_level": active.get("intervention_level") or "",
            "branch_axis": active.get("branch_axis") or {},
            "causal_debt": active.get("causal_debt") or {},
        }
    prior = previous.get("source_intervention")
    return deepcopy(prior) if isinstance(prior, dict) else {}


def _snapshot_state(active: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    snapshot = active.get("worldline_tianming_snapshot")
    if isinstance(snapshot, dict):
        return {
            "artifact": snapshot.get("artifact") or "",
            "status": snapshot.get("status") or "draft_snapshot",
            "audit_status": "pending_confirmation",
            "requires_confirmation": bool(snapshot.get("requires_confirmation", True)),
            "root_tianming_mutated": False,
        }
    prior = previous.get("tianming_snapshot")
    return deepcopy(prior) if isinstance(prior, dict) else {}


def _projection_mode(active: dict[str, Any], previous: dict[str, Any]) -> str:
    if active.get("projection_mode"):
        return str(active.get("projection_mode"))
    prior = previous.get("branch_state") if isinstance(previous.get("branch_state"), dict) else {}
    return str(prior.get("projection_mode") or "immersive")


def _anchor_state(
    actions: list[dict[str, Any]],
    delta: dict[str, Any],
    debt_score: int,
) -> dict[str, Any]:
    first = actions[0] if actions else {}
    if debt_score >= 9:
        status = "lost_anchor"
    elif debt_score >= 7:
        status = "replacement_contested"
    else:
        status = "pressured"
    return {
        "status": status,
        "current_anchor": first.get("character_id") or "unknown",
        "current_anchor_pressure": delta.get("anchor_pressure") or "上升",
        "no_qualified_anchor": status == "lost_anchor",
        "ensemble_without_mainline": status == "lost_anchor",
    }


def _replacement_candidates(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for index, action in enumerate(actions[:4]):
        inputs = action.get("decision_inputs") if isinstance(action.get("decision_inputs"), dict) else {}
        score = max(1, 8 - index * 2)
        candidates.append(
            {
                "character_id": action.get("character_id") or "",
                "character_name": action.get("character_name") or "",
                "score": score,
                "desire": inputs.get("desire") or "保住自身主动权",
                "capability": inputs.get("resource_signal") or "资源紧张",
                "resources": inputs.get("relationship_signal") or "关系网待确认",
                "resistance": action.get("risk") or "阻力未明",
                "explanation": (
                    "候选上位取决于欲望是否足够强、资源能否覆盖因果债、"
                    "以及关系网是否愿意承认其解释权。"
                ),
            }
        )
    return candidates


def _meme_state(actions: list[dict[str, Any]], previous: dict[str, Any]) -> dict[str, Any]:
    active_actions = [
        action
        for action in actions
        if isinstance(action.get("meme_contamination"), dict)
        and action["meme_contamination"].get("status") == "active"
    ]
    if active_actions:
        first = active_actions[0]
        propagation = [
            action["meme_propagation"]
            for action in actions
            if isinstance(action.get("meme_propagation"), dict)
            and action["meme_propagation"].get("status") in {"source", "received"}
        ]
        return {
            "status": "active",
            "source_character_id": first.get("character_id") or "",
            "belief_payload": first["meme_contamination"].get("belief_payload") or "",
            "spread_vector": first["meme_contamination"].get("spread_vector") or [],
            "propagation": propagation,
        }
    prior = previous.get("meme_contamination")
    return deepcopy(prior) if isinstance(prior, dict) else {"status": "none"}


def _compensation_effects(debt_score: int, actions: list[dict[str, Any]]) -> list[str]:
    names = [str(action.get("character_name") or "") for action in actions[:2]]
    joined = "、".join(name for name in names if name) or "当前锚点"
    effects = [
        f"因果债先压向{joined}，迫使其为本轮选择承担代价。",
        "若锚点拒绝主线，压力会外溢到关系网、势力和环境。",
    ]
    if debt_score >= 7:
        effects.append("候选天命承载者开始被世界推到台前，但仍可能因资源不足失败。")
    return effects


def _consequence_state(
    previous: dict[str, Any],
    round_record: dict[str, Any],
    debt_score: int,
    actions: list[dict[str, Any]],
) -> dict[str, Any]:
    prior = (
        previous.get("consequence_state")
        if isinstance(previous.get("consequence_state"), dict)
        else {}
    )
    prior_ledger = prior.get("ledger") if isinstance(prior.get("ledger"), list) else []
    domains = _consequence_domains(round_record, debt_score, actions)
    entry = {
        "source_run_id": round_record.get("run_id") or "",
        "major_event": round_record.get("major_event") or "",
        "debt_score": debt_score,
        "impacts": [
            {
                "domain": key,
                "current": value.get("current") or "",
                "pressure": value.get("pressure") or "",
            }
            for key, value in domains.items()
        ],
    }
    ledger = [item for item in prior_ledger if isinstance(item, dict)][-5:]
    ledger.append(entry)
    return {
        "status": "active",
        "summary": _consequence_summary(domains),
        "domains": domains,
        "ledger": ledger,
        "next_round_hint": "下一轮角色会把这些地点、资源、伤势、舆论、势力和环境代价当作行动前提。",
    }


def _consequence_domains(
    round_record: dict[str, Any],
    debt_score: int,
    actions: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    event = str(round_record.get("major_event") or "本轮事件")
    first = actions[0] if actions else {}
    first_name = str(first.get("character_name") or "当前锚点")
    first_id = str(first.get("character_id") or "unknown")
    level = "高" if debt_score >= 7 else "中" if debt_score >= 3 else "低"
    return {
        "location": {
            "label": "地点",
            "current": f"归云斋与事发地因“{event}”被封锁复查，暗线出入需要留下证人。",
            "pressure": f"{level}压",
            "bearer": first_id,
        },
        "resource": {
            "label": "资源",
            "current": f"{first_name}可用资源被扣到明面：军需、情报和藏匿路线必须二选一。",
            "pressure": f"{level}压",
            "bearer": first_id,
        },
        "injury": {
            "label": "伤势",
            "current": "接触异物或异常线索的人留下灼伤、梦魇或灵识刺痛，不能再无代价行动。",
            "pressure": "可见代价",
            "bearer": first_id,
        },
        "public_opinion": {
            "label": "舆论",
            "current": "城中开始流传高维改命与归云斋藏器传闻，旁观者会按旧怨选择相信或造谣。",
            "pressure": "外溢",
            "bearer": "relationship_network",
        },
        "faction": {
            "label": "势力",
            "current": "朝堂、边军和归云斋各自派人追索异常来源，候选承载者必须证明自己能收束局面。",
            "pressure": "争夺解释权",
            "bearer": "factions",
        },
        "environment": {
            "label": "环境",
            "current": "夜雨、雷火与失序梦兆反复出现，世界用自然异象提醒锚点债务尚未清偿。",
            "pressure": "世界回声",
            "bearer": "environment",
        },
    }


def _consequence_summary(domains: dict[str, dict[str, Any]]) -> str:
    parts = [
        str(domains[key].get("current") or "")
        for key in ("location", "resource", "injury", "public_opinion", "faction", "environment")
        if key in domains
    ]
    return "；".join(part for part in parts if part)


def _next_major_event(round_record: dict[str, Any], active: dict[str, Any]) -> str:
    if active.get("content"):
        return f"世界继续消化干预：{active.get('content')}"
    possibilities = round_record.get("next_story_possibilities")
    if isinstance(possibilities, list) and possibilities:
        first = possibilities[0] if isinstance(possibilities[0], dict) else {}
        return str(first.get("brief") or first.get("title") or "")
    return str(round_record.get("major_event") or "")


def _chapter_summary(chapter_text: str) -> str:
    clean = " ".join(str(chapter_text or "").split())
    return clean if len(clean) <= 180 else clean[:180] + "..."


def _merge_lists(*values: object) -> list[str]:
    result: list[str] = []
    for value in values:
        if isinstance(value, list):
            result.extend(str(item) for item in value if str(item))
    return list(dict.fromkeys(result))


def _state_path(story_path: Path, worldline_id: str) -> Path:
    return story_path / "worldlines" / worldline_id / ARTIFACT


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise WorldlineStateRequestError(f"{label} 无效")
    return checked

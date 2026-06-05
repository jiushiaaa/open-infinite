"""World Sandbox Loop v1: local deterministic sandbox round service."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
import yaml

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.service.project_health import resolve_story_path
from living_novel_engine.service.tianming_intervention_compiler import (
    TianmingInterventionCompilerRequestError,
    compile_intervention_against_tianming,
)
from living_novel_engine.service.worldline_state import (
    apply_sandbox_worldline_state,
    load_worldline_state,
)

VERSION = "world-sandbox-round-v1"
_ROUNDS_ARTIFACT = "sandbox_rounds.jsonl"
_SUBJECTIVE_MEMORY_DELTA_ARTIFACT = "subjective_memory_delta.json"
_INTERVENTION_CONSTRAINT_ARTIFACT = "intervention_constraint.json"
_AGENT_DECISION_ADVISORY_ARTIFACT = "agent_decision_advisory.json"


class _LLMDecisionItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    character_id: str = ""
    belief_update: str = ""
    visible_action: str = ""
    true_intent: str = ""
    expected_outcome: str = ""
    risk: str = ""
    deception_strategy: str = ""
    propagation_choice: str = ""
    resistance_choice: str = ""
    situational_judgement: str = ""
    trust_shift: str = ""
    memory_seed: list[str] = Field(default_factory=list)


class _LLMDecisionPack(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str = "ready"
    summary: str = ""
    decisions: list[_LLMDecisionItem] = Field(default_factory=list)


class WorldSandboxRequestError(ValueError):
    """Invalid world sandbox request."""


def run_sandbox_round(
    story_slug: str,
    *,
    major_event: str,
    intervention_content: str = "",
    intervention_target: str = "",
    intervention_projection_mode: str = "immersive",
    intervention_constraint: dict[str, Any] | None = None,
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
    worldline_id: str = "main",
    llm_decision_mode: str = "deterministic",
    llm_decision_mock: bool = False,
    llm_client: Any | None = None,
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
    normalized_llm_decision_mode = _normalize_llm_decision_mode(llm_decision_mode)

    story_path, source_kind = resolve_story_path(sid, projects_dir)
    characters = _load_characters(story_path)
    if not characters:
        raise WorldSandboxRequestError("故事缺少可参与沙盘的角色")
    selected = _select_characters(characters)
    previous_memories = _load_latest_subjective_memories(story_path, wid, selected)
    tianming_pressure = _load_tianming_pressure(story_path)
    worldline_state = load_worldline_state(story_path, wid)
    constraint = _build_intervention_constraint(
        story_slug=sid,
        worldline_id=wid,
        content=intervention_content,
        target=intervention_target,
        projection_mode=intervention_projection_mode,
        raw_constraint=intervention_constraint,
        projects_dir=projects_dir,
    )
    if constraint.get("status") != "active":
        constraint = _constraint_from_worldline_state(worldline_state)
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
        tianming_pressure=tianming_pressure,
        intervention_constraint=constraint,
        worldline_state=worldline_state,
        created_at=created_at,
        llm_decision_mode=normalized_llm_decision_mode,
        llm_decision_mock=llm_decision_mock,
        llm_client=llm_client,
    )
    _write_jsonl(run_dir / _ROUNDS_ARTIFACT, [round_record])
    decision_advisory = round_record.get("llm_decision_advisory")
    if isinstance(decision_advisory, dict) and decision_advisory.get("status") != "skipped":
        (run_dir / _AGENT_DECISION_ADVISORY_ARTIFACT).write_text(
            json.dumps(decision_advisory, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if constraint.get("status") == "active":
        (run_dir / _INTERVENTION_CONSTRAINT_ARTIFACT).write_text(
            json.dumps(constraint, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    memory_delta = _append_subjective_memory_delta(
        story_path=story_path,
        run_dir=run_dir,
        round_record=round_record,
    )
    updated_worldline_state = apply_sandbox_worldline_state(
        story_path=story_path,
        worldline_id=wid,
        round_record=round_record,
        intervention_constraint=constraint,
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
            **(
                {"intervention_constraint": _INTERVENTION_CONSTRAINT_ARTIFACT}
                if constraint.get("status") == "active"
                else {}
            ),
            **(
                {"agent_decision_advisory": _AGENT_DECISION_ADVISORY_ARTIFACT}
                if isinstance(decision_advisory, dict)
                and decision_advisory.get("status") != "skipped"
                else {}
            ),
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
        intervention_constraint=constraint,
        worldline_state=updated_worldline_state,
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
        intervention_constraint=_read_optional_json(
            run_dir / _INTERVENTION_CONSTRAINT_ARTIFACT
        ),
        worldline_state={},
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
    tianming_pressure: dict[str, Any],
    intervention_constraint: dict[str, Any],
    worldline_state: dict[str, Any],
    created_at: str,
    llm_decision_mode: str = "deterministic",
    llm_decision_mock: bool = False,
    llm_client: Any | None = None,
) -> dict[str, Any]:
    actions = [
        _character_action(
            character,
            idx,
            major_event,
            previous_memories=previous_memories,
            tianming_pressure=tianming_pressure,
            intervention_constraint=intervention_constraint,
            worldline_state=worldline_state,
        )
        for idx, character in enumerate(characters)
    ]
    _apply_meme_propagation(actions, previous_memories)
    decision_advisory = _maybe_apply_llm_decision_advisory(
        mode=llm_decision_mode,
        mock=llm_decision_mock,
        client=llm_client,
        story_slug=story_slug,
        worldline_id=worldline_id,
        major_event=major_event,
        actions=actions,
        intervention_constraint=intervention_constraint,
        worldline_state=worldline_state,
    )
    record = {
        "version": VERSION,
        "run_id": run_id,
        "story_slug": story_slug,
        "source_kind": source_kind,
        "worldline_id": worldline_id,
        "round_index": 1,
        "created_at": created_at,
        "major_event": major_event,
        "intervention_constraint": intervention_constraint,
        "character_actions": actions,
        "conflicts": _conflicts(actions, major_event),
        "information_flow": _information_flow(actions, major_event),
        "world_state_delta": _world_state_delta(actions, major_event, worldline_state),
        "next_story_possibilities": _next_story_possibilities(actions, major_event),
        "boundaries": _sandbox_boundaries(decision_advisory),
    }
    if decision_advisory.get("status") != "skipped":
        record["llm_decision_advisory"] = decision_advisory
    return record


def _character_action(
    character: dict[str, Any],
    index: int,
    major_event: str,
    *,
    previous_memories: dict[str, dict[str, Any]],
    tianming_pressure: dict[str, Any],
    intervention_constraint: dict[str, Any],
    worldline_state: dict[str, Any],
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
    previous_belief = _text(previous_memory.get("new_belief"))
    previous_anomaly = _text(previous_memory.get("anomaly_delta"))
    previous_misbelief = _first_text(previous_memory.get("misbeliefs"), "")
    relationship_signal = _relationship_signal(character)
    secret_signal = _secret_signal(character, index)
    resource_signal = _resource_signal(character)
    pressure_text = _tianming_pressure_text(tianming_pressure)
    intervention_text = _intervention_constraint_text(intervention_constraint)
    intervention_axis = _intervention_branch_axis(intervention_constraint)
    intervention_debt = _intervention_causal_debt_text(intervention_constraint)
    intervention_target = _text(intervention_constraint.get("target"))
    intervention_projection_mode = _text(intervention_constraint.get("projection_mode"))
    worldline_inputs = _worldline_decision_inputs(worldline_state)
    awareness = _awareness_signal(
        character_id=character_id,
        index=index,
        intervention_constraint=intervention_constraint,
        worldline_state=worldline_state,
    )
    decision = _deterministic_decision(
        name=name,
        location=location,
        target_hint=target_hint,
        base_posture=posture,
        index=index,
        previous_belief=previous_belief,
        previous_anomaly=previous_anomaly,
        pressure_text=pressure_text,
        intervention_text=intervention_text,
        intervention_axis=intervention_axis,
        awareness=awareness,
    )
    memory_influence = (
        f"上一轮认知“{previous_belief}”与异常感“{previous_anomaly}”改变本轮选择。"
        if previous_belief or previous_anomaly
        else "无上一轮主观记忆"
    )
    decision_inputs = {
        "desire": desire,
        "fear": fear,
        "relationship_signal": relationship_signal,
        "secret_signal": secret_signal,
        "resource_signal": resource_signal,
        "tianming_pressure": pressure_text,
        "previous_memory_belief": previous_belief,
        "previous_memory_anomaly": previous_anomaly,
        "previous_misbelief": previous_misbelief,
        "intervention_constraint": intervention_text,
        "intervention_branch_axis": intervention_axis,
        "intervention_causal_debt": intervention_debt,
        "intervention_target": intervention_target,
        "intervention_projection_mode": intervention_projection_mode,
        **worldline_inputs,
    }
    action = {
        "character_id": character_id,
        "character_name": name,
        "narrative_role": role,
        "known_information": [
            f"听闻：{target_hint}",
            f"旧记忆：{memory}",
            f"关系信号：{relationship_signal}",
            f"秘密信号：{secret_signal}",
            f"资源信号：{resource_signal}",
            f"天命压力：{pressure_text}",
            f"干预约束：{intervention_text or '无'}",
            previous_memory_ref,
        ],
        "previous_subjective_memory": previous_memory_ref,
        "decision_mode": "deterministic_agent_decision",
        "decision_inputs": decision_inputs,
        "intent": f"{name}想{desire}，同时避免{fear}。",
        "visible_action": decision["visible_action"],
        "true_intent": decision["true_intent"],
        "expected_outcome": decision["expected_outcome"],
        "risk": decision["risk"],
        "action_outcome": decision["action_outcome"],
        "memory_influence": memory_influence,
        "action": decision["visible_action"],
        "reason": (
            f"行动依据来自欲望“{desire}”、恐惧“{fear}”、旧记忆“{memory}”、"
            f"{memory_influence}以及{pressure_text}。"
        ),
        "stance": decision["stance"],
        "emotion_delta": f"{emotion} -> {emotion}中带有戒备",
        "relationship_delta": decision["relationship_delta"],
        "memory_seed": {
            "saw": [target_hint],
            "did": [decision["stance"]],
            "inferred": [decision["new_belief"]],
        },
    }
    if awareness.get("level") == "L5":
        resistance = _resistance_behavior(name, index)
        meme = _meme_contamination(name, character_id, awareness)
        action["awareness"] = awareness
        action["resistance_behavior"] = resistance
        action["meme_contamination"] = meme
        action["fate_mark"] = {
            "status": "active",
            "label": "命痕",
            "description": f"{name}把异常归因于高维读者或作者的操控。",
        }
    return action


def _normalize_llm_decision_mode(value: str) -> str:
    mode = str(value or "deterministic").strip().lower()
    if mode in {"", "deterministic", "off", "none"}:
        return "deterministic"
    if mode in {"advisory", "llm_advisory", "llm_agent_decision_advisory"}:
        return "advisory"
    raise WorldSandboxRequestError("llm_decision_mode 只支持 deterministic 或 advisory")


def _maybe_apply_llm_decision_advisory(
    *,
    mode: str,
    mock: bool,
    client: Any | None,
    story_slug: str,
    worldline_id: str,
    major_event: str,
    actions: list[dict[str, Any]],
    intervention_constraint: dict[str, Any],
    worldline_state: dict[str, Any],
) -> dict[str, Any]:
    if mode != "advisory":
        return {"status": "skipped", "mode": "deterministic", "requested": False}

    llm = client or LLMClient(mock=mock)
    if not bool(getattr(llm, "available", True)):
        return {
            "status": "fallback",
            "mode": "llm_agent_decision_advisory",
            "requested": True,
            "mock": bool(mock or getattr(llm, "mock", False)),
            "generated_by": "fallback",
            "fallback_reason": "LLM_API_KEY 未配置，已保留 deterministic 行动。",
            "action_count": 0,
            "decisions": [],
        }

    generated_by = "mock_llm" if bool(mock or getattr(llm, "mock", False)) else "real_llm"
    try:
        if hasattr(llm, "chat_json_with_usage"):
            pack, usage = llm.chat_json_with_usage(
                _llm_decision_system_prompt(),
                _llm_decision_user_prompt(
                    story_slug=story_slug,
                    worldline_id=worldline_id,
                    major_event=major_event,
                    actions=actions,
                    intervention_constraint=intervention_constraint,
                    worldline_state=worldline_state,
                ),
                _LLMDecisionPack,
                temperature=0.55,
            )
        else:
            pack = llm.chat_json(
                _llm_decision_system_prompt(),
                _llm_decision_user_prompt(
                    story_slug=story_slug,
                    worldline_id=worldline_id,
                    major_event=major_event,
                    actions=actions,
                    intervention_constraint=intervention_constraint,
                    worldline_state=worldline_state,
                ),
                _LLMDecisionPack,
                temperature=0.55,
            )
            usage = None
    except Exception as exc:  # pragma: no cover - exercised by real smoke fallback.
        return {
            "status": "fallback",
            "mode": "llm_agent_decision_advisory",
            "requested": True,
            "mock": bool(mock or getattr(llm, "mock", False)),
            "generated_by": "fallback",
            "fallback_reason": _safe_error_text(exc),
            "action_count": 0,
            "decisions": [],
        }

    by_id = {
        _text(item.character_id): item
        for item in pack.decisions
        if _text(item.character_id)
    }
    applied: list[dict[str, Any]] = []
    for action in actions:
        decision = by_id.get(_text(action.get("character_id")))
        if decision is None:
            continue
        public = _public_llm_decision(decision, generated_by=generated_by)
        _overlay_action_with_llm_decision(action, public)
        applied.append(public)

    status = "ready" if applied else "fallback"
    return {
        "status": status,
        "mode": "llm_agent_decision_advisory",
        "requested": True,
        "mock": generated_by == "mock_llm",
        "generated_by": generated_by if applied else "fallback",
        "summary": _text(pack.summary)
        or ("模型已给出逐角色决策建议。" if applied else "模型未返回可匹配角色决策。"),
        "action_count": len(applied),
        "decisions": applied,
        "usage": usage or {},
        **({"fallback_reason": "模型未返回可匹配角色决策。"} if not applied else {}),
    }


def _llm_decision_system_prompt() -> str:
    return (
        "你是未终章世界沙盘的多 Agent 决策顾问。"
        "你的任务不是写小说正文，而是让每个角色基于自己的欲望、恐惧、记忆、关系、"
        "干预痕迹、因果债和命痕压力做更像人的判断。"
        "请避免模板化三选一；每个角色都要给出采信/存疑、欺骗或隐瞒、传播或压住信息、"
        "反抗或顺势利用、临场判断。"
        "不要输出推理过程，只给可审计的决策摘要和可用于沙盘字段的短文本。"
    )


def _llm_decision_user_prompt(
    *,
    story_slug: str,
    worldline_id: str,
    major_event: str,
    actions: list[dict[str, Any]],
    intervention_constraint: dict[str, Any],
    worldline_state: dict[str, Any],
) -> str:
    payload = {
        "story_slug": story_slug,
        "worldline_id": worldline_id,
        "major_event": _event_hint(major_event),
        "intervention_constraint": _compact_for_prompt(intervention_constraint),
        "worldline_state": _compact_for_prompt(worldline_state),
        "characters": [
            {
                "character_id": action.get("character_id"),
                "character_name": action.get("character_name"),
                "narrative_role": action.get("narrative_role"),
                "baseline_stance": action.get("stance"),
                "baseline_visible_action": action.get("visible_action"),
                "baseline_true_intent": action.get("true_intent"),
                "decision_inputs": action.get("decision_inputs"),
                "previous_subjective_memory": action.get("previous_subjective_memory"),
                "awareness": action.get("awareness"),
                "meme_propagation": action.get("meme_propagation"),
            }
            for action in actions
        ],
        "required_decision_fields": [
            "belief_update",
            "visible_action",
            "true_intent",
            "expected_outcome",
            "risk",
            "deception_strategy",
            "propagation_choice",
            "resistance_choice",
            "situational_judgement",
            "trust_shift",
            "memory_seed",
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _compact_for_prompt(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    wanted = {
        "status",
        "content",
        "target",
        "projection_mode",
        "branch_axis",
        "causal_debt",
        "source_intervention",
        "tianming_snapshot",
        "causal_debt",
        "anchor_status",
        "replacement_anchor_candidates",
        "meme_contamination",
        "consequence_state",
        "continuation_inputs",
    }
    return {key: value.get(key) for key in wanted if key in value}


def _public_llm_decision(
    item: _LLMDecisionItem,
    *,
    generated_by: str,
) -> dict[str, Any]:
    return {
        "status": "ready",
        "generated_by": generated_by,
        "character_id": _text(item.character_id),
        "belief_update": _text(item.belief_update),
        "visible_action": _text(item.visible_action),
        "true_intent": _text(item.true_intent),
        "expected_outcome": _text(item.expected_outcome),
        "risk": _text(item.risk),
        "deception_strategy": _text(item.deception_strategy),
        "propagation_choice": _text(item.propagation_choice),
        "resistance_choice": _text(item.resistance_choice),
        "situational_judgement": _text(item.situational_judgement),
        "trust_shift": _text(item.trust_shift),
        "memory_seed": [_text(seed) for seed in item.memory_seed if _text(seed)][:3],
    }


def _overlay_action_with_llm_decision(
    action: dict[str, Any],
    decision: dict[str, Any],
) -> None:
    baseline = {
        "decision_mode": action.get("decision_mode"),
        "visible_action": action.get("visible_action"),
        "true_intent": action.get("true_intent"),
        "expected_outcome": action.get("expected_outcome"),
        "risk": action.get("risk"),
    }
    action["decision_mode"] = "llm_agent_decision_advisory"
    action["llm_decision_advisory"] = {
        **decision,
        "deterministic_baseline": baseline,
    }
    for field in ("visible_action", "true_intent", "expected_outcome", "risk"):
        if decision.get(field):
            action[field] = decision[field]
    if decision.get("visible_action"):
        action["action"] = decision["visible_action"]
    if decision.get("trust_shift"):
        action["relationship_delta"] = decision["trust_shift"]
    seeds = _list_text(decision.get("memory_seed"))
    if seeds:
        seed = action.get("memory_seed") if isinstance(action.get("memory_seed"), dict) else {}
        seed["inferred"] = seeds
        action["memory_seed"] = seed
    if decision.get("belief_update"):
        action["memory_influence"] = decision["belief_update"]
    action["reason"] = (
        f"{action.get('reason') or ''} 模型决策建议："
        f"{decision.get('situational_judgement') or decision.get('belief_update') or '本轮已改用角色临场判断。'}"
    ).strip()


def _sandbox_boundaries(decision_advisory: dict[str, Any]) -> list[str]:
    boundaries = [
        "本轮只写 sandbox_rounds.jsonl 和 sandbox_summary.json。",
        "不调用 run_scene，不覆盖 chapter.md、events.json、state_snapshot.json。",
    ]
    if decision_advisory.get("status") == "skipped":
        boundaries.append("不调用外部模型、GraphRAG、Zep、向量库或 reranker。")
    elif decision_advisory.get("generated_by") == "real_llm":
        boundaries.append(
            "已显式启用真实 LLM 决策建议；失败会保留 deterministic 行动。"
        )
    else:
        boundaries.append("LLM 决策建议未调用真实外部模型，已保留可降级边界。")
    return boundaries


def _safe_error_text(exc: Exception) -> str:
    text = str(exc).strip() or exc.__class__.__name__
    return text[:180]


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
    psychology = _subjective_memory_psychology(round_record, action, new_belief)
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
        "decision_mode": action.get("decision_mode") or "",
        "decision_inputs": action.get("decision_inputs") or {},
        "visible_action": action.get("visible_action") or action.get("action") or "",
        "true_intent": action.get("true_intent") or "",
        "expected_outcome": action.get("expected_outcome") or "",
        "risk": action.get("risk") or "",
        "memory_influence": action.get("memory_influence") or "",
        "action_outcome": action.get("action_outcome") or {},
        "higher_dimensional_awareness": (
            action.get("awareness", {}).get("belief_payload")
            if isinstance(action.get("awareness"), dict)
            else ""
        ),
        "fate_mark": action.get("fate_mark") or {"status": "inactive"},
        "resistance_behavior": action.get("resistance_behavior") or {},
        "meme_contamination": action.get("meme_contamination") or {"status": "none"},
        "meme_propagation": action.get("meme_propagation") or {"status": "none"},
        "llm_decision_advisory": action.get("llm_decision_advisory") or {},
        **psychology,
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


def _subjective_memory_psychology(
    round_record: dict[str, Any],
    action: dict[str, Any],
    new_belief: str,
) -> dict[str, Any]:
    character_name = _text(action.get("character_name")) or "该角色"
    character_id = _text(action.get("character_id"))
    event = _event_hint(str(round_record.get("major_event") or ""))
    participants = [
        _text(item.get("character_name"))
        for item in round_record.get("character_actions", [])
        if isinstance(item, dict) and _text(item.get("character_id")) != character_id
    ]
    other = participants[0] if participants else "另一名角色"
    known_information = _list_text(action.get("known_information"))
    perspective_index = _perspective_index(character_id)
    perceived_event_options = [
        f"{character_name}认为“{event}”是有人故意留下破绽，目的在于逼自己表态。",
        f"{character_name}认为“{event}”更像{other}布下的试探，真正线索被遮住了。",
        f"{character_name}认为“{event}”不是失控事故，而是旧秩序借机清洗证人。",
        f"{character_name}认为“{event}”只是表层动静，真正危险藏在沉默的人身上。",
    ]
    inferred_motive_options = [
        f"{other}可能想借物证嫁祸，迫使{character_name}提前暴露立场。",
        f"{other}可能在保护某个秘密，因此故意让线索看起来指向自己。",
        "幕后势力可能利用半真半假的证据切断角色之间的信任。",
        f"{character_name}可能误把天命压力当成私人背叛信号。",
    ]
    secret_visibility = ["hidden", "partial", "exposed", "partial"][
        perspective_index % 4
    ]
    misbelief = (
        f"{character_name}误以为{other}已经掌握“{event}”的关键证据"
        if perspective_index % 2 == 0
        else f"{character_name}误以为{other}正在故意遮掩“{event}”的真正动机"
    )
    return {
        "perceived_event": perceived_event_options[perspective_index % len(perceived_event_options)],
        "inner_thought": (
            f"{character_name}把本轮外在行动和真实意图分开："
            f"{_text(action.get('true_intent')) or new_belief}"
        ),
        "inferred_motive": inferred_motive_options[
            perspective_index % len(inferred_motive_options)
        ],
        "emotional_impact": _emotional_impact(action, perspective_index),
        "trust_shift": _text(action.get("relationship_delta"))
        or "信任关系出现轻微偏移",
        "anomaly_weight": _memory_anomaly_weight(action, perspective_index),
        "secret_visibility": secret_visibility,
        "known_truths": known_information[:3],
        "misbeliefs": [misbelief],
        "unknown_canon_facts": [
            f"谁真正触发了“{event}”仍未被{character_name}确认",
            f"{other}的真实意图并未进入{character_name}的视野",
        ],
        "suppressed_memory": (
            "暂时压下对旧案的联想，以免影响当前判断"
            if perspective_index % 2 == 0
            else "把对同伴的不信任藏在礼貌行动之后"
        ),
        "worldline_residue": (
            "轻微既视感：此事像是另一条世界线残留的回声"
            if perspective_index % 3 == 0
            else "暂无明确世界线残影"
        ),
        "awareness_level": _memory_awareness_level(action, perspective_index),
    }


def _memory_anomaly_weight(action: dict[str, Any], perspective_index: int) -> int:
    awareness = action.get("awareness") if isinstance(action.get("awareness"), dict) else {}
    if awareness.get("level") == "L5":
        return 10
    if awareness.get("level") == "contaminated":
        propagation = (
            action.get("meme_propagation")
            if isinstance(action.get("meme_propagation"), dict)
            else {}
        )
        believed = propagation.get("belief_decision") == "accepted"
        return 9 if believed else 8
    return min(9, 3 + perspective_index)


def _memory_awareness_level(action: dict[str, Any], perspective_index: int) -> str:
    awareness = action.get("awareness") if isinstance(action.get("awareness"), dict) else {}
    level = _text(awareness.get("level"))
    if level:
        return level
    return "ordinary" if perspective_index < 3 else "uneasy"


def _perspective_index(character_id: str) -> int:
    text = character_id or "character"
    return sum(ord(char) for char in text) % 4


def _emotional_impact(action: dict[str, Any], perspective_index: int) -> str:
    base = _text(action.get("emotion_delta")) or "情绪被扰动"
    impacts = ["戒备加深", "信任松动", "羞惭转为试探", "恐惧被压成冷静"]
    return f"{base}；{impacts[perspective_index % len(impacts)]}"


def _load_tianming_pressure(story_path: Path) -> dict[str, Any]:
    raw = _read_optional_json(story_path / "tianming.json")
    pressure = raw.get("contract_pressure") if isinstance(raw, dict) else {}
    if not isinstance(pressure, dict):
        pressure = {}
    drivers = pressure.get("drivers")
    return {
        "level": _text(pressure.get("level")) or "unconfirmed",
        "score": pressure.get("score") if isinstance(pressure.get("score"), int) else 0,
        "drivers": [item for item in _list_text(drivers) if item],
        "status": _text(raw.get("status")) if isinstance(raw, dict) else "",
    }


def _tianming_pressure_text(pressure: dict[str, Any]) -> str:
    level = _text(pressure.get("level")) or "unconfirmed"
    score = pressure.get("score") if isinstance(pressure.get("score"), int) else 0
    drivers = _list_text(pressure.get("drivers"))
    if drivers:
        return f"《天命书》压力 {level}/{score}：{drivers[0]}"
    return f"《天命书》压力 {level}/{score}：尚未确认，角色先按私心与记忆行动"


def _build_intervention_constraint(
    *,
    story_slug: str,
    worldline_id: str,
    content: str,
    target: str,
    projection_mode: str,
    raw_constraint: dict[str, Any] | None,
    projects_dir: Path | None,
) -> dict[str, Any]:
    if isinstance(raw_constraint, dict) and raw_constraint:
        normalized = dict(raw_constraint)
        normalized.setdefault("status", "active")
        normalized.setdefault("source", "provided_intervention_constraint")
        return normalized
    text = " ".join(str(content or "").split())
    if not text:
        return {"status": "none", "source": "none", "content": "", "target": ""}
    try:
        compiled = compile_intervention_against_tianming(
            story_slug,
            content=text,
            target=target,
            worldline_id=worldline_id,
            projection_mode=projection_mode,
            projects_dir=projects_dir,
        )
    except TianmingInterventionCompilerRequestError as exc:
        raise WorldSandboxRequestError(str(exc)) from exc
    return {
        "status": "active",
        "source": "tianming_intervention_compile",
        "content": compiled.get("content") or text,
        "target": compiled.get("target") or "",
        "projection_mode": compiled.get("projection_mode") or projection_mode,
        "intervention_type": compiled.get("intervention_type") or "",
        "intervention_level": compiled.get("intervention_level") or "",
        "compatibility": compiled.get("compatibility") or {},
        "translation_strategy": compiled.get("translation_strategy") or {},
        "worldline_judgement": compiled.get("worldline_judgement") or {},
        "branch_axis": compiled.get("branch_axis") or {},
        "causal_debt": compiled.get("causal_debt") or {},
        "tianming": compiled.get("tianming") or {},
        "worldline_tianming_snapshot": compiled.get("worldline_tianming_snapshot"),
        "boundaries": [
            "本约束来自《天命书》干预编译结果。",
            "它只影响本次沙盘轮次，不覆盖根 tianming.json。",
            "普通干预进入 Divergent Worldline；L4/L5/AU 仍需单独确认快照。",
        ],
    }


def _constraint_from_worldline_state(state: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(state, dict):
        return {"status": "none", "source": "none", "content": "", "target": ""}
    source = state.get("source_intervention")
    if not isinstance(source, dict) or source.get("status") != "active":
        return {"status": "none", "source": "none", "content": "", "target": ""}
    return {
        "status": "active",
        "source": "worldline_state",
        "content": source.get("content") or "",
        "target": source.get("target") or "",
        "projection_mode": source.get("projection_mode") or "immersive",
        "intervention_level": source.get("intervention_level") or "",
        "branch_axis": source.get("branch_axis") or {},
        "causal_debt": source.get("causal_debt") or {},
        "worldline_tianming_snapshot": (
            {
                "artifact": state.get("tianming_snapshot", {}).get("artifact"),
                "status": state.get("tianming_snapshot", {}).get("status"),
                "requires_confirmation": state.get("tianming_snapshot", {}).get(
                    "requires_confirmation"
                ),
            }
            if isinstance(state.get("tianming_snapshot"), dict)
            and state.get("tianming_snapshot", {}).get("artifact")
            else None
        ),
        "persisted_worldline_state": {
            "artifact": state.get("artifact") or "",
            "tianming_snapshot_audit": state.get("tianming_snapshot", {}).get(
                "audit_status"
            )
            if isinstance(state.get("tianming_snapshot"), dict)
            else "",
            "causal_debt": state.get("causal_debt") or {},
            "branch_state": state.get("branch_state") or {},
            "consequence_state": state.get("consequence_state") or {},
        },
        "boundaries": [
            "本约束来自可继续运行的 worldline_state.json。",
            "后续沙盘轮次会持续读取干预、快照审计状态、因果债、分支状态和具象代偿。",
        ],
    }


def _worldline_decision_inputs(state: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(state, dict) or state.get("status") == "new":
        return {
            "worldline_intervention_memory": "",
            "worldline_tianming_snapshot_audit": "",
            "worldline_causal_debt": "",
            "branch_continuation_status": "",
            "worldline_consequences": "",
        }
    source = state.get("source_intervention") if isinstance(state.get("source_intervention"), dict) else {}
    snapshot = state.get("tianming_snapshot") if isinstance(state.get("tianming_snapshot"), dict) else {}
    debt = state.get("causal_debt") if isinstance(state.get("causal_debt"), dict) else {}
    branch = state.get("branch_state") if isinstance(state.get("branch_state"), dict) else {}
    consequence = (
        state.get("consequence_state")
        if isinstance(state.get("consequence_state"), dict)
        else {}
    )
    return {
        "worldline_intervention_memory": _text(source.get("content")),
        "worldline_tianming_snapshot_audit": _text(snapshot.get("audit_status")),
        "worldline_causal_debt": f"{debt.get('level', '')}/{debt.get('score', 0)}",
        "branch_continuation_status": _text(branch.get("continuation_status")),
        "worldline_consequences": _consequence_input_text(consequence),
    }


def _consequence_input_text(consequence: dict[str, Any]) -> str:
    if not isinstance(consequence, dict) or consequence.get("status") != "active":
        return ""
    summary = _text(consequence.get("summary"))
    if summary:
        return summary
    domains = consequence.get("domains")
    if not isinstance(domains, dict):
        return ""
    parts = []
    for key in ("location", "resource", "injury", "public_opinion", "faction", "environment"):
        value = domains.get(key)
        if isinstance(value, dict) and value.get("current"):
            parts.append(_text(value.get("current")))
    return "；".join(part for part in parts if part)


def _awareness_signal(
    *,
    character_id: str,
    index: int,
    intervention_constraint: dict[str, Any],
    worldline_state: dict[str, Any],
) -> dict[str, Any]:
    text = _text(intervention_constraint.get("content"))
    target = _text(intervention_constraint.get("target"))
    prior = (
        worldline_state.get("meme_contamination")
        if isinstance(worldline_state.get("meme_contamination"), dict)
        else {}
    )
    tokens = ("小说人物", "高维", "读者", "作者", "操控", "大纲")
    l5 = (
        any(token in text for token in tokens)
        or _text(intervention_constraint.get("intervention_level")) == "L5"
        or prior.get("status") == "active"
    )
    if not l5:
        return {"level": "ordinary", "abnormality": ""}
    direct = not target or target == character_id or index == 0
    return {
        "level": "L5" if direct else "contaminated",
        "abnormality": "意识到自己可能是小说人物，命运正在被高维读者或作者触碰。",
        "belief_payload": "我是小说人物，读者正在高维操控我。",
        "direct_target": direct,
    }


def _resistance_behavior(name: str, index: int) -> dict[str, str]:
    options = [
        ("false_compliance", "假意服从", f"{name}表面按命运线行动，暗中把读者给的信息拆成诱饵。"),
        ("refusal", "拒绝", f"{name}拒绝把高维命令当作真理，宁愿让主线暂时失速。"),
        ("deceive_reader", "欺骗读者", f"{name}故意做出顺从姿态，诱使读者误判自己的下一步。"),
        ("protect_others", "保护他人", f"{name}把高维真相藏起来，避免同伴被异常感拖垮。"),
        ("continue_mission", "继续使命", f"{name}承认世界异常，但仍选择完成自己的旧使命。"),
        ("nihilism", "虚无", f"{name}短暂怀疑一切选择是否有意义，行动变得危险而冷静。"),
    ]
    kind, label, description = options[index % len(options)]
    return {"type": kind, "label": label, "description": description}


def _meme_contamination(
    name: str,
    character_id: str,
    awareness: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status": "active",
        "source_character_id": character_id,
        "belief_payload": awareness.get("belief_payload") or "世界可能被高维叙事操控。",
        "spread_vector": [
            f"{name}的异常言行",
            "梦兆、密信与同伴的误读",
            "关系网中关于高维真相的传闻",
        ],
    }


def _apply_meme_propagation(
    actions: list[dict[str, Any]],
    previous_memories: dict[str, dict[str, Any]],
) -> None:
    source = next(
        (
            action
            for action in actions
            if isinstance(action.get("meme_contamination"), dict)
            and action["meme_contamination"].get("status") == "active"
            and isinstance(action.get("awareness"), dict)
            and action["awareness"].get("level") == "L5"
        ),
        None,
    )
    if not source:
        return
    meme = source.get("meme_contamination") or {}
    source_reaction = source.get("resistance_behavior") or _resistance_behavior(
        _text(source.get("character_name")) or "觉醒者",
        0,
    )
    source["meme_propagation"] = {
        "status": "source",
        "source_character_id": source.get("character_id") or "",
        "source_character_name": source.get("character_name") or "",
        "belief_payload": meme.get("belief_payload") or "我是小说人物，读者正在高维操控我。",
        "belief_decision": "accepted",
        "belief_reason": "亲历命痕觉醒，已把高维真相写入主观记忆。",
        "credibility_score": 10,
        "source_channel": "命痕、异常言行与刻意留下的破绽",
        "signals": {
            "persona": "亲历高维干预",
            "relationship": "向关系网投放试探",
            "previous_memory": source.get("previous_subjective_memory") or "本轮首次觉醒",
            "anomaly": source.get("awareness", {}).get("abnormality") or "",
        },
        "reaction": source_reaction,
    }
    for idx, action in enumerate(actions):
        if action is source:
            continue
        character_id = _text(action.get("character_id"))
        name = _text(action.get("character_name")) or character_id
        inputs = action.get("decision_inputs") if isinstance(action.get("decision_inputs"), dict) else {}
        previous = previous_memories.get(character_id) or {}
        propagation = _meme_propagation_record(
            action=action,
            source=source,
            meme=meme,
            previous_memory=previous,
            ordinal=idx,
        )
        reaction = propagation["reaction"]
        action["meme_propagation"] = propagation
        action["awareness"] = {
            "level": "contaminated",
            "abnormality": "听见高维真相后，开始怀疑自身命运被读者或作者触碰。",
            "belief_payload": propagation["belief_payload"],
            "direct_target": False,
        }
        action["resistance_behavior"] = reaction
        action["fate_mark"] = {
            "status": "suspected" if propagation["belief_decision"] != "accepted" else "active",
            "label": "命痕回声",
            "description": f"{name}从{source.get('character_name')}处接触高维真相。",
            "source_character_id": source.get("character_id") or "",
            "belief_decision": propagation["belief_decision"],
        }
        action["known_information"].append(
            f"模因来源：{source.get('character_name')}传来“{propagation['belief_payload']}”"
        )
        inputs["meme_source"] = source.get("character_id") or ""
        inputs["meme_belief_decision"] = propagation["belief_decision"]
        inputs["meme_credibility_score"] = propagation["credibility_score"]
        inputs["meme_reaction"] = reaction.get("label") or ""


def _meme_propagation_record(
    *,
    action: dict[str, Any],
    source: dict[str, Any],
    meme: dict[str, Any],
    previous_memory: dict[str, Any],
    ordinal: int,
) -> dict[str, Any]:
    character_id = _text(action.get("character_id"))
    name = _text(action.get("character_name")) or character_id
    inputs = action.get("decision_inputs") if isinstance(action.get("decision_inputs"), dict) else {}
    persona_signal = _text(inputs.get("desire")) or "保住自身主动权"
    relationship_signal = _text(inputs.get("relationship_signal")) or "关系信号缺失"
    previous_signal = _previous_memory_reference(previous_memory)
    anomaly_signal = _text(previous_memory.get("anomaly_delta")) or _text(action.get("risk")) or "本轮异常刚出现"
    score = 4 + (ordinal % 3)
    if "信任" in relationship_signal or "牵动" in relationship_signal:
        score += 1
    if previous_memory:
        score += 1
    if "异常" in anomaly_signal or "高维" in anomaly_signal:
        score += 1
    score = min(10, score)
    decision = "accepted" if ordinal % 2 == 1 else "doubted"
    if score <= 4:
        decision = "rejected"
    reaction_index = [3, 5, 2, 0, 4][ordinal % 5]
    reaction = _resistance_behavior(name, reaction_index)
    return {
        "status": "received",
        "source_character_id": source.get("character_id") or "",
        "source_character_name": source.get("character_name") or "",
        "belief_payload": meme.get("belief_payload") or "世界可能被高维叙事操控。",
        "source_channel": "异常言行、密信和关系网耳语",
        "belief_decision": decision,
        "belief_reason": _meme_belief_reason(name, decision, persona_signal, relationship_signal, anomaly_signal),
        "credibility_score": score,
        "signals": {
            "persona": persona_signal,
            "relationship": relationship_signal,
            "previous_memory": previous_signal,
            "anomaly": anomaly_signal,
        },
        "reaction": reaction,
    }


def _meme_belief_reason(
    name: str,
    decision: str,
    persona_signal: str,
    relationship_signal: str,
    anomaly_signal: str,
) -> str:
    if decision == "accepted":
        return (
            f"{name}把自身欲望“{persona_signal}”、关系信号“{relationship_signal}”"
            f"和异常感“{anomaly_signal}”合在一起，暂时采信高维真相。"
        )
    if decision == "doubted":
        return (
            f"{name}承认异常感存在，但仍怀疑这可能是同伴或世界线制造的心理诱饵。"
        )
    return f"{name}把高维真相视为危险谣言，只记录来源，不让它接管行动。"


def _intervention_constraint_text(constraint: dict[str, Any]) -> str:
    if not isinstance(constraint, dict) or constraint.get("status") != "active":
        return ""
    content = _text(constraint.get("content"))
    strategy = constraint.get("translation_strategy")
    branch = constraint.get("branch_axis")
    strategy_text = ""
    axis = ""
    if isinstance(strategy, dict):
        strategy_text = _text(strategy.get("strategy"))
    if isinstance(branch, dict):
        axis = _text(branch.get("axis"))
    parts = [part for part in (content, strategy_text, axis) if part]
    return "；".join(parts)


def _intervention_branch_axis(constraint: dict[str, Any]) -> str:
    if not isinstance(constraint, dict) or constraint.get("status") != "active":
        return ""
    branch = constraint.get("branch_axis")
    if isinstance(branch, dict):
        return _text(branch.get("axis"))
    return ""


def _intervention_causal_debt_text(constraint: dict[str, Any]) -> str:
    if not isinstance(constraint, dict) or constraint.get("status") != "active":
        return ""
    debt = constraint.get("causal_debt")
    if not isinstance(debt, dict):
        return ""
    level = _text(debt.get("level")) or "medium"
    score = debt.get("score") if isinstance(debt.get("score"), int) else 0
    spread = _list_text(debt.get("spread"))
    suffix = f"：{spread[0]}" if spread else ""
    return f"干预因果债 {level}/{score}{suffix}"


def _relationship_signal(character: dict[str, Any]) -> str:
    relationships = character.get("relationships")
    if isinstance(relationships, list) and relationships:
        sample = _text(relationships[0])
        if sample:
            return f"已知关系牵动：{sample}"
        return f"关系网数量：{len(relationships)}"
    return "关系网缺口：只能临场判断同场角色"


def _secret_signal(character: dict[str, Any], index: int) -> str:
    secrets = character.get("secrets")
    if isinstance(secrets, list) and secrets:
        sample = _text(secrets[0])
        if sample:
            return f"可隐藏秘密：{sample}"
        return f"秘密数量：{len(secrets)}"
    fallback = ["隐瞒真实判断", "保留旧案线索", "试探匿名消息来源"]
    return fallback[index % len(fallback)]


def _resource_signal(character: dict[str, Any]) -> str:
    state = (
        character.get("current_state")
        if isinstance(character.get("current_state"), dict)
        else {}
    )
    resources = state.get("resources")
    if isinstance(resources, list) and resources:
        return f"可动用资源：{_text(resources[0]) or len(resources)}"
    resource_count = state.get("resource_count")
    if isinstance(resource_count, int) and resource_count > 0:
        return f"可动用资源数量：{resource_count}"
    return "资源紧张：只能使用情报、关系或误导"


def _deterministic_decision(
    *,
    name: str,
    location: str,
    target_hint: str,
    base_posture: str,
    index: int,
    previous_belief: str,
    previous_anomaly: str,
    pressure_text: str,
    intervention_text: str,
    intervention_axis: str,
    awareness: dict[str, Any],
) -> dict[str, Any]:
    has_memory = bool(previous_belief or previous_anomaly)
    has_intervention = bool(intervention_text)
    if awareness.get("level") == "L5":
        return {
            "stance": "假意服从",
            "visible_action": (
                f"{name}在{location}假意服从命运，把“{target_hint}”当作正常线索处理，"
                "却故意留下一个只有同伴能看懂的破绽。"
            ),
            "true_intent": (
                f"{name}意识到自己可能是小说人物，不再把高维指令当作真理，"
                "而是试图保护同伴并反向欺骗读者。"
            ),
            "expected_outcome": "让世界以为锚点仍在前进，同时给角色保留反抗和自救空间。",
            "risk": "高维真相会污染关系网，其他角色可能把异常感误读为背叛或疯癫。",
            "relationship_delta": "表面顺从，暗中保护同伴，信任关系进入异常压力",
            "new_belief": f"{name}把“我是小说人物/被高维操控”的认知藏进主观记忆。",
            "action_outcome": {
                "status": "misjudged",
                "reason": "角色没有机械服从高维干预，而是把干预转化为反抗策略。",
                "cost": "命痕激活，模因污染开始沿关系网传播。",
            },
        }
    if not has_memory:
        if has_intervention:
            axis = intervention_axis or "干预变量"
            return {
                "stance": "转译干预",
                "visible_action": (
                    f"{name}在{location}{base_posture}，把“{intervention_text}”当作"
                    f"{axis}的一枚密信，先试探其真假。"
                ),
                "true_intent": (
                    f"{name}不直接服从干预，而是借“{target_hint}”观察谁会抢先响应。"
                ),
                "expected_outcome": "让干预成为世界内可怀疑、可传播、可误读的变量。",
                "risk": "密信来源不明，可能诱发错误结盟或反向钓鱼。",
                "relationship_delta": "因干预线索开始试探关键关系",
                "new_belief": f"{name}认为外来线索需要先被本土化验证，不能直接当作正史。",
                "action_outcome": {
                    "status": "misjudged",
                    "reason": "干预已进入沙盘，但角色只把它当作可疑线索而非绝对命令。",
                    "cost": "信息差扩大，因果债开始压向收到线索的人。",
                },
            }
        return {
            "stance": base_posture,
            "visible_action": f"{name}在{location}{base_posture}，围绕“{target_hint}”调整下一步。",
            "true_intent": f"{name}仍在确认事件是否会牵动自己。",
            "expected_outcome": "先取得局势解释权，再决定是否扩大行动。",
            "risk": "信息不足，容易被后来者反向利用。",
            "relationship_delta": "开始重新评估同场角色的可靠性",
            "new_belief": f"{name}认为这不是孤立事件，而是世界大势的开端。",
            "action_outcome": {
                "status": "succeeded",
                "reason": "第一轮只建立试探性位置，尚未遭遇记忆反噬。",
                "cost": "暴露了自己关注此事。",
            },
        }

    tactics = [
        {
            "stance": "假意服从",
            "status": "succeeded",
            "risk": "若被识破，会被视为两面下注。",
            "relationship_delta": "表面顺从，暗中降低对同场角色的信任",
        },
        {
            "stance": "隐瞒",
            "status": "succeeded",
            "risk": "信息被压住后，误会会向关系链扩散。",
            "relationship_delta": "选择隐瞒关键判断，关系信任开始裂开",
        },
        {
            "stance": "试探结盟",
            "status": "misjudged",
            "risk": "把上一轮异常误读成同盟信号，可能引错人入局。",
            "relationship_delta": "向可疑对象释放善意，但判断并不稳定",
        },
        {
            "stance": "背叛旧约",
            "status": "failed",
            "risk": "旧约反噬会把个人选择变成公开冲突。",
            "relationship_delta": "为了自保牺牲旧关系，引发公开裂痕",
        },
    ]
    tactic = tactics[index % len(tactics)]
    visible_action = (
        f"{name}在{location}{tactic['stance']}：表面回应“{target_hint}”，"
        "却把上一轮异常感作为本轮行动前提。"
    )
    true_intent = (
        f"{name}真正想验证上一轮判断“{previous_belief or previous_anomaly}”是否被人利用，"
        f"并在{pressure_text}下保住退路。"
    )
    if has_intervention:
        visible_action += f" 同时将干预线索包装成“{intervention_axis or '分支变量'}”暗中投放。"
        true_intent += f" 还要判断外来干预“{intervention_text}”能否被自己反向利用。"
    return {
        "stance": tactic["stance"],
        "visible_action": visible_action,
        "true_intent": true_intent,
        "expected_outcome": "让旁人误判自己的立场，同时观察匿名消息和旧秩序的反应。",
        "risk": tactic["risk"],
        "relationship_delta": tactic["relationship_delta"],
        "new_belief": (
            f"{name}把上一轮记忆转化为行动策略：{tactic['stance']}可能比直面真相更安全。"
        ),
        "action_outcome": {
            "status": tactic["status"],
            "reason": (
                "行动受上一轮主观记忆、异常感、天命压力"
                + ("和已投放干预共同牵引。" if has_intervention else "共同牵引。")
            ),
            "cost": "因果债增加，至少一段关系开始带着误会运转。",
        },
    }


def _conflicts(actions: list[dict[str, Any]], major_event: str) -> list[dict[str, Any]]:
    if len(actions) < 2:
        return []
    first = actions[0]
    second = actions[1]
    first_inputs = (
        first.get("decision_inputs") if isinstance(first.get("decision_inputs"), dict) else {}
    )
    previous_misbelief = _text(first_inputs.get("previous_misbelief"))
    intervention_axis = _text(first_inputs.get("intervention_branch_axis"))
    cause = (
        f"上一轮误会“{previous_misbelief}”继续影响本轮判断，"
        f"同一大事件“{_event_hint(major_event)}”被推向互相试探。"
        if previous_misbelief
        else f"同一大事件“{_event_hint(major_event)}”被不同角色解释成不同机会。"
    )
    if intervention_axis:
        cause += f" 已投放干预把冲突推向“{intervention_axis}”。"
    return [
        {
            "id": "conflict_1",
            "title": "消息封锁与主动试探冲突",
            "participants": [
                first["character_id"],
                second["character_id"],
            ],
            "cause": cause,
            "pressure": "中",
        }
    ]


def _information_flow(
    actions: list[dict[str, Any]], major_event: str
) -> list[dict[str, Any]]:
    rows = [
        {
            "type": "world_event",
            "from": "world_event",
            "to": action["character_id"],
            "content": _event_hint(major_event),
            "distortion": action["stance"],
        }
        for action in actions
    ]
    first_inputs = (
        actions[0].get("decision_inputs")
        if actions and isinstance(actions[0].get("decision_inputs"), dict)
        else {}
    )
    intervention_text = _text(first_inputs.get("intervention_constraint"))
    intervention_axis = _text(first_inputs.get("intervention_branch_axis"))
    if intervention_text:
        rows.append(
                {
                    "type": "reader_intervention",
                    "from": "reader_intervention",
                "to": first_inputs.get("intervention_target") or "worldline",
                "content": intervention_text,
                "distortion": intervention_axis or "本土化转译",
            }
        )
    for action in actions:
        meme = action.get("meme_contamination")
        if isinstance(meme, dict) and meme.get("status") == "active":
            rows.append(
                {
                    "type": "meme_contamination",
                    "from": action.get("character_id"),
                    "to": "relationship_network",
                    "content": meme.get("belief_payload") or "世界可能被高维操控。",
                    "distortion": "其他角色会按人设、记忆和关系决定是否相信。",
                }
            )
        propagation = action.get("meme_propagation")
        if isinstance(propagation, dict) and propagation.get("status") == "received":
            rows.append(
                {
                    "type": "meme_propagation",
                    "from": propagation.get("source_character_id") or "unknown",
                    "to": action.get("character_id"),
                    "content": propagation.get("belief_payload") or "世界可能被高维操控。",
                    "distortion": (
                        f"{propagation.get('belief_decision') or 'unknown'}："
                        f"{propagation.get('belief_reason') or '未记录采信原因'}"
                    ),
                }
            )
    return rows


def _world_state_delta(
    actions: list[dict[str, Any]], major_event: str, worldline_state: dict[str, Any]
) -> dict[str, Any]:
    first_inputs = (
        actions[0].get("decision_inputs")
        if actions and isinstance(actions[0].get("decision_inputs"), dict)
        else {}
    )
    intervention_text = _text(first_inputs.get("intervention_constraint"))
    intervention_axis = _text(first_inputs.get("intervention_branch_axis"))
    intervention_projection_mode = _text(first_inputs.get("intervention_projection_mode"))
    worldline_debt = _text(first_inputs.get("worldline_causal_debt"))
    continuation = _text(first_inputs.get("branch_continuation_status"))
    consequence_state = (
        worldline_state.get("consequence_state")
        if isinstance(worldline_state.get("consequence_state"), dict)
        else {}
    )
    meme_actions = [
        action
        for action in actions
        if isinstance(action.get("meme_contamination"), dict)
        and action["meme_contamination"].get("status") == "active"
    ]
    propagation_rows = [
        action["meme_propagation"]
        for action in actions
        if isinstance(action.get("meme_propagation"), dict)
        and action["meme_propagation"].get("status") in {"source", "received"}
    ]
    projection_effect = (
        "暴走 AU 已开启：异物入侵保留为异设世界线压力，并要求世界线《天命书》快照确认"
        if intervention_projection_mode == "wild_au"
        else "沉浸模式吸收：干预会被本土化转译为世界内变量"
    )
    intervention_effects = (
        [
            f"干预已作为“{intervention_axis or '分支变量'}”进入本轮角色判断",
            projection_effect,
            "本轮干预不覆盖根天命书",
        ]
        if intervention_text
        else []
    )
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
        "intervention_effects": intervention_effects,
        "branch_state": {
            "continuation_status": continuation or "runnable",
            "worldline_state_artifact": worldline_state.get("artifact", ""),
        },
        "compensation_effects": [
            f"因果债{worldline_debt or 'low/1'}先压向当前锚点，再外溢到关系网。",
            "候选天命承载者会因欲望、资源和阻力被推到台前或失败退场。",
        ],
        "consequence_state": (
            {
                "status": "active",
                "summary": _consequence_input_text(consequence_state),
                "domains": consequence_state.get("domains") or {},
                "next_round_hint": consequence_state.get("next_round_hint") or "",
            }
            if consequence_state.get("status") == "active"
            else {"status": "none", "summary": "", "domains": {}}
        ),
        "meme_contamination": (
            {
                "status": "active",
                "source_character_id": meme_actions[0].get("character_id"),
                "belief_payload": meme_actions[0]["meme_contamination"].get(
                    "belief_payload"
                ),
                "propagation": propagation_rows,
            }
            if meme_actions
            else {"status": "none"}
        ),
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
    intervention_constraint: dict[str, Any] | None = None,
    worldline_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    actions = [
        action
        for round_record in rounds
        for action in round_record.get("character_actions", [])
        if isinstance(action, dict)
    ]
    active_constraint = _active_intervention_constraint(rounds, intervention_constraint)
    decision_advisory = _active_llm_decision_advisory(rounds)
    artifacts = {
        "sandbox_rounds": _ROUNDS_ARTIFACT,
        "sandbox_summary": "sandbox_summary.json",
        "subjective_memory_delta": _SUBJECTIVE_MEMORY_DELTA_ARTIFACT,
    }
    if active_constraint.get("status") == "active":
        artifacts["intervention_constraint"] = _INTERVENTION_CONSTRAINT_ARTIFACT
    if decision_advisory.get("status") != "skipped":
        artifacts["agent_decision_advisory"] = _AGENT_DECISION_ADVISORY_ARTIFACT
    return {
        "version": VERSION,
        "mode": (
            "llm_agent_decision_advisory"
            if decision_advisory.get("status") != "skipped"
            else "deterministic_world_sandbox_round"
        ),
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
            "llm_decision_status": decision_advisory.get("status") or "skipped",
            "llm_decision_action_count": int(
                decision_advisory.get("action_count") or 0
            ),
            "llm_decision_generated_by": decision_advisory.get("generated_by") or "",
            "external_services_required": bool(
                decision_advisory.get("requested")
                and not decision_advisory.get("mock")
                and decision_advisory.get("status") != "skipped"
            ),
            "run_scene_default_unchanged": True,
        },
        "artifacts": artifacts,
        "intervention_constraint": active_constraint,
        "worldline_state": worldline_state or {},
        "rounds": rounds,
        "subjective_memory_delta": subjective_memory_delta or {},
        "next_steps": [
            "下一刀让 UI 从主观记忆链渲染角色个人卷。",
            "再把《天命书》作为干预编译与沙盘轮次的世界宪法输入。",
        ],
    }


def _active_intervention_constraint(
    rounds: list[dict[str, Any]],
    explicit: dict[str, Any] | None,
) -> dict[str, Any]:
    if isinstance(explicit, dict) and explicit.get("status") == "active":
        return explicit
    for round_record in rounds:
        if not isinstance(round_record, dict):
            continue
        constraint = round_record.get("intervention_constraint")
        if isinstance(constraint, dict) and constraint.get("status") == "active":
            return constraint
    return {"status": "none", "source": "none", "content": "", "target": ""}


def _active_llm_decision_advisory(rounds: list[dict[str, Any]]) -> dict[str, Any]:
    for round_record in rounds:
        if not isinstance(round_record, dict):
            continue
        advisory = round_record.get("llm_decision_advisory")
        if isinstance(advisory, dict):
            return advisory
    return {"status": "skipped", "mode": "deterministic", "requested": False}


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

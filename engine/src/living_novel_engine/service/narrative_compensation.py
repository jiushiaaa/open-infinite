"""World Sandbox Loop v5: local narrative compensation."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.tianming import get_tianming_book

VERSION = "narrative-compensation-v1"
ARTIFACT = "tianming_delta.json"


class NarrativeCompensationRequestError(ValueError):
    """Invalid narrative compensation request."""


def run_narrative_compensation(
    story_slug: str,
    *,
    trigger_event: str,
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
    worldline_id: str = "main",
) -> dict[str, Any]:
    """Generate a local Tianming delta explaining worldline compensation."""

    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")
    event = " ".join(str(trigger_event or "").split())
    if not event:
        raise NarrativeCompensationRequestError("缺少 trigger_event（代偿触发事件）")
    book = get_tianming_book(sid, projects_dir=projects_dir)
    run_id = _new_run_id()
    run_dir = (outputs_dir or default_outputs_dir()) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    delta = _build_delta(
        story_slug=sid,
        worldline_id=wid,
        run_id=run_id,
        trigger_event=event,
        book=book,
    )
    (run_dir / ARTIFACT).write_text(
        json.dumps(delta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / "compensation_report.json").write_text(
        json.dumps(delta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return delta


def _build_delta(
    *,
    story_slug: str,
    worldline_id: str,
    run_id: str,
    trigger_event: str,
    book: dict[str, Any],
) -> dict[str, Any]:
    candidates = [
        row
        for row in book.get("replacement_anchor_candidates", [])
        if isinstance(row, dict)
    ]
    status = _anchor_status(trigger_event)
    next_candidate = _next_candidate(candidates)
    debt = _causal_debt_diffusion(trigger_event, status, book)
    return {
        "version": VERSION,
        "artifact": ARTIFACT,
        "run_id": run_id,
        "story_slug": story_slug,
        "worldline_id": worldline_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "trigger_event": trigger_event,
        "source_tianming": {
            "artifact": book.get("artifact") or "tianming.json",
            "status": book.get("status") or "draft",
            "anchor_status": book.get("anchor_status") or {},
            "contract_pressure": book.get("contract_pressure") or {},
        },
        "anchor_transfer": {
            "status": status,
            "current_anchor": (book.get("anchor_status") or {}).get("current_anchor_name"),
            "next_anchor_candidate": next_candidate,
            "reason": _anchor_reason(status, trigger_event, next_candidate),
        },
        "replacement_anchor_candidates": _scored_candidates(candidates, trigger_event),
        "causal_debt_diffusion": debt,
        "world_pressure_events": _world_pressure_events(trigger_event, status, debt),
        "boundaries": [
            "代偿压力必须通过世界内政治、关系、势力或环境自然涌现。",
            "不做系统管理员式抹杀，不直接覆盖 tianming.json。",
            "本报告只写 tianming_delta.json，不调用 run_scene。",
        ],
        "next_steps": [
            "让世界线页解释锚点转移和因果债扩散证据。",
            "后续世界自演可消费该 delta 作为检查点触发条件。",
        ],
    }


def _anchor_status(trigger_event: str) -> str:
    if any(token in trigger_event for token in ("死亡", "失去主锚点", "失锚")):
        return "unanchored"
    if any(token in trigger_event for token in ("拒绝", "摆烂", "离开", "觉醒")):
        return "transferring"
    return "stable"


def _next_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: int(row.get("anchor_fit") or 0), reverse=True)[0]


def _scored_candidates(
    candidates: list[dict[str, Any]],
    trigger_event: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, candidate in enumerate(candidates[:5], start=1):
        fit = int(candidate.get("anchor_fit") or max(1, 6 - idx))
        risk_text = str(candidate.get("risk") or "被世界压力吞没")
        rows.append(
            {
                "character_id": candidate.get("character_id") or f"candidate_{idx}",
                "character_name": candidate.get("character_name") or f"候选者 {idx}",
                "desire": candidate.get("desire") or "接住世界线压力",
                "ability_score": min(10, fit + 2),
                "resource_score": min(10, fit + 1),
                "risk_score": min(10, idx + (2 if "死亡" in trigger_event else 1)),
                "risk": risk_text,
                "reason": candidate.get("reason") or "拥有接替世界压力的叙事位置。",
            }
        )
    return rows


def _causal_debt_diffusion(
    trigger_event: str,
    status: str,
    book: dict[str, Any],
) -> dict[str, Any]:
    pressure = book.get("contract_pressure") if isinstance(book.get("contract_pressure"), dict) else {}
    base = 3
    if pressure.get("level") == "high":
        base += 2
    if status == "transferring":
        base += 2
    if status == "unanchored":
        base += 4
    if any(token in trigger_event for token in ("死亡", "永久", "失去")):
        base += 1
    level = "high" if base >= 7 else "medium" if base >= 4 else "low"
    return {
        "level": level,
        "score": base,
        "spread": [
            "角色信任关系重新排序",
            "势力开始争夺解释权",
            "环境或战事把选择代价推回角色身上",
        ]
        + (["主锚点暂时失效，候选承载者被迫浮现"] if status == "unanchored" else []),
    }


def _world_pressure_events(
    trigger_event: str,
    status: str,
    debt: dict[str, Any],
) -> list[dict[str, str]]:
    rows = [
        {
            "id": "pressure_relationship",
            "domain": "relationship",
            "mode": "natural_emergence",
            "event": "同伴开始质疑主锚点是否仍值得信任。",
            "evidence": trigger_event,
        },
        {
            "id": "pressure_faction",
            "domain": "faction",
            "mode": "natural_emergence",
            "event": "宗门和地方势力争夺风鸣铃事件的解释权。",
            "evidence": "天命书合约压力扩散。",
        },
        {
            "id": "pressure_environment",
            "domain": "environment",
            "mode": "natural_emergence",
            "event": "云城灵脉波动，把未偿还的因果债推回公开场域。",
            "evidence": f"因果债等级 {debt.get('level')}",
        },
    ]
    if status == "unanchored":
        rows.append(
            {
                "id": "pressure_politics",
                "domain": "politics",
                "mode": "natural_emergence",
                "event": "失锚消息引发城内权力真空，候选承载者被迫站到台前。",
                "evidence": "主锚点失效。",
            }
        )
    return rows


def _anchor_reason(
    status: str,
    trigger_event: str,
    candidate: dict[str, Any] | None,
) -> str:
    if status == "unanchored":
        name = candidate.get("character_name") if candidate else "候选者"
        return f"触发事件导致主锚点失效，世界压力会把{name}等候选承载者推到前台。"
    if status == "transferring":
        return "主锚点没有被抹杀，但拒绝/摆烂/离场会迫使世界压力向候选承载者分流。"
    return "主锚点仍稳定，代偿主要表现为关系和势力压力上升。"


def _new_run_id() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"compensation_{ts}_{uuid.uuid4().hex[:6]}"


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise NarrativeCompensationRequestError(f"{label} 无效")
    return checked

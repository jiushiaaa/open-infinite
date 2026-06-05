"""Compile free-form interventions against a local Tianming book."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.project_health import resolve_story_path
from living_novel_engine.service.tianming import get_tianming_book

VERSION = "tianming-intervention-compiler-v1"
PROJECTION_MODE_IMMERSIVE = "immersive"
PROJECTION_MODE_WILD_AU = "wild_au"
PROJECTION_MODES = {PROJECTION_MODE_IMMERSIVE, PROJECTION_MODE_WILD_AU}


class TianmingInterventionCompilerRequestError(ValueError):
    """Invalid Tianming intervention compiler request."""


def compile_intervention_against_tianming(
    story_slug: str,
    *,
    content: str,
    target: str = "",
    projects_dir: Path | None = None,
    worldline_id: str = "main",
    projection_mode: str = PROJECTION_MODE_IMMERSIVE,
) -> dict[str, Any]:
    """Read Tianming and compile one free-form intervention.

    This preflight intentionally does not run ``run_scene`` and does not mutate
    ``tianming.json``. It gives the product a Tianming-aware explanation before
    a reader intervention is projected into a worldline.
    """

    sid = _checked_id(story_slug, "story_slug")
    text = " ".join(str(content or "").split())
    if not text:
        raise TianmingInterventionCompilerRequestError("缺少 content（干预内容）")
    target_id = safe_id(str(target or "").strip()) or ""
    wid = _checked_id(worldline_id or "main", "worldline_id")
    mode = str(projection_mode or PROJECTION_MODE_IMMERSIVE).strip() or PROJECTION_MODE_IMMERSIVE
    if mode not in PROJECTION_MODES:
        raise TianmingInterventionCompilerRequestError("projection_mode 只能是 immersive 或 wild_au")
    book = get_tianming_book(sid, projects_dir=projects_dir)
    intervention_type = _classify_intervention(text)
    level = _level_for(intervention_type, text)
    compatibility = _compatibility(book, intervention_type, level, text, mode)
    judgement = _worldline_judgement(intervention_type, level, compatibility, mode)
    branch_axis = _branch_axis(intervention_type, target_id, text, judgement)
    causal_debt = _causal_debt(intervention_type, level, compatibility, book)
    snapshot = _write_worldline_snapshot(
        story_slug=sid,
        worldline_id=wid,
        content=text,
        target_id=target_id,
        level=level,
        judgement=judgement,
        compatibility=compatibility,
        causal_debt=causal_debt,
        book=book,
        projects_dir=projects_dir,
        projection_mode=mode,
    )
    requires_snapshot_audit = level in {"L4", "L5"} or judgement.get("kind") == "au"
    return {
        "version": VERSION,
        "story_slug": sid,
        "worldline_id": wid,
        "projection_mode": mode,
        "target": target_id,
        "content": text,
        "tianming": {
            "artifact": book.get("artifact") or "tianming.json",
            "status": book.get("status") or "draft",
            "anchor_status": book.get("anchor_status") or {},
            "contract_pressure": book.get("contract_pressure") or {},
            "ordinary_intervention_mutates_tianming": bool(
                book.get("ordinary_intervention_mutates_tianming", False)
            ),
        },
        "intervention_type": intervention_type,
        "intervention_level": level,
        "compatibility": compatibility,
        "translation_strategy": _translation_strategy(
            intervention_type,
            level,
            text,
            book,
            mode,
        ),
        "worldline_judgement": judgement,
        "branch_axis": branch_axis,
        "causal_debt": causal_debt,
        "worldline_tianming_snapshot": snapshot,
        "audit": {
            "required": requires_snapshot_audit,
            "can_mutate_tianming_snapshot": requires_snapshot_audit,
            "ordinary_intervention_can_mutate_tianming": False,
            "message": (
                "L4/L5 或暴走 AU 只能在审计后写世界线快照；本预编译不会改写 tianming.json。"
                if requires_snapshot_audit
                else "普通干预只能生成分支轴和因果债，不永久改写 tianming.json。"
            ),
        },
        "ordinary_intervention_mutates_tianming": False,
        "boundaries": [
            "本结果只解释干预如何投放，不调用 run_scene。",
            (
                "L4/L5 或 AU 只写世界线天命书快照，不覆盖根 tianming.json。"
                if snapshot
                else "普通干预不写 tianming.json、不写世界线天命书快照。"
            ),
            "普通干预不能永久改写《天命书》。",
        ],
    }


def _write_worldline_snapshot(
    *,
    story_slug: str,
    worldline_id: str,
    content: str,
    target_id: str,
    level: str,
    judgement: dict[str, str],
    compatibility: dict[str, Any],
    causal_debt: dict[str, Any],
    book: dict[str, Any],
    projects_dir: Path | None,
    projection_mode: str,
) -> dict[str, Any] | None:
    if level not in {"L4", "L5"} and judgement.get("kind") != "au":
        return None
    story_path, _source_kind = resolve_story_path(story_slug, projects_dir)
    snapshot_dir = story_path / "worldlines" / worldline_id
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    artifact = f"worldlines/{worldline_id}/tianming_snapshot.json"
    now = datetime.now().isoformat(timespec="seconds")
    snapshot = deepcopy(book)
    snapshot.update(
        {
            "artifact": artifact,
            "status": "draft_snapshot",
            "requires_confirmation": True,
            "worldline_id": worldline_id,
            "root_tianming_artifact": book.get("artifact") or "tianming.json",
            "root_tianming_mutated": False,
            "created_at": now,
            "updated_at": now,
            "confirmed_at": None,
            "snapshot_reason": {
                "intervention_level": level,
                "worldline_kind": judgement.get("kind") or "",
                "compatibility": compatibility.get("status") or "",
                "content_preview": content[:120],
                "target": target_id or "world",
                "projection_mode": projection_mode,
            },
            "boundaries": [
                "这是世界线《天命书》快照，不覆盖根 tianming.json。",
                "普通干预不能写入本快照；只有 L4/L5 或 AU 触发后才生成。",
                "快照仍需审计或作者确认后才能成为该世界线长期宪法。",
            ],
        }
    )
    snapshot["contract_pressure"] = _snapshot_contract_pressure(
        snapshot.get("contract_pressure"),
        level=level,
        causal_debt=causal_debt,
    )
    (snapshot_dir / "tianming_snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {
        "artifact": artifact,
        "status": "draft_snapshot",
        "worldline_id": worldline_id,
        "root_tianming_mutated": False,
        "requires_confirmation": True,
    }


def _snapshot_contract_pressure(
    raw: object,
    *,
    level: str,
    causal_debt: dict[str, Any],
) -> dict[str, Any]:
    pressure = deepcopy(raw) if isinstance(raw, dict) else {}
    active_tier = "collapse" if level == "L5" else "era"
    minimum_score = 12 if active_tier == "collapse" else 8
    pressure["active_tier"] = active_tier
    pressure["level"] = "high"
    pressure["score"] = max(
        int(pressure.get("score") or 0),
        int(causal_debt.get("score") or 0),
        minimum_score,
    )
    tiers = pressure.get("pressure_tiers")
    if isinstance(tiers, list):
        for item in tiers:
            if isinstance(item, dict):
                item["active"] = item.get("id") == pressure["active_tier"]
    pressure.setdefault(
        "drivers",
        ["高等级干预触发世界线宪法快照", "根天命书保持不变"],
    )
    return pressure


def _classify_intervention(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ("系统", "永久", "规则", "改成", "必须听命")):
        return "rule_rewrite"
    if any(token in lowered for token in ("未来", "大纲", "告诉", "密信", "预言", "传闻")):
        return "information"
    if any(
        token in lowered
        for token in (
            "给",
            "塞",
            "注入",
            "铜铃",
            "钥匙",
            "武器",
            "资源",
            "ak47",
            "枪",
            "子弹",
            "步枪",
            "热武器",
        )
    ):
        return "resource_injection"
    if any(token in lowered for token in ("命令", "强迫", "必须去", "不能", "立刻行动")):
        return "forced_action"
    return "information"


def _level_for(intervention_type: str, text: str) -> str:
    if intervention_type == "rule_rewrite":
        return "L5" if any(token in text for token in ("永久", "系统", "规则")) else "L4"
    if intervention_type == "resource_injection":
        lowered = text.lower()
        return (
            "L3"
            if any(
                token in lowered
                for token in ("偷听", "武器", "未来", "ak47", "枪", "子弹", "步枪", "热武器")
            )
            else "L2"
        )
    if intervention_type == "forced_action":
        return "L3"
    return "L3" if any(token in text for token in ("未来", "大纲", "下一章")) else "L2"


def _compatibility(
    book: dict[str, Any],
    intervention_type: str,
    level: str,
    text: str,
    projection_mode: str,
) -> dict[str, Any]:
    pressure = book.get("contract_pressure") if isinstance(book.get("contract_pressure"), dict) else {}
    pressure_level = str(pressure.get("level") or "medium")
    foreign_object_intrusion = _is_foreign_object_intrusion(text)
    if projection_mode == PROJECTION_MODE_WILD_AU:
        status = "au_requested"
        reason = "用户选择暴走 AU，异物将保留为改写世界前提的入侵变量。"
    elif level in {"L4", "L5"}:
        status = "strained"
        reason = "干预试图改写世界法则，必须转入 AU 或审计后的世界线快照。"
    elif foreign_object_intrusion and intervention_type == "resource_injection":
        status = "translated"
        reason = "检测到现代热武器异物入侵；沉浸模式会本土化重释，避免静默污染原世界。"
    elif intervention_type == "resource_injection" and pressure_level == "high":
        status = "strained"
        reason = "天命书显示合约压力较高，物品/资源注入会扩大因果债。"
    else:
        status = "compatible"
        reason = "干预可被翻译为世界内信息、物品或行动压力。"
    if "未来" in text or "大纲" in text:
        reason += " 含未来/大纲信息，需要包装成预言、密信或误传。"
    return {
        "status": status,
        "reason": reason,
        "tianming_pressure_level": pressure_level,
        "foreign_object_intrusion": foreign_object_intrusion,
    }


def _translation_strategy(
    intervention_type: str,
    level: str,
    text: str,
    book: dict[str, Any],
    projection_mode: str,
) -> dict[str, Any]:
    anchor = {}
    if isinstance(book.get("anchor_status"), dict):
        anchor = book.get("anchor_status") or {}
    anchor_name = str(anchor.get("current_anchor_name") or "主锚点")
    foreign_object_intrusion = _is_foreign_object_intrusion(text)
    if projection_mode == PROJECTION_MODE_WILD_AU:
        strategy = "保留异物入侵，另开暴走 AU 世界线；原世界线不被静默污染。"
        mode = "wild_au_intrusion"
    elif foreign_object_intrusion and intervention_type == "resource_injection":
        strategy = "本土化重释为雷鸣弩、连珠雷火机关或等价神器，并补上来源与使用代价。"
        mode = "local_reinterpretation"
    elif intervention_type == "rule_rewrite":
        strategy = "转译为世界法则震荡或 AU 分支，不直接覆盖原天命书。"
        mode = "law_reinterpretation"
    elif intervention_type == "resource_injection":
        strategy = "转译为世界内可追溯物品、线索或代价资源。"
        mode = "in_world_resource"
    elif intervention_type == "forced_action":
        strategy = "转译为诱因、压力或关系胁迫，让角色仍保留选择。"
        mode = "pressure_trigger"
    else:
        strategy = "转译为传闻、密信、梦兆、误读或预言碎片。"
        mode = "information_packaging"
    return {
        "strategy": strategy,
        "packaging": f"投放给{anchor_name}相关的信息场，但保留角色误解和反抗空间。",
        "original_hint": text[:80],
        "level": level,
        "mode": mode,
        "projection_mode": projection_mode,
        "foreign_object_intrusion": foreign_object_intrusion,
    }


def _worldline_judgement(
    intervention_type: str,
    level: str,
    compatibility: dict[str, Any],
    projection_mode: str,
) -> dict[str, str]:
    if projection_mode == PROJECTION_MODE_WILD_AU:
        return {
            "kind": "au",
            "reason": "用户选择暴走 AU：干预将作为异设世界线投放，并生成世界线《天命书》快照。",
        }
    if level in {"L4", "L5"} or intervention_type == "rule_rewrite":
        return {
            "kind": "au",
            "reason": "干预触及世界法则或天命书变更，只能作为 AU/审计后快照处理。",
        }
    if compatibility.get("status") == "strained":
        return {
            "kind": "divergent",
            "reason": "干预仍可在本世界内发生，但会制造明显分支轴和因果债。",
        }
    return {
        "kind": "divergent",
        "reason": "干预被吸收为本世界的一条分叉变量。",
    }


def _is_foreign_object_intrusion(text: str) -> bool:
    lowered = str(text or "").lower()
    return any(
        token in lowered
        for token in ("ak47", "ak-47", "枪", "子弹", "步枪", "热武器", "现代武器")
    )


def _branch_axis(
    intervention_type: str,
    target_id: str,
    text: str,
    judgement: dict[str, str],
) -> dict[str, str]:
    target = target_id or "world"
    axis_map = {
        "information": "信息差 / 预言可信度",
        "resource_injection": "资源来源 / 代价归属",
        "forced_action": "角色意志 / 外部压力",
        "rule_rewrite": "世界法则 / AU 偏移",
    }
    return {
        "id": f"{intervention_type}_{judgement.get('kind', 'divergent')}",
        "target": target,
        "axis": axis_map.get(intervention_type, "未知变量"),
        "question": f"{target}如何解释并承担“{text[:40]}”带来的后果？",
    }


def _causal_debt(
    intervention_type: str,
    level: str,
    compatibility: dict[str, Any],
    book: dict[str, Any],
) -> dict[str, Any]:
    base = {"L1": 1, "L2": 2, "L3": 4, "L4": 7, "L5": 9}.get(level, 3)
    if compatibility.get("status") == "strained":
        base += 1
    pressure = book.get("contract_pressure") if isinstance(book.get("contract_pressure"), dict) else {}
    if pressure.get("level") == "high":
        base += 1
    level_label = "high" if base >= 7 else "medium" if base >= 4 else "low"
    return {
        "level": level_label,
        "score": base,
        "spread": _debt_spread(intervention_type, level_label),
    }


def _debt_spread(intervention_type: str, level: str) -> list[str]:
    rows = {
        "information": ["误会扩散", "信任重新排序"],
        "resource_injection": ["物品来源被追查", "资源代价转嫁给关系网"],
        "forced_action": ["被迫行动引发反抗", "旁观者质疑动机"],
        "rule_rewrite": ["世界法则震荡", "原锚点失稳", "候选承载者被迫浮现"],
    }
    spread = rows.get(intervention_type, ["世界线出现新债务"])
    if level == "high":
        return spread + ["可能需要审计后的世界线快照"]
    return spread


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise TianmingInterventionCompilerRequestError(f"{label} 无效")
    return checked

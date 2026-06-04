"""Compile free-form interventions against a local Tianming book."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.tianming import get_tianming_book

VERSION = "tianming-intervention-compiler-v1"


class TianmingInterventionCompilerRequestError(ValueError):
    """Invalid Tianming intervention compiler request."""


def compile_intervention_against_tianming(
    story_slug: str,
    *,
    content: str,
    target: str = "",
    projects_dir: Path | None = None,
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
    book = get_tianming_book(sid, projects_dir=projects_dir)
    intervention_type = _classify_intervention(text)
    level = _level_for(intervention_type, text)
    compatibility = _compatibility(book, intervention_type, level, text)
    judgement = _worldline_judgement(intervention_type, level, compatibility)
    branch_axis = _branch_axis(intervention_type, target_id, text, judgement)
    causal_debt = _causal_debt(intervention_type, level, compatibility, book)
    return {
        "version": VERSION,
        "story_slug": sid,
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
        ),
        "worldline_judgement": judgement,
        "branch_axis": branch_axis,
        "causal_debt": causal_debt,
        "audit": {
            "required": level in {"L4", "L5"},
            "can_mutate_tianming_snapshot": level in {"L4", "L5"},
            "ordinary_intervention_can_mutate_tianming": False,
            "message": (
                "L4/L5 只能在审计后写世界线快照；本预编译不会改写 tianming.json。"
                if level in {"L4", "L5"}
                else "普通干预只能生成分支轴和因果债，不永久改写 tianming.json。"
            ),
        },
        "ordinary_intervention_mutates_tianming": False,
        "boundaries": [
            "本结果只解释干预如何投放，不调用 run_scene。",
            "本结果不写 tianming.json、不覆盖任何 run artifact。",
            "普通干预不能永久改写《天命书》。",
        ],
    }


def _classify_intervention(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ("系统", "永久", "规则", "改成", "必须听命")):
        return "rule_rewrite"
    if any(token in lowered for token in ("未来", "大纲", "告诉", "密信", "预言", "传闻")):
        return "information"
    if any(token in lowered for token in ("给", "塞", "注入", "铜铃", "钥匙", "武器", "资源")):
        return "resource_injection"
    if any(token in lowered for token in ("命令", "强迫", "必须去", "不能", "立刻行动")):
        return "forced_action"
    return "information"


def _level_for(intervention_type: str, text: str) -> str:
    if intervention_type == "rule_rewrite":
        return "L5" if any(token in text for token in ("永久", "系统", "规则")) else "L4"
    if intervention_type == "resource_injection":
        return "L3" if any(token in text for token in ("偷听", "武器", "未来")) else "L2"
    if intervention_type == "forced_action":
        return "L3"
    return "L3" if any(token in text for token in ("未来", "大纲", "下一章")) else "L2"


def _compatibility(
    book: dict[str, Any],
    intervention_type: str,
    level: str,
    text: str,
) -> dict[str, Any]:
    pressure = book.get("contract_pressure") if isinstance(book.get("contract_pressure"), dict) else {}
    pressure_level = str(pressure.get("level") or "medium")
    if level in {"L4", "L5"}:
        status = "strained"
        reason = "干预试图改写世界法则，必须转入 AU 或审计后的世界线快照。"
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
    }


def _translation_strategy(
    intervention_type: str,
    level: str,
    text: str,
    book: dict[str, Any],
) -> dict[str, str]:
    anchor = {}
    if isinstance(book.get("anchor_status"), dict):
        anchor = book.get("anchor_status") or {}
    anchor_name = str(anchor.get("current_anchor_name") or "主锚点")
    if intervention_type == "rule_rewrite":
        strategy = "转译为世界法则震荡或 AU 分支，不直接覆盖原天命书。"
    elif intervention_type == "resource_injection":
        strategy = "转译为世界内可追溯物品、线索或代价资源。"
    elif intervention_type == "forced_action":
        strategy = "转译为诱因、压力或关系胁迫，让角色仍保留选择。"
    else:
        strategy = "转译为传闻、密信、梦兆、误读或预言碎片。"
    return {
        "strategy": strategy,
        "packaging": f"投放给{anchor_name}相关的信息场，但保留角色误解和反抗空间。",
        "original_hint": text[:80],
        "level": level,
    }


def _worldline_judgement(
    intervention_type: str,
    level: str,
    compatibility: dict[str, Any],
) -> dict[str, str]:
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

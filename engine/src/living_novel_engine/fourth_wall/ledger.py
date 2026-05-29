from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from living_novel_engine.models import Intervention

# 觉察等级，升序排列
LEVELS = ["none", "unsettled", "suspicious", "aware", "defiant"]

# 分数 → 等级阈值（左闭右开）
_LEVEL_THRESHOLDS: list[tuple[float, str]] = [
    (0.18, "none"),
    (0.38, "unsettled"),
    (0.62, "suspicious"),
    (0.82, "aware"),
]

# 不同触发器对觉察分数的贡献
TRIGGER_WEIGHTS = {
    # 通过梦境/低语等"角色不可能正常获知"的渠道传信
    "impossible_information": 0.12,
    # 同一角色被反复干预（多次在关键节点被"安排"）
    "repeated_rescue": 0.18,
    # 干预违背角色人设（合约判定高抗拒或有违规）
    "personality_violation": 0.20,
    # 明显的命运修正（强干预 / 高合约风险）
    "fate_reversal": 0.15,
}

# 干预强度基础分
STRENGTH_BASE = {"soft": 0.06, "medium": 0.12, "strong": 0.20}

# 通过高维渠道传递信息的干预类型
_HIGH_DIM_CHANNELS = {"whisper", "dream_hint"}

# 旁观者只能感知到的异常类触发器（用于在场角色的弱外溢）
_AMBIENT_TRIGGERS = {"impossible_information", "fate_reversal"}

_SPILLOVER_RATIO = 0.25


class InterventionTrace(BaseModel):
    """一次干预在世界线上留下的痕迹。"""

    chapter: int = 0
    target: str = ""
    type: str = ""
    strength: str = "soft"
    contract_risk: str = "low"
    resistance: str = "low"
    visibility: str = "target_only"
    content_excerpt: str = ""
    triggers: list[str] = Field(default_factory=list)


class CharacterAwareness(BaseModel):
    """单个角色累积的第四面墙觉察状态。"""

    character_id: str
    score: float = 0.0
    triggers: list[str] = Field(default_factory=list)
    level: str = "none"
    attitude_toward_observer: str = "unknown"
    intervention_count: int = 0


class FourthWallLedger(BaseModel):
    """跨世界线 lineage 累积的干预记忆与角色觉察账本。"""

    enabled: bool = True
    traces: list[InterventionTrace] = Field(default_factory=list)
    awareness: dict[str, CharacterAwareness] = Field(default_factory=dict)

    def get(self, character_id: str) -> CharacterAwareness | None:
        return self.awareness.get(character_id)

    def present_awareness(
        self, present_ids: list[str]
    ) -> list[CharacterAwareness]:
        out = []
        for cid in present_ids:
            aw = self.awareness.get(cid)
            if aw is not None:
                out.append(aw)
        return out


def fourth_wall_enabled() -> bool:
    """env `LNE_FOURTH_WALL` 为 0/off/false/no 时关闭第四面墙表现，默认开启。"""
    raw = os.environ.get("LNE_FOURTH_WALL", "").strip().lower()
    if raw in ("0", "off", "false", "no", "disable", "disabled"):
        return False
    return True


def level_rank(level: str) -> int:
    try:
        return LEVELS.index(level)
    except ValueError:
        return 0


def level_from_score(score: float) -> str:
    for threshold, level in _LEVEL_THRESHOLDS:
        if score < threshold:
            return level
    return "defiant"


def attitude_from_level(level: str) -> str:
    return {
        "none": "unknown",
        "unsettled": "uneasy",
        "suspicious": "questioning",
        "aware": "confronting",
        "defiant": "defiant",
    }.get(level, "unknown")


def detect_triggers(intervention: "Intervention", *, repeat_count: int) -> list[str]:
    """根据干预属性与重复次数判定本次触发了哪些第四面墙信号。"""
    triggers: list[str] = []
    if intervention.type in _HIGH_DIM_CHANNELS:
        triggers.append("impossible_information")
    if repeat_count >= 2:
        triggers.append("repeated_rescue")
    audit = intervention.contract_audit
    if audit and (audit.expected_character_resistance == "high" or audit.violations):
        triggers.append("personality_violation")
    if intervention.strength == "strong" or intervention.contract_risk == "high":
        triggers.append("fate_reversal")
    return triggers


def _apply(aw: CharacterAwareness, delta: float, triggers: list[str]) -> None:
    aw.score = round(min(1.0, max(0.0, aw.score + max(0.0, delta))), 4)
    for t in triggers:
        if t not in aw.triggers:
            aw.triggers.append(t)
    aw.level = level_from_score(aw.score)
    aw.attitude_toward_observer = attitude_from_level(aw.level)


def _ensure(ledger: FourthWallLedger, cid: str) -> CharacterAwareness:
    aw = ledger.awareness.get(cid)
    if aw is None:
        aw = CharacterAwareness(character_id=cid)
        ledger.awareness[cid] = aw
    return aw


def accumulate_intervention(
    ledger: FourthWallLedger,
    intervention: "Intervention",
    *,
    chapter: int,
    present_ids: list[str] | None = None,
) -> FourthWallLedger:
    """把一次新干预记入账本并更新相关角色的觉察分数（原地修改并返回）。"""
    present_ids = present_ids or []
    target = intervention.target

    prior_target_traces = sum(1 for t in ledger.traces if t.target == target)
    repeat_count = prior_target_traces + 1
    triggers = detect_triggers(intervention, repeat_count=repeat_count)

    audit = intervention.contract_audit
    resistance = audit.expected_character_resistance if audit else "low"
    ledger.traces.append(
        InterventionTrace(
            chapter=chapter,
            target=target,
            type=intervention.type,
            strength=intervention.strength,
            contract_risk=intervention.contract_risk,
            resistance=resistance,
            visibility=intervention.visibility,
            content_excerpt=(intervention.content or "")[:80],
            triggers=triggers,
        )
    )

    target_delta = STRENGTH_BASE.get(intervention.strength, 0.06) + sum(
        TRIGGER_WEIGHTS.get(t, 0.0) for t in triggers
    )
    target_aw = _ensure(ledger, target)
    target_aw.intervention_count += 1
    _apply(target_aw, target_delta, triggers)

    # 场景/广域干预：在场的其他角色也会隐约察觉到"异常"
    if intervention.visibility in ("scene", "world_wide"):
        spill_triggers = [t for t in triggers if t in _AMBIENT_TRIGGERS]
        spill_delta = _SPILLOVER_RATIO * sum(
            TRIGGER_WEIGHTS.get(t, 0.0) for t in spill_triggers
        )
        if spill_delta > 0:
            for cid in present_ids:
                if cid == target:
                    continue
                _apply(_ensure(ledger, cid), spill_delta, spill_triggers)

    return ledger


def load_ledger(path: Path) -> FourthWallLedger:
    """从磁盘读取账本；缺失或损坏时返回空账本（优雅降级）。"""
    try:
        if not path.exists():
            return FourthWallLedger()
        data = json.loads(path.read_text(encoding="utf-8"))
        return FourthWallLedger.model_validate(data)
    except (ValueError, OSError):
        return FourthWallLedger()


def save_ledger(path: Path, ledger: FourthWallLedger) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(ledger.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def should_persist_ledger(ledger: FourthWallLedger | None) -> bool:
    """仅当第四面墙开启且账本有实质内容时才落盘。"""
    if ledger is None or not ledger.enabled:
        return False
    return bool(ledger.traces or ledger.awareness)


def ledger_for_pipeline(ledger: FourthWallLedger | None) -> FourthWallLedger | None:
    """关闭或未启用时，整条推演链路视为无账本（不传 snapshot / 不写盘）。"""
    if ledger is None or not ledger.enabled:
        return None
    return ledger

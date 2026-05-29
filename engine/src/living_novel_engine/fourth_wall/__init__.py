"""v0.5 第四面墙机制：干预记忆账本、角色觉察分数与表现提示。

核心思想：
- 每次干预都会在世界线 lineage 上留下痕迹（InterventionTrace）。
- 干预越频繁、越强、越违背人设、越通过"不可能渠道"传信，
  角色 fourth_wall_awareness 越高。
- 觉察分数到达阈值后，影响角色决策 prompt 与章节渲染，
  使角色能在正文中自然流露怀疑、追问、抗拒，甚至反过来利用高维干预。
- 可按需关闭（env `LNE_FOURTH_WALL=0`）。
"""

from living_novel_engine.fourth_wall.ledger import (
    LEVELS,
    CharacterAwareness,
    FourthWallLedger,
    InterventionTrace,
    accumulate_intervention,
    attitude_from_level,
    detect_triggers,
    fourth_wall_enabled,
    level_from_score,
    level_rank,
    load_ledger,
    should_persist_ledger,
    save_ledger,
)
from living_novel_engine.fourth_wall.prompts import (
    awareness_decision_hint,
    awareness_narrator_hint,
    mock_fourth_wall_aside,
)

__all__ = [
    "LEVELS",
    "CharacterAwareness",
    "FourthWallLedger",
    "InterventionTrace",
    "accumulate_intervention",
    "attitude_from_level",
    "detect_triggers",
    "fourth_wall_enabled",
    "level_from_score",
    "level_rank",
    "load_ledger",
    "should_persist_ledger",
    "save_ledger",
    "awareness_decision_hint",
    "awareness_narrator_hint",
    "mock_fourth_wall_aside",
]

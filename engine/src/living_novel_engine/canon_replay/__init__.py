"""v0.7.4 Canon Replay — 正史回放评估（本地 deterministic 轻量评估）。

把"无干预续写结果"与用户上传的正史 holdout 章节做相似度/一致性评估，
生成 canon_replay_report.json。

边界：
- 只做本地 deterministic / 轻量评估，不打 LLM、不做语义评估、不公开分享。
- holdout 文本只给 evaluator，不进入角色 / narrator / retrieval。
"""

from .evaluator import evaluate_replay
from .models import (
    CANON_REPLAY_VERSION,
    CanonReplayReport,
    HoldoutChapter,
    HoldoutManifest,
    ReplayScores,
)

__all__ = [
    "CANON_REPLAY_VERSION",
    "CanonReplayReport",
    "HoldoutChapter",
    "HoldoutManifest",
    "ReplayScores",
    "evaluate_replay",
]

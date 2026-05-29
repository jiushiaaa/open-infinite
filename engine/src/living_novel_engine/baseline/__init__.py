"""v0.7.4 Baseline Worldline — 无干预基线 artifact 契约。

Baseline 是评估层：在无高维干预时让角色按现有世界状态和人设自然发展，
作为干预世界线的对照组。它不改变 run_scene 默认行为，也不依赖
intervention.json / causal_diff / contract_audit。
"""

from .models import BASELINE_VERSION, BaselineReport

__all__ = ["BASELINE_VERSION", "BaselineReport"]

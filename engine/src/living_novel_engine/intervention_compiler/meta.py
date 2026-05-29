"""v0.7.1-B Intervention Compiler 生成元数据（generation_meta）。

记录一次 InterventionCompilation 是怎么来的，便于区分**真 LLM 编译**、
**rule-based 编译**与**回退**，并为成本观测留位。沿用 v0.6.5 `TraceMeta` 约定，
以 additive 方式写进 intervention_compilation.json 的 `generation_meta` 键，
不破坏 v0.7.1-A 既有字段。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CompilationMeta:
    source: str = "rule_based"  # rule_based | llm | fallback
    fallback_reason: str | None = None
    model_name: str | None = None
    attempt_count: int = 0
    duration_ms: int = 0
    usage: dict[str, Any] | None = None  # prompt_tokens / completion_tokens / total_tokens
    cost_estimate: float | None = None   # 占位：暂不做精确价格计算
    reconciled: bool = False             # 是否触发 rule_rewrite 安全兜底改写
    reconcile_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

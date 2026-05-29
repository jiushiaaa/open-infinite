"""v0.6.5 多 Agent 推演生成元数据（generation_meta）。

记录一次 `MultiAgentTrace` 是怎么来的，便于浏览器/调试区分**真 LLM 推演**与**回退**，
并为成本观测留位。以 additive 方式写进 `multi_agent_trace.json` 的 `generation_meta` 键，
不破坏既有读取（turn_plans / private_knowledge / ... 等结构不变）。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TraceMeta:
    source: str = "llm"  # llm | fallback | stub
    fallback_reason: str | None = None
    model_name: str | None = None
    attempt_count: int = 0
    duration_ms: int = 0
    validation_status: str = "ok"  # ok | repaired | fallback
    validator_warnings: list[str] = field(default_factory=list)
    usage: dict[str, Any] | None = None  # prompt_tokens / completion_tokens / total_tokens
    cost_estimate: float | None = None  # 占位：暂不做精确价格计算

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

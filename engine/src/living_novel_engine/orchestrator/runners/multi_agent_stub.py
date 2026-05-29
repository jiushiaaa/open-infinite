"""v0.6.2 `multi_agent_stub` runner。

在 v0.6.0 adapter + v0.6.1 协议之上的**第一个多 Agent 系 runner**：
先用协议确定性地构造一个可解释的 `MultiAgentTrace`，再经共享装配层
（`assembly.build_result_from_trace`）投影回既有契约对象
（`AcceptedEvent` / `StateDelta` / `state_snapshot`）并渲染章节。

定位：
- **stub**：不接 LLM 推理多 Agent、不接外部服务（MiroFish/OASIS），纯结构化演示。
- **非默认**：`lightweight` 仍是默认 runner；本 runner 仅在显式选择或
  `LNE_SCENE_RUNNER=multi_agent_stub` 时启用。
- **契约不变**：输出与 lightweight 同构，仅 additive 附 `multi_agent_trace`。

v0.6.4 起，trace 的「生产」与「装配」解耦：本 runner 用确定性
`build_demo_trace`，`multi_agent_llm` 用小模型推演，两者共用同一装配层。
"""

from __future__ import annotations

from living_novel_engine.models.events import SimulationResult
from living_novel_engine.orchestrator.runners.assembly import build_result_from_trace
from living_novel_engine.orchestrator.runners.base import SceneRequest, SceneRunner
from living_novel_engine.orchestrator.runners.meta import TraceMeta
from living_novel_engine.orchestrator.runners.projection import build_demo_trace


class MultiAgentStubRunner(SceneRunner):
    """协议驱动的演示型多 Agent runner（投影回既有契约）。"""

    name = "multi_agent_stub"

    def run(self, request: SceneRequest) -> SimulationResult:
        return run_multi_agent_stub(request)


def run_multi_agent_stub(request: SceneRequest) -> SimulationResult:
    trace = build_demo_trace(request)
    result = build_result_from_trace(
        request,
        trace,
        termination_reason="multi_agent_stub_complete",
        generation_meta=TraceMeta(source="stub", validation_status="ok").to_dict(),
    )
    result.runner_name = MultiAgentStubRunner.name
    return result

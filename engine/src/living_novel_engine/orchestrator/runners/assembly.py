"""多 Agent 系 runner 的共享装配层。

把「一个 `MultiAgentTrace` → 一个完整 `SimulationResult`」的流程抽出来，
供 `multi_agent_stub`（v0.6.2 确定性）与 `multi_agent_llm`（v0.6.4 小模型推演）共用：

```text
MultiAgentTrace
  → project_trace（投影成公开 AcceptedEvent / StateDelta，强制 reveal/corrected/due_round 规则）
  → apply_relationship_signals（写回角色 relationships）
  → build_state_snapshot + render_chapter（复用既有契约与 narrator）
  → SimulationResult（契约不变；additive 附 multi_agent_trace）
```

trace 的「生产方式」（确定性 stub / LLM 推演）不在本层关心——
本层只负责确定性的、可测试的投影与渲染，保证两种 runner 输出同构。
"""

from __future__ import annotations

import copy

from living_novel_engine.agents.narrator import render_chapter
from living_novel_engine.models.events import SceneRecord, SimulationResult
from living_novel_engine.orchestrator.narrative_constraints import summary_from_snapshot
from living_novel_engine.orchestrator.runners.base import SceneRequest
from living_novel_engine.orchestrator.runners.projection import (
    apply_relationship_signals,
    project_trace,
)
from living_novel_engine.orchestrator.runners.protocol import MultiAgentTrace
from living_novel_engine.orchestrator.state_snapshot import build_state_snapshot


def initial_scene_state(request: SceneRequest) -> dict:
    """构造初始场景状态（续章时继承父快照的 seed_scene_state）。"""
    world = request.world
    spec = request.spec
    if request.seed_scene_state is not None:
        scene_state = {**request.seed_scene_state, "branch_seed": spec.branch_seed}
    else:
        first_line = world.scene_description.split("\n")[0][:30] if world.scene_description else "场景"
        scene_state = {
            "location": first_line,
            "time": "当前",
            "branch_seed": spec.branch_seed,
        }
    if request.intervention:
        scene_state["intervention_target"] = request.intervention.target
    return scene_state


def scenes_from_events(events, scene_state: dict) -> list[SceneRecord]:
    """把投影出的公开事件按回合归并成 SceneRecord。"""
    rounds = sorted({e.round_num for e in events})
    scenes: list[SceneRecord] = []
    for rn in rounds:
        evs = [e for e in events if e.round_num == rn]
        summary = "；".join(e.narrative for e in evs)[:200]
        scenes.append(
            SceneRecord(
                round_num=rn,
                location=str(scene_state.get("location", "")),
                summary=summary,
                events=evs,
            )
        )
    return scenes


def build_result_from_trace(
    request: SceneRequest,
    trace: MultiAgentTrace,
    *,
    termination_reason: str,
    generation_meta: dict | None = None,
) -> SimulationResult:
    """把一个已生成的 trace 投影并渲染成完整 `SimulationResult`。

    第四面墙在多 Agent 系 runner 中暂不参与（ledger 不接入），
    快照沿用既有构造以保持契约。`generation_meta`（v0.6.5）以 additive 方式写进
    `multi_agent_trace.generation_meta`，记录本次是真 LLM 推演还是回退。
    """
    world = request.world
    spec = request.spec
    chapter_number = request.chapter_number

    chars = copy.deepcopy(
        request.seed_characters if request.seed_characters is not None else request.characters
    )
    char_map = {c.id: c for c in chars}
    scene_state = initial_scene_state(request)

    projection = project_trace(
        trace, chapter_number=chapter_number, max_rounds=request.max_rounds
    )
    apply_relationship_signals(trace, char_map)

    scenes = scenes_from_events(projection.accepted_events, scene_state)

    result = SimulationResult(
        worldline_id=spec.branch_id,
        branch_seed=spec.branch_seed,
        theme=spec.theme,
        rounds=scenes,
        accepted_events=projection.accepted_events,
        state_deltas=projection.state_deltas,
        scenes=scenes,
        termination_reason=termination_reason,
        final_scene_state=scene_state,
        multi_agent_trace=trace.model_dump(),
    )
    if generation_meta is not None and result.multi_agent_trace is not None:
        result.multi_agent_trace["generation_meta"] = generation_meta

    result.state_snapshot = build_state_snapshot(
        world, request.characters, char_map, scene_state, spec, result, ledger=None
    )
    result.summary_text = summary_from_snapshot(
        world.display_name or world.title, result
    )
    context = request.canon_excerpt or request.canon_chapter
    result.chapter_text = render_chapter(
        world,
        result,
        context,
        request.llm,
        prologue=request.prologue,
        canon_opening=request.canon_opening,
        canon_chapter=request.canon_chapter or request.canon_excerpt,
        state_snapshot=result.state_snapshot,
        chapter_number=chapter_number,
        retrieved_context=request.retrieved_context,
    )
    return result

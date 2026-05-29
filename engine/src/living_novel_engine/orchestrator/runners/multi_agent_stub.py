"""v0.6.2 `multi_agent_stub` runner。

在 v0.6.0 adapter + v0.6.1 协议之上的**第一个多 Agent 系 runner**：
先用协议确定性地构造一个可解释的 `MultiAgentTrace`，再经 `projection`
投影回既有契约对象（`AcceptedEvent` / `StateDelta` / `state_snapshot`），
最后复用既有 narrator 渲染章节。

定位：
- **stub**：不接 LLM 推理多 Agent、不接外部服务（MiroFish/OASIS），纯结构化演示。
- **非默认**：`lightweight` 仍是默认 runner；本 runner 仅在显式选择或
  `LNE_SCENE_RUNNER=multi_agent_stub` 时启用。
- **契约不变**：输出与 lightweight 同构，仅 additive 附 `multi_agent_trace`。
"""

from __future__ import annotations

import copy

from living_novel_engine.agents.narrator import render_chapter
from living_novel_engine.models.events import SceneRecord, SimulationResult
from living_novel_engine.orchestrator.narrative_constraints import summary_from_snapshot
from living_novel_engine.orchestrator.runners.base import SceneRequest, SceneRunner
from living_novel_engine.orchestrator.runners.projection import (
    apply_relationship_signals,
    build_demo_trace,
    project_trace,
)
from living_novel_engine.orchestrator.state_snapshot import build_state_snapshot


class MultiAgentStubRunner(SceneRunner):
    """协议驱动的演示型多 Agent runner（投影回既有契约）。"""

    name = "multi_agent_stub"

    def run(self, request: SceneRequest) -> SimulationResult:
        return run_multi_agent_stub(request)


def _initial_scene_state(request: SceneRequest) -> dict:
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


def _scenes_from_events(events, scene_state: dict) -> list[SceneRecord]:
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


def run_multi_agent_stub(request: SceneRequest) -> SimulationResult:
    world = request.world
    spec = request.spec
    llm = request.llm
    chapter_number = request.chapter_number

    chars = copy.deepcopy(
        request.seed_characters if request.seed_characters is not None else request.characters
    )
    char_map = {c.id: c for c in chars}
    scene_state = _initial_scene_state(request)

    trace = build_demo_trace(request)
    projection = project_trace(
        trace, chapter_number=chapter_number, max_rounds=request.max_rounds
    )
    apply_relationship_signals(trace, char_map)

    scenes = _scenes_from_events(projection.accepted_events, scene_state)

    result = SimulationResult(
        worldline_id=spec.branch_id,
        branch_seed=spec.branch_seed,
        theme=spec.theme,
        rounds=scenes,
        accepted_events=projection.accepted_events,
        state_deltas=projection.state_deltas,
        scenes=scenes,
        termination_reason="multi_agent_stub_complete",
        final_scene_state=scene_state,
        runner_name=MultiAgentStubRunner.name,
        multi_agent_trace=trace.model_dump(),
    )

    # 第四面墙在 stub 阶段不参与（ledger 不接入）；快照沿用既有构造保持契约。
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
        llm,
        prologue=request.prologue,
        canon_opening=request.canon_opening,
        canon_chapter=request.canon_chapter or request.canon_excerpt,
        state_snapshot=result.state_snapshot,
        chapter_number=chapter_number,
        retrieved_context=request.retrieved_context,
    )
    return result

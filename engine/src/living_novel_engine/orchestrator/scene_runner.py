from __future__ import annotations

from typing import Any

from living_novel_engine.fourth_wall import FourthWallLedger
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.models import CharacterAgent, Intervention, StoryWorld
from living_novel_engine.models.events import SimulationResult
from living_novel_engine.orchestrator.runners import SceneRequest, dispatch_scene
from living_novel_engine.orchestrator.worldline_brancher import BranchSpec


def run_scene(
    world: StoryWorld,
    characters: list[CharacterAgent],
    intervention: Intervention | None,
    spec: BranchSpec,
    llm: LLMClient,
    *,
    max_rounds: int = 4,
    canon_excerpt: str = "",
    prologue: str = "",
    canon_opening: str = "",
    canon_chapter: str = "",
    seed_scene_state: dict[str, Any] | None = None,
    seed_characters: list[CharacterAgent] | None = None,
    chapter_number: int = 13,
    source_type: str = "builtin_sample",
    retrieved_context: str = "",
    ledger: FourthWallLedger | None = None,
    runner_name: str | None = None,
) -> SimulationResult:
    """执行一次场景推演。

    v0.6 起为 runner adapter 的薄包装：把参数收敛为 `SceneRequest`，
    再交由注册表选取的 runner 执行（默认 `lightweight`，行为与 v0.5 一致）。
    可经 `runner_name` 参数或环境变量 `LNE_SCENE_RUNNER` 切换实现。
    """
    request = SceneRequest(
        world=world,
        characters=characters,
        intervention=intervention,
        spec=spec,
        llm=llm,
        max_rounds=max_rounds,
        canon_excerpt=canon_excerpt,
        prologue=prologue,
        canon_opening=canon_opening,
        canon_chapter=canon_chapter,
        seed_scene_state=seed_scene_state,
        seed_characters=seed_characters,
        chapter_number=chapter_number,
        source_type=source_type,
        retrieved_context=retrieved_context,
        ledger=ledger,
    )
    return dispatch_scene(request, runner_name=runner_name)

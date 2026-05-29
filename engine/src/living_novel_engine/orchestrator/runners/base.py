from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

from living_novel_engine.llm.client import LLMClient
from living_novel_engine.models import CharacterAgent, Intervention, StoryWorld
from living_novel_engine.models.events import SimulationResult
from living_novel_engine.orchestrator.worldline_brancher import BranchSpec

# 延迟到运行时再引用，避免顶层循环导入
FourthWallLedger = Any


class RunnerError(RuntimeError):
    """runner 选择 / 执行相关错误。"""


@dataclass
class SceneRequest:
    """一次场景推演的完整输入。

    把原 `run_scene` 的全部参数收敛为单一请求对象，作为所有 runner 的统一契约。
    新增 runner 实现只需消费本对象并产出 `SimulationResult`，
    不应改变 `accepted_events` / `state_snapshot` 的既有结构（仅可附加字段）。
    """

    world: StoryWorld
    characters: list[CharacterAgent]
    intervention: Intervention | None
    spec: BranchSpec
    llm: LLMClient
    max_rounds: int = 4
    canon_excerpt: str = ""
    prologue: str = ""
    canon_opening: str = ""
    canon_chapter: str = ""
    seed_scene_state: dict[str, Any] | None = None
    seed_characters: list[CharacterAgent] | None = None
    chapter_number: int = 13
    source_type: str = "builtin_sample"
    retrieved_context: str = ""
    ledger: Any = None  # FourthWallLedger | None

    @property
    def is_builtin(self) -> bool:
        return self.source_type == "builtin_sample"


class SceneRunner(ABC):
    """推演 runner 抽象。

    默认实现是 `LightweightSceneRunner`（单 prompt 多角色轮询）。
    v0.6.x 起可注册更深的多 Agent runner，替换轻量轮询，
    但必须保持 `SimulationResult` 输出契约不变。
    """

    name: ClassVar[str] = "base"

    @abstractmethod
    def run(self, request: SceneRequest) -> SimulationResult:
        """执行一次场景推演并返回结果。"""
        raise NotImplementedError

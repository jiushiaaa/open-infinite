"""v0.6 推演 runner adapter。

提供可插拔的 `SceneRunner` 抽象与注册表，把「轻量轮询」从硬编码实现
变为可替换组件。默认 runner 为 `lightweight`，行为与 v0.5 完全一致。

选择优先级：显式 `runner_name` 参数 > 环境变量 `LNE_SCENE_RUNNER` > 默认 `lightweight`。
"""

from __future__ import annotations

import os

from living_novel_engine.orchestrator.runners.base import (
    RunnerError,
    SceneRequest,
    SceneRunner,
)
from living_novel_engine.orchestrator.runners.lightweight import LightweightSceneRunner
from living_novel_engine.orchestrator.runners.multi_agent_llm import MultiAgentLLMRunner
from living_novel_engine.orchestrator.runners.multi_agent_stub import MultiAgentStubRunner

DEFAULT_RUNNER = "lightweight"
_ENV_VAR = "LNE_SCENE_RUNNER"

_REGISTRY: dict[str, SceneRunner] = {}


def register_runner(runner: SceneRunner, *, overwrite: bool = False) -> None:
    """注册一个 runner 实例。重复名称默认报错，除非 overwrite=True。"""
    name = runner.name
    if not name:
        raise RunnerError("runner.name 不能为空")
    if name in _REGISTRY and not overwrite:
        raise RunnerError(f"runner 已存在: {name}（如需替换请 overwrite=True）")
    _REGISTRY[name] = runner


def available_runners() -> list[str]:
    return sorted(_REGISTRY)


def resolve_runner_name(runner_name: str | None = None) -> str:
    """按优先级解析 runner 名称：显式 > env > 默认。"""
    if runner_name:
        return runner_name
    env_name = os.environ.get(_ENV_VAR, "").strip()
    if env_name:
        return env_name
    return DEFAULT_RUNNER


def get_runner(runner_name: str | None = None) -> SceneRunner:
    """取出指定 runner；未知名称给出清晰错误并列出可用项。"""
    name = resolve_runner_name(runner_name)
    runner = _REGISTRY.get(name)
    if runner is None:
        raise RunnerError(
            f"未知 runner: {name!r}；可用: {', '.join(available_runners()) or '（无）'}"
        )
    return runner


def dispatch_scene(
    request: SceneRequest,
    *,
    runner_name: str | None = None,
):
    """选取 runner 执行推演，并以 runner.name 权威标记结果来源。"""
    runner = get_runner(runner_name)
    result = runner.run(request)
    result.runner_name = runner.name
    return result


# 默认注册轻量 runner；multi_agent_* 为可选（非默认），需显式或经 env 选择
register_runner(LightweightSceneRunner())
register_runner(MultiAgentStubRunner())
register_runner(MultiAgentLLMRunner())

__all__ = [
    "DEFAULT_RUNNER",
    "LightweightSceneRunner",
    "MultiAgentLLMRunner",
    "MultiAgentStubRunner",
    "RunnerError",
    "SceneRequest",
    "SceneRunner",
    "available_runners",
    "dispatch_scene",
    "get_runner",
    "register_runner",
    "resolve_runner_name",
]

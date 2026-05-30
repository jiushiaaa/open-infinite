"""v0.8+ Dynamic Action Registry-A：动作计划沉淀为可复用动作注册表。"""

from __future__ import annotations

import yaml

from living_novel_engine.act_director import plan_character_actions
from living_novel_engine.dynamic_action_registry import build_action_registry
from living_novel_engine.intervention_compiler import compile_intervention
from living_novel_engine.service import run_intervention
from living_novel_engine.story_loader import load_story


def test_build_action_registry_from_act_director_plan():
    bundle = load_story("tianhuang-night")
    compilation = compile_intervention(
        "把竹林有埋伏的消息告诉林晚舟",
        target="lin_wan_zhou",
        world=bundle.world,
        characters=bundle.character_map(),
    )
    plan = plan_character_actions(
        compilation,
        world=bundle.world,
        characters=bundle.character_map(),
        story_slug="tianhuang-night",
    )

    registry = build_action_registry(plan)

    assert registry.version == "v0.8-dynamic-action-registry-a"
    assert registry.kind == "dynamic_action_registry"
    assert registry.story_slug == "tianhuang-night"
    assert registry.actions
    assert registry.actions[0].source_step_ids
    assert "验证高维信息" in registry.actions[0].aliases
    assert registry.summary["action_count"] == len(registry.actions)


def test_run_intervention_writes_dynamic_action_registry(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")

    result = run_intervention(
        story_slug="tianhuang-night",
        target="lin_wan_zhou",
        content="告诉林晚舟今夜不要去竹林",
        mock=True,
        rounds=1,
    )

    path = outputs / result.run_id / "dynamic_action_registry.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    assert data["kind"] == "dynamic_action_registry"
    assert data["story_slug"] == "tianhuang-night"
    assert data["actions"]
    assert result.extra["dynamic_action_registry"]["actions"]

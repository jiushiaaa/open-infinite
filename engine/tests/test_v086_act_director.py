"""v0.8+ ActDirector-A：AbstractIntervention -> CharacterActionPlan artifact。"""

from __future__ import annotations

import json

from living_novel_engine.act_director import plan_character_actions
from living_novel_engine.intervention_compiler import compile_intervention
from living_novel_engine.service import run_intervention
from living_novel_engine.story_loader import load_story


def test_plan_information_intervention_to_action_steps():
    bundle = load_story("tianhuang-night")
    char_map = bundle.character_map()
    compilation = compile_intervention(
        "告诉林晚舟今晚不要去竹林",
        target="lin_wan_zhou",
        world=bundle.world,
        characters=char_map,
    )

    plan = plan_character_actions(
        compilation,
        world=bundle.world,
        characters=char_map,
        story_slug="tianhuang-night",
    )

    assert plan.version == "v0.8-actdirector-a"
    assert plan.story_slug == "tianhuang-night"
    assert len(plan.steps) == len(compilation.branch_axis)
    assert all(step.character_id == "lin_wan_zhou" for step in plan.steps)
    assert all(step.preconditions for step in plan.steps)
    assert all(step.effects for step in plan.steps)
    assert {step.branch_axis_id for step in plan.steps} == {
        axis.id for axis in compilation.branch_axis
    }


def test_plan_rule_rewrite_marks_alternate_and_repairs():
    bundle = load_story("tianhuang-night")
    compilation = compile_intervention(
        "让林晚舟获得现代系统和无限子弹手枪",
        target="lin_wan_zhou",
        world=bundle.world,
        characters=bundle.character_map(),
        declared_type="rule_rewrite",
    )

    plan = plan_character_actions(
        compilation,
        world=bundle.world,
        characters=bundle.character_map(),
        story_slug="tianhuang-night",
    )

    assert plan.lineage_type == "alternate_novel"
    assert plan.warnings
    assert all(step.risk == "high" for step in plan.steps)
    assert any(step.repair_suggestions for step in plan.steps)


def test_run_intervention_writes_act_director_plan(tmp_path, monkeypatch):
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

    path = outputs / result.run_id / "act_director_plan.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["kind"] == "act_director_plan"
    assert data["story_slug"] == "tianhuang-night"
    assert data["steps"]
    assert result.extra["act_director_plan"]["steps"]

"""v0.7.1-A Intervention Compiler 最小闭环测试。

覆盖：四类干预分类、动态 branch_axis、lineage_type、兼容性、
affected_scope、与现有 branch_spec 的映射，以及 intervene artifact 落盘。
"""

from __future__ import annotations

import json

import pytest

from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.intervention_compiler import (
    InterventionCompilation,
    classify,
    compile_intervention,
)
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import (
    build_branch_specs_from_compilation,
)
from living_novel_engine.output.writer import write_run_output
from living_novel_engine.samples import load_sample


@pytest.fixture(scope="module")
def tianhuang():
    return load_sample("tianhuang-night")


# ─── 分类器 ────────────────────────────────────────────────


class TestClassifier:
    def test_information_default(self):
        itype, _ = classify("今夜竹林会有埋伏，墨青烟在骗你")
        assert itype == "information"

    def test_forced_action_not_go(self):
        itype, hits = classify("林晚舟今夜不要去城外竹林，留在城里")
        assert itype == "forced_action"
        assert hits

    def test_resource_injection(self):
        itype, _ = classify("让林晚舟在药庐捡到一枚破障丹")
        assert itype == "resource_injection"

    def test_rule_rewrite_system(self):
        itype, hits = classify("给林晚舟绑定一个修仙系统，签到就能升级")
        assert itype == "rule_rewrite"
        assert any("系统" in h for h in hits)

    def test_rule_rewrite_modern_weapon(self):
        itype, _ = classify("给林凡一把AK47去扫平竹林")
        assert itype == "rule_rewrite"

    def test_rule_rewrite_time_travel(self):
        itype, _ = classify("让墨青烟其实是穿越者，带着前世记忆")
        assert itype == "rule_rewrite"

    def test_declared_type_overrides(self):
        itype, _ = classify("随便一句话", declared_type="forced_action")
        assert itype == "forced_action"


# ─── information 型：仍可用相信/怀疑/拒绝，但谱系为 divergent ──────────


class TestInformation:
    def test_axis_and_lineage(self, tianhuang):
        comp = compile_intervention(
            "今夜竹林有埋伏，别完全相信墨青烟",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
        )
        assert comp.abstract_intervention.intervention_type == "information"
        assert comp.lineage_type == "divergent_worldline"
        assert comp.compatibility.status == "compatible"
        stances = {a.stance for a in comp.branch_axis}
        assert stances == {"believe", "doubt", "reject"}


# ─── forced_action 型：分支轴必须不同于 believe/doubt/reject 命名 ──────


class TestForcedAction:
    def test_dynamic_axis_labels(self, tianhuang):
        comp = compile_intervention(
            "林晚舟今夜必须留在城里，不要去城外竹林",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
        )
        assert comp.abstract_intervention.intervention_type == "forced_action"
        assert comp.lineage_type == "divergent_worldline"
        labels = [a.label for a in comp.branch_axis]
        # 不能是固定的相信/怀疑/拒绝命名
        assert labels[:3] == ["主动改道", "被迫延迟", "抗拒命运压力"]
        assert "城外竹林" in comp.abstract_intervention.desired_effect or comp.affected_scope.locations

    def test_affected_scope_location(self, tianhuang):
        comp = compile_intervention(
            "林晚舟不要去城外竹林",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
        )
        assert "bamboo_grove" in comp.affected_scope.locations
        assert "lin_wan_zhou" in comp.affected_scope.characters


# ─── resource_injection 型 ──────────────────────────────────


class TestResourceInjection:
    def test_reasonable_item_divergent(self, tianhuang):
        comp = compile_intervention(
            "让林晚舟在药庐得到一枚醒神散",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
        )
        assert comp.abstract_intervention.intervention_type == "resource_injection"
        assert comp.lineage_type == "divergent_worldline"
        assert comp.compatibility.status == "partial"
        labels = [a.label for a in comp.branch_axis]
        assert "同世界合理吸收" in labels
        assert "降级转译" in labels


# ─── rule_rewrite 型：必须 reject/translate/alternate，且 alternate_novel ──


class TestRuleRewrite:
    @pytest.mark.parametrize(
        "text",
        [
            "给林凡一把AK47扫平竹林",
            "给林晚舟绑定一个签到系统",
            "让墨青烟其实是穿越者，带着前世记忆和金手指",
        ],
    )
    def test_rule_rewrite_alternate_novel(self, text, tianhuang):
        comp = compile_intervention(
            text,
            target="lin_fan",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
        )
        assert comp.abstract_intervention.intervention_type == "rule_rewrite"
        assert comp.lineage_type == "alternate_novel"
        assert comp.compatibility.status == "incompatible"
        assert comp.compatibility.risk == "high"
        # 必须给出 reject / translate / alternate 三条出路之一
        outcomes = {a.outcome for a in comp.branch_axis}
        assert outcomes == {"rejected", "translated", "alternate"}
        # realization 不静默注入原世界线
        assert comp.realization.in_world is False

    def test_system_conflicts_with_world_rule(self, tianhuang):
        comp = compile_intervention(
            "给林晚舟一个系统",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
        )
        # 天荒城 world.yaml 明确禁止系统/穿越/重生等设定
        assert comp.compatibility.contract_conflicts
        assert any("未声明设定" in c for c in comp.compatibility.contract_conflicts)

    def test_alternate_per_axis_lineage(self, tianhuang):
        comp = compile_intervention(
            "给林凡一把机枪",
            target="lin_fan",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
        )
        alt = [a for a in comp.branch_axis if a.outcome == "alternate"]
        assert alt and alt[0].lineage_type == "alternate_novel"


# ─── compiler 在缺 world/characters 时也可用 ────────────────────


class TestCompilerRobust:
    def test_no_world(self):
        comp = compile_intervention("告诉他未来会下雨", target="someone")
        assert isinstance(comp, InterventionCompilation)
        assert comp.abstract_intervention.intervention_type == "information"
        assert comp.branch_axis


# ─── 与现有 branch_spec 的映射 ──────────────────────────────


class TestBranchSpecMapping:
    def test_maps_to_stable_ids_with_stance_seed(self, tianhuang):
        comp = compile_intervention(
            "林晚舟今夜必须留在城里，不要去竹林",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
        )
        specs = build_branch_specs_from_compilation(comp, count=3)
        assert [s.branch_id for s in specs] == ["branch_a", "branch_b", "branch_c"]
        # branch_seed 仍是机制种子，驱动既有 runner
        assert {s.branch_seed for s in specs} <= {"believe", "doubt", "reject"}
        # theme 是动态轴 label，不是固定三分支
        assert specs[0].theme == "主动改道"

    def test_empty_axis_fallback(self, tianhuang):
        comp = compile_intervention(
            "随便", target="lin_wan_zhou", world=tianhuang.world,
            characters=tianhuang.character_map(),
        )
        comp.branch_axis = []
        specs = build_branch_specs_from_compilation(comp, count=3)
        assert len(specs) == 3
        assert {s.branch_seed for s in specs} == {"believe", "doubt", "reject"}


# ─── intervene artifact 落盘 ────────────────────────────────


class TestArtifact:
    def test_write_run_output_writes_compilation(self, tianhuang):
        intervention = build_intervention(
            target="lin_wan_zhou",
            content="林晚舟今夜不要去竹林",
            intervention_type="whisper",
        )
        intervention = audit_intervention(
            intervention, tianhuang.world, tianhuang.character_map()
        )
        comp = compile_intervention(
            "林晚舟今夜不要去竹林",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
        )
        specs = build_branch_specs_from_compilation(comp, count=2)
        llm = LLMClient(mock=True)
        results = [
            run_scene(
                tianhuang.world,
                tianhuang.characters,
                intervention,
                spec,
                llm,
                max_rounds=2,
                source_type="builtin_sample",
            )
            for spec in specs
        ]
        output = write_run_output(
            intervention, results, run_id="test_compiler_run", compilation=comp
        )
        artifact = output.run_dir / "intervention_compilation.json"
        assert artifact.exists()
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["abstract_intervention"]["intervention_type"] == "forced_action"
        assert data["lineage_type"] == "divergent_worldline"
        assert data["branch_axis"]
        assert "abstract_intervention" in data
        assert "compatibility" in data
        assert "realization" in data
        assert "affected_scope" in data

    def test_write_run_output_without_compilation_backward_compat(self, tianhuang):
        """不传 compilation 时不写 artifact，保持向后兼容。"""
        intervention = build_intervention(
            target="lin_wan_zhou", content="测试", intervention_type="whisper"
        )
        intervention = audit_intervention(
            intervention, tianhuang.world, tianhuang.character_map()
        )
        comp = compile_intervention("测试", target="lin_wan_zhou", world=tianhuang.world)
        specs = build_branch_specs_from_compilation(comp, count=2)
        llm = LLMClient(mock=True)
        results = [
            run_scene(
                tianhuang.world, tianhuang.characters, intervention, spec, llm,
                max_rounds=2, source_type="builtin_sample",
            )
            for spec in specs
        ]
        output = write_run_output(
            intervention, results, run_id="test_compiler_run_nocomp"
        )
        assert not (output.run_dir / "intervention_compilation.json").exists()

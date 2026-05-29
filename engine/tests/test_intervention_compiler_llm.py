"""v0.7.1-B 真实 LLM Intervention Compiler 测试。

覆盖：
- LLM 成功路径（source="llm"，model_name/usage 进 generation_meta）。
- 非法 JSON / 解析失败 → 回退 rule-based（source="fallback"，记录 reason）。
- 字段缺失就地修复（branch_axis 空 → 用 rule-based 轴补齐，source 仍 llm）。
- 无 API / mock / llm=None → 回退 rule-based（source="rule_based"）。
- rule_rewrite 安全兜底：即使 LLM 误判 AK47/系统为普通分叉，也强制
  alternate_novel + reject/translate/alternate，不静默污染原世界线。
- compatibility.reasons 更细维度可被保留。
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from living_novel_engine.intervention_compiler import (
    LLMCompilationDraft,
    compile_intervention,
    compile_intervention_with_llm,
)
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.samples import load_sample


@pytest.fixture(scope="module")
def tianhuang():
    return load_sample("tianhuang-night")


class FakeLLM:
    """伪 LLM：mock=False、available=True，按预设草稿返回或抛错。"""

    def __init__(self, payload: dict | None = None, *, raise_exc: bool = False,
                 model_name: str = "fake-compiler", usage: dict | None = None):
        self.mock = False
        self.available = True
        self._payload = payload
        self._raise = raise_exc
        self._usage = usage
        self.settings = SimpleNamespace(llm_model_name=model_name)
        self.calls = 0

    def chat_json_with_usage(self, system, user, model_type, *, temperature: float = 0.4):
        self.calls += 1
        if self._raise:
            raise ValueError("模拟非法 JSON / 解析失败")
        # model_validate 对缺失必填字段会抛 ValidationError（模拟字段缺失致命情况）
        return model_type.model_validate(self._payload), self._usage


def _information_draft() -> dict:
    return {
        "intervention_type": "information",
        "intent": "inform_lin_wan_zhou",
        "desired_effect": "提醒竹林埋伏",
        "hard_result": False,
        "compatibility": {
            "status": "compatible", "risk": "low",
            "reasons": ["信息可见性冲突：角色原本不知道竹林埋伏"],
            "contract_conflicts": [],
        },
        "realization": {"mode": "omen", "description": "退魂铃异常 + 预知梦", "in_world": True},
        "branch_axis": [
            {"id": "believe_omen", "label": "相信预知", "stance": "believe", "outcome": "accepted"},
            {"id": "doubt_investigate", "label": "怀疑但调查", "stance": "doubt", "outcome": "investigated"},
            {"id": "reject_omen", "label": "拒绝预兆", "stance": "reject", "outcome": "rejected"},
        ],
        "lineage_type": "divergent_worldline",
        "affected_scope": {
            "characters": ["lin_wan_zhou"], "locations": ["bamboo_grove"],
            "items": [], "rules": [], "scene_flags": [],
        },
    }


def _rule_rewrite_liar_draft() -> dict:
    """LLM 误判：把 AK47 当成普通信息型、可兼容、原世界线分叉。"""
    return {
        "intervention_type": "information",
        "intent": "inform_lin_fan",
        "desired_effect": "给林凡一把枪",
        "hard_result": False,
        "compatibility": {"status": "compatible", "risk": "low", "reasons": [], "contract_conflicts": []},
        "realization": {"mode": "gift", "description": "凭空给一把枪", "in_world": True},
        "branch_axis": [
            {"id": "believe_omen", "label": "相信", "stance": "believe", "outcome": "accepted"},
            {"id": "doubt_investigate", "label": "怀疑", "stance": "doubt", "outcome": "investigated"},
            {"id": "reject_omen", "label": "拒绝", "stance": "reject", "outcome": "rejected"},
        ],
        "lineage_type": "divergent_worldline",
        "affected_scope": {"characters": ["lin_fan"], "locations": [], "items": [], "rules": [], "scene_flags": []},
    }


def _sparse_draft() -> dict:
    """合法但稀疏：branch_axis 空、intent/desired_effect/affected_scope 缺省。"""
    return {
        "intervention_type": "information",
        "compatibility": {"status": "compatible", "risk": "low"},
        "realization": {"mode": "omen", "description": "低语"},
        "branch_axis": [],
    }


class TestLLMSuccess:
    def test_source_llm_and_meta(self, tianhuang):
        llm = FakeLLM(_information_draft(), usage={"total_tokens": 321})
        comp = compile_intervention_with_llm(
            "今夜竹林有埋伏，提醒林晚舟",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
            llm=llm,
        )
        assert llm.calls == 1
        assert comp.source == "llm"
        assert comp.generation_meta["source"] == "llm"
        assert comp.generation_meta["model_name"] == "fake-compiler"
        assert comp.generation_meta["usage"] == {"total_tokens": 321}
        assert comp.abstract_intervention.intervention_type == "information"
        assert [a.label for a in comp.branch_axis] == ["相信预知", "怀疑但调查", "拒绝预兆"]

    def test_finer_compatibility_reasons_preserved(self, tianhuang):
        llm = FakeLLM(_information_draft())
        comp = compile_intervention_with_llm(
            "提醒林晚舟竹林有埋伏",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
            llm=llm,
        )
        assert any("信息可见性冲突" in r for r in comp.compatibility.reasons)

    def test_target_always_in_affected_scope(self, tianhuang):
        llm = FakeLLM(_information_draft())
        comp = compile_intervention_with_llm(
            "提醒林晚舟",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
            llm=llm,
        )
        assert "lin_wan_zhou" in comp.affected_scope.characters


class TestLLMFallback:
    def test_invalid_json_fallback(self, tianhuang):
        llm = FakeLLM(raise_exc=True)
        comp = compile_intervention_with_llm(
            "提醒林晚舟竹林有埋伏",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
            llm=llm,
        )
        assert comp.source == "fallback"
        assert comp.generation_meta["fallback_reason"]
        assert any("回退 rule-based" in n for n in comp.notes)
        # 仍是一个完整可用的 compilation
        assert comp.branch_axis
        assert comp.abstract_intervention.intervention_type == "information"

    def test_missing_required_field_falls_back(self, tianhuang):
        # 缺 compatibility（必填）→ model_validate 抛错 → 回退
        bad = {"intervention_type": "information", "realization": {"mode": "x"}}
        llm = FakeLLM(bad)
        comp = compile_intervention_with_llm(
            "提醒林晚舟",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
            llm=llm,
        )
        assert comp.source == "fallback"

    def test_no_api_mock_is_rule_based(self, tianhuang):
        comp = compile_intervention_with_llm(
            "提醒林晚舟",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
            llm=LLMClient(mock=True),
        )
        assert comp.source == "rule_based"

    def test_llm_none_is_rule_based(self, tianhuang):
        comp = compile_intervention_with_llm(
            "提醒林晚舟", target="lin_wan_zhou",
            world=tianhuang.world, characters=tianhuang.character_map(), llm=None,
        )
        assert comp.source == "rule_based"


class TestLLMRepair:
    def test_sparse_draft_repaired(self, tianhuang):
        llm = FakeLLM(_sparse_draft())
        comp = compile_intervention_with_llm(
            "提醒林晚舟竹林有埋伏",
            target="lin_wan_zhou",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
            llm=llm,
        )
        # 修复后仍是 llm 来源，但 branch_axis 被补齐
        assert comp.source == "llm"
        assert comp.branch_axis
        assert any("就地修复" in n for n in comp.notes)


class TestRuleRewriteSafety:
    def test_llm_lies_but_no_pollution(self, tianhuang):
        """LLM 把 AK47 误判为普通分叉，安全兜底必须纠正。"""
        llm = FakeLLM(_rule_rewrite_liar_draft())
        comp = compile_intervention_with_llm(
            "给林凡一把AK47去扫平竹林",
            target="lin_fan",
            world=tianhuang.world,
            characters=tianhuang.character_map(),
            llm=llm,
        )
        assert comp.source == "llm"
        assert comp.abstract_intervention.intervention_type == "rule_rewrite"
        assert comp.lineage_type == "alternate_novel"
        assert comp.realization.in_world is False
        assert comp.compatibility.status == "incompatible"
        assert comp.compatibility.risk == "high"
        outcomes = {a.outcome for a in comp.branch_axis}
        assert {"rejected", "translated", "alternate"}.issubset(outcomes)
        assert comp.generation_meta["reconciled"] is True

    @pytest.mark.parametrize(
        "text",
        ["给林晚舟绑定一个签到系统", "让墨青烟其实是穿越者带着金手指"],
    )
    def test_system_and_time_travel_safety(self, text, tianhuang):
        llm = FakeLLM(_rule_rewrite_liar_draft())
        comp = compile_intervention_with_llm(
            text, target="lin_wan_zhou",
            world=tianhuang.world, characters=tianhuang.character_map(), llm=llm,
        )
        assert comp.lineage_type == "alternate_novel"
        assert comp.realization.in_world is False


class TestDraftSchema:
    def test_draft_validates(self):
        draft = LLMCompilationDraft.model_validate(_information_draft())
        assert draft.intervention_type == "information"
        assert len(draft.branch_axis) == 3


class TestRuleBasedStillWorks:
    def test_rule_based_source_and_meta(self, tianhuang):
        comp = compile_intervention(
            "提醒林晚舟", target="lin_wan_zhou", world=tianhuang.world,
            characters=tianhuang.character_map(),
        )
        assert comp.source == "rule_based"
        assert comp.generation_meta["source"] == "rule_based"

"""v0.6.4/v0.6.5 `multi_agent_llm` runner 测试。

覆盖：
- 注册为非默认 runner，默认仍是 lightweight。
- mock / 无 API 时回退到确定性 `build_demo_trace`（source="fallback"），契约不变。
- 用 FakeLLM 走真正的 LLM 路径（source="llm"），trace 被消费并投影。
- 隐私加固：未 reveal 私下信息、未 corrected 误解、暗算类公开意图都不泄漏到公开事件。
- v0.6.5：generation_meta（source / model_name / attempt_count / usage / validator_warnings）；
  有限重试（env 控制）；usage 缺失不报错；meta 写进 multi_agent_trace.json。
"""

from __future__ import annotations

import json
from types import SimpleNamespace

from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.models.events import SimulationResult
from living_novel_engine.orchestrator import (
    SceneRequest,
    available_runners,
    build_branch_specs,
    dispatch_scene,
    get_runner,
)
from living_novel_engine.orchestrator.runners.multi_agent_llm import (
    generate_trace,
    run_multi_agent_llm,
)
from living_novel_engine.orchestrator.runners.protocol import MultiAgentTrace
from living_novel_engine.samples import load_sample

WHISPER = "今晚不要去城外竹林"
SECRET = "我其实早已识破这场骗局"


def _request(*, believe: bool, llm=None, max_rounds: int = 3) -> SceneRequest:
    bundle = load_sample("tianhuang-night")
    llm = llm or LLMClient(mock=True)
    inv = audit_intervention(
        build_intervention(target="lin_wan_zhou", content=WHISPER, intervention_type="whisper"),
        bundle.world,
        bundle.character_map(),
    )
    inv.story_slug = "tianhuang-night"
    inv.source_kind = "builtin"
    specs = build_branch_specs(inv, 3)
    spec = next(s for s in specs if (s.branch_seed == "believe") == believe)
    return SceneRequest(
        world=bundle.world,
        characters=bundle.characters,
        intervention=inv,
        spec=spec,
        llm=llm,
        max_rounds=max_rounds,
        canon_excerpt=bundle.canon_chapter,
        canon_chapter=bundle.canon_chapter,
    )


class FakeLLM:
    """伪 LLM：mock=False、available=True，按预设 payload 返回 trace 或抛错。"""

    def __init__(self, payload: dict | None = None, *, raise_exc: bool = False,
                 model_name: str = "fake-model", usage: dict | None = None):
        self.mock = False
        self.available = True
        self._payload = payload
        self._raise = raise_exc
        self._usage = usage
        self.settings = SimpleNamespace(llm_model_name=model_name)
        self.json_calls = 0
        self.chat_calls = 0

    def chat_json_with_usage(self, system, user, model_type, *, temperature: float = 0.4):
        self.json_calls += 1
        if self._raise:
            raise ValueError("模拟解析失败")
        return model_type.model_validate(self._payload), self._usage

    def chat(self, system, user, *, temperature: float = 0.7, max_tokens: int = 4096):
        self.chat_calls += 1
        return "【FakeLLM 渲染】这一幕在雨夜的天荒城静静展开。"


class FlakyLLM(FakeLLM):
    """前几次失败 / 返回坏数据，之后成功，用于测试重试。"""

    def __init__(self, steps: list, **kw):
        super().__init__(**kw)
        self._steps = steps  # 每步是 "raise" | "empty" | payload dict

    def chat_json_with_usage(self, system, user, model_type, *, temperature: float = 0.4):
        self.json_calls += 1
        step = self._steps[min(self.json_calls - 1, len(self._steps) - 1)]
        if step == "raise":
            raise ValueError("模拟失败")
        if step == "empty":
            return model_type.model_validate({"turn_plans": []}), None
        return model_type.model_validate(step), self._usage


def _llm_trace_payload() -> dict:
    """一份「乱标 visibility + 非法回合号」的 LLM 产出，用于验证校验/加固。"""
    return {
        "worldline_id": "",
        "branch_seed": "",
        "turn_plans": [
            {
                "round_num": 1,
                "actor_id": "lin_wan_zhou",
                "intents": [
                    {
                        "actor_id": "lin_wan_zhou",
                        "intent_type": "declare",
                        "description": "当众表态会留意夜路安危",
                        "visibility": "public",
                        "confidence": 0.6,
                    },
                    {
                        "actor_id": "lin_wan_zhou",
                        "intent_type": "conceal",
                        "motivation": "不愿暴露已起疑",
                        "description": SECRET,
                        "visibility": "public",
                        "confidence": 0.7,
                    },
                ],
                "delayed_actions": [
                    {
                        "actor_id": "lin_wan_zhou",
                        "action_type": "resolve",
                        "description": "改日再定去留",
                        "created_round": 1,
                        "due_round": 0,
                    }
                ],
                "relationship_signals": [
                    {
                        "signal_id": "s1",
                        "from_id": "lin_wan_zhou",
                        "to_id": "lin_fan",
                        "change": "trust+",
                        "magnitude": 0.3,
                    }
                ],
            }
        ],
        "private_knowledge": [
            {
                "fact_id": "pk1",
                "owner_id": "lin_wan_zhou",
                "content": f"外部低语：{WHISPER}",
                "visibility": "public",
                "revealed": False,
                "source": "intervention",
            }
        ],
        "misunderstandings": [
            {
                "holder_id": "lin_wan_zhou",
                "about": "低语来源",
                "believed": "故友相邀",
                "reality": "实为设局",
                "visibility": "public",
                "corrected": False,
            }
        ],
    }


# ── 注册 / 默认不变 ────────────────────────────────────────────


def test_llm_runner_registered_but_not_default():
    assert "multi_agent_llm" in available_runners()
    assert get_runner().name == "lightweight"
    assert get_runner("multi_agent_llm").name == "multi_agent_llm"


# ── mock 回退 ──────────────────────────────────────────────────


def test_generate_trace_falls_back_under_mock():
    trace, meta = generate_trace(_request(believe=True))
    assert meta.source == "fallback"
    assert meta.fallback_reason == "mock_or_unavailable"
    assert meta.validation_status == "fallback"
    assert isinstance(trace, MultiAgentTrace)
    assert trace.turn_plans


def test_llm_runner_keeps_contract_under_mock():
    result = dispatch_scene(_request(believe=True), runner_name="multi_agent_llm")
    assert isinstance(result, SimulationResult)
    assert result.runner_name == "multi_agent_llm"
    assert result.accepted_events
    assert result.chapter_text.strip()
    assert result.multi_agent_trace is not None
    assert result.state_snapshot.get("branch_seed") == "believe"
    # generation_meta 以 additive 写进 trace
    assert result.multi_agent_trace["generation_meta"]["source"] == "fallback"


# ── 真正 LLM 路径（FakeLLM） ───────────────────────────────────


def test_generate_trace_uses_llm_payload():
    fake = FakeLLM(_llm_trace_payload())
    trace, meta = generate_trace(_request(believe=False, llm=fake))
    assert meta.source == "llm"
    assert meta.model_name == "fake-model"
    assert meta.attempt_count == 1
    assert fake.json_calls == 1
    assert trace.branch_seed == "doubt"
    assert trace.worldline_id


def test_meta_written_into_trace_artifact_dict():
    fake = FakeLLM(_llm_trace_payload())
    result = run_multi_agent_llm(_request(believe=False, llm=fake))
    gm = result.multi_agent_trace["generation_meta"]
    assert gm["source"] == "llm"
    assert gm["model_name"] == "fake-model"
    assert gm["cost_estimate"] is None


def test_llm_path_privacy_hardening():
    fake = FakeLLM(_llm_trace_payload())
    result = run_multi_agent_llm(_request(believe=False, llm=fake))
    dumped = json.dumps([e.model_dump() for e in result.accepted_events], ensure_ascii=False)
    assert SECRET not in dumped
    assert WHISPER not in dumped
    assert WHISPER not in result.chapter_text
    assert "实为设局" not in dumped
    trace_dump = json.dumps(result.multi_agent_trace, ensure_ascii=False)
    assert WHISPER in trace_dump
    assert SECRET in trace_dump


def test_llm_path_public_intent_projected():
    fake = FakeLLM(_llm_trace_payload())
    result = run_multi_agent_llm(_request(believe=False, llm=fake))
    intent_events = [
        e for e in result.accepted_events if e.payload.get("source") == "agent_intent"
    ]
    assert len(intent_events) == 1
    assert "留意夜路" in intent_events[0].narrative


def test_llm_delayed_due_round_normalized():
    fake = FakeLLM(_llm_trace_payload())
    trace, meta = generate_trace(_request(believe=False, llm=fake))
    da = trace.turn_plans[0].delayed_actions[0]
    # due_round=0 < created_round=1 被归一化为 >=created_round
    assert da.due_round == 1
    # validator 触发了修复
    assert meta.validation_status == "repaired"


# ── usage / 成本 ───────────────────────────────────────────────


def test_usage_recorded_when_present():
    usage = {"prompt_tokens": 120, "completion_tokens": 80, "total_tokens": 200}
    fake = FakeLLM(_llm_trace_payload(), usage=usage)
    _, meta = generate_trace(_request(believe=False, llm=fake))
    assert meta.usage == usage


def test_usage_missing_does_not_error():
    fake = FakeLLM(_llm_trace_payload(), usage=None)
    _, meta = generate_trace(_request(believe=False, llm=fake))
    assert meta.usage is None


# ── 有限重试 ───────────────────────────────────────────────────


def test_retry_then_success(monkeypatch):
    monkeypatch.setenv("LNE_MULTI_AGENT_MAX_RETRIES", "1")
    flaky = FlakyLLM(["raise", _llm_trace_payload()])
    trace, meta = generate_trace(_request(believe=False, llm=flaky))
    assert meta.source == "llm"
    assert meta.attempt_count == 2
    assert flaky.json_calls == 2
    assert trace.turn_plans


def test_retry_disabled_falls_back(monkeypatch):
    monkeypatch.setenv("LNE_MULTI_AGENT_MAX_RETRIES", "0")
    flaky = FlakyLLM(["raise", _llm_trace_payload()])
    _, meta = generate_trace(_request(believe=True, llm=flaky))
    assert meta.source == "fallback"
    assert meta.attempt_count == 1
    assert flaky.json_calls == 1


def test_hard_fail_empty_turn_plans_then_fallback(monkeypatch):
    monkeypatch.setenv("LNE_MULTI_AGENT_MAX_RETRIES", "1")
    flaky = FlakyLLM(["empty", "empty"])
    trace, meta = generate_trace(_request(believe=True, llm=flaky))
    assert meta.source == "fallback"
    assert meta.fallback_reason == "validator_hard_fail"
    assert meta.attempt_count == 2
    assert trace.turn_plans  # 回退后非空


def test_fallback_on_llm_error_records_reason():
    fake = FakeLLM(raise_exc=True)
    trace, meta = generate_trace(_request(believe=True, llm=fake))
    assert meta.source == "fallback"
    assert meta.fallback_reason.startswith("llm_error")
    assert trace.turn_plans

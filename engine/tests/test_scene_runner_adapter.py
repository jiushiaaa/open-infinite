from __future__ import annotations

import json

import pytest

from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.models.events import SimulationResult
from living_novel_engine.orchestrator import (
    DEFAULT_RUNNER,
    SceneRequest,
    SceneRunner,
    available_runners,
    build_branch_specs,
    dispatch_scene,
    get_runner,
    register_runner,
    run_scene,
)
from living_novel_engine.orchestrator.runners import RunnerError, resolve_runner_name
from living_novel_engine.output.writer import write_run_output
from living_novel_engine.samples import load_sample


def _branch_a_request(max_rounds: int = 2) -> SceneRequest:
    bundle = load_sample("tianhuang-night")
    llm = LLMClient(mock=True)
    inv = audit_intervention(
        build_intervention(
            target="lin_wan_zhou",
            content="今晚不要去城外竹林",
            intervention_type="whisper",
        ),
        bundle.world,
        bundle.character_map(),
    )
    inv.story_slug = "tianhuang-night"
    inv.source_kind = "builtin"
    spec = next(s for s in build_branch_specs(inv, 3) if s.branch_id == "branch_a")
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


# ── 注册表 / 解析 ──────────────────────────────────────────────


def test_lightweight_registered_by_default():
    assert DEFAULT_RUNNER == "lightweight"
    assert "lightweight" in available_runners()
    assert get_runner().name == "lightweight"
    assert get_runner("lightweight").name == "lightweight"


def test_resolve_priority_explicit_over_env(monkeypatch):
    monkeypatch.setenv("LNE_SCENE_RUNNER", "from_env")
    assert resolve_runner_name("explicit") == "explicit"
    assert resolve_runner_name(None) == "from_env"
    monkeypatch.delenv("LNE_SCENE_RUNNER", raising=False)
    assert resolve_runner_name(None) == "lightweight"


def test_unknown_runner_raises():
    with pytest.raises(RunnerError):
        get_runner("does-not-exist")


def test_register_duplicate_requires_overwrite():
    class Dummy(SceneRunner):
        name = "lightweight"

        def run(self, request):  # pragma: no cover - 不应被调用
            raise AssertionError

    with pytest.raises(RunnerError):
        register_runner(Dummy())


# ── 默认 runner：契约不变 ──────────────────────────────────────


def test_run_scene_uses_lightweight_and_keeps_contract():
    result = run_scene(
        **_request_as_kwargs(_branch_a_request())
    )
    assert isinstance(result, SimulationResult)
    assert result.runner_name == "lightweight"
    assert result.accepted_events
    assert result.state_snapshot.get("branch_seed") == "believe"
    assert result.chapter_text.strip()


def _request_as_kwargs(req: SceneRequest) -> dict:
    return {
        "world": req.world,
        "characters": req.characters,
        "intervention": req.intervention,
        "spec": req.spec,
        "llm": req.llm,
        "max_rounds": req.max_rounds,
        "canon_excerpt": req.canon_excerpt,
        "canon_chapter": req.canon_chapter,
    }


def test_dispatch_scene_equivalent_to_run_scene():
    req = _branch_a_request()
    via_dispatch = dispatch_scene(req)
    assert via_dispatch.runner_name == "lightweight"
    assert via_dispatch.worldline_id == "branch_a"


# ── 自定义 runner 可替换 ───────────────────────────────────────


class StubRunner(SceneRunner):
    name = "stub-test"

    def run(self, request: SceneRequest) -> SimulationResult:
        return SimulationResult(
            worldline_id=request.spec.branch_id,
            branch_seed=request.spec.branch_seed,
            theme=request.spec.theme,
            termination_reason="stub",
            chapter_text="（stub runner 产出）",
        )


def test_custom_runner_swappable_via_param():
    register_runner(StubRunner(), overwrite=True)
    assert "stub-test" in available_runners()
    result = run_scene(
        **_request_as_kwargs(_branch_a_request()),
        runner_name="stub-test",
    )
    assert result.runner_name == "stub-test"
    assert result.termination_reason == "stub"


def test_custom_runner_swappable_via_env(monkeypatch):
    register_runner(StubRunner(), overwrite=True)
    monkeypatch.setenv("LNE_SCENE_RUNNER", "stub-test")
    result = run_scene(**_request_as_kwargs(_branch_a_request()))
    assert result.runner_name == "stub-test"


def test_dispatch_sets_runner_name_when_missing():
    class NoNameRunner(SceneRunner):
        name = "noname-test"

        def run(self, request: SceneRequest) -> SimulationResult:
            # 故意不设置 runner_name（留默认）；dispatch 不应覆盖非空默认
            r = SimulationResult(
                worldline_id="x", branch_seed="believe", theme="t"
            )
            r.runner_name = ""
            return r

    register_runner(NoNameRunner(), overwrite=True)
    result = dispatch_scene(_branch_a_request(), runner_name="noname-test")
    assert result.runner_name == "noname-test"


# ── runner 名进入 events.json ──────────────────────────────────


def test_runner_name_written_to_events(tmp_path, monkeypatch):
    import living_novel_engine.output.writer as writer_mod

    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)

    result = run_scene(**_request_as_kwargs(_branch_a_request()))
    inv = _branch_a_request().intervention
    out = write_run_output(inv, [result], run_id="test_runner_events")
    events = json.loads(
        (out.run_dir / "branch_a" / "events.json").read_text(encoding="utf-8")
    )
    assert events.get("runner") == "lightweight"

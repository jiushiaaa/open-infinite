from __future__ import annotations

from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.orchestrator.narrative_constraints import (
    build_narrative_constraints,
    summary_from_snapshot,
    validate_chapter_against_snapshot,
)
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import build_branch_specs
from living_novel_engine.samples import load_sample


def _run_branch(bundle, seed: str, rounds: int = 3):
    llm = LLMClient(mock=True)
    intervention = audit_intervention(
        build_intervention(
            target="lin_wan_zhou",
            content="今晚不要去城外竹林",
            intervention_type="whisper",
        ),
        bundle.world,
        bundle.character_map(),
    )
    spec = next(s for s in build_branch_specs(intervention, count=3) if s.branch_seed == seed)
    return run_scene(
        bundle.world,
        bundle.characters,
        intervention,
        spec,
        llm,
        max_rounds=rounds,
        canon_excerpt=bundle.canon_context_for_narrator(),
        prologue=bundle.prologue,
        canon_opening=bundle.canon_opening,
        canon_chapter=bundle.canon_chapter,
    )


def test_jade_slip_at_most_one_use_item_event():
    bundle = load_sample("tianhuang-night")
    result = _run_branch(bundle, "believe", rounds=4)
    jade_events = [
        e
        for e in result.accepted_events
        if e.subject == "lin_fan" and e.event_type in ("use_item", "message")
        and ("玉简" in e.payload.get("content", "") or "传讯" in e.payload.get("content", ""))
    ]
    assert len(jade_events) <= 1


def test_fan_warning_at_most_one_communicate_style():
    bundle = load_sample("tianhuang-night")
    result = _run_branch(bundle, "believe", rounds=4)
    warn_events = [
        e
        for e in result.accepted_events
        if e.subject == "lin_fan"
        and e.event_type
        in (
            "communicate",
            "message",
            "message_transmission",
            "subtle_interference",
            "use_item",
        )
        and "师姐" in e.payload.get("content", "")
    ]
    assert len(warn_events) <= 1
    assert result.final_scene_state.get("fan_warning_delivered")


def test_believe_branch_stays_in_city_flags():
    bundle = load_sample("tianhuang-night")
    result = _run_branch(bundle, "believe")
    flags = result.state_snapshot["scene_flags"]
    assert flags["lin_wan_zhou_departed"] is False
    assert flags["bamboo_grove_triggered"] is False
    assert flags.get("investigating") is True


def test_doubt_branch_no_bamboo():
    bundle = load_sample("tianhuang-night")
    result = _run_branch(bundle, "doubt")
    flags = result.state_snapshot["scene_flags"]
    assert flags["lin_wan_zhou_departed"] is False
    assert flags["bamboo_grove_triggered"] is False


def test_reject_branch_departs():
    bundle = load_sample("tianhuang-night")
    result = _run_branch(bundle, "reject")
    flags = result.state_snapshot["scene_flags"]
    assert flags["lin_wan_zhou_departed"] is True


def test_reject_branch_lwz_location_synced_to_bamboo():
    bundle = load_sample("tianhuang-night")
    result = _run_branch(bundle, "reject", rounds=4)
    flags = result.state_snapshot["scene_flags"]
    lwz = result.state_snapshot["characters"]["lin_wan_zhou"]
    if flags.get("bamboo_grove_triggered"):
        assert "竹林" in lwz["location"] or "城外" in lwz["location"]
    elif flags.get("lin_wan_zhou_departed"):
        assert "门外" in lwz["location"] or "城外" in lwz["location"]


def test_polish_chapter_fixes_city_and_jade_wording():
    from living_novel_engine.orchestrator.narrative_constraints import polish_chapter_text

    bundle = load_sample("tianhuang-night")
    raw = "青云城内，林晚舟手中的传讯玉简微微发烫。"
    out = polish_chapter_text(raw, bundle.world)
    assert "天荒城" in out
    assert "青云城" not in out
    assert "手中的传讯玉简" not in out


def test_summary_never_empty():
    bundle = load_sample("tianhuang-night")
    result = _run_branch(bundle, "doubt")
    assert result.summary_text.strip()


def test_narrative_constraints_forbid_bamboo_when_not_departed():
    snap = {
        "scene_flags": {
            "lin_wan_zhou_departed": False,
            "bamboo_grove_triggered": False,
            "investigating": True,
            "jade_slip_used": True,
        },
        "next_chapter_hook": "调查",
    }
    text = "林晚舟踏入城外竹林，与墨青烟在竹林石亭对峙。"
    violations = validate_chapter_against_snapshot(text, snap)
    assert violations
    constraints = build_narrative_constraints(
        snap, branch_seed="believe", branch_theme="相信干预"
    )
    assert "林晚舟尚未离城赴约" in constraints


def test_render_chapter_structured_when_repair_empty_on_believe(monkeypatch):
    from living_novel_engine.agents import narrator as narrator_mod

    bundle = load_sample("tianhuang-night")
    result = _run_branch(bundle, "believe", rounds=2)
    calls: list[int] = []

    def fake_chat(system, user, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            return "首稿：林晚舟已至城外竹林石亭，与墨青烟对峙。"
        return ""

    llm = LLMClient(mock=False)
    monkeypatch.setattr(llm, "chat", fake_chat)
    monkeypatch.setattr(
        narrator_mod,
        "validate_chapter_against_snapshot",
        lambda _t, _s: ["违规测试"],
    )

    text = narrator_mod.render_chapter(
        bundle.world,
        result,
        bundle.canon_chapter,
        llm,
        state_snapshot=result.state_snapshot,
    )
    assert text.strip()
    assert "第13章" in text or "第十三章" in text
    assert "引擎结构化草稿" not in text
    assert "未踏入城外" in text or "林晚舟" in text
    assert "竹林石亭" not in text


def test_chapter_from_snapshot_nonempty():
    from living_novel_engine.orchestrator.narrative_constraints import (
        chapter_from_snapshot_and_events,
    )

    bundle = load_sample("tianhuang-night")
    result = _run_branch(bundle, "doubt", rounds=2)
    text = chapter_from_snapshot_and_events(result, result.state_snapshot)
    assert len(text) > 100
    assert "林晚舟" in text or "林凡" in text


def test_summary_fallback_helper():
    bundle = load_sample("tianhuang-night")
    result = _run_branch(bundle, "reject")
    text = summary_from_snapshot(bundle.display_name, result)
    assert "拒绝" in text or "赴约" in text or "林晚舟" in text

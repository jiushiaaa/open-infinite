from __future__ import annotations

import json
from pathlib import Path

import pytest

from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import build_continuation_spec
from living_novel_engine.output.writer import write_resume_output, write_run_output
from living_novel_engine.resume import (
    build_seed_scene_state,
    load_parent_snapshot,
    project_characters_from_parent,
)
from living_novel_engine.samples import load_sample


def _parent_from_intervene(tmp_path, monkeypatch, branch_id: str = "branch_a"):
    import living_novel_engine.output.writer as writer_mod

    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)

    bundle = load_sample("tianhuang-night")
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
    intervention.story_slug = "tianhuang-night"
    intervention.source_kind = "builtin"
    from living_novel_engine.orchestrator.worldline_brancher import build_branch_specs

    spec = next(s for s in build_branch_specs(intervention, 3) if s.branch_id == branch_id)
    result = run_scene(
        bundle.world,
        bundle.characters,
        intervention,
        spec,
        llm,
        max_rounds=2,
        canon_excerpt=bundle.canon_chapter,
        canon_chapter=bundle.canon_chapter,
    )
    out = write_run_output(intervention, [result], run_id="test_parent_run")
    return str(out.run_dir), branch_id


def test_continuation_spec_is_linear():
    spec = build_continuation_spec("believe", "branch_a")
    assert spec.branch_seed == "linear"
    assert spec.branch_id == "linear"
    assert spec.forced_stance == ""


def test_load_parent_snapshot_from_real_run(tmp_path, monkeypatch):
    run_id, branch_id = _parent_from_intervene(tmp_path, monkeypatch)
    parent = load_parent_snapshot(run_id, branch_id)
    assert parent.run_id == "test_parent_run"
    assert parent.branch_id == branch_id
    assert parent.chapter_text
    assert parent.snapshot.get("characters")
    assert parent.sample_slug == "tianhuang-night"

    chars, _ = project_characters_from_parent(parent)
    lwz = next(c for c in chars if c.id == "lin_wan_zhou")
    assert lwz.current_state.location
    assert any("章续前" in m for m in lwz.memory)


def test_resume_continue_no_intervention_runs(tmp_path, monkeypatch):
    run_id, branch_id = _parent_from_intervene(tmp_path, monkeypatch, "branch_a")
    parent = load_parent_snapshot(run_id, branch_id)
    characters, world = project_characters_from_parent(parent)
    spec = build_continuation_spec(parent.branch_seed, parent.branch_id)
    llm = LLMClient(mock=True)

    result = run_scene(
        world,
        characters,
        None,
        spec,
        llm,
        max_rounds=2,
        canon_excerpt=parent.chapter_text,
        canon_chapter=parent.chapter_text,
        seed_scene_state=build_seed_scene_state(parent),
        seed_characters=characters,
        chapter_number=14,
    )
    out = write_resume_output(parent, result)

    meta = json.loads((out.run_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["kind"] == "resume_continue"
    assert meta["parent_run_id"] == parent.run_id
    assert meta["parent_branch"] == branch_id
    assert meta["current_chapter"] == 14

    chapter = (out.run_dir / "linear" / "chapter.md").read_text(encoding="utf-8")
    assert chapter.strip()
    assert (out.run_dir / "linear" / "state_snapshot.json").exists()
    assert (out.run_dir / "parent_chapter.md").exists()

    snap = json.loads(
        (out.run_dir / "linear" / "state_snapshot.json").read_text(encoding="utf-8")
    )
    flags = snap.get("scene_flags") or {}
    events = json.loads((out.run_dir / "linear" / "events.json").read_text(encoding="utf-8"))
    lwz_events = [
        e for e in events.get("accepted_events", []) if e.get("subject") == "lin_wan_zhou"
    ]
    if lwz_events and any(
        "收回" in str(e.get("payload", {}).get("content", ""))
        or e.get("event_type") == "investigate"
        for e in lwz_events
    ):
        if not parent.scene_flags.get("lin_wan_zhou_departed"):
            assert flags.get("lin_wan_zhou_departed") is not True
            assert flags.get("bamboo_grove_triggered") is not True

    chapter_text = chapter
    from living_novel_engine.orchestrator.narrative_constraints import (
        validate_debug_variable_leak,
    )

    assert not validate_debug_variable_leak(chapter_text)

    jade_uses = [
        e
        for e in events.get("accepted_events", [])
        if e.get("subject") == "lin_fan"
        and e.get("event_type") in ("use_item", "message")
        and "玉简" in str(e.get("payload", {}).get("content", ""))
    ]
    if parent.scene_flags.get("jade_slip_used"):
        assert len(jade_uses) == 0


def test_resume_continue_preserves_departed_state(tmp_path, monkeypatch):
    run_id, branch_id = _parent_from_intervene(tmp_path, monkeypatch, "branch_c")
    parent = load_parent_snapshot(run_id, branch_id)
    flags = parent.scene_flags
    if not flags.get("lin_wan_zhou_departed"):
        pytest.skip("mock branch_c 未离城，跳过竹林延续测试")

    characters, world = project_characters_from_parent(parent)
    spec = build_continuation_spec(parent.branch_seed, parent.branch_id)
    llm = LLMClient(mock=True)
    result = run_scene(
        world,
        characters,
        None,
        spec,
        llm,
        max_rounds=2,
        canon_excerpt=parent.chapter_text,
        canon_chapter=parent.chapter_text,
        seed_scene_state=build_seed_scene_state(parent),
        seed_characters=characters,
        chapter_number=14,
    )
    snap = result.state_snapshot
    assert snap["scene_flags"].get("lin_wan_zhou_departed") is True
    lwz = snap["characters"]["lin_wan_zhou"]
    assert "竹林" in lwz["location"] or "城外" in lwz["location"]

from __future__ import annotations

import json

import pytest

from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import (
    build_branch_specs,
    build_continuation_spec,
)
from living_novel_engine.output.writer import (
    write_resume_intervene_output,
    write_resume_output,
    write_run_output,
)
from living_novel_engine.resume import (
    build_seed_scene_state,
    build_seed_scene_state_for_intervene,
    load_parent_snapshot,
    project_characters_from_parent,
)
from living_novel_engine.samples import load_sample


def _chain_continue_parent(tmp_path, monkeypatch, branch_id: str = "branch_a"):
    import living_novel_engine.output.writer as writer_mod
    import living_novel_engine.resume.loader as loader_mod

    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)
    monkeypatch.setattr(loader_mod, "_outputs_dir", lambda: tmp_path)

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
    intervene_out = write_run_output(intervention, [result], run_id="test_ch13_run")

    parent13 = load_parent_snapshot(intervene_out.run_id, branch_id)
    characters, world = project_characters_from_parent(parent13)
    cont_spec = build_continuation_spec(parent13.branch_seed, parent13.branch_id)
    cont_result = run_scene(
        world,
        characters,
        None,
        cont_spec,
        llm,
        max_rounds=2,
        canon_excerpt=parent13.chapter_text,
        canon_chapter=parent13.chapter_text,
        seed_scene_state=build_seed_scene_state(parent13),
        seed_characters=characters,
        chapter_number=14,
    )
    continue_out = write_resume_output(parent13, cont_result)
    return continue_out.run_id, continue_out.run_dir


def test_seed_scene_state_for_intervene_preserves_flags(tmp_path, monkeypatch):
    run_id, _ = _chain_continue_parent(tmp_path, monkeypatch)
    parent = load_parent_snapshot(run_id, "linear")
    seed = build_seed_scene_state_for_intervene(parent, "lin_fan")
    assert seed.get("branch_seed") is None
    assert seed.get("intervention_target") == "lin_fan"
    if parent.scene_flags.get("jade_slip_used"):
        assert seed.get("jade_slip_used") is True


def test_resume_intervene_three_branches_and_meta(tmp_path, monkeypatch):
    run_id, continue_dir = _chain_continue_parent(tmp_path, monkeypatch)
    parent = load_parent_snapshot(run_id, "linear")
    characters, world = project_characters_from_parent(parent)
    bundle = load_sample(parent.sample_slug)

    intervention = audit_intervention(
        build_intervention(
            target="lin_fan",
            content="告诉林晚舟，她身后的影子来自乱葬岗",
            intervention_type="whisper",
        ),
        bundle.world,
        bundle.character_map(),
    )
    llm = LLMClient(mock=True)
    seed = build_seed_scene_state_for_intervene(parent, intervention.target)
    specs = build_branch_specs(intervention, 3)
    results = []
    for spec in specs:
        results.append(
            run_scene(
                world,
                characters,
                intervention,
                spec,
                llm,
                max_rounds=2,
                canon_excerpt=parent.chapter_text,
                canon_chapter=parent.chapter_text,
                seed_scene_state=seed,
                seed_characters=characters,
                chapter_number=15,
            )
        )

    out = write_resume_intervene_output(parent, intervention, results)
    meta = json.loads((out.run_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["kind"] == "resume_intervene"
    assert meta["parent_run_id"] == run_id
    assert meta["parent_branch"] == "linear"
    assert meta["parent_chapter"] == 14
    assert meta["current_chapter"] == 15
    assert f"{run_id}:linear" in meta["lineage"]
    assert "believe" in meta.get("branch_seed_lineage", [])

    for bid in ("branch_a", "branch_b", "branch_c"):
        assert (out.run_dir / bid / "chapter.md").read_text(encoding="utf-8").strip()
        events = json.loads((out.run_dir / bid / "events.json").read_text(encoding="utf-8"))
        assert events.get("chapter") == 15
        assert events.get("branch_seed") in ("believe", "doubt", "reject")

    assert (out.run_dir / "intervention.json").exists()
    assert (out.run_dir / "compare.md").exists()
    assert (out.run_dir / "parent_chapter.md").exists()

    inv = json.loads((out.run_dir / "intervention.json").read_text(encoding="utf-8"))
    assert inv.get("resume_parent_run_id") == run_id
    assert inv.get("resume_parent_branch") == "linear"

    if parent.scene_flags.get("jade_slip_used"):
        for spec in specs:
            snap = json.loads(
                (out.run_dir / spec.branch_id / "state_snapshot.json").read_text(
                    encoding="utf-8"
                )
            )
            assert snap.get("scene_flags", {}).get("jade_slip_used") is True

    from living_novel_engine.orchestrator.narrative_constraints import (
        is_structured_chapter_fallback,
    )

    for bid in ("branch_a", "branch_b", "branch_c"):
        chapter = (out.run_dir / bid / "chapter.md").read_text(encoding="utf-8")
        assert not is_structured_chapter_fallback(chapter), (
            f"{bid} 不应落为带引擎标记的结构化兜底"
        )
        events = json.loads((out.run_dir / bid / "events.json").read_text(encoding="utf-8"))
        blob = json.dumps(events, ensure_ascii=False)
        if parent.scene_flags.get("jade_slip_used"):
            assert "应急竹简" not in blob
            assert "墨色竹简" not in blob

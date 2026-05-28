"""v0.2.1：imported project 上的 resume continue / resume intervene。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from living_novel_engine.import_novel.mock_extractor import mock_extract
from living_novel_engine.import_novel.splitter import split_chapters
from living_novel_engine.import_novel.writer import write_project
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
from living_novel_engine.story_loader import load_story

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "mini_novel"
STORY_SLUG = "resume-test"


def _patch_dirs(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    projects_dir = tmp_path / "projects"
    outputs_dir = tmp_path / "outputs"
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects_dir))
    import living_novel_engine.output.writer as writer_mod
    import living_novel_engine.resume.loader as loader_mod

    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: outputs_dir)
    monkeypatch.setattr(loader_mod, "_outputs_dir", lambda: outputs_dir)
    return projects_dir, outputs_dir


def _imported_intervene_run(
    tmp_path: Path,
    monkeypatch,
    *,
    branch_id: str = "branch_a",
    run_id: str = "imported_intervene_run",
) -> tuple[str, str]:
    projects_dir, _ = _patch_dirs(tmp_path, monkeypatch)
    chapters = split_chapters(FIXTURES_DIR)
    extraction = mock_extract(chapters, story_name=STORY_SLUG)
    write_project(STORY_SLUG, chapters, extraction, projects_dir=projects_dir)

    bundle = load_story(STORY_SLUG)
    llm = LLMClient(mock=True)
    intervention = audit_intervention(
        build_intervention(
            target="zhao_xuan",
            content="今夜不要去归云斋",
            intervention_type="whisper",
        ),
        bundle.world,
        bundle.character_map(),
    )
    intervention.story_slug = STORY_SLUG
    intervention.source_kind = "imported"

    spec = next(s for s in build_branch_specs(intervention, 3) if s.branch_id == branch_id)
    result = run_scene(
        bundle.world,
        bundle.characters,
        intervention,
        spec,
        llm,
        max_rounds=2,
        canon_excerpt=bundle.canon_context_for_narrator(),
        canon_chapter=bundle.canon_chapter,
        source_type="imported",
    )
    out = write_run_output(intervention, [result], run_id=run_id)
    return out.run_id, branch_id


class TestResumeContinueImported:
    def test_load_parent_has_story_metadata(self, tmp_path, monkeypatch):
        run_id, branch_id = _imported_intervene_run(tmp_path, monkeypatch)
        parent = load_parent_snapshot(run_id, branch_id)
        assert parent.story_slug == STORY_SLUG
        assert parent.source_kind == "imported"
        assert parent.sample_slug == STORY_SLUG

    def test_resume_continue_linear(self, tmp_path, monkeypatch):
        run_id, branch_id = _imported_intervene_run(tmp_path, monkeypatch)
        parent = load_parent_snapshot(run_id, branch_id)
        characters, world = project_characters_from_parent(parent)
        bundle = load_story(parent.story_slug)

        spec = build_continuation_spec(parent.branch_seed, parent.branch_id)
        next_chapter = parent.chapter_number + 1
        llm = LLMClient(mock=True)

        result = run_scene(
            world,
            characters,
            None,
            spec,
            llm,
            max_rounds=2,
            canon_excerpt=parent.chapter_text,
            prologue=bundle.prologue,
            canon_opening=bundle.canon_opening,
            canon_chapter=parent.chapter_text,
            seed_scene_state=build_seed_scene_state(parent),
            seed_characters=characters,
            chapter_number=next_chapter,
            source_type=parent.source_type,
        )
        out = write_resume_output(parent, result)

        meta = json.loads((out.run_dir / "meta.json").read_text(encoding="utf-8"))
        assert meta["kind"] == "resume_continue"
        assert meta["story_slug"] == STORY_SLUG
        assert meta["source_kind"] == "imported"
        assert (out.run_dir / "linear" / "chapter.md").exists()

        events = json.loads(
            (out.run_dir / "linear" / "events.json").read_text(encoding="utf-8")
        )
        all_text = " ".join(
            str(e.get("payload", {}).get("content", "")) + e.get("narrative", "")
            for e in events.get("accepted_events", [])
        )
        for marker in ("传讯玉简", "林晚舟", "林凡", "听雨轩", "竹林"):
            assert marker not in all_text, f"续章不应含天荒城术语: {marker}"


class TestResumeInterveneImported:
    def test_full_chain_intervene_continue_intervene(self, tmp_path, monkeypatch):
        run_id, branch_id = _imported_intervene_run(tmp_path, monkeypatch)

        parent13 = load_parent_snapshot(run_id, branch_id)
        chars13, world13 = project_characters_from_parent(parent13)
        bundle = load_story(parent13.story_slug)
        llm = LLMClient(mock=True)

        cont = run_scene(
            world13,
            chars13,
            None,
            build_continuation_spec(parent13.branch_seed, parent13.branch_id),
            llm,
            max_rounds=2,
            canon_excerpt=parent13.chapter_text,
            canon_chapter=parent13.chapter_text,
            seed_scene_state=build_seed_scene_state(parent13),
            seed_characters=chars13,
            chapter_number=parent13.chapter_number + 1,
            source_type=parent13.source_type,
        )
        continue_out = write_resume_output(parent13, cont)

        parent14 = load_parent_snapshot(continue_out.run_id, "linear")
        assert parent14.source_kind == "imported"
        assert parent14.story_slug == STORY_SLUG

        chars14, world14 = project_characters_from_parent(parent14)
        intervention = audit_intervention(
            build_intervention(
                target="shen_bing_yue",
                content="韩无归没有说出全部真相",
                intervention_type="whisper",
            ),
            world14,
            {c.id: c for c in chars14},
        )
        intervention.story_slug = STORY_SLUG
        intervention.source_kind = "imported"

        specs = build_branch_specs(intervention, 3)
        results = [
            run_scene(
                world14,
                chars14,
                intervention,
                spec,
                llm,
                max_rounds=2,
                canon_excerpt=parent14.chapter_text,
                prologue=bundle.prologue,
                canon_chapter=parent14.chapter_text,
                seed_scene_state=build_seed_scene_state_for_intervene(
                    parent14, "shen_bing_yue"
                ),
                seed_characters=chars14,
                chapter_number=parent14.chapter_number + 1,
                source_type=parent14.source_type,
            )
            for spec in specs
        ]
        ri_out = write_resume_intervene_output(parent14, intervention, results)

        meta = json.loads((ri_out.run_dir / "meta.json").read_text(encoding="utf-8"))
        assert meta["story_slug"] == STORY_SLUG
        assert meta["source_kind"] == "imported"

        inv = json.loads(
            (ri_out.run_dir / "intervention.json").read_text(encoding="utf-8")
        )
        assert inv["story_slug"] == STORY_SLUG
        assert inv["source_kind"] == "imported"
        assert inv["sample_slug"] == STORY_SLUG
        assert inv["sample_slug"] != "tianhuang-night"

        assert len(list(ri_out.run_dir.glob("branch_*"))) == 3

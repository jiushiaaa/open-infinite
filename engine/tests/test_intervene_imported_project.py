"""测试 imported project 可通过 load_story + intervene 跑通三分叉。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from living_novel_engine.import_novel.splitter import split_chapters
from living_novel_engine.import_novel.mock_extractor import mock_extract
from living_novel_engine.import_novel.writer import write_project
from living_novel_engine.import_novel.validator import validate_project
from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import build_branch_specs
from living_novel_engine.output.writer import write_run_output
from living_novel_engine.story_loader import StoryBundle, load_story


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "mini_novel"


def _setup_imported_project(tmp_path: Path) -> Path:
    chapters = split_chapters(FIXTURES_DIR)
    extraction = mock_extract(chapters, story_name="int-test")
    return write_project("int-test", chapters, extraction, projects_dir=tmp_path)


class TestLoadStory:
    def test_load_builtin(self):
        bundle = load_story("tianhuang-night")
        assert bundle.source_kind == "builtin"
        assert bundle.world.source_type == "builtin_sample"

    def test_load_imported(self, tmp_path: Path, monkeypatch):
        project_dir = _setup_imported_project(tmp_path)
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))

        bundle = load_story("int-test")
        assert bundle.source_kind == "imported"
        assert bundle.world.source_type == "imported"
        assert len(bundle.characters) >= 2

    def test_load_not_found(self):
        with pytest.raises(FileNotFoundError, match="不存在"):
            load_story("nonexistent-slug-xyz")


class TestInterveneImported:
    def test_three_branches_mock(self, tmp_path: Path, monkeypatch):
        """imported project mock intervene 产生三分支。"""
        _setup_imported_project(tmp_path)
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))

        bundle = load_story("int-test")
        char_map = bundle.character_map()
        target_id = "zhao_xuan"
        assert target_id in char_map

        intervention = build_intervention(
            target=target_id,
            content="今夜不要去归云斋，韩无归已布下陷阱",
            intervention_type="whisper",
        )
        intervention = audit_intervention(intervention, bundle.world, char_map)
        intervention.story_slug = "int-test"
        intervention.source_kind = "imported"

        assert intervention.contract_audit is not None
        assert intervention.contract_audit.allowed is True

        llm = LLMClient(mock=True)
        specs = build_branch_specs(intervention, count=3)
        assert len(specs) == 3

        results = []
        for spec in specs:
            result = run_scene(
                bundle.world,
                bundle.characters,
                intervention,
                spec,
                llm,
                max_rounds=4,
                canon_excerpt=bundle.canon_context_for_narrator(),
                prologue=bundle.prologue,
                canon_opening=bundle.canon_opening,
                canon_chapter=bundle.canon_chapter,
                source_type=bundle.world.source_type,
            )
            results.append(result)

        assert len(results) == 3
        branch_ids = [r.worldline_id for r in results]
        assert "branch_a" in branch_ids
        assert "branch_b" in branch_ids
        assert "branch_c" in branch_ids

        for r in results:
            assert len(r.accepted_events) > 0
            assert r.chapter_text  # mock 生成的章节非空
            assert r.state_snapshot is not None

    def test_no_tianhuang_pollution(self, tmp_path: Path, monkeypatch):
        """imported 结果不含天荒城专属术语。"""
        _setup_imported_project(tmp_path)
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))

        bundle = load_story("int-test")
        intervention = build_intervention(
            target="zhao_xuan",
            content="韩无归有陷阱",
            intervention_type="whisper",
        )
        intervention = audit_intervention(
            intervention, bundle.world, bundle.character_map()
        )

        llm = LLMClient(mock=True)
        specs = build_branch_specs(intervention, count=3)
        result = run_scene(
            bundle.world,
            bundle.characters,
            intervention,
            specs[0],
            llm,
            max_rounds=2,
            source_type="imported",
        )

        all_text = " ".join(
            e.narrative for e in result.accepted_events
        )
        tianhuang_markers = ["传讯玉简", "林晚舟", "林凡", "听雨轩", "竹林"]
        for marker in tianhuang_markers:
            assert marker not in all_text, f"imported 结果不应含天荒城术语: {marker}"

    def test_write_run_output_has_story_slug(self, tmp_path: Path, monkeypatch):
        """写出的 intervention.json 含 story_slug 而非 tianhuang-night。"""
        _setup_imported_project(tmp_path)
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))

        bundle = load_story("int-test")
        intervention = build_intervention(
            target="zhao_xuan",
            content="测试",
            intervention_type="whisper",
        )
        intervention = audit_intervention(
            intervention, bundle.world, bundle.character_map()
        )
        intervention.story_slug = "int-test"
        intervention.source_kind = "imported"

        llm = LLMClient(mock=True)
        specs = build_branch_specs(intervention, count=3)
        results = [
            run_scene(
                bundle.world,
                bundle.characters,
                intervention,
                spec,
                llm,
                max_rounds=2,
                source_type="imported",
            )
            for spec in specs
        ]

        output = write_run_output(intervention, results)
        with open(output.run_dir / "intervention.json", encoding="utf-8") as f:
            data = json.load(f)

        assert data.get("story_slug") == "int-test"
        assert data.get("source_kind") == "imported"
        assert data.get("sample_slug") != "tianhuang-night"

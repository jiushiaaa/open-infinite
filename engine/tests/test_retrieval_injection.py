"""Tests for retrieval context injection into run_scene / character_agent / narrator."""

import json
from pathlib import Path

from living_novel_engine.import_novel.mock_extractor import mock_extract
from living_novel_engine.import_novel.splitter import split_chapters
from living_novel_engine.import_novel.writer import write_project
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import build_branch_specs
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.retrieval import retrieve_context
from living_novel_engine.story_loader import load_story


def _setup_project(tmp_path: Path) -> Path:
    """Import a test project with facts/summaries/contract."""
    fixtures = Path(__file__).parent / "fixtures" / "mini_novel"
    chapters = split_chapters(fixtures, max_chapters=3)
    extraction = mock_extract(chapters, story_name="retrieval-test")
    return write_project(
        "retrieval-test", chapters, extraction,
        projects_dir=tmp_path, allow_overwrite=True,
    )


class TestRetrievalInjection:
    def test_run_scene_accepts_retrieved_context(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        project_dir = _setup_project(tmp_path)
        bundle = load_story("retrieval-test")

        ctx = retrieve_context(project_dir, "赵轩 韩无归")
        retrieved_ctx = ctx.as_prompt_block()
        assert len(retrieved_ctx) > 0

        intervention = build_intervention(
            target="zhao_xuan", content="韩无归和赵远山旧事有关", intervention_type="whisper"
        )
        specs = build_branch_specs(intervention, count=2)
        llm = LLMClient(mock=True)

        result = run_scene(
            bundle.world,
            bundle.characters,
            intervention,
            specs[0],
            llm,
            max_rounds=2,
            source_type="imported",
            retrieved_context=retrieved_ctx,
        )
        result.retrieval_record = ctx.to_artifact()
        assert result.chapter_text
        assert len(result.accepted_events) > 0
        assert result.retrieval_record["items"]

    def test_builtin_sample_not_affected(self):
        """真实加载 tianhuang-night，不触发检索、不写 retrieval_record。"""
        bundle = load_story("tianhuang-night")
        assert bundle.source_kind == "builtin"
        assert bundle.project_dir is None

        intervention = build_intervention(
            target="lin_wan_zhou",
            content="今夜不要去城外竹林",
            intervention_type="whisper",
        )
        specs = build_branch_specs(intervention, count=2)
        llm = LLMClient(mock=True)

        result = run_scene(
            bundle.world,
            bundle.characters,
            intervention,
            specs[0],
            llm,
            max_rounds=2,
            source_type=bundle.world.source_type,
            retrieved_context="",
        )
        assert result.chapter_text
        assert result.retrieval_record is None

    def test_imported_no_retrieval_files_graceful(self, tmp_path, monkeypatch):
        """Imported project missing facts/summaries still works."""
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        project_dir = _setup_project(tmp_path)

        import shutil
        shutil.rmtree(project_dir / "canon", ignore_errors=True)
        shutil.rmtree(project_dir / "summaries", ignore_errors=True)
        (project_dir / "story_contract.yaml").unlink(missing_ok=True)

        ctx = retrieve_context(project_dir, "任何查询")
        assert ctx.as_prompt_block() == ""

        bundle = load_story("retrieval-test")
        intervention = build_intervention(
            target="zhao_xuan", content="test", intervention_type="whisper"
        )
        specs = build_branch_specs(intervention, count=2)
        llm = LLMClient(mock=True)

        result = run_scene(
            bundle.world,
            bundle.characters,
            intervention,
            specs[0],
            llm,
            max_rounds=2,
            source_type="imported",
            retrieved_context="",
        )
        assert result.chapter_text

    def test_project_dir_exposed_in_bundle(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        _setup_project(tmp_path)
        bundle = load_story("retrieval-test")
        assert bundle.project_dir is not None
        assert bundle.project_dir.name == "retrieval-test"

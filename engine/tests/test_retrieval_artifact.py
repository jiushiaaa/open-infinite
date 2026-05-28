"""Tests for retrieval_context.json artifact write-through."""

import json
from pathlib import Path

from living_novel_engine.import_novel.mock_extractor import mock_extract
from living_novel_engine.import_novel.splitter import split_chapters
from living_novel_engine.import_novel.writer import write_project
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import build_branch_specs
from living_novel_engine.output.writer import write_run_output, write_resume_output
from living_novel_engine.retrieval import retrieve_context
from living_novel_engine.story_loader import load_story


def _setup_project(tmp_path: Path) -> Path:
    fixtures = Path(__file__).parent / "fixtures" / "mini_novel"
    chapters = split_chapters(fixtures, max_chapters=3)
    extraction = mock_extract(chapters, story_name="artifact-test")
    return write_project(
        "artifact-test", chapters, extraction,
        projects_dir=tmp_path, allow_overwrite=True,
    )


class TestRetrievalArtifactWrite:
    def test_write_run_output_creates_retrieval_context_json(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        outputs = tmp_path / "outputs"
        outputs.mkdir()
        monkeypatch.setattr(
            "living_novel_engine.output.writer._outputs_dir",
            lambda: outputs,
        )

        _setup_project(tmp_path)
        bundle = load_story("artifact-test")
        intervention = build_intervention(
            target="zhao_xuan",
            content="韩无归和风鸣铃有关",
            intervention_type="whisper",
        )
        ctx = retrieve_context(bundle.project_dir, "韩无归 风鸣铃")
        artifact = ctx.to_artifact()
        specs = build_branch_specs(intervention, count=2)
        llm = LLMClient(mock=True)
        results = []
        for spec in specs:
            result = run_scene(
                bundle.world,
                bundle.characters,
                intervention,
                spec,
                llm,
                max_rounds=2,
                source_type="imported",
                retrieved_context=ctx.as_prompt_block(),
            )
            result.retrieval_record = artifact
            results.append(result)

        out = write_run_output(intervention, results)
        for spec in specs:
            path = out.run_dir / spec.branch_id / "retrieval_context.json"
            assert path.exists(), f"missing {path}"
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data["query"]
            assert "prompt_block" in data
            assert isinstance(data["items"], list)
            assert data["items"]
            assert all("source" in item for item in data["items"])

    def test_builtin_run_has_no_retrieval_context_json(
        self, tmp_path, monkeypatch
    ):
        outputs = tmp_path / "outputs"
        outputs.mkdir()
        monkeypatch.setattr(
            "living_novel_engine.output.writer._outputs_dir",
            lambda: outputs,
        )

        bundle = load_story("tianhuang-night")
        intervention = build_intervention(
            target="lin_wan_zhou",
            content="今夜不要去竹林",
            intervention_type="whisper",
        )
        specs = build_branch_specs(intervention, count=2)
        llm = LLMClient(mock=True)
        results = []
        for spec in specs:
            result = run_scene(
                bundle.world,
                bundle.characters,
                intervention,
                spec,
                llm,
                max_rounds=2,
                source_type=bundle.world.source_type,
            )
            assert result.retrieval_record is None
            results.append(result)

        out = write_run_output(intervention, results)
        for spec in specs:
            path = out.run_dir / spec.branch_id / "retrieval_context.json"
            assert not path.exists()

    def test_intervene_retrieval_uses_anchor_chapter_not_one(
        self, tmp_path, monkeypatch
    ):
        """3 章 imported 项目锚点在第 3 章，首次 intervene 检索章节不应写死为 1。"""
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        outputs = tmp_path / "outputs"
        outputs.mkdir()
        monkeypatch.setattr(
            "living_novel_engine.output.writer._outputs_dir",
            lambda: outputs,
        )

        _setup_project(tmp_path)
        bundle = load_story("artifact-test")
        assert bundle.intervention_chapter() == 3

        intervention = build_intervention(
            target="zhao_xuan",
            content="韩无归和风鸣铃有关",
            intervention_type="whisper",
        )
        ctx = retrieve_context(
            bundle.project_dir,
            "韩无归 风鸣铃",
            current_chapter=bundle.intervention_chapter(),
        )
        artifact = ctx.to_artifact()
        assert artifact["current_chapter"] == 3

        spec = build_branch_specs(intervention, count=1)[0]
        result = run_scene(
            bundle.world,
            bundle.characters,
            intervention,
            spec,
            LLMClient(mock=True),
            max_rounds=1,
            source_type="imported",
            retrieved_context=ctx.as_prompt_block(),
        )
        result.retrieval_record = artifact
        out = write_run_output(intervention, [result])
        data = json.loads(
            (out.run_dir / spec.branch_id / "retrieval_context.json").read_text(
                encoding="utf-8"
            )
        )
        assert data["current_chapter"] == 3
        assert data["current_chapter"] != 1

    def test_empty_retrieval_still_writes_stable_structure(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        outputs = tmp_path / "outputs"
        outputs.mkdir()
        monkeypatch.setattr(
            "living_novel_engine.output.writer._outputs_dir",
            lambda: outputs,
        )

        project_dir = _setup_project(tmp_path)
        import shutil
        shutil.rmtree(project_dir / "canon", ignore_errors=True)
        shutil.rmtree(project_dir / "summaries", ignore_errors=True)
        (project_dir / "story_contract.yaml").unlink(missing_ok=True)

        bundle = load_story("artifact-test")
        ctx = retrieve_context(bundle.project_dir, "query")
        artifact = ctx.to_artifact()
        intervention = build_intervention(
            target="zhao_xuan", content="test", intervention_type="whisper"
        )
        spec = build_branch_specs(intervention, count=1)[0]
        result = run_scene(
            bundle.world, bundle.characters, intervention, spec,
            LLMClient(mock=True), max_rounds=1, source_type="imported",
        )
        result.retrieval_record = artifact
        out = write_run_output(intervention, [result])
        path = out.run_dir / spec.branch_id / "retrieval_context.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["items"] == []
        assert data["prompt_block"] == ""

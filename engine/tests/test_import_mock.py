"""测试 import-novel mock 全链路：拆分 → 抽取 → 写入项目目录。"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from living_novel_engine.cli import main
from living_novel_engine.import_novel.splitter import (
    SplitChapter,
    split_chapters,
    split_from_directory,
    split_from_file,
)
from living_novel_engine.import_novel.mock_extractor import mock_extract
from living_novel_engine.import_novel.writer import write_project


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "mini_novel"


class TestSplitter:
    def test_split_from_directory(self):
        chapters = split_from_directory(FIXTURES_DIR)
        assert len(chapters) == 3
        assert chapters[0].index == 1
        assert "风起云城" in chapters[0].title
        assert "赵轩" in chapters[0].content

    def test_split_chapters_auto_detect_dir(self):
        chapters = split_chapters(FIXTURES_DIR)
        assert len(chapters) == 3

    def test_split_from_file_merged(self, tmp_path: Path):
        merged = tmp_path / "novel.md"
        text = (
            "第一章 开端\n\n这是第一章正文。\n\n"
            "第二章 发展\n\n这是第二章正文。\n\n"
            "第三章 高潮\n\n这是第三章正文。\n"
        )
        merged.write_text(text, encoding="utf-8")
        chapters = split_from_file(merged)
        assert len(chapters) == 3
        assert "开端" in chapters[0].title
        assert "第一章正文" in chapters[0].content

    def test_split_rejects_too_many(self, tmp_path: Path):
        for i in range(15):
            (tmp_path / f"ch_{i:03d}.md").write_text(f"第{i}章内容", encoding="utf-8")
        with pytest.raises(ValueError, match="超过上限"):
            split_from_directory(tmp_path, max_chapters=10)

    def test_split_rejects_empty_dir(self, tmp_path: Path):
        with pytest.raises(ValueError, match="未找到"):
            split_from_directory(tmp_path)


class TestMockExtractor:
    def test_basic_extraction(self):
        chapters = split_chapters(FIXTURES_DIR)
        result = mock_extract(chapters, story_name="test-story")

        assert result.world_yaml["source_type"] == "imported"
        assert len(result.world_yaml["rules"]) >= 3
        assert len(result.world_yaml["locations"]) >= 2
        assert len(result.characters_yaml["characters"]) >= 2
        assert len(result.open_threads) >= 2
        assert result.anchor_proposal["confidence"] == "mock"

    def test_characters_have_required_fields(self):
        chapters = split_chapters(FIXTURES_DIR)
        result = mock_extract(chapters, story_name="test-story")

        for char in result.characters_yaml["characters"]:
            assert "id" in char
            assert "name" in char
            assert "persona" in char
            assert "current_state" in char
            assert "present_in_scene" in char


class TestWriter:
    def test_write_project_structure(self, tmp_path: Path):
        chapters = split_chapters(FIXTURES_DIR)
        extraction = mock_extract(chapters, story_name="test-story")
        project_dir = write_project(
            "test-story", chapters, extraction, projects_dir=tmp_path
        )

        assert project_dir == tmp_path / "test-story"
        assert (project_dir / "world.yaml").exists()
        assert (project_dir / "characters.yaml").exists()
        assert (project_dir / "canon_chapter.md").exists()
        assert (project_dir / "anchor_proposal.yaml").exists()
        assert (project_dir / "import_meta.json").exists()
        assert (project_dir / "source").is_dir()
        assert (project_dir / "prologue.md").exists()
        assert (project_dir / "canon_opening.md").exists()

    def test_source_files_count(self, tmp_path: Path):
        chapters = split_chapters(FIXTURES_DIR)
        extraction = mock_extract(chapters, story_name="test-story")
        project_dir = write_project(
            "test-story", chapters, extraction, projects_dir=tmp_path
        )

        source_files = list((project_dir / "source").iterdir())
        assert len(source_files) == 3

    def test_world_yaml_loadable(self, tmp_path: Path):
        chapters = split_chapters(FIXTURES_DIR)
        extraction = mock_extract(chapters, story_name="test-story")
        project_dir = write_project(
            "test-story", chapters, extraction, projects_dir=tmp_path
        )

        with open(project_dir / "world.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["id"] == "world_test-story"
        assert data["source_type"] == "imported"
        assert isinstance(data["rules"], list)
        assert isinstance(data["locations"], list)

    def test_characters_yaml_loadable(self, tmp_path: Path):
        chapters = split_chapters(FIXTURES_DIR)
        extraction = mock_extract(chapters, story_name="test-story")
        project_dir = write_project(
            "test-story", chapters, extraction, projects_dir=tmp_path
        )

        with open(project_dir / "characters.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "characters" in data
        assert len(data["characters"]) >= 2

    def test_overwrite_existing(self, tmp_path: Path):
        chapters = split_chapters(FIXTURES_DIR)
        extraction = mock_extract(chapters, story_name="test-story")
        write_project("test-story", chapters, extraction, projects_dir=tmp_path)
        # 二次写入不报错（默认 allow_overwrite=True）
        project_dir = write_project(
            "test-story", chapters, extraction, projects_dir=tmp_path
        )
        assert (project_dir / "world.yaml").exists()

    def test_overwrite_rejected_when_disallowed(self, tmp_path: Path):
        chapters = split_chapters(FIXTURES_DIR)
        extraction = mock_extract(chapters, story_name="test-story")
        write_project("test-story", chapters, extraction, projects_dir=tmp_path)
        with pytest.raises(FileExistsError, match="已存在"):
            write_project(
                "test-story",
                chapters,
                extraction,
                projects_dir=tmp_path,
                allow_overwrite=False,
            )


class TestImportNovelCli:
    def test_no_api_key_uses_mock_extractor(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        monkeypatch.setenv("LLM_API_KEY", "")
        monkeypatch.delenv("LNE_MOCK", raising=False)

        result = CliRunner().invoke(
            main,
            [
                "import-novel",
                str(FIXTURES_DIR),
                "--name",
                "cli-no-key",
            ],
        )

        assert result.exit_code == 0, result.output
        project_dir = tmp_path / "cli-no-key"
        assert (project_dir / "world.yaml").exists()
        with open(project_dir / "characters.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert len(data["characters"]) >= 2

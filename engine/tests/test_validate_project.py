"""测试 validate-project：校验结构完整性与字段要求。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from living_novel_engine.import_novel.splitter import split_chapters
from living_novel_engine.import_novel.mock_extractor import mock_extract
from living_novel_engine.import_novel.writer import write_project
from living_novel_engine.import_novel.validator import validate_project


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "mini_novel"


def _make_project(tmp_path: Path) -> Path:
    chapters = split_chapters(FIXTURES_DIR)
    extraction = mock_extract(chapters, story_name="val-test")
    return write_project("val-test", chapters, extraction, projects_dir=tmp_path)


class TestValidateHappyPath:
    def test_valid_project(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        result = validate_project(project_dir)
        assert result.valid is True
        assert result.errors == []
        assert result.world is not None
        assert len(result.characters) >= 2

    def test_world_is_storyworld(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        result = validate_project(project_dir)
        from living_novel_engine.models import StoryWorld

        assert isinstance(result.world, StoryWorld)
        assert result.world.source_type == "imported"

    def test_characters_are_agents(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        result = validate_project(project_dir)
        from living_novel_engine.models import CharacterAgent

        for c in result.characters:
            assert isinstance(c, CharacterAgent)

    def test_has_present_character(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        result = validate_project(project_dir)
        present = [c for c in result.characters if c.present_in_scene]
        assert len(present) >= 1


class TestValidateErrors:
    def test_missing_world_yaml(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        (project_dir / "world.yaml").unlink()
        result = validate_project(project_dir)
        assert result.valid is False
        assert any("world.yaml" in e for e in result.errors)

    def test_missing_characters_yaml(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        (project_dir / "characters.yaml").unlink()
        result = validate_project(project_dir)
        assert result.valid is False
        assert any("characters.yaml" in e for e in result.errors)

    def test_missing_canon_chapter(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        (project_dir / "canon_chapter.md").unlink()
        result = validate_project(project_dir)
        assert result.valid is False
        assert any("canon_chapter" in e for e in result.errors)

    def test_empty_canon_chapter(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        (project_dir / "canon_chapter.md").write_text("", encoding="utf-8")
        result = validate_project(project_dir)
        assert result.valid is False
        assert any("为空" in e for e in result.errors)

    def test_nonexistent_dir(self, tmp_path: Path):
        result = validate_project(tmp_path / "ghost")
        assert result.valid is False

    def test_invalid_yaml(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        (project_dir / "world.yaml").write_text(": [invalid\nyaml", encoding="utf-8")
        result = validate_project(project_dir)
        assert result.valid is False

    def test_duplicate_character_ids(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        with open(project_dir / "characters.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        data["characters"].append(data["characters"][0].copy())
        with open(project_dir / "characters.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)
        result = validate_project(project_dir)
        assert result.valid is False
        assert any("重复" in e for e in result.errors)

    def test_no_present_character(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        with open(project_dir / "characters.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for c in data["characters"]:
            c["present_in_scene"] = False
        with open(project_dir / "characters.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)
        result = validate_project(project_dir)
        assert result.valid is False
        assert any("present_in_scene" in e for e in result.errors)


class TestValidateWarnings:
    def test_missing_meta_is_warning(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        (project_dir / "import_meta.json").unlink()
        result = validate_project(project_dir)
        assert result.valid is True
        assert any("import_meta" in w for w in result.warnings)

    def test_missing_source_is_warning(self, tmp_path: Path):
        project_dir = _make_project(tmp_path)
        import shutil

        shutil.rmtree(project_dir / "source")
        result = validate_project(project_dir)
        assert result.valid is True
        assert any("source" in w for w in result.warnings)

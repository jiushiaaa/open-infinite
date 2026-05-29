"""v0.7 第七刀：项目健康检查（service.project_health.check_project_health）。"""

from __future__ import annotations

import pytest

from living_novel_engine.service import check_project_health, generate_story

PREMISE = "一名守陵人发现先祖封印松动，必须在城破前查明真相。"


def _make_project(tmp_path, slug="proj"):
    generate_story(name=slug, premise=PREMISE, mock=True, projects_dir=tmp_path)
    return tmp_path / slug


class TestHealth:
    def test_normal_ok(self, tmp_path):
        _make_project(tmp_path, "good")
        h = check_project_health("good", projects_dir=tmp_path)
        assert h.status in ("ok", "warning")
        assert h.files["world.yaml"] == "ok"
        assert h.files["characters.yaml"] == "ok"
        assert h.errors == []

    def test_world_broken_no_500(self, tmp_path):
        pdir = _make_project(tmp_path, "broken-world")
        (pdir / "world.yaml").write_text("key: value: another\n", encoding="utf-8")
        h = check_project_health("broken-world", projects_dir=tmp_path)
        assert h.status == "error"
        assert h.files["world.yaml"] == "error"
        assert any("world.yaml" in e for e in h.errors)

    def test_characters_broken_locates_file(self, tmp_path):
        pdir = _make_project(tmp_path, "broken-chars")
        (pdir / "characters.yaml").write_text("a:\n  - x\n - y\n", encoding="utf-8")
        h = check_project_health("broken-chars", projects_dir=tmp_path)
        assert h.status == "error"
        assert h.files["characters.yaml"] == "error"
        assert any("characters.yaml" in e for e in h.errors)

    def test_missing_story(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            check_project_health("nope", projects_dir=tmp_path)

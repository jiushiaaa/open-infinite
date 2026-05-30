"""v0.8.5-A Long Canon Replay：runtime_visible / holdout_private 隔离清单。"""

from __future__ import annotations

import json

from living_novel_engine.retrieval import retrieve_context
from living_novel_engine.service import import_novel_from_payload, get_holdout, write_holdout


def _chapters(n: int = 4) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i + 1:03d}.md",
            "content": f"第{i + 1}章 可见正文\n林凡追查退魂铃线索，第 {i + 1} 章仍未触及终局。",
        }
        for i in range(n)
    ]


class TestLongCanonReplayIsolation:
    def test_write_holdout_creates_visibility_manifest(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        import_novel_from_payload(
            name="visible-private",
            chapters=_chapters(4),
            mock=True,
            projects_dir=tmp_path,
        )

        manifest = write_holdout(
            "visible-private",
            chapters=[
                {
                    "chapter": 5,
                    "title": "第五章 隐藏终局",
                    "content": "绝密终章不可泄漏，只有 evaluator 可以读取。",
                }
            ],
            projects_dir=tmp_path,
        )

        project_dir = tmp_path / "visible-private"
        visibility = json.loads(
            (project_dir / "canon" / "visibility_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        assert manifest["visibility_manifest"]["holdout_private"]["chapter_count"] == 1
        assert visibility["version"] == "v0.8.5"
        assert visibility["runtime_visible"]["chapter_count"] == 4
        assert visibility["holdout_private"]["available_chapters"] == [5]
        assert (project_dir / "holdout_private" / "chapter_005.md").exists()

    def test_holdout_private_text_is_not_retrieved(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        import_novel_from_payload(
            name="private-not-retrieved",
            chapters=_chapters(4),
            mock=True,
            projects_dir=tmp_path,
        )
        write_holdout(
            "private-not-retrieved",
            chapters=[{"chapter": 5, "content": "绝密终章不可泄漏。"}],
            projects_dir=tmp_path,
        )

        project_dir = tmp_path / "private-not-retrieved"
        ctx = retrieve_context(project_dir, "绝密终章不可泄漏")
        artifact = ctx.to_artifact()

        assert "绝密终章不可泄漏" not in artifact["prompt_block"]
        assert all("绝密终章不可泄漏" not in item["text"] for item in artifact["items"])

    def test_get_holdout_returns_visibility_manifest_summary(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        import_novel_from_payload(
            name="holdout-summary",
            chapters=_chapters(3),
            mock=True,
            projects_dir=tmp_path,
        )
        write_holdout(
            "holdout-summary",
            chapters=[{"chapter": 4, "content": "隐藏评估章节。"}],
            projects_dir=tmp_path,
        )

        manifest = get_holdout("holdout-summary", projects_dir=tmp_path)

        assert manifest["visibility_manifest"]["runtime_visible"]["chapter_count"] == 3
        assert manifest["visibility_manifest"]["holdout_private"]["available_chapters"] == [4]

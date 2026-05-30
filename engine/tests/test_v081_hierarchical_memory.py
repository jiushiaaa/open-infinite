"""v0.8.1-A Hierarchical Memory：导入时生成分层记忆骨架。"""

from __future__ import annotations

import json

import yaml

from living_novel_engine.service import import_novel_from_payload


def _chapters(n: int = 5) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i + 1:03d}.md",
            "content": (
                f"第{i + 1}章 记忆骨架\n"
                f"林凡在第 {i + 1} 章追查退魂铃余波，林晚舟留下新的线索。"
            ),
        }
        for i in range(n)
    ]


def _load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestHierarchicalMemory:
    def test_import_writes_memory_manifest_and_layers(self, tmp_path):
        import_novel_from_payload(
            name="memory-story",
            chapters=_chapters(5),
            mock=True,
            projects_dir=tmp_path,
        )

        project_dir = tmp_path / "memory-story"
        memory_dir = project_dir / "memory"
        manifest = json.loads(
            (memory_dir / "memory_manifest.json").read_text(encoding="utf-8")
        )

        assert manifest["version"] == "v0.8.1"
        assert manifest["story_slug"] == "memory-story"
        assert manifest["layers"]["contract"]["path"] == "memory/master_setting.yaml"
        assert manifest["layers"]["chapters"]["count"] == 5
        assert manifest["layers"]["volumes"]["count"] == 1
        assert manifest["layers"]["character_states"]["count"] >= 1
        assert (memory_dir / "master_setting.yaml").exists()
        assert (memory_dir / "volumes" / "volume_001.yaml").exists()
        assert (memory_dir / "chapters" / "chapter_0001.yaml").exists()
        assert (memory_dir / "timeline.yaml").exists()
        assert (memory_dir / "plot_threads.yaml").exists()
        assert (memory_dir / "propagation_debts.yaml").exists()

    def test_memory_chapter_and_character_files_are_auditable(self, tmp_path):
        import_novel_from_payload(
            name="memory-audit",
            chapters=_chapters(3),
            mock=True,
            projects_dir=tmp_path,
        )

        memory_dir = tmp_path / "memory-audit" / "memory"
        chapter = _load_yaml(memory_dir / "chapters" / "chapter_0002.yaml")
        master = _load_yaml(memory_dir / "master_setting.yaml")
        timeline = _load_yaml(memory_dir / "timeline.yaml")
        plot_threads = _load_yaml(memory_dir / "plot_threads.yaml")
        debts = _load_yaml(memory_dir / "propagation_debts.yaml")

        character_files = list((memory_dir / "character_states").glob("*.yaml"))
        character_state = _load_yaml(character_files[0])

        assert chapter["chapter"] == 2
        assert chapter["source_ref"] == "source/chapter_002.md"
        assert chapter["raw_ref"] == "source_raw/chapter_002.md"
        assert isinstance(master["world_rules"], list)
        assert timeline["events"]
        assert plot_threads["active_threads"] is not None
        assert debts["debts"] == []
        assert character_state["character_id"]
        assert "source_refs" in character_state

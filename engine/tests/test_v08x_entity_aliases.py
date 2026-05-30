"""v0.8.x Entity Aliases：导入生成别名骨架，检索/审计可读取别名映射。"""

from __future__ import annotations

import json

import yaml

from living_novel_engine.browser import indexer
from living_novel_engine.entity_aliases import load_entity_aliases
from living_novel_engine.retrieval import retrieve_context
from living_novel_engine.service import import_novel_from_payload


def _chapters(n: int = 3) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i + 1:03d}.md",
            "content": (
                f"第{i + 1}章 别名骨架\n"
                f"林凡在第 {i + 1} 章追查退魂铃余波，林晚舟记录新的线索。"
            ),
        }
        for i in range(n)
    ]


def _read_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_import_writes_entity_alias_skeleton_and_manifest_layer(tmp_path):
    import_novel_from_payload(
        name="alias-story",
        chapters=_chapters(3),
        mock=True,
        projects_dir=tmp_path,
    )

    memory_dir = tmp_path / "alias-story" / "memory"
    aliases = _read_yaml(memory_dir / "entity_aliases.yaml")
    manifest = json.loads(
        (memory_dir / "memory_manifest.json").read_text(encoding="utf-8")
    )
    report = json.loads(
        (memory_dir / "consistency_report.json").read_text(encoding="utf-8")
    )

    assert aliases["version"] == "v0.8.x"
    assert aliases["story_slug"] == "alias-story"
    assert aliases["entities"]
    assert any(e["entity_type"] == "character" for e in aliases["entities"])
    assert "lookup" in aliases
    assert manifest["layers"]["entity_aliases"]["path"] == "memory/entity_aliases.yaml"
    assert manifest["layers"]["entity_aliases"]["count"] == len(aliases["entities"])
    assert report["summary"]["entity_alias_count"] == len(aliases["entities"])


def test_load_entity_aliases_corrupt_file_gracefully_returns_empty(tmp_path):
    project_dir = tmp_path / "broken-alias"
    memory_dir = project_dir / "memory"
    memory_dir.mkdir(parents=True)
    (memory_dir / "entity_aliases.yaml").write_text("aliases: [broken", encoding="utf-8")

    aliases = load_entity_aliases(project_dir)

    assert aliases.entities == {}
    assert aliases.lookup == {}
    assert aliases.status == "damaged"


def test_retrieval_normalizes_query_aliases_for_canon_ledger_entities(tmp_path):
    project = tmp_path / "alias-retrieval"
    (project / "memory").mkdir(parents=True)
    (project / "canon").mkdir()
    (project / "summaries").mkdir()
    (project / "story_contract.yaml").write_text("world_rules: []\n", encoding="utf-8")
    ledger = {
        "id": "canon_000001",
        "type": "resource",
        "chapter": 2,
        "scene": 1,
        "entities": ["mo_qing_yan", "retreat_bell"],
        "statement": "她确认那枚旧铃曾在听雨轩响过。",
        "truth_status": "canon",
        "source_ref": "source/chapter_002.md",
        "confidence": 0.9,
        "valid_from": 2,
        "valid_until": None,
    }
    (project / "memory" / "canon_ledger.jsonl").write_text(
        json.dumps(ledger, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (project / "memory" / "entity_aliases.yaml").write_text(
        yaml.safe_dump(
            {
                "version": "v0.8.x",
                "story_slug": "alias-retrieval",
                "entities": [
                    {
                        "entity_id": "mo_qing_yan",
                        "canonical_name": "墨青烟",
                        "entity_type": "character",
                        "aliases": ["墨青烟", "墨姑娘"],
                        "source_refs": ["characters.yaml"],
                    },
                    {
                        "entity_id": "retreat_bell",
                        "canonical_name": "退魂铃",
                        "entity_type": "item",
                        "aliases": ["退魂铃", "摄魂铃"],
                        "source_refs": ["memory/canon_ledger.jsonl"],
                    },
                ],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    result = retrieve_context(project, "墨姑娘 摄魂铃", current_chapter=2)

    ledger_items = [i for i in result.items if i["source"] == "canon_ledger"]
    assert ledger_items
    assert ledger_items[0]["resolved_entities"] == ["mo_qing_yan", "retreat_bell"]


def test_world_anchor_returns_read_only_alias_summary(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "projects_dir", lambda: tmp_path)
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path / "_out")
    import_novel_from_payload(
        name="alias-anchor",
        chapters=_chapters(3),
        mock=True,
        projects_dir=tmp_path,
    )

    anchor = indexer.get_world_anchor("alias-anchor")

    assert anchor["entity_aliases"]["status"] == "ready"
    assert anchor["entity_aliases"]["count"] >= 1
    assert anchor["entity_aliases"]["path"] == "memory/entity_aliases.yaml"

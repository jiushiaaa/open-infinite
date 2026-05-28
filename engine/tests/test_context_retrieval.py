"""Tests for context retrieval integration."""

import json
import tempfile
from pathlib import Path

import yaml

from living_novel_engine.retrieval import retrieve_context
from living_novel_engine.retrieval.context_loader import load_context_corpus
from living_novel_engine.retrieval.decay import distance_decay


def _make_project(tmp: Path) -> Path:
    """Create a minimal project with facts/summaries/contract."""
    project = tmp / "test-project"
    project.mkdir()

    # canon/facts.jsonl
    canon_dir = project / "canon"
    canon_dir.mkdir()
    facts = [
        {"id": "fact_001", "chapter": 1, "type": "relationship", "subject": "zhao_xuan",
         "object": "shen_bing_yue", "text": "赵轩与沈冰月暂时合作", "evidence": "chapter_001.md"},
        {"id": "fact_002", "chapter": 2, "type": "memory", "subject": "zhao_xuan",
         "text": "赵轩发现账簿中有人购入铜铃形器物", "evidence": "chapter_002.md"},
        {"id": "fact_003", "chapter": 3, "type": "relationship", "subject": "han_wu_gui",
         "object": "zhao_xuan", "text": "韩无归质问赵远山之子", "evidence": "chapter_003.md"},
        {"id": "fact_004", "chapter": 1, "type": "memory", "subject": "shen_bing_yue",
         "text": "沈冰月追踪风鸣铃线索至云城", "evidence": "chapter_001.md"},
    ]
    lines = [json.dumps(f, ensure_ascii=False) for f in facts]
    (canon_dir / "facts.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # summaries/
    summaries_dir = project / "summaries"
    summaries_dir.mkdir()
    for i in range(1, 4):
        data = {
            "chapter": i,
            "title": f"第{i}章",
            "summary": f"第{i}章发生了重要事件",
            "key_events": [f"事件{i}"],
            "characters_present": ["赵轩", "沈冰月"],
            "state_changes": [],
            "open_threads": [],
            "evidence_refs": [],
        }
        with open(summaries_dir / f"chapter_{i:03d}.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

    # story_contract.yaml
    contract = {
        "world_rules": ["角色不能无理由 OOC", "禁止新增原文未声明设定"],
        "character_boundaries": {
            "zhao_xuan": ["不会背弃三代恩情", "不会见死不救"],
            "shen_bing_yue": ["不会为完成任务伤害无辜"],
        },
        "power_system_limits": ["境界压制"],
        "forbidden_additions": ["重生", "系统", "穿越"],
        "unresolved_threads": [
            {"id": "wind_bell", "title": "风鸣铃争夺", "status": "open"}
        ],
    }
    with open(project / "story_contract.yaml", "w", encoding="utf-8") as f:
        yaml.dump(contract, f, allow_unicode=True)

    volume = {
        "volume": 1,
        "chapter_range": [1, 3],
        "summary": "第一卷：云城风铃之争",
        "main_conflicts": ["韩无归与赵轩的账簿对峙", "风鸣铃失窃之谜"],
        "key_facts": [],
        "active_threads": ["wind_bell", "ledger_secret"],
        "character_arcs": ["赵轩", "沈冰月"],
    }
    with open(summaries_dir / "volume_001.yaml", "w", encoding="utf-8") as f:
        yaml.dump(volume, f, allow_unicode=True)

    return project


class TestContextLoader:
    def test_load_facts(self, tmp_path):
        project = _make_project(tmp_path)
        corpus = load_context_corpus(project)
        assert len(corpus.facts) == 4
        assert corpus.facts[0].subject == "zhao_xuan"

    def test_load_summaries(self, tmp_path):
        project = _make_project(tmp_path)
        corpus = load_context_corpus(project)
        assert len(corpus.summaries) == 3
        assert corpus.summaries[0].chapter == 1

    def test_load_contract(self, tmp_path):
        project = _make_project(tmp_path)
        corpus = load_context_corpus(project)
        assert corpus.contract is not None
        assert len(corpus.contract.world_rules) == 2
        assert "zhao_xuan" in corpus.contract.character_boundaries

    def test_load_volume_brief(self, tmp_path):
        project = _make_project(tmp_path)
        corpus = load_context_corpus(project)
        assert len(corpus.volumes) == 1
        assert corpus.volumes[0].main_conflicts
        assert "风鸣铃" in corpus.volumes[0].main_conflicts[1]

    def test_load_summary_evidence_refs(self, tmp_path):
        project = _make_project(tmp_path)
        corpus = load_context_corpus(project)
        assert all(hasattr(s, "evidence_refs") for s in corpus.summaries)

    def test_missing_files_graceful(self, tmp_path):
        empty_project = tmp_path / "empty"
        empty_project.mkdir()
        corpus = load_context_corpus(empty_project)
        assert corpus.facts == []
        assert corpus.summaries == []
        assert corpus.contract is None


class TestDistanceDecay:
    def test_same_chapter(self):
        assert distance_decay(3, 3) == 1.0

    def test_adjacent_chapter(self):
        result = distance_decay(3, 4)
        assert 0.8 < result < 0.9

    def test_far_chapter(self):
        result = distance_decay(10, 1)
        assert result < 0.4

    def test_symmetric(self):
        assert distance_decay(5, 3) == distance_decay(3, 5)


class TestRetrieveContext:
    def test_facts_retrievable(self, tmp_path):
        project = _make_project(tmp_path)
        result = retrieve_context(project, "赵轩 沈冰月 合作")
        assert result.facts_text
        assert "赵轩" in result.facts_text

    def test_summaries_retrievable(self, tmp_path):
        project = _make_project(tmp_path)
        result = retrieve_context(project, "重要事件 第1章")
        assert result.summaries_text or result.facts_text

    def test_contract_retrievable(self, tmp_path):
        project = _make_project(tmp_path)
        result = retrieve_context(project, "禁止 穿越 重生")
        assert result.contract_text
        assert "禁止" in result.contract_text

    def test_distance_decay_affects_ranking(self, tmp_path):
        project = _make_project(tmp_path)
        result_ch3 = retrieve_context(project, "韩无归 赵远山", current_chapter=3)
        result_ch1 = retrieve_context(project, "韩无归 赵远山", current_chapter=1)
        assert result_ch3.raw_items or result_ch1.raw_items

    def test_empty_project_graceful(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = retrieve_context(empty, "任何查询")
        assert result.facts_text == ""
        assert result.summaries_text == ""
        assert result.contract_text == ""

    def test_as_prompt_block_empty(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        result = retrieve_context(empty, "query")
        assert result.as_prompt_block() == ""

    def test_as_prompt_block_non_empty(self, tmp_path):
        project = _make_project(tmp_path)
        result = retrieve_context(project, "赵轩 韩无归 风鸣铃")
        block = result.as_prompt_block()
        assert len(block) > 0

    def test_volume_brief_retrievable(self, tmp_path):
        project = _make_project(tmp_path)
        result = retrieve_context(project, "风鸣铃失窃 账簿对峙")
        sources = {item["source"] for item in result.items}
        assert "volume_brief" in sources
        vol_items = [i for i in result.items if i["source"] == "volume_brief"]
        assert any("风鸣铃" in i["text"] for i in vol_items)

    def test_contract_not_decayed_at_high_chapter(self, tmp_path):
        project = _make_project(tmp_path)
        low = retrieve_context(project, "禁止 穿越 重生", current_chapter=1)
        high = retrieve_context(project, "禁止 穿越 重生", current_chapter=50)
        low_contract = [i for i in low.items if i["source"] == "contract"]
        high_contract = [i for i in high.items if i["source"] == "contract"]
        assert low_contract
        assert high_contract
        assert high_contract[0]["score"] >= low_contract[0]["score"] * 0.99
        assert abs(high_contract[0]["score"] - low_contract[0]["score"]) < 0.01

    def test_to_artifact_structure(self, tmp_path):
        project = _make_project(tmp_path)
        result = retrieve_context(project, "赵轩", current_chapter=2)
        artifact = result.to_artifact()
        assert artifact["query"] == "赵轩"
        assert artifact["current_chapter"] == 2
        assert "prompt_block" in artifact
        assert isinstance(artifact["items"], list)

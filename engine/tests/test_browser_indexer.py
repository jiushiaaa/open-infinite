from __future__ import annotations

import json
from pathlib import Path

import pytest

from living_novel_engine.browser import indexer


def _write_minimal_intervene_run(tmp_path: Path, run_id: str, story_slug: str) -> Path:
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True)
    intervention = {
        "target": "hero",
        "content": "测试干预",
        "story_slug": story_slug,
        "source_kind": "imported",
    }
    (run_dir / "intervention.json").write_text(
        json.dumps(intervention, ensure_ascii=False), encoding="utf-8"
    )
    for bid, theme in [
        ("branch_a", "相信干预"),
        ("branch_b", "半信半疑"),
        ("branch_c", "拒绝干预"),
    ]:
        bdir = run_dir / bid
        bdir.mkdir()
        (bdir / "chapter.md").write_text(f"# {bid}\n\n{theme} 正文。", encoding="utf-8")
        (bdir / "summary.md").write_text(f"摘要 {bid}", encoding="utf-8")
        snap = {
            "branch_theme": theme,
            "characters": {
                "hero": {
                    "name": "主角",
                    "location": "城中",
                    "emotion": "警觉",
                }
            },
            "next_chapter_hook": f"钩子-{bid}",
        }
        (bdir / "state_snapshot.json").write_text(
            json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (bdir / "events.json").write_text(
            json.dumps({"theme": theme, "termination_reason": "回合耗尽"}, ensure_ascii=False),
            encoding="utf-8",
        )
    (run_dir / "compare.md").write_text("# 对比\n", encoding="utf-8")
    return run_dir


def test_index_run_intervene(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_minimal_intervene_run(tmp_path, "run_test_001", "mini-story")

    summary = indexer.index_run(tmp_path / "run_test_001")
    assert summary is not None
    assert summary.kind == "intervene"
    assert summary.story_slug == "mini-story"
    assert len(summary.branches) == 3
    assert summary.has_compare
    assert summary.branches[0].chapter_chars > 0


def test_get_branch_and_tree(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_minimal_intervene_run(tmp_path, "run_parent", "chain-story")

    child_dir = tmp_path / "run_child_continue"
    child_dir.mkdir()
    meta = {
        "kind": "resume_continue",
        "parent_run_id": "run_parent",
        "parent_branch": "branch_a",
        "story_slug": "chain-story",
        "source_kind": "imported",
        "current_chapter": 14,
        "lineage": ["run_parent:branch_a"],
    }
    (child_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    linear = child_dir / "linear"
    linear.mkdir()
    (linear / "chapter.md").write_text("续章 linear", encoding="utf-8")
    (linear / "state_snapshot.json").write_text(
        json.dumps({"branch_theme": "时间流逝", "characters": {}}), encoding="utf-8"
    )

    branch = indexer.get_branch("run_parent", "branch_a")
    assert "相信干预" in branch["chapter_md"]
    assert branch["state_snapshot"]["characters"]["hero"]["name"] == "主角"
    assert "run_child_continue" in branch["child_runs"]

    tree = indexer.build_worldline_tree(story_slug="chain-story")
    assert len(tree) == 1
    assert tree[0]["run_id"] == "run_parent"
    assert tree[0]["branches"][0]["child_runs"][0]["run_id"] == "run_child_continue"


def test_list_runs_filters_story(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_minimal_intervene_run(tmp_path, "run_a", "story-a")
    _write_minimal_intervene_run(tmp_path, "run_b", "story-b")

    runs_a = indexer.list_runs(story_slug="story-a")
    assert len(runs_a) == 1
    assert runs_a[0].run_id == "run_a"


def test_corrupt_meta_does_not_break_indexing(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_minimal_intervene_run(tmp_path, "run_ok", "story-a")

    bad = tmp_path / "run_broken"
    bad.mkdir()
    (bad / "meta.json").write_text("{not json", encoding="utf-8")
    (bad / "intervention.json").write_text("###", encoding="utf-8")
    bdir = bad / "branch_a"
    bdir.mkdir()
    (bdir / "chapter.md").write_text("content", encoding="utf-8")

    runs = indexer.list_runs()
    ids = {r.run_id for r in runs}
    assert "run_ok" in ids
    assert "run_broken" in ids
    broken = next(r for r in runs if r.run_id == "run_broken")
    assert broken.story_slug == "tianhuang-night"
    assert len(broken.branches) == 1


def test_orphan_child_run_appears_as_root(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    orphan = tmp_path / "run_orphan"
    orphan.mkdir()
    meta = {
        "kind": "resume_continue",
        "parent_run_id": "run_does_not_exist",
        "parent_branch": "branch_a",
        "story_slug": "story-a",
        "source_kind": "imported",
        "current_chapter": 14,
    }
    (orphan / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    linear = orphan / "linear"
    linear.mkdir()
    (linear / "chapter.md").write_text("orphan continuation", encoding="utf-8")

    tree = indexer.build_worldline_tree(story_slug="story-a")
    assert len(tree) == 1
    assert tree[0]["run_id"] == "run_orphan"


def test_branch_with_missing_files_returns_safely(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    run_dir = tmp_path / "run_partial"
    run_dir.mkdir()
    bdir = run_dir / "branch_a"
    bdir.mkdir()
    (bdir / "events.json").write_text(
        json.dumps({"theme": "测试", "termination_reason": "中断"}), encoding="utf-8"
    )
    # chapter.md and state_snapshot.json intentionally missing

    branch = indexer.get_branch("run_partial", "branch_a")
    assert branch["chapter_md"] == ""
    assert branch["state_snapshot"] is None
    assert branch["theme"] == "测试"


def test_tree_root_order_is_deterministic(tmp_path, monkeypatch):
    """多 root 时按 run_id 倒序，孤儿与正常根一起排序。"""
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    # 故意以乱序写入，期望按 run_id 倒序输出。
    for name in [
        "run_20260101_000001_aaaaaa",
        "run_20260301_000001_cccccc",
        "run_20260201_000001_bbbbbb",
    ]:
        _write_minimal_intervene_run(tmp_path, name, "multi-root-story")

    # 再加一个 orphan child（parent 不在索引内）。
    orphan = tmp_path / "run_20260401_000001_dddddd_continue_branch_a"
    orphan.mkdir()
    meta = {
        "kind": "resume_continue",
        "parent_run_id": "run_does_not_exist",
        "parent_branch": "branch_a",
        "story_slug": "multi-root-story",
        "source_kind": "imported",
        "current_chapter": 14,
    }
    (orphan / "meta.json").write_text(__import__("json").dumps(meta), encoding="utf-8")
    linear = orphan / "linear"
    linear.mkdir()
    (linear / "chapter.md").write_text("orphan", encoding="utf-8")

    tree = indexer.build_worldline_tree(story_slug="multi-root-story")
    ids = [n["run_id"] for n in tree]
    assert ids == sorted(ids, reverse=True), f"root 顺序非倒序: {ids}"
    # 孤儿被标记
    orphan_node = next(n for n in tree if n["run_id"] == orphan.name)
    assert orphan_node["is_orphan"] is True
    # 普通 root 不标记
    normal_node = next(
        n for n in tree if n["run_id"] == "run_20260301_000001_cccccc"
    )
    assert normal_node["is_orphan"] is False


def test_tree_child_order_is_deterministic(tmp_path, monkeypatch):
    """同一分支多个子 run 按 run_id 倒序。"""
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_minimal_intervene_run(tmp_path, "run_parent_for_children", "child-order-story")

    for ts in ["20260102_000000_aa1111", "20260103_000000_bb2222", "20260101_000000_cc3333"]:
        cdir = tmp_path / f"run_{ts}_continue_branch_a"
        cdir.mkdir()
        meta = {
            "kind": "resume_continue",
            "parent_run_id": "run_parent_for_children",
            "parent_branch": "branch_a",
            "story_slug": "child-order-story",
            "source_kind": "imported",
            "current_chapter": 14,
        }
        (cdir / "meta.json").write_text(
            __import__("json").dumps(meta), encoding="utf-8"
        )

    tree = indexer.build_worldline_tree(story_slug="child-order-story")
    assert len(tree) == 1
    branch_a = next(b for b in tree[0]["branches"] if b["branch_id"] == "branch_a")
    child_ids = [c["run_id"] for c in branch_a["child_runs"]]
    assert child_ids == sorted(child_ids, reverse=True)


def test_mixed_builtin_and_imported_stories_listed(tmp_path, monkeypatch):
    """builtin sample 与 imported project 同时存在时都能被列出。"""
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)

    proj_root = tmp_path / "_projects"
    proj_root.mkdir()
    p = proj_root / "story-imported"
    p.mkdir()
    (p / "world.yaml").write_text(
        "id: x\ntitle: Imported Story\ndisplay_name: 导入示例\n", encoding="utf-8"
    )
    monkeypatch.setattr(indexer, "projects_dir", lambda: proj_root)

    _write_minimal_intervene_run(tmp_path, "run_imp", "story-imported")
    _write_minimal_intervene_run(tmp_path, "run_b", "tianhuang-night")

    stories = indexer.list_stories()
    slugs = {s.slug for s in stories}
    assert "story-imported" in slugs
    assert any(s.source_kind == "builtin" for s in stories)
    imp = next(s for s in stories if s.slug == "story-imported")
    assert imp.display_name == "导入示例"
    assert imp.run_count == 1
    assert imp.source_kind == "imported"

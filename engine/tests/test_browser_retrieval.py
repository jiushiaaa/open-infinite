"""v0.4.2: browser surfaces retrieval_context.json per branch."""

from __future__ import annotations

import json
from pathlib import Path

from living_novel_engine.browser import indexer


def _write_branch(
    run_dir: Path,
    branch_id: str,
    *,
    with_retrieval: bool = True,
) -> Path:
    bdir = run_dir / branch_id
    bdir.mkdir(parents=True)
    (bdir / "chapter.md").write_text(f"# {branch_id}\n\n正文。", encoding="utf-8")
    (bdir / "events.json").write_text(
        json.dumps({"theme": "相信", "termination_reason": "回合耗尽"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (bdir / "state_snapshot.json").write_text(
        json.dumps({"branch_theme": "相信", "characters": {}}, ensure_ascii=False),
        encoding="utf-8",
    )
    if with_retrieval:
        record = {
            "query": "韩无归 风鸣铃",
            "current_chapter": 3,
            "prompt_block": "【检索到的正史事实】\n- [zhao_xuan] 赵轩与沈冰月暂时合作",
            "items": [
                {
                    "id": "fact:fact_001",
                    "source": "fact",
                    "type": "fact",
                    "score": 1.234,
                    "text": "赵轩与沈冰月暂时合作",
                    "chapter": 1,
                    "evidence": "chapter_001.md",
                },
                {
                    "id": "contract:0",
                    "source": "contract",
                    "type": "contract",
                    "score": 2.0,
                    "text": "禁止: 穿越",
                    "chapter": 1,
                    "evidence": "",
                },
            ],
        }
        (bdir / "retrieval_context.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return bdir


def _write_intervene_run(tmp_path: Path, run_id: str, slug: str, **kw) -> Path:
    run_dir = tmp_path / run_id
    run_dir.mkdir()
    (run_dir / "intervention.json").write_text(
        json.dumps(
            {"target": "zhao_xuan", "content": "干预", "story_slug": slug, "source_kind": "imported"},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    _write_branch(run_dir, "branch_a", **kw)
    return run_dir


def test_get_branch_includes_retrieval(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_intervene_run(tmp_path, "run_r1", "imp-story")

    branch = indexer.get_branch("run_r1", "branch_a")
    assert branch["retrieval"] is not None
    assert branch["retrieval"]["query"] == "韩无归 风鸣铃"
    assert branch["retrieval"]["current_chapter"] == 3
    assert len(branch["retrieval"]["items"]) == 2
    sources = {it["source"] for it in branch["retrieval"]["items"]}
    assert sources == {"fact", "contract"}


def test_get_branch_without_retrieval_is_none(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_intervene_run(tmp_path, "run_r2", "imp-story", with_retrieval=False)

    branch = indexer.get_branch("run_r2", "branch_a")
    assert branch["retrieval"] is None


def test_branch_summary_has_retrieval_flags(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_intervene_run(tmp_path, "run_r3", "imp-story")

    summary = indexer.index_run(tmp_path / "run_r3")
    assert summary is not None
    b = summary.branches[0]
    assert b.has_retrieval is True
    assert b.retrieval_count == 2


def test_tree_branch_exposes_retrieval_count(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_intervene_run(tmp_path, "run_r4", "tree-story")

    tree = indexer.build_worldline_tree(story_slug="tree-story")
    assert len(tree) == 1
    branch_a = next(b for b in tree[0]["branches"] if b["branch_id"] == "branch_a")
    assert branch_a["retrieval_count"] == 2


def test_corrupt_retrieval_json_degrades_gracefully(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    run_dir = _write_intervene_run(tmp_path, "run_r5", "imp-story")
    (run_dir / "branch_a" / "retrieval_context.json").write_text(
        "{not valid json", encoding="utf-8"
    )

    # index_run should not raise; retrieval_count falls back to 0
    summary = indexer.index_run(run_dir)
    assert summary is not None
    assert summary.branches[0].has_retrieval is True
    assert summary.branches[0].retrieval_count == 0

    # get_branch returns an empty dict for retrieval (defensive _read_json)
    branch = indexer.get_branch("run_r5", "branch_a")
    assert branch["retrieval"] == {}

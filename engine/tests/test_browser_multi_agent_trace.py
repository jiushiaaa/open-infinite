"""v0.6.3: browser surfaces multi_agent_trace.json per branch."""

from __future__ import annotations

import json
from pathlib import Path

from living_novel_engine.browser import indexer

_TRACE = {
    "worldline_id": "branch_a",
    "branch_seed": "believe",
    "turn_plans": [
        {
            "round_num": 1,
            "actor_id": "lin_fan",
            "intents": [
                {"actor_id": "lin_fan", "intent_type": "declare", "visibility": "public"}
            ],
            "delayed_actions": [],
            "relationship_signals": [
                {"from_id": "lin_fan", "to_id": "lin_wan_zhou", "change": "concern+"}
            ],
        },
        {
            "round_num": 1,
            "actor_id": "lin_wan_zhou",
            "intents": [
                {"actor_id": "lin_wan_zhou", "intent_type": "conceal", "visibility": "private"}
            ],
            "delayed_actions": [
                {"actor_id": "lin_wan_zhou", "due_round": 2, "executed": True}
            ],
            "relationship_signals": [],
        },
    ],
    "private_knowledge": [
        {"fact_id": "pk_whisper", "owner_id": "lin_wan_zhou", "content": "外部低语", "revealed": True}
    ],
    "misunderstandings": [
        {"holder_id": "lin_wan_zhou", "about": "低语来源", "corrected": True}
    ],
}


def _write_branch(run_dir: Path, branch_id: str, *, with_trace: bool = True) -> Path:
    bdir = run_dir / branch_id
    bdir.mkdir(parents=True)
    (bdir / "chapter.md").write_text(f"# {branch_id}\n\n正文。", encoding="utf-8")
    (bdir / "events.json").write_text(
        json.dumps({"theme": "相信", "runner": "multi_agent_stub"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (bdir / "state_snapshot.json").write_text(
        json.dumps({"branch_theme": "相信", "characters": {}}, ensure_ascii=False),
        encoding="utf-8",
    )
    if with_trace:
        (bdir / "multi_agent_trace.json").write_text(
            json.dumps(_TRACE, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return bdir


def _write_run(tmp_path: Path, run_id: str, slug: str, **kw) -> Path:
    run_dir = tmp_path / run_id
    run_dir.mkdir()
    (run_dir / "intervention.json").write_text(
        json.dumps(
            {"target": "lin_wan_zhou", "content": "干预", "story_slug": slug, "source_kind": "builtin"},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    _write_branch(run_dir, "branch_a", **kw)
    return run_dir


def test_get_branch_includes_trace(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_run(tmp_path, "run_t1", "tianhuang-night")

    branch = indexer.get_branch("run_t1", "branch_a")
    assert branch["multi_agent_trace"] is not None
    assert branch["multi_agent_trace"]["branch_seed"] == "believe"
    assert len(branch["multi_agent_trace"]["turn_plans"]) == 2


def test_get_branch_without_trace_is_none(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_run(tmp_path, "run_t2", "tianhuang-night", with_trace=False)

    branch = indexer.get_branch("run_t2", "branch_a")
    assert branch["multi_agent_trace"] is None


def test_corrupt_trace_json_degrades_gracefully(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    run_dir = _write_run(tmp_path, "run_t3", "tianhuang-night")
    (run_dir / "branch_a" / "multi_agent_trace.json").write_text(
        "{not valid json", encoding="utf-8"
    )

    summary = indexer.index_run(run_dir)
    assert summary is not None
    assert summary.branches[0].has_multi_agent_trace is True
    assert summary.branches[0].multi_agent_trace_count == 0

    branch = indexer.get_branch("run_t3", "branch_a")
    assert branch["multi_agent_trace"] == {}


def test_branch_summary_has_trace_flags(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_run(tmp_path, "run_t4", "tianhuang-night")

    summary = indexer.index_run(tmp_path / "run_t4")
    assert summary is not None
    b = summary.branches[0]
    assert b.has_multi_agent_trace is True
    assert b.multi_agent_trace_count == 2


def test_tree_branch_exposes_trace_flags(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_run(tmp_path, "run_t5", "tree-tianhuang")

    tree = indexer.build_worldline_tree(story_slug="tree-tianhuang")
    assert len(tree) == 1
    branch_a = next(b for b in tree[0]["branches"] if b["branch_id"] == "branch_a")
    assert branch_a["has_multi_agent_trace"] is True
    assert branch_a["multi_agent_trace_count"] == 2


def test_tree_branch_no_trace_flag_false(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_run(tmp_path, "run_t6", "tree-tianhuang2", with_trace=False)

    tree = indexer.build_worldline_tree(story_slug="tree-tianhuang2")
    branch_a = next(b for b in tree[0]["branches"] if b["branch_id"] == "branch_a")
    assert branch_a["has_multi_agent_trace"] is False
    assert branch_a["multi_agent_trace_count"] == 0

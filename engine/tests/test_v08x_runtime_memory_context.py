"""v0.8.x Runner Consumption-A：只读运行时记忆上下文。"""

from __future__ import annotations

import json

from living_novel_engine.browser import indexer
from living_novel_engine.output import writer as writer_mod
from living_novel_engine.runtime_memory import build_runtime_memory_context
from living_novel_engine.service import import_novel_from_payload, run_intervention


def _chapters(n: int = 3) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i + 1:03d}.md",
            "content": (
                f"第{i + 1}章 风鸣铃余波\n"
                f"赵轩与沈冰月在归云斋追查风鸣铃，第 {i + 1} 章韩无归留下新线索。"
            ),
        }
        for i in range(n)
    ]


def _import_project(tmp_path, name: str = "runtime-story"):
    return import_novel_from_payload(
        name=name,
        chapters=_chapters(3),
        mock=True,
        projects_dir=tmp_path,
    )


def test_runtime_memory_context_builds_prompt_and_artifact(tmp_path):
    _import_project(tmp_path)
    project_dir = tmp_path / "runtime-story"

    ctx = build_runtime_memory_context(
        project_dir,
        query="赵轩 风鸣铃",
        current_chapter=3,
    )

    artifact = ctx.to_artifact()
    assert ctx.as_prompt_block()
    assert "【运行时记忆层】" in ctx.as_prompt_block()
    assert "zhao_xuan" in ctx.as_prompt_block()
    assert artifact["version"] == "v0.8.x-runtime-memory"
    assert artifact["entity_aliases"]["status"] == "ready"
    assert artifact["resolved_query_entities"] == ["zhao_xuan"]
    assert "retrieval" in artifact
    assert artifact["retrieval"]["items"]
    assert "canon_ledger" in artifact["consumed_layers"]


def test_runtime_memory_context_corrupt_alias_degrades_to_warning(tmp_path):
    _import_project(tmp_path, name="runtime-broken")
    project_dir = tmp_path / "runtime-broken"
    (project_dir / "memory" / "entity_aliases.yaml").write_text(
        "entities: [broken",
        encoding="utf-8",
    )

    ctx = build_runtime_memory_context(
        project_dir,
        query="赵轩 风鸣铃",
        current_chapter=3,
    )

    artifact = ctx.to_artifact()
    assert artifact["entity_aliases"]["status"] == "damaged"
    assert artifact["warnings"]
    assert artifact["retrieval"]["items"]


def test_run_intervention_writes_runtime_memory_context_artifact(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setattr(indexer, "projects_dir", lambda: tmp_path)
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path / "_outputs")
    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path / "_outputs")
    _import_project(tmp_path)

    result = run_intervention(
        story_slug="runtime-story",
        target="zhao_xuan",
        content="韩无归和风鸣铃旧案有关",
        branches=2,
        rounds=1,
        mock=True,
    )

    branch_dir = result.run_dir / result.branch_ids[0]
    runtime_path = branch_dir / "runtime_memory_context.json"
    retrieval_path = branch_dir / "retrieval_context.json"
    assert runtime_path.exists()
    assert retrieval_path.exists()
    data = json.loads(runtime_path.read_text(encoding="utf-8"))
    assert data["query"] == "韩无归和风鸣铃旧案有关 赵轩"
    assert data["entity_aliases"]["status"] == "ready"
    assert data["resolved_query_entities"] == ["han_wu_gui", "zhao_xuan"]
    assert data["retrieval"]["items"]
    assert "prompt_block" in data

    branch = indexer.get_branch(result.run_id, result.branch_ids[0])
    assert branch["runtime_memory_context"]["consumed_layers"]

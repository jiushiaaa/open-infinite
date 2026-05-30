"""v0.8.x front-end artifact panel contract."""

from __future__ import annotations

import json

import yaml

from living_novel_engine.browser import indexer


def _write_json(path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_branch_detail_exposes_artifact_panel_bundle(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    run_dir = outputs / "run_artifact_panel"
    branch_dir = run_dir / "branch_a"
    branch_dir.mkdir(parents=True)
    monkeypatch.setattr(indexer, "outputs_dir", lambda: outputs)

    _write_json(
        branch_dir / "events.json",
        {"theme": "夜雨归舟", "termination_reason": "round_limit"},
    )
    (branch_dir / "chapter.md").write_text("林晚舟听见雨声。", encoding="utf-8")
    _write_json(
        branch_dir / "runtime_memory_context.json",
        {
            "version": "v0.8.x-runtime-memory",
            "query": "林晚舟",
            "current_chapter": 3,
            "consumed_layers": ["entity_aliases", "canon_ledger"],
        },
    )
    _write_json(
        branch_dir / "narrative_diagnostics.json",
        {
            "version": "v0.8-narrative-diagnostics-a",
            "kind": "narrative_diagnostics",
            "metrics": {"char_count": 8, "sentence_count": 1},
            "warnings": ["正文偏短"],
            "suggestions": ["补足转折"],
        },
    )
    _write_json(
        run_dir / "act_director_plan.json",
        {
            "version": "v0.8-actdirector-a",
            "kind": "act_director_plan",
            "steps": [{"action_id": "step-1", "action_label": "避开竹林"}],
            "warnings": [],
        },
    )
    (run_dir / "dynamic_action_registry.yaml").write_text(
        yaml.safe_dump(
            {
                "version": "v0.8-dynamic-action-registry-a",
                "kind": "dynamic_action_registry",
                "actions": [{"action_type": "avoid", "action_label": "避开"}],
                "aliases": {"避开": "avoid"},
                "summary": {"action_count": 1},
                "warnings": [],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    _write_json(
        run_dir / "emergence_nodes.json",
        {
            "version": "v0.8-emergence-mining-a",
            "kind": "emergence_nodes",
            "run_id": "run_artifact_panel",
            "nodes": [{"node_id": "n1", "title": "雨夜岔路", "score": 0.72}],
            "summary": {"node_count": 1},
            "warnings": [],
        },
    )

    detail = indexer.get_branch("run_artifact_panel", "branch_a")

    assert detail["runtime_memory_context"]["consumed_layers"] == [
        "entity_aliases",
        "canon_ledger",
    ]
    assert detail["act_director_plan"]["kind"] == "act_director_plan"
    assert detail["dynamic_action_registry"]["summary"]["action_count"] == 1
    assert detail["narrative_diagnostics"]["kind"] == "narrative_diagnostics"
    assert detail["emergence_nodes"]["summary"]["node_count"] == 1


def test_branch_detail_degrades_corrupt_artifacts_to_empty_state(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    run_dir = outputs / "run_artifact_broken"
    branch_dir = run_dir / "branch_a"
    branch_dir.mkdir(parents=True)
    monkeypatch.setattr(indexer, "outputs_dir", lambda: outputs)

    (branch_dir / "chapter.md").write_text("旧分支。", encoding="utf-8")
    (branch_dir / "narrative_diagnostics.json").write_text("{broken", encoding="utf-8")
    (run_dir / "act_director_plan.json").write_text("{broken", encoding="utf-8")
    (run_dir / "dynamic_action_registry.yaml").write_text("actions: [broken", encoding="utf-8")
    (run_dir / "emergence_nodes.json").write_text("{broken", encoding="utf-8")

    detail = indexer.get_branch("run_artifact_broken", "branch_a")

    assert detail["act_director_plan"] == {}
    assert detail["dynamic_action_registry"] is None
    assert detail["narrative_diagnostics"] == {}
    assert detail["emergence_nodes"] == {}

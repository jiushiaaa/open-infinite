"""v0.7.2：旧 run_scene / events.json / state_snapshot.json 契约不变。

确认 CharacterAction additive 字段不会泄漏进既有输出契约，
默认 lightweight runner 行为与 v0.7 完全一致。
"""

from __future__ import annotations

import json

from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.orchestrator import build_branch_specs, run_scene
from living_novel_engine.output.writer import write_run_output
from living_novel_engine.samples import load_sample

# CharacterAction v0.7.2 新增字段——不得出现在 events.json / state_snapshot.json 中。
_NEW_ACTION_FIELDS = (
    "preconditions",
    "effects",
    "failure_reason",
    "repair_suggestions",
    "action_label",
)


def _run_branch_a():
    bundle = load_sample("tianhuang-night")
    llm = LLMClient(mock=True)
    inv = audit_intervention(
        build_intervention(
            target="lin_wan_zhou",
            content="今晚不要去城外竹林",
            intervention_type="whisper",
        ),
        bundle.world,
        bundle.character_map(),
    )
    inv.story_slug = "tianhuang-night"
    inv.source_kind = "builtin"
    spec = next(s for s in build_branch_specs(inv, 3) if s.branch_id == "branch_a")
    result = run_scene(
        bundle.world,
        bundle.characters,
        inv,
        spec,
        llm,
        max_rounds=2,
        canon_excerpt=bundle.canon_chapter,
        canon_chapter=bundle.canon_chapter,
    )
    return inv, result


def test_lightweight_simulation_contract_unchanged():
    _, result = _run_branch_a()
    assert result.runner_name == "lightweight"
    assert result.accepted_events
    assert result.chapter_text.strip()
    assert result.state_snapshot.get("branch_seed") == "believe"
    # multi_agent_trace 仍恒为 None（lightweight 不产出）
    assert result.multi_agent_trace is None


def test_events_and_snapshot_do_not_leak_new_action_fields(tmp_path, monkeypatch):
    import living_novel_engine.output.writer as writer_mod

    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)

    inv, result = _run_branch_a()
    out = write_run_output(inv, [result], run_id="test_v072_contract")

    events_text = (out.run_dir / "branch_a" / "events.json").read_text(encoding="utf-8")
    snapshot_text = (
        out.run_dir / "branch_a" / "state_snapshot.json"
    ).read_text(encoding="utf-8")

    events = json.loads(events_text)
    # 既有契约键仍在
    assert events.get("runner") == "lightweight"
    assert "theme" in events

    # 新增 CharacterAction 字段不得泄漏进既有产物
    for field in _NEW_ACTION_FIELDS:
        assert field not in events_text
        assert field not in snapshot_text

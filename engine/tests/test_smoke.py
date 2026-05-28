from __future__ import annotations

import json
from pathlib import Path

import pytest

from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.models import CharacterAgent
from living_novel_engine.models.contract_audit import ContractAuditResult
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import FIXED_BRANCHES, build_branch_specs
from living_novel_engine.output.writer import write_run_output
from living_novel_engine.samples import list_samples, load_sample


def test_list_samples_english_slug():
    samples = list_samples()
    assert "tianhuang-night" in samples


def test_load_sample_bundle():
    bundle = load_sample("tianhuang-night")
    assert bundle.display_name == "天荒城残夜"
    assert bundle.slug == "tianhuang-night"
    assert len(bundle.characters) >= 5
    assert bundle.canon_chapter
    assert "林晚舟" in bundle.canon_chapter
    assert bundle.prologue
    assert "前情提要" in bundle.prologue
    assert bundle.canon_opening
    assert "第一章" in bundle.canon_opening
    assert "前情提要" in bundle.canon_context_for_narrator()


def test_intervention_audit_structured():
    bundle = load_sample("tianhuang-night")
    intervention = build_intervention(
        target="lin_wan_zhou",
        content="今晚不要去城外竹林，那是墨青烟设的局",
        intervention_type="whisper",
    )
    audited = audit_intervention(intervention, bundle.world, bundle.character_map())
    assert audited.contract_audit is not None
    audit = audited.contract_audit
    assert isinstance(audit, ContractAuditResult)
    assert hasattr(audit, "allowed")
    assert hasattr(audit, "risk")
    assert hasattr(audit, "violations")
    assert hasattr(audit, "repair_suggestions")
    assert hasattr(audit, "expected_character_resistance")
    assert audit.risk in ("low", "medium", "high")
    assert audit.expected_character_resistance in ("low", "medium", "high")


def test_branch_specs_fixed_three():
    intervention = build_intervention(
        target="lin_wan_zhou", content="测试", intervention_type="whisper"
    )
    specs = build_branch_specs(intervention, count=3)
    assert len(specs) == 3
    assert [s.theme for s in specs] == [b["theme"] for b in FIXED_BRANCHES]
    assert {s.branch_seed for s in specs} == {"believe", "doubt", "reject"}


def test_mock_scene_run_state_snapshot(tmp_path, monkeypatch):
    bundle = load_sample("tianhuang-night")
    llm = LLMClient(mock=True)
    intervention = build_intervention(
        target="lin_wan_zhou",
        content="今晚不要去城外竹林",
        intervention_type="whisper",
    )
    intervention = audit_intervention(intervention, bundle.world, bundle.character_map())
    spec = build_branch_specs(intervention, count=1)[0]

    result = run_scene(
        bundle.world,
        bundle.characters,
        intervention,
        spec,
        llm,
        max_rounds=2,
        canon_excerpt=bundle.canon_context_for_narrator(),
        prologue=bundle.prologue,
        canon_opening=bundle.canon_opening,
        canon_chapter=bundle.canon_chapter,
    )
    assert result.accepted_events
    assert result.summary_text
    assert result.chapter_text
    assert "前情提要" in result.chapter_text
    assert "第一章" in result.chapter_text
    snap = result.state_snapshot
    assert "characters" in snap
    assert "relationship_changes" in snap
    assert "open_threads" in snap
    assert "next_chapter_hook" in snap and snap["next_chapter_hook"]
    assert "lin_wan_zhou" in snap["characters"] or len(snap["characters"]) >= 1
  # mock 含前情+开篇+干预章节选，不验证 1500 字
    assert len(result.chapter_text) < 12000

    import living_novel_engine.output.writer as writer_mod

    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)

    out = write_run_output(intervention, [result], run_id="test_run")
    assert (out.run_dir / "intervention.json").exists()
    assert (out.run_dir / "branch_a" / "state_snapshot.json").exists()
    chapter = (out.run_dir / "branch_a" / "chapter.md").read_text(encoding="utf-8")
    assert chapter.strip()

    snapshot = json.loads(
        (out.run_dir / "branch_a" / "state_snapshot.json").read_text(encoding="utf-8")
    )
    assert snapshot.get("next_chapter_hook")
    assert "characters" in snapshot
    assert "open_threads" in snapshot


def test_three_branches_different_hooks():
    bundle = load_sample("tianhuang-night")
    llm = LLMClient(mock=True)
    intervention = audit_intervention(
        build_intervention(
            target="lin_wan_zhou",
            content="今晚不要去城外竹林",
            intervention_type="whisper",
        ),
        bundle.world,
        bundle.character_map(),
    )
    hooks = []
    for spec in build_branch_specs(intervention, count=3):
        r = run_scene(
            bundle.world,
            bundle.characters,
            intervention,
            spec,
            llm,
            max_rounds=2,
            canon_excerpt=bundle.canon_context_for_narrator(),
            prologue=bundle.prologue,
            canon_opening=bundle.canon_opening,
            canon_chapter=bundle.canon_chapter,
        )
        hooks.append(r.state_snapshot.get("next_chapter_hook", ""))
    assert len(set(hooks)) >= 2


def test_pydantic_character_validation():
    c = CharacterAgent(
        id="test",
        name="测试",
        persona={"traits": ["冷静"], "desires": [], "fears": [], "boundaries": ["不会说谎"]},
    )
    assert "不会说谎" in c.persona.boundaries[0]


def test_genre_fallback_builtin_only(monkeypatch):
    monkeypatch.delenv("WEBNOVEL_GENRE_TEMPLATE", raising=False)
    from living_novel_engine.agents.narrator import genre_style_hint

    hint = genre_style_hint()
    assert "内置" in hint or "修真" in hint or "短句" in hint

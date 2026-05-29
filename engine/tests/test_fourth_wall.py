from __future__ import annotations

import json

from living_novel_engine.fourth_wall import (
    FourthWallLedger,
    accumulate_intervention,
    awareness_decision_hint,
    awareness_narrator_hint,
    detect_triggers,
    fourth_wall_enabled,
    level_from_score,
    level_rank,
    load_ledger,
    save_ledger,
    should_persist_ledger,
)
from living_novel_engine.fourth_wall.ledger import CharacterAwareness
from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import build_branch_specs
from living_novel_engine.output.writer import (
    load_lineage_ledger,
    load_run_ledger,
    write_run_output,
)
from living_novel_engine.samples import load_sample


def _audited(target: str, content: str, *, intervention_type="whisper", strength=None):
    bundle = load_sample("tianhuang-night")
    inv = build_intervention(
        target=target,
        content=content,
        intervention_type=intervention_type,
        strength=strength,
    )
    inv = audit_intervention(inv, bundle.world, bundle.character_map())
    inv.story_slug = "tianhuang-night"
    inv.source_kind = "builtin"
    return inv


# ── 打分 / 触发器 ──────────────────────────────────────────────


def test_level_thresholds_ascending():
    assert level_from_score(0.0) == "none"
    assert level_from_score(0.2) == "unsettled"
    assert level_from_score(0.5) == "suspicious"
    assert level_from_score(0.7) == "aware"
    assert level_from_score(0.95) == "defiant"
    # rank 单调
    assert level_rank("none") < level_rank("suspicious") < level_rank("defiant")


def test_detect_triggers_channel_and_strength():
    inv = _audited("lin_wan_zhou", "今晚不要去城外竹林", strength="strong")
    triggers = detect_triggers(inv, repeat_count=1)
    assert "impossible_information" in triggers  # whisper 渠道
    assert "fate_reversal" in triggers  # strong
    assert "personality_violation" in triggers  # 审计高抗拒/违规
    assert "repeated_rescue" not in triggers


def test_detect_triggers_repeated_rescue():
    inv = _audited("lin_wan_zhou", "再救她一次", intervention_type="dream_hint")
    assert "repeated_rescue" in detect_triggers(inv, repeat_count=2)
    assert "repeated_rescue" not in detect_triggers(inv, repeat_count=1)


def test_accumulate_raises_score_and_level():
    ledger = FourthWallLedger()
    inv = _audited("lin_wan_zhou", "今晚不要去城外竹林")
    accumulate_intervention(ledger, inv, chapter=12, present_ids=["lin_wan_zhou", "lin_fan"])
    aw = ledger.awareness["lin_wan_zhou"]
    assert aw.score > 0
    assert aw.intervention_count == 1
    first = aw.score

    # 再来一次强干预，分数上升、等级不降
    inv2 = _audited("lin_wan_zhou", "她身后影子来自乱葬岗", strength="strong")
    accumulate_intervention(ledger, inv2, chapter=13, present_ids=["lin_wan_zhou", "lin_fan"])
    aw = ledger.awareness["lin_wan_zhou"]
    assert aw.score > first
    assert aw.intervention_count == 2
    assert "repeated_rescue" in aw.triggers
    assert level_rank(aw.level) >= level_rank("unsettled")
    assert len(ledger.traces) == 2


def test_score_clamped_to_one():
    ledger = FourthWallLedger()
    for i in range(20):
        inv = _audited("lin_wan_zhou", "必须立刻离开", strength="strong")
        accumulate_intervention(ledger, inv, chapter=12 + i, present_ids=["lin_wan_zhou"])
    assert ledger.awareness["lin_wan_zhou"].score <= 1.0
    assert ledger.awareness["lin_wan_zhou"].level == "defiant"


def test_scene_visibility_spillover():
    ledger = FourthWallLedger()
    inv = _audited(
        "lin_wan_zhou", "在场众人皆见异象", intervention_type="whisper", strength="strong"
    )
    # 强制广域可见
    inv = inv.model_copy(update={"visibility": "world_wide"})
    accumulate_intervention(ledger, inv, chapter=12, present_ids=["lin_wan_zhou", "lin_fan"])
    assert ledger.awareness["lin_wan_zhou"].score > 0
    # 旁观者也有较弱的觉察
    assert "lin_fan" in ledger.awareness
    assert ledger.awareness["lin_fan"].score < ledger.awareness["lin_wan_zhou"].score


def test_target_only_no_spillover():
    ledger = FourthWallLedger()
    inv = _audited("lin_wan_zhou", "今晚不要去城外竹林")  # target_only
    accumulate_intervention(ledger, inv, chapter=12, present_ids=["lin_wan_zhou", "lin_fan"])
    assert "lin_fan" not in ledger.awareness


# ── 提示文案分级 ──────────────────────────────────────────────


def test_decision_hint_threshold():
    none = CharacterAwareness(character_id="x", level="none")
    assert awareness_decision_hint(none, "甲") == ""
    susp = CharacterAwareness(character_id="x", level="suspicious")
    assert "怀疑" in awareness_decision_hint(susp, "林晚舟")
    aware = CharacterAwareness(character_id="x", level="aware")
    assert awareness_decision_hint(aware, "林晚舟") != ""


def test_narrator_hint_only_above_suspicious():
    unsettled = [CharacterAwareness(character_id="x", level="unsettled")]
    assert awareness_narrator_hint(unsettled) == ""
    aware = [CharacterAwareness(character_id="x", level="aware")]
    assert awareness_narrator_hint(aware) != ""


# ── 持久化 ─────────────────────────────────────────────────────


def test_ledger_roundtrip(tmp_path):
    ledger = FourthWallLedger()
    inv = _audited("lin_wan_zhou", "今晚不要去城外竹林", strength="strong")
    accumulate_intervention(ledger, inv, chapter=12, present_ids=["lin_wan_zhou"])
    path = tmp_path / "fourth_wall.json"
    save_ledger(path, ledger)
    loaded = load_ledger(path)
    assert loaded.awareness["lin_wan_zhou"].score == ledger.awareness["lin_wan_zhou"].score
    assert len(loaded.traces) == 1


def test_load_corrupt_ledger_returns_empty(tmp_path):
    path = tmp_path / "fourth_wall.json"
    path.write_text("{not valid json", encoding="utf-8")
    loaded = load_ledger(path)
    assert loaded.awareness == {}
    assert loaded.traces == []


def test_load_missing_ledger_returns_empty(tmp_path):
    assert load_ledger(tmp_path / "nope.json").traces == []


def test_fourth_wall_enabled_env(monkeypatch):
    monkeypatch.delenv("LNE_FOURTH_WALL", raising=False)
    assert fourth_wall_enabled() is True
    monkeypatch.setenv("LNE_FOURTH_WALL", "0")
    assert fourth_wall_enabled() is False
    monkeypatch.setenv("LNE_FOURTH_WALL", "off")
    assert fourth_wall_enabled() is False
    monkeypatch.setenv("LNE_FOURTH_WALL", "1")
    assert fourth_wall_enabled() is True


# ── 与 run_scene 集成 ─────────────────────────────────────────


def _run_branch_a(ledger: FourthWallLedger | None):
    bundle = load_sample("tianhuang-night")
    llm = LLMClient(mock=True)
    inv = _audited("lin_wan_zhou", "她身后影子来自乱葬岗", strength="strong")
    spec = next(s for s in build_branch_specs(inv, 3) if s.branch_id == "branch_a")
    return run_scene(
        bundle.world,
        bundle.characters,
        inv,
        spec,
        llm,
        max_rounds=2,
        canon_excerpt=bundle.canon_chapter,
        canon_chapter=bundle.canon_chapter,
        ledger=ledger,
    ), inv


def test_run_scene_embeds_fourth_wall_in_snapshot():
    ledger = FourthWallLedger(enabled=True)
    inv = _audited("lin_wan_zhou", "她身后影子来自乱葬岗", strength="strong")
    accumulate_intervention(
        ledger, inv, chapter=13, present_ids=["lin_wan_zhou", "lin_fan"]
    )
    result, _ = _run_branch_a(ledger)
    snap = result.state_snapshot
    assert "fourth_wall" in snap
    fw = snap["fourth_wall"]
    assert fw["enabled"] is True
    assert "lin_wan_zhou" in fw["characters"]
    lwz = snap["characters"]["lin_wan_zhou"]
    assert "fourth_wall_awareness" in lwz


def test_aware_level_surfaces_in_mock_chapter():
    ledger = FourthWallLedger(enabled=True)
    inv = _audited("lin_wan_zhou", "她身后影子来自乱葬岗", strength="strong")
    accumulate_intervention(
        ledger, inv, chapter=13, present_ids=["lin_wan_zhou", "lin_fan"]
    )
    # 已是 aware/defiant，正文应出现第四面墙旁白
    assert level_rank(ledger.awareness["lin_wan_zhou"].level) >= level_rank("aware")
    result, _ = _run_branch_a(ledger)
    assert "安排这一切" in result.chapter_text or "你在看着" in result.chapter_text


def test_disabled_ledger_no_fourth_wall_leak(tmp_path, monkeypatch):
    """LNE_FOURTH_WALL=0：无 prompt 注入、无 snapshot 字段、不写 fourth_wall.json。"""
    import living_novel_engine.output.writer as writer_mod

    monkeypatch.setenv("LNE_FOURTH_WALL", "0")
    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)
    assert fourth_wall_enabled() is False

    result, inv = _run_branch_a(None)
    snap = result.state_snapshot
    assert "fourth_wall" not in snap
    for cs in snap.get("characters", {}).values():
        assert "fourth_wall_awareness" not in cs
        assert "fourth_wall_level" not in cs
    assert "安排这一切" not in result.chapter_text
    assert "你在看着" not in result.chapter_text

    out = write_run_output(inv, [result], run_id="test_fw_off", ledger=None)
    assert not (out.run_dir / "fourth_wall.json").exists()


def test_should_persist_ledger_requires_enabled_and_content():
    empty = FourthWallLedger(enabled=True)
    assert should_persist_ledger(empty) is False
    assert should_persist_ledger(FourthWallLedger(enabled=False)) is False
    assert should_persist_ledger(None) is False
    ledger = FourthWallLedger(enabled=True)
    accumulate_intervention(
        ledger,
        _audited("lin_wan_zhou", "test"),
        chapter=1,
        present_ids=["lin_wan_zhou"],
    )
    assert should_persist_ledger(ledger) is True


def test_load_lineage_ledger_skips_child_without_artifact(tmp_path, monkeypatch):
    import living_novel_engine.output.writer as writer_mod

    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)

    parent_dir = tmp_path / "parent_run"
    parent_dir.mkdir()
    parent_ledger = FourthWallLedger(enabled=True)
    accumulate_intervention(
        parent_ledger,
        _audited("lin_wan_zhou", "今晚不要去城外竹林"),
        chapter=12,
        present_ids=["lin_wan_zhou"],
    )
    save_ledger(parent_dir / "fourth_wall.json", parent_ledger)
    parent_score = parent_ledger.awareness["lin_wan_zhou"].score

    child_dir = tmp_path / "child_run"
    child_dir.mkdir()
    (child_dir / "meta.json").write_text(
        json.dumps({"parent_run_id": "parent_run"}), encoding="utf-8"
    )

    loaded = load_lineage_ledger("child_run")
    assert loaded.awareness["lin_wan_zhou"].score == parent_score
    assert len(loaded.traces) == 1


def test_reenable_does_not_inherit_disabled_period_traces(tmp_path, monkeypatch):
    """关闭期间的干预不计入账本；重新开启后沿 lineage 继承关闭前状态。"""
    import living_novel_engine.output.writer as writer_mod

    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)

    ledger_a = FourthWallLedger(enabled=True)
    inv1 = _audited("lin_wan_zhou", "今晚不要去城外竹林", strength="medium")
    accumulate_intervention(ledger_a, inv1, chapter=12, present_ids=["lin_wan_zhou"])
    result_a, _ = _run_branch_a(ledger_a)
    write_run_output(inv1, [result_a], run_id="run_enabled_a", ledger=ledger_a)
    traces_before = len(ledger_a.traces)

    child_dir = tmp_path / "run_disabled_gap"
    child_dir.mkdir()
    (child_dir / "meta.json").write_text(
        json.dumps({"parent_run_id": "run_enabled_a"}), encoding="utf-8"
    )
    # 关闭期 run：无 fourth_wall.json（模拟 disabled 输出）

    ledger_resumed = load_lineage_ledger("run_disabled_gap")
    assert len(ledger_resumed.traces) == traces_before

    inv2 = _audited("lin_wan_zhou", "她必须立刻离开", strength="strong")
    accumulate_intervention(
        ledger_resumed, inv2, chapter=14, present_ids=["lin_wan_zhou"]
    )
    assert len(ledger_resumed.traces) == traces_before + 1


def test_write_run_output_persists_ledger(tmp_path, monkeypatch):
    import living_novel_engine.output.writer as writer_mod

    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)

    ledger = FourthWallLedger(enabled=True)
    inv = _audited("lin_wan_zhou", "今晚不要去城外竹林", strength="strong")
    accumulate_intervention(ledger, inv, chapter=12, present_ids=["lin_wan_zhou"])
    result, _ = _run_branch_a(FourthWallLedger(enabled=True))

    out = write_run_output(inv, [result], run_id="test_fw_run", ledger=ledger)
    fw_file = out.run_dir / "fourth_wall.json"
    assert fw_file.exists()
    data = json.loads(fw_file.read_text(encoding="utf-8"))
    assert "lin_wan_zhou" in data["awareness"]

    # load_run_ledger 能读回
    reloaded = load_run_ledger("test_fw_run")
    assert reloaded.awareness["lin_wan_zhou"].score > 0

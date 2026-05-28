from __future__ import annotations

from living_novel_engine.orchestrator.canon_guard import (
    normalize_canon_text,
    polish_canon_in_chapter,
    validate_canon_consistency,
)
from living_novel_engine.samples import load_sample


def test_forbidden_rebirth_trope():
    v = validate_canon_consistency("林凡重生的记忆涌上心头。")
    assert any("重生" in x or "重生" in x for x in v)


def test_soul_bell_origin_drift():
    v = validate_canon_consistency("退魂铃乃是青云宗至宝，宗门长辈所赐。")
    assert len(v) >= 1


def test_character_name_typo():
    v = validate_canon_consistency("莫青烟站在竹林中。")
    assert any("莫青烟" in x for x in v)
    assert normalize_canon_text("莫青烟冷笑。") == "墨青烟冷笑。"


def test_polish_canon_in_chapter():
    raw = "莫青烟离去。退魂铃是青云宗至宝，林凡重生的记忆浮现。"
    out = polish_canon_in_chapter(raw)
    assert "莫青烟" not in out
    assert "墨青烟" in out
    assert "青云宗至宝" not in out
    assert "重生的记忆" not in out


def test_discipline_hall_normalized():
    assert normalize_canon_text("外门弟子被戒律堂问责。") == "外门弟子被执法堂问责。"


def test_world_yaml_has_canon_rules():
    bundle = load_sample("tianhuang-night")
    rules_text = bundle.world.rules_text()
    assert "重生" in rules_text
    assert "墨青烟" in rules_text

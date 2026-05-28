from __future__ import annotations

from living_novel_engine.models.events import CharacterAction
from living_novel_engine.orchestrator.canon_guard import (
    normalize_canon_text,
    validate_canon_consistency,
)
from living_novel_engine.orchestrator.scene_rules import (
    lin_wan_zhou_jade_resource_drift,
    rewrite_lwz_jade_resource_drift,
)


def test_rewrite_lwz_does_not_introduce_bamboo_slip():
    action = CharacterAction(
        character_id="lin_wan_zhou",
        character_name="林晚舟",
        stance="believe",
        action_type="investigate",
        target="lin_fan",
        content=(
            "林晚舟凝视着那枚已经封好的竹简，声音微沉："
            "「林凡，外门应急竹简一生仅此一枚……」"
        ),
        internal_thought="玉简已碎",
        intervention_response="believe",
    )
    scene_state = {"jade_slip_used": True}
    assert lin_wan_zhou_jade_resource_drift(action, scene_state)
    fixed = rewrite_lwz_jade_resource_drift(action, scene_state)
    assert "应急竹简" not in fixed.content
    assert "墨色竹简" not in fixed.content
    assert "封好的竹简" not in fixed.content
    assert "竹简" not in fixed.content or "传讯" in fixed.content


def test_normalize_preserves_mo_apology_slip_when_jade_unused():
    text = "她在墨色竹简上刻下推脱之辞。"
    assert normalize_canon_text(text, jade_slip_used=False) == text


def test_normalize_mo_slip_when_jade_used_becomes_echo():
    text = "她收起墨色竹简，只闻耳畔余音。"
    out = normalize_canon_text(text, jade_slip_used=True)
    assert "墨色竹简" not in out
    assert "传讯" in out


def test_validate_lwz_holding_slip():
    text = "林晚舟握着那枚应急竹简，放到案几上。"
    violations = validate_canon_consistency(text)
    assert any("林晚舟" in v or "术语" in v for v in violations)

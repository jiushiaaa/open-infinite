"""v0.7.2 CharacterAction additive 字段兼容性。

确认新增结构化动作字段全部 additive：
- 旧构造调用（不传新字段）仍可用，新字段为安全默认空值。
- 旧 dump 读取不被破坏；新字段可选填且独立。
"""

from __future__ import annotations

from living_novel_engine.models.events import CharacterAction


def test_legacy_construction_still_works():
    # 旧调用方式（v0.7.1 之前）不传任何新字段。
    act = CharacterAction(
        character_id="hero",
        character_name="主角",
        stance="believe",
        action_type="speak",
        target="ally",
        content="低声示警",
    )
    assert act.action_id is None
    assert act.action_label == ""
    assert act.preconditions == []
    assert act.effects == []
    assert act.failure_reason == ""
    assert act.repair_suggestions == []
    assert act.risk == ""
    assert act.visibility == ""


def test_new_fields_optional_and_independent():
    act = CharacterAction(
        character_id="hero",
        character_name="主角",
        action_type="use_item",
        content="捏碎玉简",
        action_id="act_001",
        action_label="传讯示警",
        preconditions=["持有传讯玉简"],
        effects=["玉简碎裂", "警告送达"],
        failure_reason="",
        repair_suggestions=["改用口信"],
        risk="medium",
        visibility="target_only",
    )
    assert act.action_id == "act_001"
    assert act.preconditions == ["持有传讯玉简"]
    assert act.effects == ["玉简碎裂", "警告送达"]
    assert act.risk == "medium"


def test_dump_roundtrip_preserves_legacy_keys():
    act = CharacterAction(
        character_id="hero",
        character_name="主角",
        action_type="observe",
        content="静观其变",
    )
    data = act.model_dump()
    # 旧字段仍在
    for key in (
        "character_id",
        "character_name",
        "stance",
        "action_type",
        "target",
        "content",
        "internal_thought",
        "intervention_response",
    ):
        assert key in data
    # 新字段以默认值出现，不破坏序列化
    assert data["preconditions"] == []
    restored = CharacterAction(**data)
    assert restored == act

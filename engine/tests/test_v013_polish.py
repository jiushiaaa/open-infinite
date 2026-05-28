from __future__ import annotations

from living_novel_engine.models.events import AcceptedEvent, SimulationResult
from living_novel_engine.orchestrator.canon_guard import (
    normalize_canon_text,
    validate_canon_consistency,
)
from living_novel_engine.orchestrator.narrative_constraints import (
    chapter_from_snapshot_and_events,
    is_structured_chapter_fallback,
    summary_from_snapshot,
)
from living_novel_engine.orchestrator.scene_rules import ensure_bamboo_arrival_event
from living_novel_engine.output.writer import _build_compare_md


def test_summary_bamboo_over_investigating():
    result = SimulationResult(
        worldline_id="branch_c",
        branch_seed="reject",
        theme="拒绝干预·反弹",
        termination_reason="竹林线已触发",
    )
    result.state_snapshot = {
        "scene_flags": {
            "bamboo_grove_triggered": True,
            "investigating": False,
            "lin_wan_zhou_departed": True,
            "jade_slip_used": True,
        },
        "characters": {
            "lin_wan_zhou": {"location": "城外竹林（石亭）", "emotion": "决意"},
        },
        "next_chapter_hook": "石亭阵纹亮如骨烛",
    }
    text = summary_from_snapshot("天荒城", result)
    assert "已抵达城外竹林" in text
    assert "未赴竹林" not in text


def test_ensure_bamboo_arrival_event_appends_move():
    scene_state = {
        "bamboo_grove_triggered": True,
        "branch_seed": "reject",
        "lin_wan_zhou_departed": True,
    }
    events: list = [
        AcceptedEvent(
            event_id="e1",
            chapter=15,
            round_num=1,
            event_type="speak",
            subject="lin_wan_zhou",
            payload={"content": "否则我今夜必去竹林赴约", "stance": "reject"},
            narrative="",
        )
    ]
    ensure_bamboo_arrival_event(scene_state, events, {}, chapter_number=15)
    assert len(events) == 2
    assert events[-1].event_type == "move_to_bamboo_grove"


def test_normalize_jade_slip_drift():
    out = normalize_canon_text("他握紧师门唯一的竹简。", jade_slip_used=True)
    assert "传讯玉简" in out
    assert "师门唯一的竹简" not in out
    assert "墨色竹简" not in out or "传讯玉简" in out


def test_normalize_preserves_ink_bamboo_slip_when_jade_unused():
    text = "她在墨色竹简上刻下推脱之辞。"
    assert normalize_canon_text(text, jade_slip_used=False) == text


def test_chapter_fallback_uses_chapter_number_not_hardcoded_13():
    result = SimulationResult(
        worldline_id="branch_a",
        branch_seed="believe",
        theme="相信干预",
        termination_reason="调查拖延成功",
    )
    result.accepted_events = [
        AcceptedEvent(
            event_id="e1",
            chapter=15,
            round_num=1,
            event_type="speak",
            subject="lin_fan",
            payload={"content": "低语告知乱葬岗影子"},
            narrative="",
        )
    ]
    result.state_snapshot = {
        "scene_flags": {"investigating": True, "lin_wan_zhou_departed": False},
        "next_chapter_hook": "钩子",
    }
    text = chapter_from_snapshot_and_events(
        result, result.state_snapshot, chapter_number=15
    )
    assert "# 第15章" in text
    assert "第十三章" not in text
    assert not is_structured_chapter_fallback(text)


def test_compare_md_uses_snapshot_summary():
    r = SimulationResult(
        worldline_id="branch_c",
        branch_seed="reject",
        theme="拒绝干预·反弹",
        termination_reason="竹林线已触发",
        summary_text="旧文案：林晚舟未赴竹林",
    )
    r.state_snapshot = {
        "scene_flags": {"bamboo_grove_triggered": True},
        "characters": {"lin_wan_zhou": {"location": "城外竹林（石亭）"}},
        "next_chapter_hook": "石亭阵纹亮如骨烛",
    }
    md = _build_compare_md([r])
    assert "已抵达城外竹林" in md
    assert "未赴竹林" not in md
    assert "石亭阵纹" in md

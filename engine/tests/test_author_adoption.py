"""World Sandbox Loop v8: author adoption desk."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

from living_novel_engine.browser import server
from living_novel_engine.service import import_novel_from_payload
from living_novel_engine.service.author_adoption import record_author_adoption
from living_novel_engine.service.author_chapter_draft import generate_author_chapter_draft
from living_novel_engine.service.author_chapter_confirmation import (
    confirm_author_chapter_entry,
)
from living_novel_engine.service.character_lens import generate_character_lens_briefs
from living_novel_engine.service.author_chapter_rewrite_application import (
    apply_author_chapter_rewrites,
)


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 作者采纳台\n"
                "赵轩追查风鸣铃，沈冰月守住苍澜派规矩，韩无归逼问旧案。"
            ),
        }
        for idx in range(1, n + 1)
    ]


def _make_project(tmp_path, slug: str = "adoption-story"):
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    return tmp_path / slug


def test_author_adoption_writes_ledger_and_export_brief(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃现世，赵轩选择隐瞒。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )

    report = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="partial",
        original_outline="赵轩按旧大纲公开风鸣铃线索，苍澜派保持稳定。",
        author_note="保留隐瞒动作，但不立刻推翻苍澜派。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    run_dir = outputs_dir / report["run_id"]
    ledger_path = tmp_path / "adoption-story" / "author_adoption_ledger.jsonl"

    assert report["version"] == "author-adoption-desk-v1"
    assert report["decision"] == "partial"
    assert report["artifact"] == "author_adoption_record.json"
    assert report["comparison"]["original_outline"]
    assert "风鸣铃" in report["comparison"]["sandbox_emergence"]
    assert report["adoption_entry"]["source_run_id"] == lens["run_id"]
    assert ledger_path.exists()
    assert (run_dir / "author_adoption_record.json").exists()
    assert (run_dir / "author_adoption_brief.md").exists()
    assert "部分采纳" in (run_dir / "author_adoption_brief.md").read_text(
        encoding="utf-8"
    )
    rows = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows[-1]["decision"] == "partial"


def test_author_adoption_feeds_next_chapter_brief_and_worldline_continuation(tmp_path):
    project_dir = _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃现世，赵轩选择隐瞒，沈冰月误判他的真实立场。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )

    report = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="adopted",
        original_outline="赵轩公开消息，沈冰月继续相信他。",
        author_note="采纳误判，让下一章从两人的信息差开场。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    run_dir = outputs_dir / report["run_id"]
    state_path = project_dir / "worldlines" / "branch_from_sandbox" / "worldline_state.json"

    assert report["artifacts"]["next_chapter_brief"] == "next_chapter_brief.json"
    assert (run_dir / "next_chapter_brief.json").exists()
    assert report["next_chapter_brief"]["opening_scene"]
    assert report["next_chapter_brief"]["sandbox_inputs"]["major_event"]
    assert report["next_chapter_brief"]["sandbox_inputs"]["worldline_id"] == "branch_from_sandbox"
    assert report["next_chapter_brief"]["materialized_consequences"]
    assert any("归云斋" in item for item in report["next_chapter_brief"]["materialized_consequences"])
    assert report["outline_diff"]["status"] in {"aligned", "diverged", "partially_aligned"}
    assert report["foreshadowing_adjustments"]
    assert report["reviewer_suggestions"]
    assert report["continuation_effect"]["affects_future_sandbox"] is True
    assert state_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["author_adoption"]["latest_decision"] == "adopted"
    assert state["next_chapter_brief"]["source_run_id"] == report["run_id"]


def test_author_chapter_draft_turns_adoption_brief_into_readable_chapter(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃现世，赵轩选择隐瞒，沈冰月误判他的真实立场。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    adoption = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="adopted",
        original_outline="赵轩公开消息，沈冰月继续相信他。",
        author_note="采纳误判，让下一章从两人的信息差开场。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )

    draft = generate_author_chapter_draft(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        mock=True,
    )
    run_dir = outputs_dir / adoption["run_id"]

    assert draft["version"] == "author-chapter-draft-v1.2"
    assert draft["story_slug"] == "adoption-story"
    assert draft["worldline_id"] == "branch_from_sandbox"
    assert draft["source_adoption_run_id"] == adoption["run_id"]
    assert draft["chapter_title"]
    assert "赵轩" in draft["chapter_text"]
    assert "沈冰月" in draft["chapter_text"]
    assert "风鸣铃" in draft["chapter_text"]
    assert "信息差" in draft["chapter_text"] or "误判" in draft["chapter_text"]
    assert len(draft["chapter_text"]) > 260
    assert draft["evidence_chain"]["adoption_record"] == "author_adoption_record.json"
    assert draft["evidence_chain"]["next_chapter_brief"] == "next_chapter_brief.json"
    assert draft["evidence_chain"]["worldline_state_artifact"].endswith(
        "worldline_state.json"
    )
    assert draft["reviewer_checklist"]
    assert draft["evidence_chain"]["materialized_consequences"]
    assert all(item["passed"] for item in draft["reviewer_checklist"])
    assert draft["revision_pack"]["artifact"] == "draft_revision_pack.json"
    assert draft["revision_pack"]["localized_rewrites"]
    assert draft["revision_pack"]["confirmation_gate"]["ready_for_confirmation"] is True
    assert any(
        "next_chapter_brief.json" in ref
        for item in draft["revision_pack"]["localized_rewrites"]
        for ref in item["evidence_refs"]
    )
    assert draft["artifacts"]["next_chapter_draft"] == "next_chapter_draft.json"
    assert draft["artifacts"]["next_chapter_markdown"] == "next_chapter_draft.md"
    assert draft["artifacts"]["draft_revision_pack"] == "draft_revision_pack.json"
    assert draft["artifacts"]["continuous_reading_chapter"] == (
        "continuous_reading_chapter.json"
    )
    assert draft["artifacts"]["continuous_reading_markdown"] == (
        "continuous_reading_chapter.md"
    )
    reading = draft["continuous_reading_chapter"]
    assert reading["artifact"] == "continuous_reading_chapter.json"
    assert reading["status"] == "ready"
    assert reading["chapter_title"] == draft["chapter_title"]
    assert len(reading["reading_body_md"]) > 500
    assert "##" in reading["reading_body_md"]
    assert "赵轩" in reading["reading_body_md"]
    assert "沈冰月" in reading["reading_body_md"]
    assert len(reading["reading_sections"]) >= 4
    assert reading["reading_flow"]["scene_count"] >= 4
    assert reading["reading_flow"]["opening_hook"]
    assert reading["reading_flow"]["next_chapter_hook"]
    assert reading["s8_source"]["lens_run_id"] == lens["run_id"]
    assert reading["s8_source"]["source_sandbox_run_id"] == lens["source"]["sandbox_run_id"]
    assert any(
        "character_lens_volumes.json" in ref
        for section in reading["cross_volume_refs"]
        for ref in section["evidence_refs"]
    )
    assert (run_dir / "next_chapter_draft.json").exists()
    assert (run_dir / "next_chapter_draft.md").exists()
    assert (run_dir / "draft_revision_pack.json").exists()
    assert (run_dir / "continuous_reading_chapter.json").exists()
    assert (run_dir / "continuous_reading_chapter.md").exists()


def test_author_chapter_confirmation_formalizes_edited_text_for_worldline(tmp_path):
    project_dir = _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃现世，赵轩选择隐瞒，沈冰月误判他的真实立场。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    adoption = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="partial",
        original_outline="赵轩公开消息，沈冰月继续相信他。",
        author_note="保留误判，把下一章写成世界线继续运行的入口。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    draft = generate_author_chapter_draft(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        mock=True,
    )
    edited = (
        draft["chapter_text"]
        + "\n\n作者确认：赵轩仍然隐瞒风鸣铃，沈冰月记住了这次信息差，"
        "归云斋的因果债会推着下一轮沙盘继续运行。"
    )

    confirmation = confirm_author_chapter_entry(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        edited_chapter_text=edited,
        author_note="确认入卷，下一轮从归云斋因果债继续。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    run_dir = outputs_dir / adoption["run_id"]
    state_path = project_dir / "worldlines" / "branch_from_sandbox" / "worldline_state.json"

    assert confirmation["version"] == "author-chapter-confirmation-v1"
    assert confirmation["artifact"] == "confirmed_chapter_entry.json"
    assert confirmation["source_adoption_run_id"] == adoption["run_id"]
    assert confirmation["worldline_id"] == "branch_from_sandbox"
    assert confirmation["edited"] is True
    assert "作者确认" in confirmation["chapter_text"]
    assert confirmation["evidence_chain"]["next_chapter_draft"] == "next_chapter_draft.json"
    assert confirmation["evidence_chain"]["worldline_state_artifact"].endswith(
        "worldline_state.json"
    )
    assert confirmation["continuation_effect"]["affects_future_sandbox"] is True
    assert "归云斋因果债" in confirmation["continuation_effect"]["next_sandbox_entry"]["major_event"]
    assert all(item["passed"] for item in confirmation["reviewer_checklist"])
    assert (run_dir / "confirmed_chapter_entry.json").exists()
    assert (run_dir / "confirmed_chapter.md").exists()
    assert not (run_dir / "chapter.md").exists()

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["confirmed_chapter_entry"]["source_adoption_run_id"] == adoption["run_id"]
    assert state["confirmed_chapter_entry"]["artifact"] == "confirmed_chapter_entry.json"
    assert state["confirmed_chapter_entry"]["edited"] is True
    assert state["confirmed_chapter_entry"]["affects_future_sandbox"] is True
    assert state["confirmed_chapter_entries"][-1]["source_adoption_run_id"] == adoption["run_id"]
    assert state["continuation_inputs"]["major_event_hint"].startswith("作者确认章节")


def test_continuous_reading_packet_tracks_viewpoints_bias_and_evidence_toggle(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃现世，赵轩选择隐瞒，沈冰月误判他的真实立场。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    adoption = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="adopted",
        original_outline="赵轩公开风鸣铃，沈冰月继续相信他。",
        author_note="让正文默认像小说阅读，可切换到角色误读和证据。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )

    draft = generate_author_chapter_draft(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        mock=True,
    )

    reading = draft["continuous_reading_chapter"]
    assert reading["default_mode"] == "novel"
    assert {tab["id"] for tab in reading["viewpoint_tabs"]} >= {
        "world_chronicle",
        "character_volume",
        "event_multi_perspective",
    }
    assert reading["evidence_toggle"]["default_visible"] is False
    assert reading["continuity_threads"]["foreshadowing"]
    assert reading["continuity_threads"]["payoff"]
    assert reading["chapter_cliffhanger"] == reading["reading_flow"]["next_chapter_hook"]
    assert all(section["viewpoint"] for section in reading["reading_sections"])
    assert all(section["cognitive_bias"] for section in reading["reading_sections"])
    assert any(section["evidence_mode"]["refs"] for section in reading["reading_sections"])


def test_continuous_reading_consumes_s8_scene_plan_as_story_beats(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃在夜雨里倒响，赵轩压住真相，沈冰月只看见他迟疑。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    adoption = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="adopted",
        original_outline="赵轩立刻公开全部真相，沈冰月没有误会。",
        author_note="让连续阅读稿按 S8 场景计划推进，不再像卷宗摘要。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )

    draft = generate_author_chapter_draft(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        mock=True,
    )

    reading = draft["continuous_reading_chapter"]
    assert reading["story_beat_source"]["kind"] == "s8_novel_scene_plan"
    beat_types = [section["source_beat_type"] for section in reading["reading_sections"]]
    assert beat_types[:5] == [
        "opening_hook",
        "viewpoint_misread",
        "materialized_consequence",
        "conflict_turn",
        "cliffhanger",
    ]
    assert all(section["narrative_role"] for section in reading["reading_sections"])
    assert all(section["body"].strip() for section in reading["reading_sections"])
    assert "卷宗" not in reading["reading_sections"][0]["body"]


def test_revision_pack_contains_semantic_reviewer_and_adoption_direction(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃现世，赵轩选择隐瞒，沈冰月误判他的真实立场。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    adoption = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="adopted",
        original_outline="赵轩公开风鸣铃，沈冰月继续相信他。",
        author_note="需要编辑指出动机、冲突、世界代偿是否自然入文。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )

    draft = generate_author_chapter_draft(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        mock=True,
    )

    pack = draft["revision_pack"]
    assert pack["semantic_reviewer"]["status"] == "ready"
    assert {item["dimension"] for item in pack["semantic_reviewer"]["review_items"]} >= {
        "人物动机",
        "冲突张力",
        "世界代偿入文",
        "视角清晰度",
    }
    first_rewrite = pack["localized_rewrites"][0]
    assert first_rewrite["original_problem"]
    assert first_rewrite["revision_intent"]
    assert first_rewrite["suggested_rewrite"]
    assert first_rewrite["impact_on_characters"]
    assert first_rewrite["impact_on_world_state"]
    assert first_rewrite["adoption_direction"] in {
        "建议采纳后确认入卷",
        "建议先局部改写再确认入卷",
    }
    assert pack["adoption_feedback"]["surface"] == "author_adoption_desk"
    assert pack["adoption_feedback"]["feeds"] >= [
        "next_chapter_draft",
        "chapter_confirmation",
    ]


def test_revision_pack_builds_editorial_preview_draft_without_overwriting_author_text(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃现世，赵轩选择隐瞒，沈冰月误判他的真实立场。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    adoption = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="adopted",
        original_outline="赵轩公开风鸣铃，沈冰月继续相信他。",
        author_note="需要 Reviewer 给出应用后的局部改写预览，而不是只列建议。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )

    draft = generate_author_chapter_draft(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        mock=True,
    )

    preview = draft["revision_pack"]["editorial_revision_draft"]
    assert preview["status"] == "ready"
    assert preview["preview_text_md"]
    assert preview["preview_text_md"] != draft["chapter_text"]
    assert len(preview["applied_rewrite_ids"]) >= 1
    assert preview["feeds"] == ["author_adoption_desk", "chapter_confirmation", "next_chapter_brief"]
    assert preview["does_not_overwrite"] == ["next_chapter_draft.md", "confirmed_chapter.md", "chapter.md"]
    assert draft["revision_pack"]["confirmation_gate"]["editorial_preview_available"] is True


def test_author_can_apply_selected_rewrites_to_draft_and_confirmation_entry(tmp_path):
    project_dir = _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃现世，赵轩选择隐瞒，沈冰月误判他的真实立场。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    adoption = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="adopted",
        original_outline="赵轩公开风鸣铃，沈冰月继续相信他。",
        author_note="让作者能直接采纳 Reviewer 局部重写。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    generate_author_chapter_draft(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        mock=True,
    )

    application = apply_author_chapter_rewrites(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        rewrite_ids=["sharpen_character_misread", "materialize_consequence"],
        author_note="采纳误判和代偿两条局部重写。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    run_dir = outputs_dir / adoption["run_id"]

    assert application["version"] == "author-chapter-rewrite-application-v1"
    assert application["artifact"] == "accepted_local_rewrites.json"
    assert application["markdown_artifact"] == "next_chapter_draft_revised.md"
    assert application["applied_rewrite_ids"] == [
        "sharpen_character_misread",
        "materialize_consequence",
    ]
    assert all(
        item["original_problem"]
        and item["revision_intent"]
        and item["suggested_rewrite"]
        and item["impact_on_world_state"]
        for item in application["applied_rewrites"]
    )
    assert "## 已采纳的 Reviewer 局部重写" in application["revised_chapter_text"]
    assert "sharpen_character_misread" in application["revised_chapter_text"]
    assert (run_dir / "accepted_local_rewrites.json").exists()
    assert (run_dir / "next_chapter_draft_revised.md").exists()

    draft_payload = json.loads(
        (run_dir / "next_chapter_draft.json").read_text(encoding="utf-8")
    )
    assert draft_payload["accepted_local_rewrites"]["artifact"] == (
        "accepted_local_rewrites.json"
    )
    assert draft_payload["accepted_local_rewrites"]["applied_rewrite_ids"] == (
        application["applied_rewrite_ids"]
    )
    assert draft_payload["chapter_text_with_accepted_rewrites"] == (
        application["revised_chapter_text"]
    )

    confirmation = confirm_author_chapter_entry(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        edited_chapter_text=application["revised_chapter_text"],
        author_note="确认入卷，并沿用已采纳的局部重写。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    assert confirmation["accepted_local_rewrites"]["applied_rewrite_ids"] == (
        application["applied_rewrite_ids"]
    )
    assert confirmation["evidence_chain"]["accepted_local_rewrites"] == (
        "accepted_local_rewrites.json"
    )
    assert "accepted_local_rewrites" in confirmation["continuation_effect"][
        "next_sandbox_entry"
    ]

    state = json.loads(
        (
            project_dir
            / "worldlines"
            / "branch_from_sandbox"
            / "worldline_state.json"
        ).read_text(encoding="utf-8")
    )
    assert state["confirmed_chapter_entry"]["accepted_rewrite_ids"] == (
        application["applied_rewrite_ids"]
    )


def test_author_chapter_confirmation_links_back_to_cross_volume_evidence(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃现世，赵轩连续隐瞒消息，沈冰月误以为他投向暗线。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    adoption = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="adopted",
        original_outline="赵轩公开风鸣铃线索，沈冰月不再怀疑。",
        author_note="采纳信息差，让确认章节可回读多视角证据。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    draft = generate_author_chapter_draft(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        mock=True,
    )

    confirmation = confirm_author_chapter_entry(
        "adoption-story",
        adoption_run_id=adoption["run_id"],
        edited_chapter_text=draft["chapter_text"]
        + "\n\n作者确认：这章必须能回读世界正史卷、赵轩个人卷和事件多视角证据。",
        author_note="确认入卷并开启跨卷宗阅读。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    run_dir = outputs_dir / adoption["run_id"]
    trail_path = run_dir / "confirmed_chapter_reading_trail.json"

    assert confirmation["artifacts"]["confirmed_chapter_reading_trail"] == (
        "confirmed_chapter_reading_trail.json"
    )
    assert trail_path.exists()
    trail = confirmation["reading_trail"]
    section_ids = {section["id"] for section in trail["sections"]}
    assert trail["source_lens_run_id"] == lens["run_id"]
    assert trail["source_sandbox_run_id"] == lens["source"]["sandbox_run_id"]
    assert {
        "confirmed_chapter",
        "worldline_state",
        "world_chronicle",
        "character_volume",
        "event_multi_perspective",
    } <= section_ids
    character_section = next(
        section for section in trail["sections"] if section["id"] == "character_volume"
    )
    assert character_section["event_node_count"] >= 3
    assert character_section["character_id"] == "zhao_xuan"
    assert any(
        "character_lens_volumes.json" in ref
        for section in trail["sections"]
        for ref in section["evidence_refs"]
    )
    assert all(item["passed"] for item in confirmation["reviewer_checklist"])
    assert any(
        item["item"] == "可回读世界正史卷、角色个人卷和事件多视角"
        and item["passed"]
        for item in confirmation["reviewer_checklist"]
    )


def test_author_adoption_supports_allowed_decisions(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    for decision in ("adopted", "partial", "new_branch", "export_brief"):
        report = record_author_adoption(
            "adoption-story",
            source_event="风鸣铃现世。",
            sandbox_summary="赵轩隐瞒消息，沈冰月开始怀疑。",
            decision=decision,
            original_outline="赵轩公开消息。",
            projects_dir=tmp_path,
            outputs_dir=outputs_dir,
        )
        assert report["decision"] == decision
        assert report["adoption_entry"]["mode_label"]


def test_author_adoption_decisions_build_distinct_chapter_feed_forward(tmp_path):
    project_dir = _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    reports = {}
    for decision in ("adopted", "partial", "new_branch"):
        reports[decision] = record_author_adoption(
            "adoption-story",
            source_event="风鸣铃现世，赵轩隐瞒消息。",
            sandbox_summary="赵轩隐瞒风鸣铃，沈冰月误判他的真实立场，归云斋被封锁复查。",
            decision=decision,
            original_outline="赵轩公开风鸣铃线索，沈冰月继续信任他。",
            author_note="让下一章从信息差和归云斋封锁继续。",
            projects_dir=tmp_path,
            outputs_dir=outputs_dir,
            worldline_id="branch_from_sandbox",
        )

    adopted_brief = reports["adopted"]["next_chapter_brief"]
    partial_brief = reports["partial"]["next_chapter_brief"]
    branch_brief = reports["new_branch"]["next_chapter_brief"]

    assert adopted_brief["writing_plan"]["stance"] == "canon_candidate"
    assert adopted_brief["writing_plan"]["next_chapter_brief_md"]
    assert adopted_brief["feed_forward"]["chapter_generation_inputs"]["decision"] == "adopted"
    assert adopted_brief["feed_forward"]["sandbox_continuation_inputs"]["worldline_id"] == (
        "branch_from_sandbox"
    )
    assert "next_chapter_brief" in adopted_brief["feed_forward"]["next_round_reads"]

    assert partial_brief["writing_plan"]["stance"] == "revision_required"
    assert partial_brief["writing_plan"]["manual_review_points"]
    assert partial_brief["feed_forward"]["chapter_generation_inputs"]["unresolved_conflicts"]
    assert partial_brief["feed_forward"]["sandbox_continuation_inputs"]["author_note"]

    assert branch_brief["writing_plan"]["stance"] == "author_branch"
    assert branch_brief["author_branch"]["branch_id"].startswith("author_branch_from_sandbox_")
    assert branch_brief["feed_forward"]["sandbox_continuation_inputs"]["worldline_id"] == (
        branch_brief["author_branch"]["branch_id"]
    )
    assert branch_brief["feed_forward"]["root_canon_policy"] == "preserve_root_canon"
    branch_state_path = (
        project_dir
        / "worldlines"
        / branch_brief["author_branch"]["branch_id"]
        / "worldline_state.json"
    )
    assert branch_state_path.exists()
    branch_state = json.loads(branch_state_path.read_text(encoding="utf-8"))
    assert branch_state["author_branch"]["source_worldline_id"] == "branch_from_sandbox"
    assert branch_state["continuation_inputs"]["worldline_id"] == branch_brief["author_branch"]["branch_id"]
    assert branch_state["branch_state"]["continuation_status"] == "runnable"

    source_state = json.loads(
        (
            project_dir
            / "worldlines"
            / "branch_from_sandbox"
            / "worldline_state.json"
        ).read_text(encoding="utf-8")
    )
    assert source_state["author_adoption"]["latest_decision"] == "partial"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _post(port: int, path: str, body: dict) -> tuple[int, dict]:
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_author_adoption_http_statuses(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "adoption-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _post(
            port,
            "/api/stories/adoption-http/author-adoption",
            {
                "source_event": "风鸣铃现世。",
                "sandbox_summary": "赵轩隐瞒消息。",
                "decision": "adopted",
                "original_outline": "赵轩公开消息。",
            },
        )
        assert status == 200
        assert body["artifact"] == "author_adoption_record.json"
        assert body["decision"] == "adopted"
        adoption_run_id = body["run_id"]

        draft_status, draft = _post(
            port,
            f"/api/stories/adoption-http/author-adoption/{adoption_run_id}/chapter-draft",
            {"mock": True},
        )
        assert draft_status == 200
        assert draft["artifact"] == "next_chapter_draft.json"
        assert "赵轩" in draft["chapter_text"]
        assert draft["evidence_chain"]["next_chapter_brief"] == "next_chapter_brief.json"
        assert draft["evidence_chain"]["materialized_consequences"]
        assert draft["artifacts"]["continuous_reading_chapter"] == (
            "continuous_reading_chapter.json"
        )
        assert draft["continuous_reading_chapter"]["reading_flow"]["scene_count"] >= 4
        assert "赵轩" in draft["continuous_reading_chapter"]["reading_body_md"]
        assert all(item["passed"] for item in draft["reviewer_checklist"])

        rewrite_status, rewrite_application = _post(
            port,
            f"/api/stories/adoption-http/author-adoption/{adoption_run_id}/chapter-rewrites",
            {
                "rewrite_ids": ["sharpen_character_misread"],
                "author_note": "采纳一条 Reviewer 局部改写。",
            },
        )
        assert rewrite_status == 200
        assert rewrite_application["artifact"] == "accepted_local_rewrites.json"
        assert rewrite_application["applied_rewrite_ids"] == ["sharpen_character_misread"]
        assert "## 已采纳的 Reviewer 局部重写" in rewrite_application["revised_chapter_text"]

        confirm_status, confirmation = _post(
            port,
            f"/api/stories/adoption-http/author-adoption/{adoption_run_id}/chapter-confirmation",
            {
                "edited_chapter_text": rewrite_application["revised_chapter_text"]
                + "\n\n作者确认：赵轩继续隐瞒风鸣铃，沈冰月记住信息差，归云斋因果债继续运行。",
                "author_note": "确认入卷。",
            },
        )
        assert confirm_status == 200
        assert confirmation["artifact"] == "confirmed_chapter_entry.json"
        assert confirmation["edited"] is True
        assert confirmation["evidence_chain"]["next_chapter_draft"] == "next_chapter_draft.json"
        assert confirmation["continuation_effect"]["affects_future_sandbox"] is True
        assert confirmation["accepted_local_rewrites"]["applied_rewrite_ids"] == [
            "sharpen_character_misread"
        ]
        assert (
            confirmation["continuation_effect"]["next_sandbox_entry"][
                "accepted_local_rewrites"
            ]
            == "accepted_local_rewrites.json"
        )
        assert confirmation["artifacts"]["confirmed_chapter_reading_trail"] == (
            "confirmed_chapter_reading_trail.json"
        )
        assert all(item["passed"] for item in confirmation["reviewer_checklist"])

        bad_status, bad = _post(
            port,
            "/api/stories/..%2Fbad/author-adoption",
            {"source_event": "风鸣铃现世。"},
        )
        assert bad_status == 400
        assert bad["error"] == "invalid slug"

        invalid_status, invalid = _post(
            port,
            "/api/stories/adoption-http/author-adoption",
            {"source_event": "风鸣铃现世。", "decision": "overwrite"},
        )
        assert invalid_status == 400
        assert "decision" in invalid["error"]

        bad_draft_status, bad_draft = _post(
            port,
            "/api/stories/adoption-http/author-adoption/..%2Fbad/chapter-draft",
            {"mock": True},
        )
        assert bad_draft_status == 400
        assert "adoption_run_id" in bad_draft["error"] or "invalid" in bad_draft["error"]

        bad_rewrite_status, bad_rewrite = _post(
            port,
            "/api/stories/adoption-http/author-adoption/..%2Fbad/chapter-rewrites",
            {"rewrite_ids": ["sharpen_character_misread"]},
        )
        assert bad_rewrite_status == 400
        assert "adoption_run_id" in bad_rewrite["error"] or "invalid" in bad_rewrite["error"]

        bad_confirm_status, bad_confirm = _post(
            port,
            "/api/stories/adoption-http/author-adoption/..%2Fbad/chapter-confirmation",
            {"edited_chapter_text": "赵轩隐瞒风鸣铃，沈冰月误判。"},
        )
        assert bad_confirm_status == 400
        assert "adoption_run_id" in bad_confirm["error"] or "invalid" in bad_confirm["error"]

        missing_status, missing = _post(
            port,
            "/api/stories/adoption-http/author-adoption/adoption_missing/chapter-draft",
            {"mock": True},
        )
        assert missing_status == 404
        assert "不存在" in missing["error"]

        missing_confirm_status, missing_confirm = _post(
            port,
            "/api/stories/adoption-http/author-adoption/adoption_missing/chapter-confirmation",
            {"edited_chapter_text": "赵轩隐瞒风鸣铃，沈冰月误判。"},
        )
        assert missing_confirm_status == 404
        assert "不存在" in missing_confirm["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()

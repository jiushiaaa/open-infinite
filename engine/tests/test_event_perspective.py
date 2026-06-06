"""Productized event perspective dossier packet."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

from living_novel_engine.browser import server
from living_novel_engine.service import import_novel_from_payload
from living_novel_engine.service.author_adoption import record_author_adoption
from living_novel_engine.service.author_chapter_confirmation import (
    confirm_author_chapter_entry,
)
from living_novel_engine.service.author_chapter_draft import generate_author_chapter_draft
from living_novel_engine.service.character_lens import generate_character_lens_briefs
from living_novel_engine.service.event_perspective import get_event_perspective


def _chapters() -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 事件多视角\n"
                "赵轩追查风鸣铃，沈冰月守住苍澜派规矩，韩无归逼问旧案。"
            ),
        }
        for idx in range(1, 7)
    ]


def _make_project(tmp_path, slug: str = "event-story") -> None:
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )


def _make_event_chain(tmp_path, slug: str = "event-story") -> str:
    _make_project(tmp_path, slug)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        slug,
        source_event="风鸣铃现世，赵轩选择隐瞒，沈冰月误判他的真实立场。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    adoption = record_author_adoption(
        slug,
        source_run_id=lens["run_id"],
        decision="adopted",
        original_outline="赵轩公开消息，沈冰月继续相信他。",
        author_note="采纳误判，让下一章从事件多视角开场。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    draft = generate_author_chapter_draft(
        slug,
        adoption_run_id=adoption["run_id"],
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        mock=True,
    )
    confirm_author_chapter_entry(
        slug,
        adoption_run_id=adoption["run_id"],
        edited_chapter_text=(
            draft["chapter_text"]
            + "\n\n作者确认：这一次事件必须能回读多视角、角色误会和世界线代偿。"
        ),
        author_note="确认事件多视角入卷。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    return lens["source"]["sandbox_run_id"]


def test_event_perspective_builds_event_page_packet_from_existing_dossier(tmp_path):
    sandbox_run_id = _make_event_chain(tmp_path)

    packet = get_event_perspective(
        "event-story",
        worldline_id="branch_from_sandbox",
        event_id="main",
        projects_dir=tmp_path,
        outputs_dir=tmp_path / "_outputs",
    )

    assert packet["version"] == "event-perspective-v1"
    assert packet["status"] == "ready"
    assert packet["event_id"] == "main"
    assert "风鸣铃" in packet["title"]
    assert packet["source_runs"]["sandbox_run_id"] == sandbox_run_id
    assert packet["event_volume"]["id"] == "event_multi_perspective"
    assert len(packet["scene_beats"]) == 5
    assert [beat["beat_type"] for beat in packet["scene_beats"]] == [
        "opening_hook",
        "viewpoint_misread",
        "materialized_consequence",
        "conflict_turn",
        "cliffhanger",
    ]
    assert packet["information_gap"]["canon_vs_character"]
    assert packet["evidence_panel"]["default_open"] is False
    assert packet["evidence_panel"]["ref_count"] >= 3
    assert any(action["id"] == "character_volume" for action in packet["next_actions"])
    assert any(action["id"] == "author" for action in packet["next_actions"])
    assert packet["boundaries"]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_event_perspective_http_statuses(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_event_chain(tmp_path, "event-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _get(
            port,
            "/api/stories/event-http/worldlines/branch_from_sandbox/events/main/perspectives",
        )
        assert status == 200
        assert body["status"] == "ready"
        assert body["event_volume"]["id"] == "event_multi_perspective"

        bad_status, bad = _get(
            port,
            "/api/stories/event-http/worldlines/..%2Fbad/events/main/perspectives",
        )
        assert bad_status == 400
        assert bad["error"] == "invalid slug, worldline id or event id"

        missing_status, missing = _get(
            port,
            "/api/stories/no-such-story/worldlines/main/events/main/perspectives",
        )
        assert missing_status == 404
        assert "不存在" in missing["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()

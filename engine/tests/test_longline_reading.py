"""Longline reading packet for cross-event worldline understanding."""

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
from living_novel_engine.service.longline_reading import get_longline_reading


def _chapters() -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 长线卷\n"
                "赵轩追查风鸣铃，沈冰月守住苍澜派规矩，韩无归逼问旧案。"
            ),
        }
        for idx in range(1, 7)
    ]


def _make_project(tmp_path, slug: str = "longline-story") -> None:
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )


def _make_longline_chain(tmp_path, slug: str = "longline-story") -> str:
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
        author_note="采纳误会长线，让下一章追踪事件、角色记忆和势力代偿。",
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
            + "\n\n作者确认：风鸣铃事件不是单点，它会持续牵动赵轩的隐瞒、"
            "沈冰月的误判和苍澜派的公开姿态。"
        ),
        author_note="确认长线卷入口。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    return adoption["run_id"]


def test_longline_reading_builds_cross_event_worldline_packet(tmp_path):
    adoption_run_id = _make_longline_chain(tmp_path)

    packet = get_longline_reading(
        "longline-story",
        worldline_id="branch_from_sandbox",
        projects_dir=tmp_path,
        outputs_dir=tmp_path / "_outputs",
    )

    assert packet["version"] == "longline-reading-v1"
    assert packet["status"] == "ready"
    assert packet["default_axis"] == "cause"
    assert packet["source_runs"]["adoption_run_id"] == adoption_run_id
    assert packet["title"].startswith("branch_from_sandbox")
    assert len(packet["timeline_entries"]) >= 5
    assert {entry["phase"] for entry in packet["timeline_entries"]} >= {
        "scene",
        "volume",
        "confirmation",
    }
    assert packet["timeline_entries"][0]["route"].startswith("#/world/longline-story")
    assert {thread["id"] for thread in packet["longline_threads"]} >= {
        "misbelief",
        "character_memory",
        "faction_pressure",
        "author_continuation",
    }
    assert packet["current_tension"]["summary"]
    assert packet["evidence_panel"]["default_open"] is False
    assert packet["evidence_panel"]["ref_count"] >= 3
    assert any(action["id"] == "event_perspective" for action in packet["next_actions"])
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


def test_longline_reading_http_statuses(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_longline_chain(tmp_path, "longline-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _get(
            port,
            "/api/stories/longline-http/worldlines/branch_from_sandbox/longline-reading",
        )
        assert status == 200
        assert body["status"] == "ready"
        assert body["timeline_entries"]

        bad_status, bad = _get(
            port,
            "/api/stories/longline-http/worldlines/..%2Fbad/longline-reading",
        )
        assert bad_status == 400
        assert bad["error"] == "invalid slug or worldline id"

        missing_status, missing = _get(
            port,
            "/api/stories/no-such-story/worldlines/main/longline-reading",
        )
        assert missing_status == 404
        assert "不存在" in missing["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()

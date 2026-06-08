"""Productized dossier reading page packet."""

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
from living_novel_engine.service.dossier_reading import get_dossier_reading


def _chapters() -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 卷宗阅读\n"
                "赵轩追查风鸣铃，沈冰月守住苍澜派规矩，韩无归逼问旧案。"
            ),
        }
        for idx in range(1, 7)
    ]


def _make_project(tmp_path, slug: str = "reading-story") -> None:
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )


def _make_reading_chain(tmp_path, slug: str = "reading-story") -> str:
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
        author_note="采纳误判，让下一章从两人的信息差开场。",
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
            + "\n\n作者确认：赵轩仍然隐瞒风鸣铃，沈冰月记住了这次信息差，"
            "归云斋的因果债会推着下一轮沙盘继续运行。"
        ),
        author_note="确认入卷并开启连续阅读。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    return adoption["run_id"]


def test_dossier_reading_prefers_novel_mode_and_keeps_evidence_folded(tmp_path):
    adoption_run_id = _make_reading_chain(tmp_path)

    packet = get_dossier_reading(
        "reading-story",
        worldline_id="branch_from_sandbox",
        projects_dir=tmp_path,
        outputs_dir=tmp_path / "_outputs",
    )

    assert packet["version"] == "dossier-reading-v1"
    assert packet["status"] == "ready"
    assert packet["default_mode"] == "novel"
    assert packet["default_tab"] == "continuous_reading"
    assert packet["source_runs"]["adoption_run_id"] == adoption_run_id
    assert packet["continuous_reading"]["reading_body_md"].startswith("#")
    assert len(packet["continuous_reading"]["reading_sections"]) >= 4
    assert packet["confirmed_chapter"]["body_md"]
    assert packet["reading_trail"]["status"] == "ready"
    assert packet["evidence_panel"]["default_open"] is False
    assert packet["evidence_panel"]["ref_count"] >= 3
    assert {tab["id"] for tab in packet["volume_tabs"]} >= {
        "world_chronicle",
        "anchor_volume",
        "character_volume",
        "faction_volume",
        "event_multi_perspective",
    }
    character_tab = next(tab for tab in packet["volume_tabs"] if tab["id"] == "character_volume")
    assert character_tab["cognitive_bias"]
    assert character_tab["body_md"]
    assert any(item["cognitive_bias"] for item in packet["perspective_biases"])


def test_dossier_reading_adds_inline_evidence_anchors_to_reading_sections(tmp_path):
    _make_reading_chain(tmp_path)

    packet = get_dossier_reading(
        "reading-story",
        worldline_id="branch_from_sandbox",
        projects_dir=tmp_path,
        outputs_dir=tmp_path / "_outputs",
    )

    sections = packet["continuous_reading"]["reading_sections"]
    anchors = [
        anchor
        for section in sections
        for anchor in section.get("inline_evidence_anchors", [])
    ]

    assert anchors
    assert {anchor["kind"] for anchor in anchors} >= {
        "character_memory",
        "world_state",
        "causal_debt",
        "event_perspective",
        "author_adoption",
    }
    assert all(anchor["label"] for anchor in anchors)
    assert all(anchor["target"]["type"] for anchor in anchors)
    assert any(anchor["target"]["type"] == "tab" and anchor["target"]["tab"] == "character_volume" for anchor in anchors)
    assert any(anchor["target"]["type"] == "worldline" for anchor in anchors)
    assert any(anchor["target"]["type"] == "author" for anchor in anchors)
    assert packet["inline_evidence_anchor_panel"]["label"] == "正文内证据锚点"
    assert packet["inline_evidence_anchor_panel"]["anchor_count"] == len(anchors)


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


def test_dossier_reading_http_statuses(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_reading_chain(tmp_path, "reading-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _get(
            port,
            "/api/stories/reading-http/worldlines/branch_from_sandbox/dossier-reading",
        )
        assert status == 200
        assert body["default_tab"] == "continuous_reading"
        assert body["evidence_panel"]["default_open"] is False

        bad_status, bad = _get(
            port,
            "/api/stories/reading-http/worldlines/..%2Fbad/dossier-reading",
        )
        assert bad_status == 400
        assert bad["error"] == "invalid slug or worldline id"

        missing_status, missing = _get(
            port,
            "/api/stories/no-such-story/worldlines/main/dossier-reading",
        )
        assert missing_status == 404
        assert "不存在" in missing["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()

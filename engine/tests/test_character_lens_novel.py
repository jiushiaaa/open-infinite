"""World Sandbox Loop v7: character lens novel briefs."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

from living_novel_engine.browser import server
from living_novel_engine.service import import_novel_from_payload
from living_novel_engine.service.character_lens import generate_character_lens_briefs


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 多视角活体小说\n"
                "赵轩追查风鸣铃，沈冰月守住苍澜派规矩，韩无归逼问旧案。"
            ),
        }
        for idx in range(1, n + 1)
    ]


def _make_project(tmp_path, slug: str = "lens-story"):
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )


def test_character_lens_writes_briefs_from_sandbox_and_subjective_memory(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    report = generate_character_lens_briefs(
        "lens-story",
        source_event="风鸣铃现世，苍澜派诸峰各自隐瞒消息。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    run_dir = outputs_dir / report["run_id"]

    assert report["version"] == "character-lens-novel-v1"
    assert report["artifact"] == "character_lens_briefs.json"
    assert (run_dir / "character_lens_briefs.json").exists()
    assert report["source"]["sandbox_run_id"]
    assert report["brief_count"] >= 5
    assert {brief["lens_type"] for brief in report["briefs"]} >= {
        "world_chronicle",
        "anchor_volume",
        "character_volume",
        "faction_volume",
        "event_multi_perspective",
    }

    character_brief = next(
        brief for brief in report["briefs"] if brief["lens_type"] == "character_volume"
    )
    assert character_brief["character_id"] == "zhao_xuan"
    assert character_brief["evidence"]["source"] == "subjective_memory"
    assert "赵轩" in character_brief["body"]
    assert "不是孤立事件" in character_brief["body"]

    perspective = next(
        brief
        for brief in report["briefs"]
        if brief["lens_type"] == "event_multi_perspective"
    )
    assert len(perspective["perspectives"]) >= 3
    assert all(item["character_id"] for item in perspective["perspectives"])


def test_character_lens_rejects_missing_event(tmp_path):
    _make_project(tmp_path)

    try:
        generate_character_lens_briefs(
            "lens-story",
            source_event="",
            projects_dir=tmp_path,
            outputs_dir=tmp_path / "_outputs",
        )
    except ValueError as exc:
        assert "source_event" in str(exc)
    else:
        raise AssertionError("expected missing source_event to fail")


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


def test_character_lens_http_statuses(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "lens-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _post(
            port,
            "/api/stories/lens-http/character-lens/generate",
            {
                "source_event": "风鸣铃现世。",
                "character_id": "zhao_xuan",
            },
        )
        assert status == 200
        assert body["artifact"] == "character_lens_briefs.json"
        assert body["brief_count"] >= 5

        bad_status, bad = _post(
            port,
            "/api/stories/..%2Fbad/character-lens/generate",
            {"source_event": "风鸣铃现世。"},
        )
        assert bad_status == 400
        assert bad["error"] == "invalid slug"

        empty_status, empty = _post(
            port,
            "/api/stories/lens-http/character-lens/generate",
            {"source_event": ""},
        )
        assert empty_status == 400
        assert "source_event" in empty["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()

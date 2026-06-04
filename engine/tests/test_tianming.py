"""World Sandbox Loop v3: Tianming book draft and confirmation."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import import_novel_from_payload
from living_novel_engine.service.tianming import (
    TianmingRequestError,
    confirm_tianming_book,
    generate_tianming_book,
    get_tianming_book,
)


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 天命书\n"
                f"赵轩追查风鸣铃，沈冰月守住苍澜派规矩，韩无归逼问旧案。"
            ),
        }
        for idx in range(1, n + 1)
    ]


def _make_project(tmp_path, slug: str = "tianming-story"):
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    return tmp_path / slug


def test_generate_tianming_book_writes_required_world_constitution(tmp_path):
    project_dir = _make_project(tmp_path)

    report = generate_tianming_book("tianming-story", projects_dir=tmp_path)
    path = project_dir / "tianming.json"
    saved = json.loads(path.read_text(encoding="utf-8"))

    assert report["status"] == "draft"
    assert report["requires_confirmation"] is True
    assert report["artifact"] == "tianming.json"
    assert path.exists()
    assert saved["narrative_attractors"]
    assert saved["genre_constraints"]
    assert saved["anchor_status"]["status"] in {"anchored", "needs_anchor"}
    assert saved["contract_pressure"]["level"] in {"low", "medium", "high"}
    assert saved["replacement_anchor_candidates"]
    assert saved["ordinary_intervention_mutates_tianming"] is False

    loaded = get_tianming_book("tianming-story", projects_dir=tmp_path)
    assert loaded["story_slug"] == "tianming-story"
    assert loaded["status"] == "draft"


def test_confirm_tianming_book_is_lightweight_and_requires_explicit_confirm(tmp_path):
    _make_project(tmp_path)
    generate_tianming_book("tianming-story", projects_dir=tmp_path)

    with pytest.raises(TianmingRequestError):
        confirm_tianming_book("tianming-story", confirm=False, projects_dir=tmp_path)

    confirmed = confirm_tianming_book(
        "tianming-story",
        confirm=True,
        projects_dir=tmp_path,
    )

    assert confirmed["status"] == "confirmed"
    assert confirmed["requires_confirmation"] is False
    assert confirmed["confirmed_at"]
    assert confirmed["confirmation"]["method"] == "lightweight"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "tianming-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


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


def test_tianming_http_generate_read_confirm_and_statuses(running_server):
    port = running_server

    generate_status, generated = _post(
        port,
        "/api/stories/tianming-http/tianming/generate",
        {},
    )
    assert generate_status == 200
    assert generated["status"] == "draft"
    assert generated["narrative_attractors"]

    read_status, loaded = _get(port, "/api/stories/tianming-http/tianming")
    assert read_status == 200
    assert loaded["artifact"] == "tianming.json"

    confirm_status, confirmed = _post(
        port,
        "/api/stories/tianming-http/tianming/confirm",
        {"confirm": True},
    )
    assert confirm_status == 200
    assert confirmed["status"] == "confirmed"

    bad_status, bad = _get(port, "/api/stories/..%2Fbad/tianming")
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    missing_status, _missing = _get(port, "/api/stories/ghost/tianming")
    assert missing_status == 404

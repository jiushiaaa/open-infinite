"""Cards Workspace MVP: read-only setting cards for long projects."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import get_cards_workspace, import_novel_from_payload


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 卡片工作台\n"
                f"赵轩在归云斋整理第 {idx} 条人物卡，沈冰月记录风格边界。"
            ),
        }
        for idx in range(1, n + 1)
    ]


def _make_project(tmp_path, slug: str = "cards-story"):
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    return tmp_path / slug


def test_cards_workspace_builds_world_style_and_character_cards(tmp_path):
    _make_project(tmp_path)

    report = get_cards_workspace("cards-story", projects_dir=tmp_path)
    cards = {card["id"]: card for card in report["cards"]}

    assert report["version"] == "cards-workspace-mvp"
    assert report["mode"] == "read_only_cards_workspace"
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["world_card_count"] == 1
    assert report["summary"]["style_card_count"] == 1
    assert report["summary"]["character_card_count"] >= 1
    assert {"world", "style"}.issubset(cards)
    assert cards["world"]["type"] == "world"
    assert cards["world"]["editable_fields"]
    assert cards["style"]["type"] == "style"
    assert any(card["type"] == "character" for card in report["cards"])
    assert "不写 artifact" in "；".join(report["boundaries"])


def test_cards_workspace_degrades_damaged_master_setting(tmp_path):
    project_dir = _make_project(tmp_path, "cards-damaged")
    (project_dir / "memory" / "master_setting.yaml").write_text(
        "world_rules: [", encoding="utf-8"
    )

    report = get_cards_workspace("cards-damaged", projects_dir=tmp_path)

    assert report["status"] == "attention"
    assert report["summary"]["character_card_count"] >= 1
    assert report["warnings"]
    world = next(card for card in report["cards"] if card["id"] == "world")
    assert world["status"] == "attention"
    assert world["editable_fields"] == []


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
    _make_project(tmp_path, "cards-http")
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


def test_cards_workspace_http_statuses(running_server):
    port = running_server

    status, body = _get(port, "/api/stories/cards-http/cards-workspace")
    assert status == 200
    assert body["version"] == "cards-workspace-mvp"
    assert body["summary"]["card_count"] >= 3

    bad_status, bad = _get(port, "/api/stories/..%2Fx/cards-workspace")
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    missing_status, _missing = _get(port, "/api/stories/ghost/cards-workspace")
    assert missing_status == 404

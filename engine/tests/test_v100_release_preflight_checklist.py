"""v1.0-beta Release Preflight Checklist-R：发布前只读检查清单。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import get_release_preflight_checklist


def test_release_preflight_is_secret_safe_and_local_first(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-release-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-release-secret-8899")
    monkeypatch.setenv("LNE_MOCK", "1")

    report = get_release_preflight_checklist(api_host="127.0.0.1", api_port=8765)
    text = json.dumps(report, ensure_ascii=False)
    checkpoints = {item["id"]: item for item in report["checkpoints"]}

    assert report["version"] == "v1.0-beta-release-preflight-checklist-r"
    assert report["mode"] == "read_only_release_preflight"
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["checkpoint_count"] >= 6
    assert checkpoints["local_deployment"]["source_endpoint"] == (
        "GET /api/settings/deployment-readiness"
    )
    assert checkpoints["local_smoke"]["status"] == "ready"
    assert checkpoints["project_rights"]["status"] == "attention"
    assert checkpoints["project_rights"]["source_endpoint"] == (
        "GET /api/stories/<slug>/copyright-statement"
    )
    assert any("不执行真实发布" in step for step in report["next_steps"])
    assert "release-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_MOCK", "1")
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


def test_release_preflight_http_ok(running_server):
    status, body = _get(running_server, "/api/settings/release-preflight")

    assert status == 200
    assert body["version"] == "v1.0-beta-release-preflight-checklist-r"
    assert body["summary"]["checkpoint_count"] >= 6


def test_release_preflight_http_bad_story_slug_400(running_server):
    status, body = _get(
        running_server,
        "/api/settings/release-preflight?story_slug=..%2Fbad",
    )

    assert status == 400
    assert "invalid story_slug" in body["error"]

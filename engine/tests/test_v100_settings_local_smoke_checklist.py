"""v1.0-beta Settings Local Smoke Checklist-Q：设置页本地冒烟清单。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import get_settings_local_smoke_checklist


def test_settings_local_smoke_checklist_is_secret_safe_and_actionable(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-smoke-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-smoke-secret-8899")
    monkeypatch.setenv("LNE_MOCK", "1")

    report = get_settings_local_smoke_checklist(api_host="127.0.0.1", api_port=8765)
    text = json.dumps(report, ensure_ascii=False)
    paths = {item["path"] for item in report["checks"]}

    assert report["version"] == "v1.0-beta-settings-local-smoke-checklist-q"
    assert report["status"] == "ready"
    assert report["mode"] == "read_only_local_smoke_checklist"
    assert report["summary"]["external_services_required"] is False
    assert {
        "/",
        "/api/stories",
        "/api/settings/runtime",
        "/api/settings/providers",
        "/api/settings/provider-usage",
        "/api/settings/commercial-status-overview",
        "/api/settings/deployment-readiness",
        "/api/stories/<slug>/audit-log/export",
    }.issubset(paths)
    assert all(item["method"] == "GET" for item in report["checks"])
    assert all(item["status"] == "ready_to_run" for item in report["checks"])
    assert any("Vite" in step for step in report["run_steps"])
    assert "smoke-secret" not in text
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


def test_settings_local_smoke_checklist_http_ok(running_server):
    status, body = _get(running_server, "/api/settings/local-smoke-checklist")

    assert status == 200
    assert body["version"] == "v1.0-beta-settings-local-smoke-checklist-q"
    assert body["summary"]["check_count"] >= 8

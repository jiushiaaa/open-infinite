"""v1.0-beta Commercial Status Overview-O：设置页商业化状态总览。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import get_commercial_status_overview


@pytest.fixture
def iso_env(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-status-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-status-secret-8899")
    monkeypatch.setenv("LNE_MOCK", "1")
    yield


def test_commercial_status_overview_summarizes_local_first_state(iso_env):
    overview = get_commercial_status_overview()
    text = json.dumps(overview, ensure_ascii=False)

    assert overview["version"] == "v1.0-beta-commercial-status-overview-o"
    assert overview["mode"] == "read_only_settings_overview"
    assert overview["overall_status"] == "attention"
    assert overview["summary"]["total_domains"] >= 7
    assert overview["summary"]["attention_domains"] >= 1
    ids = {domain["id"] for domain in overview["domains"]}
    assert {
        "commercial_scope",
        "audit_and_rights",
        "permission_model",
        "cloud_persistence",
        "local_deployment",
    }.issubset(ids)
    assert "status-secret" not in text
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


def test_commercial_status_overview_http(running_server):
    with urllib.request.urlopen(
        f"http://127.0.0.1:{running_server}/api/settings/commercial-status-overview",
        timeout=5,
    ) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    assert resp.status == 200
    assert body["version"] == "v1.0-beta-commercial-status-overview-o"
    assert body["mode"] == "read_only_settings_overview"
    assert any(domain["id"] == "quota_observability" for domain in body["domains"])

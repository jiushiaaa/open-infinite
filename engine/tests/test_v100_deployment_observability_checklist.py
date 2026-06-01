"""v1.0-beta Deployment Observability Checklist-T：部署观测只读清单。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import get_deployment_observability_checklist


def test_deployment_observability_is_secret_safe_and_local_first(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-observe-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-observe-secret-8899")
    monkeypatch.setenv("LNE_MOCK", "1")

    report = get_deployment_observability_checklist(
        api_host="127.0.0.1",
        api_port=8765,
    )
    text = json.dumps(report, ensure_ascii=False)
    signals = {item["id"]: item for item in report["signals"]}

    assert report["version"] == "v1.0-beta-deployment-observability-checklist-t"
    assert report["mode"] == "read_only_deployment_observability_checklist"
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["cloud_monitoring_enabled"] is False
    assert report["summary"]["signal_count"] >= 6
    assert signals["local_deployment_health"]["source_endpoint"] == (
        "GET /api/settings/deployment-readiness"
    )
    assert signals["quota_usage"]["source_endpoint"] == (
        "GET /api/settings/quota-observability"
    )
    assert signals["project_audit_timeline"]["source_endpoint"] == (
        "GET /api/stories/<slug>/audit-log"
    )
    assert any("云端观测" in step for step in report["next_steps"])
    assert "observe-secret" not in text
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


def test_deployment_observability_http_ok(running_server):
    status, body = _get(running_server, "/api/settings/deployment-observability")

    assert status == 200
    assert body["version"] == "v1.0-beta-deployment-observability-checklist-t"
    assert body["summary"]["cloud_monitoring_enabled"] is False


def test_deployment_observability_http_bad_story_slug_400(running_server):
    status, body = _get(
        running_server,
        "/api/settings/deployment-observability?story_slug=..%2Fbad",
    )

    assert status == 400
    assert "invalid story_slug" in body["error"]

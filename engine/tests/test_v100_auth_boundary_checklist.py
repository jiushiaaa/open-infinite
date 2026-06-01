"""v1.0-beta Auth Boundary Checklist-U：认证边界只读清单。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import get_auth_boundary_checklist


def test_auth_boundary_is_secret_safe_and_not_enforced(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-auth-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-auth-secret-8899")
    monkeypatch.setenv("LNE_MOCK", "1")

    report = get_auth_boundary_checklist(api_host="127.0.0.1", api_port=8765)
    checkpoints = {item["id"]: item for item in report["checkpoints"]}
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "v1.0-beta-auth-boundary-checklist-u"
    assert report["mode"] == "read_only_auth_boundary_checklist"
    assert report["summary"]["auth_enforced"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["checkpoint_count"] >= 5
    assert checkpoints["local_operator_mode"]["source_endpoint"] == (
        "GET /api/settings/account-project-space-boundary"
    )
    assert checkpoints["permission_matrix"]["source_endpoint"] == (
        "GET /api/settings/permission-matrix"
    )
    assert checkpoints["request_acl"]["status"] == "attention"
    assert any("真实认证" in step for step in report["next_steps"])
    assert "auth-secret" not in text
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


def test_auth_boundary_http_ok(running_server):
    status, body = _get(running_server, "/api/settings/auth-boundary")

    assert status == 200
    assert body["version"] == "v1.0-beta-auth-boundary-checklist-u"
    assert body["summary"]["auth_enforced"] is False

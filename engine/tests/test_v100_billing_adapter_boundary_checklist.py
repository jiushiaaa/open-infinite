"""v1.0-beta Billing Adapter Boundary Checklist-X：计费 adapter 边界只读清单。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import get_billing_adapter_boundary_checklist


def test_billing_adapter_boundary_is_read_only_and_secret_safe(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-billing-boundary-secret-1122")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-billing-boundary-secret-3344")
    monkeypatch.setenv("LNE_MOCK", "1")

    report = get_billing_adapter_boundary_checklist(api_host="127.0.0.1", api_port=8765)
    checks = {item["id"]: item for item in report["checks"]}
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "v1.0-beta-billing-adapter-boundary-checklist-x"
    assert report["mode"] == "read_only_billing_adapter_boundary_checklist"
    assert report["summary"]["adapter_implemented"] is False
    assert report["summary"]["billing_writes_enabled"] is False
    assert report["summary"]["external_billing_required"] is False
    assert report["summary"]["check_count"] >= 6
    assert checks["usage_pricing_input"]["source_endpoint"] == (
        "GET /api/settings/provider-usage"
    )
    assert checks["payment_provider_adapter"]["status"] == "attention"
    assert checks["invoice_refund_trail"]["status"] == "attention"
    assert any("计费" in step for step in report["next_steps"])
    assert "billing-boundary-secret" not in text
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


def test_billing_adapter_boundary_http_ok(running_server):
    status, body = _get(running_server, "/api/settings/billing-adapter-boundary")

    assert status == 200
    assert body["version"] == "v1.0-beta-billing-adapter-boundary-checklist-x"
    assert body["summary"]["adapter_implemented"] is False
    assert body["summary"]["billing_writes_enabled"] is False

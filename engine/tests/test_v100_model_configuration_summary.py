"""v1.0-local Model Configuration UX：模型配置摘要。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server


def test_model_configuration_summary_is_secret_safe_and_actionable(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-model-config-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-model-config-secret-8899")
    monkeypatch.setenv("LNE_MOCK", "1")

    import living_novel_engine.service as service

    assert hasattr(service, "get_model_configuration_summary")
    report = service.get_model_configuration_summary()
    text = json.dumps(report, ensure_ascii=False)
    sections = {section["id"]: section for section in report["sections"]}

    assert report["version"] == "v1.0-local-model-configuration-ux"
    assert report["mode"] == "read_only_model_configuration_summary"
    assert report["status"] == "attention"
    assert report["summary"]["llm_configured"] is True
    assert report["summary"]["mock_enabled"] is True
    assert report["summary"]["visual_configured"] is True
    assert report["summary"]["plaintext_key_returned"] is False
    assert {"text_model", "connection_test", "visual_model", "secret_boundary"}.issubset(
        sections
    )
    assert sections["secret_boundary"]["status"] == "ready"
    assert any("模型" in step for step in report["next_steps"])
    assert "model-config-secret" not in text
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
        try:
            return exc.code, json.loads(exc.read().decode("utf-8"))
        except json.JSONDecodeError:
            return exc.code, {}


def test_model_configuration_summary_http_ok(running_server):
    status, body = _get(running_server, "/api/settings/model-configuration")

    assert status == 200
    assert body["version"] == "v1.0-local-model-configuration-ux"
    assert body["summary"]["connectivity_check_available"] is True
    assert any(section["id"] == "text_model" for section in body["sections"])

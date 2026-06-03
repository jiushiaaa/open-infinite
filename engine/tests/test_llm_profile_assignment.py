"""LLM Profile Assignment MVP: read-only task model profiles."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import get_llm_profile_assignment


def test_llm_profile_assignment_is_secret_safe_and_task_scoped(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-profile-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-profile-secret-8899")
    monkeypatch.setenv("LNE_MOCK", "1")

    report = get_llm_profile_assignment()
    text = json.dumps(report, ensure_ascii=False)
    profiles = {item["id"]: item for item in report["profiles"]}

    assert report["version"] == "llm-profile-assignment-mvp"
    assert report["mode"] == "read_only_llm_profile_assignment"
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert {
        "reader_intervention",
        "story_genesis",
        "import_extraction",
        "reader_revision",
        "visual_assets",
    }.issubset(profiles)
    assert profiles["reader_intervention"]["temperature"] == 0.65
    assert profiles["import_extraction"]["temperature"] == 0.3
    assert profiles["reader_revision"]["fallback"] == "deterministic_reader_panel"
    assert "profile-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text


def test_llm_profile_assignment_reflects_provider_route(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-profile-secret-7788")
    monkeypatch.setenv("LNE_MOCK", "0")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_VISUAL_ASSETS", "0")

    report = get_llm_profile_assignment()
    profiles = {item["id"]: item for item in report["profiles"]}

    assert report["status"] in {"ready", "attention"}
    assert profiles["reader_intervention"]["mode"] == "provider"
    assert profiles["story_genesis"]["provider_id"] == "primary_llm"
    assert profiles["visual_assets"]["mode"] == "disabled"
    assert profiles["visual_assets"]["fallback"] == "placeholder"


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


def test_llm_profile_assignment_http_ok(running_server):
    status, body = _get(running_server, "/api/settings/llm-profile-assignment")

    assert status == 200
    assert body["version"] == "llm-profile-assignment-mvp"
    assert body["summary"]["profile_count"] >= 5
    assert any(item["id"] == "reader_revision" for item in body["profiles"])

"""v0.7 第八刀：运行设置面板（service.runtime_settings + /api/settings/runtime[/test]）。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.orchestrator import available_runners
from living_novel_engine.service import (
    SettingsError,
    default_mock,
    default_rounds,
    default_runner,
    get_runtime_settings,
    update_runtime_settings,
)
from living_novel_engine.service import test_connectivity as connectivity_check

_ENV_KEYS = [
    "LLM_API_KEY",
    "LLM_BASE_URL",
    "LLM_MODEL_NAME",
    "LNE_MOCK",
    "LNE_DEFAULT_ROUNDS",
    "LNE_SCENE_RUNNER",
    "SEEDREAM_API_KEY",
    "SEEDREAM_BASE_URL",
    "SEEDREAM_MODEL",
    "LNE_VISUAL_ASSETS",
]


@pytest.fixture
def iso_env(monkeypatch):
    """隔离运行设置环境变量：默认无 key，teardown 由 monkeypatch 还原。"""
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    protected = ("LLM_API_KEY", "SEEDREAM_API_KEY")
    for k in [key for key in _ENV_KEYS if key not in protected]:
        monkeypatch.delenv(k, raising=False)
    yield


# ── service 层 ────────────────────────────────────────────


class TestService:
    def test_get_defaults(self, iso_env):
        s = get_runtime_settings()
        assert s.llm_api_key_present is False
        assert s.masked_key == ""
        assert s.default_runner in available_runners()
        assert 1 <= s.default_rounds <= 12
        assert s.seedream_enabled is False
        assert s.visual_assets_enabled is True

    def test_visual_assets_enabled_is_independent_from_seedream_key(self, iso_env):
        s = update_runtime_settings({"visual_assets_enabled": False})
        assert s.visual_assets_enabled is False
        assert s.seedream_enabled is False
        assert s.seedream_key_present is False

        s = update_runtime_settings(
            {"visual_assets_enabled": True, "seedream_api_key": "sd-secret-1234"}
        )
        assert s.visual_assets_enabled is True
        assert s.seedream_enabled is True
        assert s.seedream_masked_key.endswith("1234")
        assert "secret" not in s.seedream_masked_key

    def test_update_sets_and_masks_key(self, iso_env):
        s = update_runtime_settings({"api_key": "sk-supersecret-7788", "model_name": "foo"})
        assert s.llm_api_key_present is True
        assert s.masked_key.endswith("7788")
        assert "supersecret" not in s.masked_key
        assert s.llm_model_name == "foo"

    def test_empty_key_clears(self, iso_env):
        update_runtime_settings({"api_key": "sk-x12345"})
        s = update_runtime_settings({"api_key": ""})
        assert s.llm_api_key_present is False

    def test_rounds_out_of_range(self, iso_env):
        with pytest.raises(SettingsError):
            update_runtime_settings({"default_rounds": 99})
        with pytest.raises(SettingsError):
            update_runtime_settings({"default_rounds": 0})

    def test_runner_invalid(self, iso_env):
        with pytest.raises(SettingsError):
            update_runtime_settings({"default_runner": "no-such-runner"})

    def test_runner_valid(self, iso_env):
        name = available_runners()[0]
        s = update_runtime_settings({"default_runner": name})
        assert s.default_runner == name
        assert default_runner() == name

    def test_defaults_read_back(self, iso_env):
        update_runtime_settings({"default_mock": False, "default_rounds": 7})
        assert default_mock() is False
        assert default_rounds() == 7

    def test_connectivity_no_key(self, iso_env):
        assert connectivity_check()["available"] is False

    def test_connectivity_mock(self, iso_env):
        assert connectivity_check(mock=True)["available"] is True


# ── HTTP ──────────────────────────────────────────────────


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_out"))
    for k in _ENV_KEYS[1:]:
        if k != "LLM_API_KEY":
            monkeypatch.delenv(k, raising=False)
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def _post(port: int, path: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def _get(port: int, path: str) -> tuple[int, dict]:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


class TestHttp:
    def test_get_runtime(self, running_server):
        status, body = _get(running_server, "/api/settings/runtime")
        assert status == 200
        assert body["llm_api_key_present"] is False
        assert "available_runners" in body

    def test_post_update_no_plaintext(self, running_server):
        status, body = _post(
            running_server,
            "/api/settings/runtime",
            {"api_key": "sk-do-not-echo-9999"},
        )
        assert status == 200
        assert body["llm_api_key_present"] is True
        assert "do-not-echo" not in json.dumps(body)
        assert body["masked_key"].endswith("9999")

    def test_post_rounds_400(self, running_server):
        status, _b = _post(running_server, "/api/settings/runtime", {"default_rounds": 50})
        assert status == 400

    def test_post_runner_400(self, running_server):
        status, _b = _post(
            running_server, "/api/settings/runtime", {"default_runner": "ghost"}
        )
        assert status == 400

    def test_test_endpoint_no_key(self, running_server):
        status, body = _post(running_server, "/api/settings/runtime/test", {})
        assert status == 200
        assert body["available"] is False

    def test_intervention_uses_settings_default_mock(self, running_server):
        # body 不带 mock → 回退 settings 默认（无 key → mock=True），端到端成功
        status, body = _post(
            running_server,
            "/api/interventions",
            {
                "story_slug": "tianhuang-night",
                "target": "lin_wan_zhou",
                "content": "我希望林晚舟今夜不要独自赴约。",
            },
        )
        assert status == 200
        assert body["llm_mock"] is True

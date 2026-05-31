"""v0.7 第八刀：运行设置面板（service.runtime_settings + /api/settings/runtime[/test]）。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from living_novel_engine.browser import server
from living_novel_engine.orchestrator import available_runners
from living_novel_engine.service import (
    SettingsError,
    default_mock,
    default_rounds,
    default_runner,
    get_commercial_hardening_scope,
    get_provider_gateway_summary,
    get_provider_usage_summary,
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
    "LNE_LLM_INPUT_COST_PER_1K",
    "LNE_LLM_OUTPUT_COST_PER_1K",
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


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class TestService:
    def test_get_defaults(self, iso_env):
        s = get_runtime_settings()
        assert s.llm_api_key_present is False
        assert s.masked_key == ""
        assert s.default_runner in available_runners()
        assert 1 <= s.default_rounds <= 12
        assert s.seedream_enabled is False
        assert s.visual_assets_enabled is True
        assert s.llm_input_cost_per_1k == 0
        assert s.llm_output_cost_per_1k == 0

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

    def test_cost_rates_are_configurable(self, iso_env):
        s = update_runtime_settings(
            {"llm_input_cost_per_1k": "0.01", "llm_output_cost_per_1k": 0.03}
        )
        assert s.llm_input_cost_per_1k == 0.01
        assert s.llm_output_cost_per_1k == 0.03

        with pytest.raises(SettingsError):
            update_runtime_settings({"llm_input_cost_per_1k": -1})
        with pytest.raises(SettingsError):
            update_runtime_settings({"llm_output_cost_per_1k": "bad"})

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

    def test_provider_gateway_defaults_do_not_expose_keys(self, iso_env):
        summary = get_provider_gateway_summary()
        text = json.dumps(summary, ensure_ascii=False)
        assert summary["version"] == "v0.9.1-provider-cost-lite"
        assert summary["routing"]["mode"] == "single_provider"
        assert summary["routing"]["llm_route"] == "mock"
        assert summary["cost_policy"]["estimation_mode"] == "usage_metadata_only"
        routes = {route["id"]: route for route in summary["routes"]}
        assert routes["intervention"]["provider_id"] == "mock"
        assert routes["story_genesis"]["provider_id"] == "mock"
        assert routes["import_extraction"]["provider_id"] == "mock"
        assert routes["visual_assets"]["provider_id"] == "placeholder"
        assert "LLM_API_KEY" not in text
        assert "SEEDREAM_API_KEY" not in text

    def test_provider_gateway_masks_configured_keys(self, iso_env):
        update_runtime_settings(
            {
                "api_key": "sk-provider-secret-7788",
                "default_mock": False,
                "seedream_api_key": "sd-provider-secret-8899",
            }
        )
        summary = get_provider_gateway_summary()
        text = json.dumps(summary, ensure_ascii=False)
        assert summary["routing"]["llm_route"] == "primary_llm"
        assert summary["routing"]["visual_route"] == "seedream_visual"
        routes = {route["id"]: route for route in summary["routes"]}
        assert routes["intervention"]["provider_id"] == "primary_llm"
        assert routes["story_genesis"]["provider_id"] == "primary_llm"
        assert routes["import_extraction"]["provider_id"] == "primary_llm"
        assert routes["visual_assets"]["provider_id"] == "seedream_visual"
        assert "provider-secret" not in text
        assert "7788" in text
        assert "8899" in text

    def test_commercial_hardening_scope_is_local_first_and_secret_safe(self, iso_env):
        update_runtime_settings(
            {
                "api_key": "sk-commercial-secret-7788",
                "default_mock": False,
                "seedream_api_key": "sd-commercial-secret-8899",
            }
        )

        scope = get_commercial_hardening_scope()
        text = json.dumps(scope, ensure_ascii=False)

        assert scope["version"] == "v1.0-beta-commercial-hardening-scope-a"
        assert scope["status"] == "scope_defined"
        assert scope["stage"] == "local_first_scope_review"
        assert scope["scope"]["implementation_mode"] == "read_only_scope_report"
        domain_ids = {domain["id"] for domain in scope["domains"]}
        assert {
            "account_project_space",
            "permission_model",
            "cloud_persistence",
            "quota_cost_guard",
            "audit_log",
            "copyright_share_guard",
            "deployment_observability",
        }.issubset(domain_ids)
        deferred_ids = {item["id"] for item in scope["deferred_actions"]}
        assert "multi_tenant_auth" in deferred_ids
        assert "cloud_object_storage" in deferred_ids
        assert "billing_system" in deferred_ids
        assert "commercial-secret" not in text
        assert "LLM_API_KEY" not in text
        assert "SEEDREAM_API_KEY" not in text

    def test_provider_usage_summary_aggregates_existing_artifacts(
        self, iso_env, tmp_path, monkeypatch
    ):
        monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "outputs"))
        update_runtime_settings(
            {"llm_input_cost_per_1k": 0.01, "llm_output_cost_per_1k": 0.03}
        )
        run_dir = tmp_path / "outputs" / "run_usage"
        _write_json(
            run_dir / "intervention.json",
            {"story_slug": "story-a", "source_kind": "imported"},
        )
        _write_json(
            run_dir / "intervention_compilation.json",
            {
                "generation_meta": {
                    "source": "llm",
                    "model_name": "compiler-model",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    },
                }
            },
        )
        _write_json(
            run_dir / "branch_a" / "multi_agent_trace.json",
            {
                "turn_plans": [],
                "generation_meta": {
                    "source": "llm",
                    "model_name": "trace-model",
                    "usage": {
                        "prompt_tokens": 20,
                        "completion_tokens": 10,
                        "total_tokens": 30,
                    },
                },
            },
        )
        _write_json(
            run_dir / "branch_b" / "multi_agent_trace.json",
            {"turn_plans": [], "generation_meta": {"source": "fallback"}},
        )

        summary = get_provider_usage_summary(story_slug="story-a")

        assert summary["version"] == "v0.9.1-provider-usage-lite"
        assert summary["run_count"] == 1
        assert summary["record_count"] == 2
        assert summary["missing_usage_record_count"] == 1
        assert summary["totals"]["prompt_tokens"] == 30
        assert summary["totals"]["completion_tokens"] == 15
        assert summary["totals"]["total_tokens"] == 45
        assert summary["by_provider"][0]["provider_id"] == "primary_llm"
        assert summary["by_provider"][0]["total_tokens"] == 45
        assert summary["cost_estimate"]["estimated_total"] == 0.00075
        assert summary["cost_estimate"]["reason"] == "configured"

    def test_provider_usage_summary_filters_story_slug(self, iso_env, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "outputs"))
        for slug, tokens in (("story-a", 11), ("story-b", 99)):
            run_dir = tmp_path / "outputs" / f"run_{slug}"
            _write_json(run_dir / "intervention.json", {"story_slug": slug})
            _write_json(
                run_dir / "intervention_compilation.json",
                {
                    "generation_meta": {
                        "source": "llm",
                        "usage": {"total_tokens": tokens},
                    }
                },
            )

        summary = get_provider_usage_summary(story_slug="story-a")

        assert summary["run_count"] == 1
        assert summary["totals"]["total_tokens"] == 11


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

    def test_get_provider_gateway(self, running_server):
        status, body = _get(running_server, "/api/settings/providers")
        assert status == 200
        assert body["version"] == "v0.9.1-provider-cost-lite"
        assert body["routing"]["mode"] == "single_provider"
        assert body["routing"]["llm_route"] == "mock"

    def test_get_provider_usage(self, running_server):
        status, body = _get(running_server, "/api/settings/provider-usage")
        assert status == 200
        assert body["version"] == "v0.9.1-provider-usage-lite"
        assert body["totals"]["total_tokens"] == 0

    def test_get_provider_usage_rejects_bad_story_slug(self, running_server):
        try:
            _get(running_server, "/api/settings/provider-usage?story_slug=../bad")
        except urllib.error.HTTPError as exc:
            assert exc.code == 400
            body = json.loads(exc.read().decode("utf-8"))
            assert body["error"] == "invalid story_slug"
        else:
            raise AssertionError("bad story_slug should return 400")

    def test_get_commercial_hardening_scope(self, running_server):
        status, body = _get(running_server, "/api/settings/commercial-hardening-scope")
        assert status == 200
        assert body["version"] == "v1.0-beta-commercial-hardening-scope-a"
        assert body["status"] == "scope_defined"
        assert body["scope"]["implementation_mode"] == "read_only_scope_report"
        assert any(domain["id"] == "audit_log" for domain in body["domains"])

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

    def test_post_cost_rate_400(self, running_server):
        status, _b = _post(
            running_server, "/api/settings/runtime", {"llm_input_cost_per_1k": -1}
        )
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

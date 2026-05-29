"""v0.7.2 干预护栏：evaluate_guardrail + service + POST /api/interventions/guardrail。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.intervention.guardrail import evaluate_guardrail
from living_novel_engine.models import (
    CharacterAgent,
    CharacterPersona,
    StoryWorld,
)
from living_novel_engine.service import (
    GuardrailRequestError,
    check_intervention_guardrail,
)


def _world() -> StoryWorld:
    return StoryWorld(
        id="w",
        title="测试世界",
        rules=["境界压制不可逆，禁止越级秒杀", "禁止未声明设定：重生/穿越/系统"],
    )


def _chars() -> dict[str, CharacterAgent]:
    return {
        "hero": CharacterAgent(
            id="hero",
            name="主角",
            persona=CharacterPersona(boundaries=["不会无理由背叛同门", "不会轻信传闻"]),
        )
    }


# ── evaluate_guardrail（纯函数）─────────────────────────────


class TestEvaluate:
    def test_benign_information_low_risk(self):
        r = evaluate_guardrail(
            "提醒主角今晚小心城外的动静",
            world=_world(),
            characters=_chars(),
            target="hero",
        )
        assert r.allowed is True
        assert r.risk in ("low", "medium")
        assert len(r.categories) == 6

    def test_rule_rewrite_blocked_and_alternate(self):
        r = evaluate_guardrail(
            "给主角一把AK47直接秒杀对手",
            world=_world(),
            characters=_chars(),
            target="hero",
        )
        assert r.intervention_type == "rule_rewrite"
        assert r.risk == "high"
        assert r.allowed is False  # 题材/世界规则改写 → 提示另开异设世界线
        assert r.safer_alternative
        genre = next(c for c in r.categories if c.category == "genre")
        assert genre.passed is False

    def test_forced_action_against_boundary_high_resistance(self):
        r = evaluate_guardrail(
            "命令主角必须立刻背叛同门",
            world=_world(),
            characters=_chars(),
            target="hero",
        )
        persona = next(c for c in r.categories if c.category == "persona")
        assert persona.passed is False
        assert r.repair_suggestions

    def test_strength_and_visibility_flags(self):
        r = evaluate_guardrail(
            "主角必须立刻去做这件事",
            world=_world(),
            characters=_chars(),
            target="hero",
            visibility="world_wide",
            strength="strong",
        )
        strength = next(c for c in r.categories if c.category == "strength")
        vis = next(c for c in r.categories if c.category == "visibility")
        assert strength.passed is False
        assert vis.passed is False

    def test_unknown_target_does_not_crash(self):
        r = evaluate_guardrail(
            "提醒某人小心",
            world=_world(),
            characters=_chars(),
            target="nobody",
        )
        assert r.allowed is True


# ── service 层 ─────────────────────────────────────────────


class TestService:
    def test_builtin_story(self):
        r = check_intervention_guardrail(
            story_slug="tianhuang-night",
            content="今晚不要去城外竹林",
            target="lin_wan_zhou",
        )
        assert r.intervention_type in (
            "information",
            "forced_action",
            "resource_injection",
            "rule_rewrite",
        )
        assert len(r.categories) == 6

    def test_missing_content_raises(self):
        with pytest.raises(GuardrailRequestError):
            check_intervention_guardrail(
                story_slug="tianhuang-night", content="", target="lin_wan_zhou"
            )

    def test_missing_story_raises_filenotfound(self):
        with pytest.raises(FileNotFoundError):
            check_intervention_guardrail(
                story_slug="no-such-story-xyz", content="随便", target="x"
            )

    def test_corrupt_story_yaml_maps_to_request_error(self, tmp_path, monkeypatch):
        pdir = tmp_path / "broken-guardrail"
        pdir.mkdir()
        (pdir / "world.yaml").write_text("key: value: another\n", encoding="utf-8")
        (pdir / "characters.yaml").write_text(
            "characters:\n  - id: qing\n    name: 青衫客\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))

        with pytest.raises(GuardrailRequestError):
            check_intervention_guardrail(
                story_slug="broken-guardrail", content="提醒青衫客小心", target="qing"
            )


# ── HTTP ──────────────────────────────────────────────────


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server():
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
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


class TestHttp:
    def test_guardrail_ok(self, running_server):
        status, body = _post(
            running_server,
            "/api/interventions/guardrail",
            {
                "story_slug": "tianhuang-night",
                "target": "lin_wan_zhou",
                "content": "今晚不要去城外竹林",
            },
        )
        assert status == 200
        assert "risk" in body
        assert len(body["categories"]) == 6

    def test_guardrail_rule_rewrite(self, running_server):
        status, body = _post(
            running_server,
            "/api/interventions/guardrail",
            {
                "story_slug": "tianhuang-night",
                "target": "lin_wan_zhou",
                "content": "给她一把AK47秒杀所有人",
            },
        )
        assert status == 200
        assert body["intervention_type"] == "rule_rewrite"
        assert body["allowed"] is False

    def test_guardrail_missing_content_400(self, running_server):
        status, body = _post(
            running_server,
            "/api/interventions/guardrail",
            {"story_slug": "tianhuang-night", "content": ""},
        )
        assert status == 400
        assert "error" in body

    def test_guardrail_missing_story_404(self, running_server):
        status, body = _post(
            running_server,
            "/api/interventions/guardrail",
            {"story_slug": "no-such-xyz", "content": "随便"},
        )
        assert status == 404

    def test_guardrail_bad_slug_400(self, running_server):
        status, body = _post(
            running_server,
            "/api/interventions/guardrail",
            {"story_slug": "..%2Fsamples", "content": "随便"},
        )
        assert status == 400

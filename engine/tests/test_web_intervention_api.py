"""v0.7 Web Generate Loop：service.run_intervention 与 POST /api/interventions。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import indexer, server
from living_novel_engine.output import writer as writer_mod
from living_novel_engine.service import (
    InterventionRequestError,
    run_intervention,
)


@pytest.fixture(autouse=True)
def _isolate_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)
    return tmp_path


# ── service 层 ────────────────────────────────────────────


class TestService:
    def test_mock_success(self, tmp_path):
        result = run_intervention(
            story_slug="tianhuang-night",
            target="lin_wan_zhou",
            content="今夜不要去城外竹林",
            branches=3,
            rounds=2,
            mock=True,
        )
        assert result.run_id.startswith("run_")
        assert result.branch_ids
        assert result.llm_mock is True
        assert result.compilation.branch_axis
        # 落盘
        assert (result.run_dir / "intervention_compilation.json").exists()
        bid = result.branch_ids[0]
        assert (result.run_dir / bid / "causal_diff.json").exists()
        assert (result.run_dir / bid / "chapter.md").exists()

    def test_missing_content(self):
        with pytest.raises(InterventionRequestError):
            run_intervention(story_slug="tianhuang-night", target="lin_wan_zhou", content="  ", mock=True)

    def test_missing_target(self):
        with pytest.raises(InterventionRequestError):
            run_intervention(story_slug="tianhuang-night", target="", content="x", mock=True)

    def test_unknown_story(self):
        with pytest.raises(InterventionRequestError):
            run_intervention(story_slug="no-such-story", target="x", content="y", mock=True)

    def test_unknown_target(self):
        with pytest.raises(InterventionRequestError) as ei:
            run_intervention(
                story_slug="tianhuang-night", target="ghost_id", content="x", mock=True
            )
        assert "未知角色" in str(ei.value)


# ── HTTP POST /api/interventions ──────────────────────────


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
    url = f"http://127.0.0.1:{port}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


class TestPostApi:
    def test_post_mock_success(self, running_server):
        status, body = _post(
            running_server,
            "/api/interventions",
            {
                "story_slug": "tianhuang-night",
                "target": "lin_wan_zhou",
                "content": "今夜不要去城外竹林",
                "branches": 3,
                "rounds": 2,
                "mock": True,
            },
        )
        assert status == 200, body
        assert body["run_id"].startswith("run_")
        assert body["branch_ids"]
        assert body["primary_branch"] == body["branch_ids"][0]
        assert body["intervention_compilation"]["branch_axis"]
        # 返回刷新后的树，且包含新 run
        run_ids = [n["run_id"] for n in body["tree"]]
        assert body["run_id"] in run_ids

    def test_post_missing_content(self, running_server):
        status, body = _post(
            running_server,
            "/api/interventions",
            {"story_slug": "tianhuang-night", "target": "lin_wan_zhou", "content": "", "mock": True},
        )
        assert status == 400
        assert "content" in body["error"]

    def test_post_unknown_target(self, running_server):
        status, body = _post(
            running_server,
            "/api/interventions",
            {"story_slug": "tianhuang-night", "target": "ghost", "content": "x", "mock": True},
        )
        assert status == 400
        assert "未知角色" in body["error"]

    def test_post_invalid_json(self, running_server):
        url = f"http://127.0.0.1:{running_server}/api/interventions"
        req = urllib.request.Request(
            url, data=b"{not json", headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                status, body = resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            status, body = e.code, json.loads(e.read().decode("utf-8"))
        assert status == 400
        assert "JSON" in body["error"]

    def test_get_still_works(self, running_server):
        # 只读链路不回归
        url = f"http://127.0.0.1:{running_server}/api/stories"
        with urllib.request.urlopen(url, timeout=5) as resp:
            assert resp.status == 200

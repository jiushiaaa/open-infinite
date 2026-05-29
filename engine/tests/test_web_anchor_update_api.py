"""v0.7 第七刀：世界锚定轻编辑写回（service.anchor_update + GET health / POST anchor）。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest
import yaml

from living_novel_engine.browser import indexer, server
from living_novel_engine.service import (
    AnchorReadOnlyError,
    AnchorUpdateError,
    generate_story,
    update_world_anchor,
)

PREMISE = "一名守陵人发现先祖封印松动，必须在城破前查明真相。"


def _make_project(tmp_path, slug="proj"):
    generate_story(name=slug, premise=PREMISE, mock=True, projects_dir=tmp_path)
    return tmp_path / slug


def _patch():
    return {
        "world": {"rules": ["新规则甲", "新规则乙"], "scene_description": "改后的此刻场景"},
        "characters": [
            {
                "id": "protagonist",
                "persona": {"boundaries": ["不会出卖同伴"], "traits": ["冷静"]},
                "current_state": {"location": "新地点", "emotion": "笃定"},
            }
        ],
        "open_threads": [
            {"id": "t1", "title": "新伏笔", "description": "说明", "status": "open"}
        ],
    }


# ── service 层 ────────────────────────────────────────────


class TestService:
    def test_patch_success(self, tmp_path):
        pdir = _make_project(tmp_path, "edit-me")
        result = update_world_anchor("edit-me", _patch(), projects_dir=tmp_path)
        assert result.changed
        # 备份生成
        assert result.backup_dir is not None and result.backup_dir.exists()
        assert (result.backup_dir / "world.yaml").exists()
        # 写回生效
        world = yaml.safe_load((pdir / "world.yaml").read_text(encoding="utf-8"))
        assert world["rules"] == ["新规则甲", "新规则乙"]
        assert world["scene_description"] == "改后的此刻场景"
        chars = yaml.safe_load((pdir / "characters.yaml").read_text(encoding="utf-8"))
        prot = next(c for c in chars["characters"] if c["id"] == "protagonist")
        assert prot["persona"]["boundaries"] == ["不会出卖同伴"]
        assert prot["current_state"]["location"] == "新地点"
        threads = yaml.safe_load((pdir / "open_threads.yaml").read_text(encoding="utf-8"))
        assert threads[0]["title"] == "新伏笔"

    def test_no_whitelist_fields(self, tmp_path):
        _make_project(tmp_path, "nochange")
        with pytest.raises(AnchorUpdateError):
            update_world_anchor("nochange", {"world": {"id": "hacked"}}, projects_dir=tmp_path)

    def test_broken_yaml_rejected(self, tmp_path):
        pdir = _make_project(tmp_path, "corrupt")
        (pdir / "world.yaml").write_text("key: value: another\n", encoding="utf-8")
        with pytest.raises(AnchorUpdateError):
            update_world_anchor("corrupt", _patch(), projects_dir=tmp_path)

    def test_broken_story_contract_rejected(self, tmp_path):
        pdir = _make_project(tmp_path, "corrupt-contract")
        (pdir / "story_contract.yaml").write_text(
            "contract: value: another\n", encoding="utf-8"
        )
        with pytest.raises(AnchorUpdateError):
            update_world_anchor("corrupt-contract", _patch(), projects_dir=tmp_path)

    def test_missing_story(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            update_world_anchor("nope", _patch(), projects_dir=tmp_path)

    def test_builtin_readonly(self):
        # 内置样例不在 tmp，默认解析到 samples → 只读
        with pytest.raises(AnchorReadOnlyError):
            update_world_anchor("tianhuang-night", _patch())


# ── HTTP ──────────────────────────────────────────────────


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    # 预置一个可编辑项目
    generate_story(name="web-edit", premise=PREMISE, mock=True, projects_dir=tmp_path)
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port, tmp_path
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
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


class TestHttp:
    def test_health_200(self, running_server):
        port, _ = running_server
        status, body = _get(port, "/api/stories/web-edit/health")
        assert status == 200
        assert body["status"] in ("ok", "warning")
        assert body["files"]["world.yaml"] == "ok"

    def test_health_bad_slug_400(self, running_server):
        port, _ = running_server
        status, _b = _get(port, "/api/stories/..%2Fsamples/health")
        assert status == 400

    def test_post_anchor_success(self, running_server):
        port, _ = running_server
        status, body = _post(port, "/api/stories/web-edit/anchor", _patch())
        assert status == 200
        assert "anchor" in body and "health" in body
        assert body["changed"]
        assert body["backup"]
        # anchor 已反映新规则
        assert body["anchor"]["world"]["rules"] == ["新规则甲", "新规则乙"]

    def test_post_bad_slug_400(self, running_server):
        port, _ = running_server
        status, _b = _post(port, "/api/stories/..%2Fx/anchor", _patch())
        assert status == 400

    def test_post_missing_404(self, running_server):
        port, _ = running_server
        status, _b = _post(port, "/api/stories/ghost/anchor", _patch())
        assert status == 404

    def test_post_broken_yaml_400(self, running_server):
        port, tmp_path = running_server
        (tmp_path / "web-edit" / "world.yaml").write_text(
            "key: value: another\n", encoding="utf-8"
        )
        status, _b = _post(port, "/api/stories/web-edit/anchor", _patch())
        assert status == 400

    def test_post_broken_story_contract_400(self, running_server):
        port, tmp_path = running_server
        (tmp_path / "web-edit" / "story_contract.yaml").write_text(
            "contract: value: another\n", encoding="utf-8"
        )
        status, _b = _post(port, "/api/stories/web-edit/anchor", _patch())
        assert status == 400

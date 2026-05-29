"""v0.7 第四刀：世界锚定页（indexer.get_world_anchor + GET /api/stories/<slug>/anchor）。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest
import yaml

from living_novel_engine.browser import indexer, server


def _make_imported(projects_root, slug="imp-anchor"):
    pdir = projects_root / slug
    pdir.mkdir(parents=True)
    (pdir / "world.yaml").write_text(
        yaml.safe_dump(
            {
                "display_name": "导入测试世界",
                "source_type": "imported",
                "rules": ["规则一"],
                "locations": [{"id": "loc1", "name": "城门", "description": "入口"}],
                "factions": ["甲派"],
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    (pdir / "characters.yaml").write_text(
        yaml.safe_dump(
            {
                "characters": [
                    {
                        "id": "hero",
                        "name": "主角",
                        "narrative_role": "protagonist",
                        "persona": {"boundaries": ["不会无理由背叛"]},
                        "current_state": {"location": "城门", "emotion": "警惕"},
                    }
                ]
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    (pdir / "import_meta.json").write_text(
        json.dumps({"anchor_chapter_index": 2, "chapter_count": 3}), encoding="utf-8"
    )
    return slug


# ── indexer 层 ────────────────────────────────────────────


class TestIndexer:
    def test_builtin_success(self):
        a = indexer.get_world_anchor("tianhuang-night")
        assert a["source_kind"] == "builtin"
        assert a["display_name"]
        assert a["world"]["rules"]
        assert a["world"]["locations"]
        # 角色含人设边界与当前状态
        lin = next(c for c in a["characters"] if c["id"] == "lin_wan_zhou")
        assert lin["persona"]["boundaries"]
        assert lin["current_state"]["location"]
        assert a["open_threads"]
        # tianhuang-night 无 contract / summaries → null / []
        assert a["story_contract"] is None
        assert a["summaries"] == []

    def test_imported_success(self, tmp_path, monkeypatch):
        monkeypatch.setattr(indexer, "projects_dir", lambda: tmp_path)
        monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path / "_out")
        slug = _make_imported(tmp_path)
        a = indexer.get_world_anchor(slug)
        assert a["source_kind"] == "imported"
        assert a["world"]["current_chapter"] == 3  # anchor_idx 2 → chapter 3
        assert a["characters"][0]["persona"]["boundaries"] == ["不会无理由背叛"]

    def test_missing_story(self):
        with pytest.raises(FileNotFoundError):
            indexer.get_world_anchor("no-such-story-xyz")


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


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


class TestHttp:
    def test_anchor_builtin(self, running_server):
        status, body = _get(running_server, "/api/stories/tianhuang-night/anchor")
        assert status == 200
        assert body["slug"] == "tianhuang-night"
        assert body["characters"]
        assert body["world"]["rules"]

    def test_anchor_missing_404(self, running_server):
        status, body = _get(running_server, "/api/stories/nope-story/anchor")
        assert status == 404
        assert "error" in body

    def test_anchor_traversal_400(self, running_server):
        status, body = _get(running_server, "/api/stories/..%2Fsamples/anchor")
        assert status == 400
        assert "invalid" in body["error"].lower()

    def test_plain_story_still_works(self, running_server):
        # 不破坏既有 GET /api/stories/<slug> 契约
        status, body = _get(running_server, "/api/stories/tianhuang-night")
        assert status == 200
        assert body["slug"] == "tianhuang-night"

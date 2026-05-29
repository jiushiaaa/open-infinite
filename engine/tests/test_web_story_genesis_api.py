"""v0.7 第六刀：主题创世 Web 入口（service.story_genesis + POST /api/story-genesis）。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import indexer, server
from living_novel_engine.service import (
    GenesisProjectExistsError,
    GenesisRequestError,
    generate_story,
)

PREMISE = "一名守陵人发现先祖留下的禁忌封印松动，必须在城破之前找出真相。"


# ── service 层 ────────────────────────────────────────────


class TestService:
    def test_mock_success(self, tmp_path):
        r = generate_story(
            name="gen-story",
            premise=PREMISE,
            protagonist_hint="守陵人 顾长夜",
            mock=True,
            projects_dir=tmp_path,
        )
        assert r.story_slug == "gen-story"
        assert r.chapter_count == 1
        assert r.character_count >= 3
        assert r.generation_mode == "mock"
        pdir = tmp_path / "gen-story"
        # 与 import-novel 同构
        for rel in [
            "world.yaml",
            "characters.yaml",
            "open_threads.yaml",
            "canon_chapter.md",
            "canon_opening.md",
            "story_contract.yaml",
            "canon/facts.jsonl",
            "summaries/chapter_001.yaml",
            "summaries/volume_001.yaml",
            "import_meta.json",
            "genesis_meta.json",
        ]:
            assert (pdir / rel).exists(), f"缺少 {rel}"
        assert (pdir / "source" / "chapter_001.md").exists()

    def test_deterministic_mock(self, tmp_path):
        r1 = generate_story(name="det-a", premise=PREMISE, mock=True, projects_dir=tmp_path)
        r2 = generate_story(name="det-b", premise=PREMISE, mock=True, projects_dir=tmp_path)
        # 同输入下首章正文一致（slug 不同不影响正文）
        t1 = (tmp_path / "det-a" / "canon_chapter.md").read_text(encoding="utf-8")
        t2 = (tmp_path / "det-b" / "canon_chapter.md").read_text(encoding="utf-8")
        assert t1 == t2
        assert r1.character_count == r2.character_count

    def test_existing_force_false_409(self, tmp_path):
        generate_story(name="dup", premise=PREMISE, mock=True, projects_dir=tmp_path)
        with pytest.raises(GenesisProjectExistsError):
            generate_story(name="dup", premise=PREMISE, mock=True, projects_dir=tmp_path)

    def test_force_overwrites(self, tmp_path):
        generate_story(name="dup2", premise=PREMISE, mock=True, projects_dir=tmp_path)
        r = generate_story(
            name="dup2", premise="完全不同的新主题故事", mock=True, force=True, projects_dir=tmp_path
        )
        assert r.story_slug == "dup2"

    def test_bad_slug(self, tmp_path):
        with pytest.raises(GenesisRequestError):
            generate_story(name="Bad Slug!", premise=PREMISE, mock=True, projects_dir=tmp_path)

    def test_empty_premise(self, tmp_path):
        with pytest.raises(GenesisRequestError):
            generate_story(name="nopre", premise="   ", mock=True, projects_dir=tmp_path)

    def test_anchor_readable_after_genesis(self, tmp_path, monkeypatch):
        monkeypatch.setattr(indexer, "projects_dir", lambda: tmp_path)
        monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path / "_out")
        generate_story(name="readable", premise=PREMISE, mock=True, projects_dir=tmp_path)
        a = indexer.get_world_anchor("readable")
        assert a["source_kind"] == "imported"
        assert a["characters"]
        assert a["world"]["rules"]
        assert a["world"]["current_chapter"] == 1


# ── HTTP ──────────────────────────────────────────────────


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
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
    def test_genesis_success(self, running_server):
        status, body = _post(
            running_server,
            "/api/story-genesis",
            {"name": "web-gen", "premise": PREMISE, "mock": True},
        )
        assert status == 200
        assert body["story_slug"] == "web-gen"
        assert body["chapter_count"] == 1
        assert body["anchor_hash"] == "#/anchor/web-gen"
        # 创世后 anchor 可读
        s2, anchor = _get(running_server, "/api/stories/web-gen/anchor")
        assert s2 == 200
        assert anchor["characters"]

    def test_existing_force_false_409(self, running_server):
        payload = {"name": "web-dup", "premise": PREMISE, "mock": True}
        _post(running_server, "/api/story-genesis", payload)
        status, body = _post(running_server, "/api/story-genesis", payload)
        assert status == 409
        assert "error" in body

    def test_empty_premise_400(self, running_server):
        status, body = _post(
            running_server,
            "/api/story-genesis",
            {"name": "web-empty", "premise": "", "mock": True},
        )
        assert status == 400

    def test_bad_slug_400(self, running_server):
        status, body = _post(
            running_server,
            "/api/story-genesis",
            {"name": "Bad Slug", "premise": PREMISE, "mock": True},
        )
        assert status == 400
        assert "invalid" in body["error"].lower()

"""v0.7 第五刀：导入小说 Web 入口（service.import_novel + POST /api/import-novel）。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import indexer, server
from living_novel_engine.service import (
    ImportRequestError,
    ProjectExistsError,
    import_novel_from_payload,
)


def _chapters(n: int = 4) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i + 1:03d}.md",
            "content": f"第{i + 1}章 测试\n林凡走进归云斋，发现一枚退魂铃。这是第 {i + 1} 章的正文内容。",
        }
        for i in range(n)
    ]


# ── service 层 ────────────────────────────────────────────


class TestService:
    def test_mock_import_success(self, tmp_path):
        r = import_novel_from_payload(
            name="svc-story", chapters=_chapters(4), mock=True, projects_dir=tmp_path
        )
        assert r.story_slug == "svc-story"
        assert r.chapter_count == 4
        assert r.character_count >= 1
        assert r.extraction_mode == "mock"
        pdir = tmp_path / "svc-story"
        assert (pdir / "world.yaml").exists()
        assert (pdir / "characters.yaml").exists()
        assert (pdir / "canon_chapter.md").exists()
        assert (pdir / "import_meta.json").exists()
        # 与 CLI import-novel 结构一致
        assert len(list((pdir / "source").glob("chapter_*.md"))) == 4

    def test_existing_force_false_409(self, tmp_path):
        import_novel_from_payload(
            name="dup", chapters=_chapters(3), mock=True, projects_dir=tmp_path
        )
        with pytest.raises(ProjectExistsError):
            import_novel_from_payload(
                name="dup", chapters=_chapters(3), mock=True, projects_dir=tmp_path
            )

    def test_force_true_overwrites(self, tmp_path):
        import_novel_from_payload(
            name="dup2", chapters=_chapters(3), mock=True, projects_dir=tmp_path
        )
        r = import_novel_from_payload(
            name="dup2", chapters=_chapters(5), mock=True, force=True, projects_dir=tmp_path
        )
        assert r.chapter_count == 5

    def test_too_few_chapters(self, tmp_path):
        with pytest.raises(ImportRequestError):
            import_novel_from_payload(
                name="few", chapters=_chapters(2), mock=True, projects_dir=tmp_path
            )

    def test_bad_slug(self, tmp_path):
        with pytest.raises(ImportRequestError):
            import_novel_from_payload(
                name="Bad Slug!", chapters=_chapters(3), mock=True, projects_dir=tmp_path
            )

    def test_anchor_readable_after_import(self, tmp_path, monkeypatch):
        monkeypatch.setattr(indexer, "projects_dir", lambda: tmp_path)
        monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path / "_out")
        import_novel_from_payload(
            name="readable", chapters=_chapters(4), mock=True, projects_dir=tmp_path
        )
        a = indexer.get_world_anchor("readable")
        assert a["source_kind"] == "imported"
        assert a["characters"]
        assert a["world"]["current_chapter"] == 4


# ── HTTP ──────────────────────────────────────────────────


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    # 导入落到 tmp，避免污染真实 projects/
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
    def test_import_success(self, running_server):
        status, body = _post(
            running_server,
            "/api/import-novel",
            {"name": "web-import", "chapters": _chapters(4), "mock": True},
        )
        assert status == 200
        assert body["story_slug"] == "web-import"
        assert body["chapter_count"] == 4
        assert body["anchor_hash"] == "#/anchor/web-import"

    def test_import_then_anchor_readable(self, running_server):
        _post(
            running_server,
            "/api/import-novel",
            {"name": "web-anchor", "chapters": _chapters(4), "mock": True},
        )
        status, body = _get(running_server, "/api/stories/web-anchor/anchor")
        assert status == 200
        assert body["source_kind"] == "imported"
        # /api/stories 也能立刻看到
        s2, list_body = _get(running_server, "/api/stories")
        assert s2 == 200
        slugs = [s["slug"] for s in list_body["stories"]]
        assert "web-anchor" in slugs

    def test_existing_force_false_409(self, running_server):
        payload = {"name": "web-dup", "chapters": _chapters(3), "mock": True}
        _post(running_server, "/api/import-novel", payload)
        status, body = _post(running_server, "/api/import-novel", payload)
        assert status == 409
        assert "error" in body

    def test_too_few_chapters_400(self, running_server):
        status, body = _post(
            running_server,
            "/api/import-novel",
            {"name": "web-few", "chapters": _chapters(2), "mock": True},
        )
        assert status == 400

    def test_bad_slug_400(self, running_server):
        status, body = _post(
            running_server,
            "/api/import-novel",
            {"name": "Bad Slug", "chapters": _chapters(3), "mock": True},
        )
        assert status == 400
        assert "invalid" in body["error"].lower()

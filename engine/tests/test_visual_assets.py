"""v0.7.3 Visual Asset Generation —— prompt / store / seedream client / service / HTTP。

全程不打真实外网：seedream client 用 monkeypatch / fake，service 用 mock 或 fake client。
"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.models import CharacterAgent, StoryWorld
from living_novel_engine.models.character import CharacterPersona, CharacterState
from living_novel_engine.models.world import Location, OpenThread
from living_novel_engine.service import (
    VisualAssetPathError,
    VisualAssetRequestError,
    generate_story,
    generate_visual_assets,
    get_visual_assets,
    resolve_asset_path,
)
from living_novel_engine.visual_assets import prompt_builder, store
from living_novel_engine.visual_assets.models import VisualAssets
from living_novel_engine.visual_assets.seedream_client import (
    ImageResult,
    SeedreamClient,
    SeedreamSettings,
)

PREMISE = "一名守陵人发现先祖留下的禁忌封印松动，必须在城破之前找出真相。"


def _world() -> StoryWorld:
    return StoryWorld(
        id="w1",
        title="天荒城残夜",
        display_name="天荒城残夜",
        canonical_place_name="天荒城",
        scene_description="残夜未央，城楼火光将熄。",
        rules=["低境界者不可凭蛮力胜高境者", "禁止重生/系统/穿越"],
        locations=[Location(id="l1", name="听雨轩", description="城东")],
        open_threads=[OpenThread(id="t1", title="封印之谜")],
    )


def _char() -> CharacterAgent:
    return CharacterAgent(
        id="lin_wan_zhou",
        name="林晚舟",
        narrative_role="protagonist",
        gender="女",
        persona=CharacterPersona(
            traits=["冷静", "坚韧"], desires=["查明真相"], fears=["失去同门"]
        ),
        current_state=CharacterState(location="听雨轩", emotion="警觉"),
    )


class FakeClient:
    """可注入的假 Seedream 客户端：available + 确定性字节，统计调用次数。"""

    def __init__(self, *, available: bool = True, payload: bytes = b"FAKEPNGBYTES"):
        self._available = available
        self.payload = payload
        self.calls = 0

    @property
    def available(self) -> bool:
        return self._available

    def generate_image(self, prompt: str) -> ImageResult:
        self.calls += 1
        return ImageResult(ok=True, data=self.payload, ext="png")


# ── prompt_builder ────────────────────────────────────────


class TestPromptBuilder:
    def test_cover_prompt_uses_title(self):
        p = prompt_builder.build_cover_prompt(_world())
        assert "天荒城残夜" in p
        assert "封面" in p
        # 不应出现英文占位词
        for bad in ("placeholder", "loading", "TODO", "lorem"):
            assert bad.lower() not in p.lower()

    def test_character_prompt_uses_persona(self):
        p = prompt_builder.build_character_prompt(_world(), _char())
        assert "林晚舟" in p
        assert "主角" in p
        assert "冷静" in p

    def test_scene_prompt(self):
        p = prompt_builder.build_scene_prompt(_world(), chapter_summary="夜探听雨轩")
        assert "听雨轩" in p or "残夜" in p
        assert "夜探听雨轩" in p

    def test_deterministic(self):
        a = prompt_builder.build_cover_prompt(_world())
        b = prompt_builder.build_cover_prompt(_world())
        assert a == b


# ── store ─────────────────────────────────────────────────


class TestStore:
    def test_missing_returns_none_status(self, tmp_path):
        va = store.load(tmp_path, "demo")
        assert va.status == "none"
        assert va.story_slug == "demo"

    def test_save_load_roundtrip(self, tmp_path):
        va = VisualAssets(story_slug="demo", status="ready")
        store.save(tmp_path, va)
        loaded = store.load(tmp_path, "demo")
        assert loaded.status == "ready"
        assert (tmp_path / "visual_assets.json").exists()

    def test_corrupt_degrades(self, tmp_path):
        (tmp_path / "visual_assets.json").write_text("{ not json", encoding="utf-8")
        va = store.load(tmp_path, "demo")
        assert va.status == "none"

    def test_write_image_and_resolve(self, tmp_path):
        rel = store.write_image(tmp_path, "characters/hero.png", b"DATA")
        assert rel == "assets/characters/hero.png"
        found = store.resolve_asset_file(tmp_path, "characters/hero.png")
        assert found is not None and found.read_bytes() == b"DATA"

    def test_resolve_missing_returns_none(self, tmp_path):
        assert store.resolve_asset_file(tmp_path, "nope.png") is None

    def test_resolve_traversal_raises(self, tmp_path):
        with pytest.raises(ValueError):
            store.resolve_asset_file(tmp_path, "../../secret.txt")

    def test_write_traversal_raises(self, tmp_path):
        with pytest.raises(ValueError):
            store.write_image(tmp_path, "../escape.png", b"x")


# ── seedream client ───────────────────────────────────────


class TestSeedreamClient:
    def test_no_key_unavailable(self, monkeypatch):
        monkeypatch.delenv("SEEDREAM_API_KEY", raising=False)
        monkeypatch.delenv("LNE_VISUAL_ASSETS", raising=False)
        c = SeedreamClient(SeedreamSettings(api_key="", enabled=True))
        assert c.available is False
        r = c.generate_image("x")
        assert r.ok is False
        assert "SEEDREAM_API_KEY" in r.error

    def test_disabled_flag(self):
        c = SeedreamClient(SeedreamSettings(api_key="k", enabled=False))
        assert c.available is False
        assert c.generate_image("x").ok is False

    def test_mock_available_no_network(self):
        c = SeedreamClient(SeedreamSettings(api_key="", enabled=True), mock=True)
        assert c.available is True
        assert c.generate_image("x").ok is False  # 由 service 落占位

    def test_parse_b64(self):
        import base64

        c = SeedreamClient(SeedreamSettings(api_key="k", enabled=True))
        payload = {"data": [{"b64_json": base64.b64encode(b"hello").decode()}]}
        r = c._parse(payload)
        assert r.ok and r.data == b"hello"

    def test_parse_unrecognized(self):
        c = SeedreamClient(SeedreamSettings(api_key="k", enabled=True))
        assert c._parse({"weird": 1}).ok is False

    def test_generate_via_monkeypatched_network(self, monkeypatch):
        import base64

        c = SeedreamClient(SeedreamSettings(api_key="k", enabled=True))
        monkeypatch.setattr(
            c,
            "_raw_generate",
            lambda prompt: {"data": [{"b64_json": base64.b64encode(b"img").decode()}]},
        )
        r = c.generate_image("画一张图")
        assert r.ok and r.data == b"img"

    def test_network_exception_fallback(self, monkeypatch):
        c = SeedreamClient(SeedreamSettings(api_key="k", enabled=True))

        def boom(prompt):
            raise OSError("connection refused")

        monkeypatch.setattr(c, "_raw_generate", boom)
        r = c.generate_image("x")
        assert r.ok is False
        assert "k" not in r.error.replace("Seedream", "")  # 不泄漏 key 本体


# ── service ───────────────────────────────────────────────


def _make_project(tmp_path, slug="vis-demo"):
    generate_story(name=slug, premise=PREMISE, mock=True, projects_dir=tmp_path)
    return slug


class TestService:
    def test_generate_mock_placeholders(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        slug = _make_project(tmp_path)
        va = generate_visual_assets(slug, mock=True, projects_dir=tmp_path)
        assert va.cover is not None and va.cover.status == "placeholder"
        assert va.scenes["main"].status == "placeholder"
        assert va.characters  # 3 个角色
        assert all(e.status == "placeholder" for e in va.characters.values())
        assert va.status == "none"  # 仅占位
        # 占位不落图片文件
        assert not (tmp_path / slug / "assets").exists()
        # artifact 已落盘
        assert (tmp_path / slug / "visual_assets.json").exists()

    def test_generate_with_fake_client_ready(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        slug = _make_project(tmp_path)
        fake = FakeClient()
        va = generate_visual_assets(slug, client=fake, projects_dir=tmp_path)
        assert va.cover.status == "ready"
        assert va.cover.path == "assets/cover.png"
        assert (tmp_path / slug / "assets" / "cover.png").read_bytes() == fake.payload
        assert va.status == "ready"
        first_calls = fake.calls
        assert first_calls >= 5  # cover + 3 chars + scene

    def test_force_false_skips_ready(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        slug = _make_project(tmp_path)
        fake = FakeClient()
        generate_visual_assets(slug, client=fake, projects_dir=tmp_path)
        calls_after_first = fake.calls
        generate_visual_assets(slug, client=fake, projects_dir=tmp_path, force=False)
        assert fake.calls == calls_after_first  # 不重复生成已 ready

    def test_force_true_regenerates(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        slug = _make_project(tmp_path)
        fake = FakeClient()
        generate_visual_assets(slug, client=fake, projects_dir=tmp_path)
        calls_after_first = fake.calls
        generate_visual_assets(slug, client=fake, projects_dir=tmp_path, force=True)
        assert fake.calls > calls_after_first

    def test_only_cover_kind(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        slug = _make_project(tmp_path)
        fake = FakeClient()
        va = generate_visual_assets(
            slug, kinds=["cover"], client=fake, projects_dir=tmp_path
        )
        assert va.cover.status == "ready"
        assert not va.characters and not va.scenes

    def test_bad_slug(self, tmp_path):
        with pytest.raises(VisualAssetRequestError):
            generate_visual_assets("Bad Slug!", mock=True, projects_dir=tmp_path)

    def test_invalid_kind(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        slug = _make_project(tmp_path)
        with pytest.raises(VisualAssetRequestError):
            generate_visual_assets(slug, kinds=["bogus"], projects_dir=tmp_path)

    def test_missing_story(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        with pytest.raises(FileNotFoundError):
            generate_visual_assets("ghost", mock=True, projects_dir=tmp_path)

    def test_get_missing_artifact(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        slug = _make_project(tmp_path)
        va = get_visual_assets(slug, projects_dir=tmp_path)
        assert va.status == "none"

    def test_resolve_traversal(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        slug = _make_project(tmp_path)
        with pytest.raises(VisualAssetPathError):
            resolve_asset_path(slug, "../../world.yaml", projects_dir=tmp_path)


# ── HTTP ──────────────────────────────────────────────────


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
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


def _get_raw(port: int, path: str) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def _seed_project(port: int, slug: str = "web-vis") -> str:
    _post(port, "/api/story-genesis", {"name": slug, "premise": PREMISE, "mock": True})
    return slug


class TestHttp:
    def test_get_artifact_placeholder(self, running_server):
        port, _ = running_server
        slug = _seed_project(port)
        status, body = _get(port, f"/api/stories/{slug}/visual-assets")
        assert status == 200
        assert body["status"] == "none"
        assert body["story_slug"] == slug

    def test_get_missing_story_404(self, running_server):
        port, _ = running_server
        status, _body = _get(port, "/api/stories/ghost/visual-assets")
        assert status == 404

    def test_get_bad_slug_400(self, running_server):
        port, _ = running_server
        # 大写 slug 过 safe_id 但不过 service slug 校验 → 400
        status, _body = _get(port, "/api/stories/BadSlug/visual-assets")
        assert status == 400

    def test_post_generate_no_key_placeholder(self, running_server):
        port, _ = running_server
        slug = _seed_project(port)
        status, body = _post(
            port, f"/api/stories/{slug}/visual-assets/generate", {"kinds": ["cover"]}
        )
        assert status == 200
        # 无 key → 占位，不打外网
        assert body["cover"]["status"] == "placeholder"

    def test_post_generate_mock(self, running_server):
        port, _ = running_server
        slug = _seed_project(port)
        status, body = _post(
            port,
            f"/api/stories/{slug}/visual-assets/generate",
            {"kinds": ["characters"], "mock": True},
        )
        assert status == 200
        assert body["characters"]
        assert all(e["status"] == "placeholder" for e in body["characters"].values())

    def test_post_generate_missing_story_404(self, running_server):
        port, _ = running_server
        status, _body = _post(
            port, "/api/stories/ghost/visual-assets/generate", {"mock": True}
        )
        assert status == 404

    def test_asset_file_served(self, running_server):
        port, tmp_path = running_server
        slug = _seed_project(port)
        store.write_image(tmp_path / slug, "cover.png", b"PNGRAWDATA")
        status, data = _get_raw(port, f"/api/stories/{slug}/assets/cover.png")
        assert status == 200
        assert data == b"PNGRAWDATA"

    def test_asset_file_missing_404(self, running_server):
        port, _ = running_server
        slug = _seed_project(port)
        status, _data = _get_raw(port, f"/api/stories/{slug}/assets/nope.png")
        assert status == 404

    def test_asset_path_traversal_403(self, running_server):
        port, _ = running_server
        slug = _seed_project(port)
        status, _data = _get_raw(
            port, f"/api/stories/{slug}/assets/%2e%2e%2f%2e%2e%2fworld.yaml"
        )
        assert status == 403

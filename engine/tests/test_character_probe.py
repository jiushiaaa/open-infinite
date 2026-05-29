"""v0.7.2 角色探针：probe_character + GET /api/stories/<slug>/characters/<id>/probe。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest
import yaml

from living_novel_engine.browser import server
from living_novel_engine.service import ProbeRequestError, probe_character


# ── service 层（内置样例）─────────────────────────────────


class TestService:
    def test_builtin_character(self):
        p = probe_character(
            story_slug="tianhuang-night", character_id="lin_wan_zhou"
        )
        assert p.character_id == "lin_wan_zhou"
        assert p.name
        assert p.belief_summary
        assert p.boundaries  # 林晚舟有人设边界
        assert p.resistance_level in ("low", "medium", "high")
        assert p.obedience_risk in ("low", "medium", "high")
        assert p.explanation

    def test_forced_action_intervention_predicts_resistance(self):
        p = probe_character(
            story_slug="tianhuang-night",
            character_id="lin_wan_zhou",
            intervention_text="你必须立刻背叛林凡",
        )
        # 强制行动 + 人设边界 → 抗拒
        assert p.resistance_level in ("medium", "high")
        assert p.likely_intervention_response

    def test_rule_rewrite_intervention_high_resistance(self):
        p = probe_character(
            story_slug="tianhuang-night",
            character_id="lin_wan_zhou",
            intervention_text="给她一台修仙系统面板",
        )
        assert p.resistance_level == "high"
        assert p.obedience_risk == "low"

    def test_missing_character_404(self):
        with pytest.raises(FileNotFoundError):
            probe_character(
                story_slug="tianhuang-night", character_id="no-such-char"
            )

    def test_missing_story_404(self):
        with pytest.raises(FileNotFoundError):
            probe_character(story_slug="no-such-xyz", character_id="x")

    def test_missing_args(self):
        with pytest.raises(ProbeRequestError):
            probe_character(story_slug="tianhuang-night", character_id="")

    def test_snapshot_override(self, tmp_path):
        # 构造一个 state_snapshot.json，验证 run/branch 叠加情绪与第四面墙觉察
        run_dir = tmp_path / "run_test" / "branch_a"
        run_dir.mkdir(parents=True)
        (run_dir / "state_snapshot.json").write_text(
            json.dumps(
                {
                    "characters": {
                        "lin_wan_zhou": {
                            "emotion": "惊疑",
                            "fourth_wall_awareness": 0.9,
                            "fourth_wall_level": "defiant",
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        p = probe_character(
            story_slug="tianhuang-night",
            character_id="lin_wan_zhou",
            run_id="run_test",
            branch_id="branch_a",
            outputs_root=tmp_path,
        )
        assert p.current_emotion == "惊疑"
        assert p.fourth_wall_awareness == 0.9
        assert p.fourth_wall_level == "defiant"

    def test_corrupt_snapshot_does_not_crash(self, tmp_path):
        run_dir = tmp_path / "run_bad" / "branch_a"
        run_dir.mkdir(parents=True)
        (run_dir / "state_snapshot.json").write_text("{not json", encoding="utf-8")
        p = probe_character(
            story_slug="tianhuang-night",
            character_id="lin_wan_zhou",
            run_id="run_bad",
            branch_id="branch_a",
            outputs_root=tmp_path,
        )
        assert p.character_id == "lin_wan_zhou"

    def test_corrupt_story_yaml_maps_to_request_error(self, tmp_path, monkeypatch):
        pdir = tmp_path / "broken-probe"
        pdir.mkdir()
        (pdir / "world.yaml").write_text("key: value: another\n", encoding="utf-8")
        (pdir / "characters.yaml").write_text(
            yaml.safe_dump(
                {"characters": [{"id": "qing", "name": "青衫客"}]},
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))

        with pytest.raises(ProbeRequestError):
            probe_character(story_slug="broken-probe", character_id="qing")


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
    def test_probe_ok(self, running_server):
        status, body = _get(
            running_server,
            "/api/stories/tianhuang-night/characters/lin_wan_zhou/probe",
        )
        assert status == 200
        assert body["character_id"] == "lin_wan_zhou"
        assert body["boundaries"]
        assert body["explanation"]

    def test_probe_with_intervention_text(self, running_server):
        status, body = _get(
            running_server,
            "/api/stories/tianhuang-night/characters/lin_wan_zhou/probe"
            "?intervention_text=%E7%BB%99%E5%A5%B9%E4%B8%80%E5%8F%B0%E7%B3%BB%E7%BB%9F",
        )
        assert status == 200
        assert body["resistance_level"] == "high"

    def test_probe_missing_character_404(self, running_server):
        status, body = _get(
            running_server,
            "/api/stories/tianhuang-night/characters/nope/probe",
        )
        assert status == 404

    def test_probe_missing_story_404(self, running_server):
        status, body = _get(
            running_server,
            "/api/stories/no-such-xyz/characters/hero/probe",
        )
        assert status == 404

    def test_plain_story_still_works(self, running_server):
        status, body = _get(running_server, "/api/stories/tianhuang-night")
        assert status == 200
        assert body["slug"] == "tianhuang-night"

    def test_imported_probe(self, tmp_path, monkeypatch):
        # imported 项目角色也可探针（用临时 projects 目录）
        pdir = tmp_path / "probe-proj"
        pdir.mkdir(parents=True)
        (pdir / "world.yaml").write_text(
            yaml.safe_dump(
                {"display_name": "探针项目", "source_type": "imported", "rules": []},
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        (pdir / "characters.yaml").write_text(
            yaml.safe_dump(
                {
                    "characters": [
                        {
                            "id": "qing",
                            "name": "青衫客",
                            "persona": {
                                "desires": ["复仇"],
                                "fears": ["孤独"],
                                "boundaries": ["不会无理由背叛"],
                            },
                        }
                    ]
                },
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        # service 层直接读 story_loader（受 LNE_PROJECTS_DIR 影响）；此处直接走 service
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
        p = probe_character(story_slug="probe-proj", character_id="qing")
        assert p.name == "青衫客"
        assert p.desires == ["复仇"]

    def test_probe_corrupt_yaml_http_400(self, tmp_path, monkeypatch):
        pdir = tmp_path / "broken-probe-http"
        pdir.mkdir()
        (pdir / "world.yaml").write_text("key: value: another\n", encoding="utf-8")
        (pdir / "characters.yaml").write_text(
            yaml.safe_dump(
                {"characters": [{"id": "qing", "name": "青衫客"}]},
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))

        port = _free_port()
        httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            status, body = _get(
                port,
                "/api/stories/broken-probe-http/characters/qing/probe",
            )
        finally:
            httpd.shutdown()
            httpd.server_close()

        assert status == 400
        assert "解析失败" in body["error"]

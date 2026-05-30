"""v0.7.5 Worldline Judge —— branch-level deterministic judgement + HTTP."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import (
    WorldlineJudgeRequestError,
    get_worldline_judgement,
    judge_worldline,
)
from living_novel_engine.worldline_judge.evaluator import evaluate_worldline

BUILTIN_SLUG = "tianhuang-night"


@pytest.fixture
def isolated_outputs(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    return outputs


def _write_branch(outputs, *, run_id="run_judge_demo", branch_id="branch_a"):
    run_dir = outputs / run_id
    branch_dir = run_dir / branch_id
    branch_dir.mkdir(parents=True)
    (run_dir / "meta.json").write_text(
        json.dumps(
            {
                "kind": "intervene",
                "story_slug": BUILTIN_SLUG,
                "source_kind": "builtin",
                "current_chapter": 13,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "intervention.json").write_text(
        json.dumps(
            {"story_slug": BUILTIN_SLUG, "content": "让林晚舟今晚避开城外竹林"},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "intervention_compilation.json").write_text(
        json.dumps(
            {
                "lineage_type": "divergent_worldline",
                "affected_scope": {"characters": ["lin_wan_zhou"], "rules": []},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (branch_dir / "chapter.md").write_text(
        (
            "林晚舟没有立刻赴约。她在听雨轩前停步，忽然意识到纸鹤传来的警讯并非幻觉。"
            "墨青烟布下的杀局因此提前暴露，陆沉舟被迫改道入城。"
            "可封印裂缝仍在扩大，天荒城的钟声一遍遍压下来，她必须在黎明前决定是否反将一军。"
        ),
        encoding="utf-8",
    )
    (branch_dir / "summary.md").write_text(
        "林晚舟因警讯改道，竹林杀局提前暴露，封印危机被推向下一章。",
        encoding="utf-8",
    )
    (branch_dir / "events.json").write_text(
        json.dumps(
            {
                "worldline_id": branch_id,
                "theme": "相信警讯并改道",
                "branch_seed": "believe",
                "chapter": 13,
                "accepted_events": [
                    {"character_id": "lin_wan_zhou", "narrative": "林晚舟改道调查"},
                    {"character_id": "mo_qing_yan", "narrative": "墨青烟杀局暴露"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (branch_dir / "state_snapshot.json").write_text(
        json.dumps(
            {
                "next_chapter_hook": "林晚舟必须在黎明前反将一军。",
                "characters": {
                    "lin_wan_zhou": {"name": "林晚舟", "emotion": "警惕"},
                    "mo_qing_yan": {"name": "墨青烟", "emotion": "震怒"},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (branch_dir / "causal_diff.json").write_text(
        json.dumps(
            {
                "lineage_type": "divergent_worldline",
                "blocks": [
                    {
                        "id": "diff_1",
                        "old_text": "林晚舟赴约。",
                        "new_text": "林晚舟改道调查。",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return run_id, branch_id


class TestWorldlineEvaluator:
    def test_scores_are_in_range_and_recommends_continuation(self):
        ev = evaluate_worldline(
            chapter_text=(
                "林晚舟忽然停步，意识到墨青烟的杀局已经逼近。"
                "她转而进入听雨轩调查，封印裂缝仍在扩大，下一章必须反击。"
            ),
            summary_text="林晚舟改道调查，封印危机升级。",
            events={
                "theme": "相信警讯",
                "branch_seed": "believe",
                "accepted_events": [{"narrative": "林晚舟改道调查"}],
            },
            state_snapshot={
                "next_chapter_hook": "她必须在黎明前反击。",
                "characters": {"lin": {"name": "林晚舟", "emotion": "警惕"}},
            },
            known_character_names=["林晚舟", "墨青烟"],
            world_rules=["天荒城封印不可被凡物轻易破坏"],
            causal_diff={"blocks": [{"id": "d1"}]},
            intervention={"content": "提醒林晚舟避开竹林"},
            compilation={"lineage_type": "divergent_worldline"},
        )
        assert ev.recommendation == "推荐继续"
        assert ev.scores.overall > 0.55
        assert ev.scores.emergence_score > 0.4
        assert ev.turning_points
        for value in ev.scores.model_dump().values():
            assert 0.0 <= value <= 1.0

    def test_flat_repetitive_text_warns_and_archives(self):
        ev = evaluate_worldline(
            chapter_text="命运的齿轮开始转动。命运的齿轮开始转动。命运的齿轮开始转动。",
            summary_text="",
            events={},
            state_snapshot={},
            known_character_names=["林晚舟"],
            world_rules=[],
        )
        assert ev.recommendation == "建议归档"
        assert ev.scores.anti_slop < 0.6
        assert ev.warnings


class TestWorldlineJudgeService:
    def test_judge_writes_and_reads_branch_artifact(self, isolated_outputs):
        outputs = isolated_outputs
        run_id, branch_id = _write_branch(outputs)
        report = judge_worldline(
            run_id=run_id,
            branch_id=branch_id,
            story_slug=BUILTIN_SLUG,
            outputs_dir=outputs,
        )
        assert report["kind"] == "worldline_judgement"
        assert report["story_slug"] == BUILTIN_SLUG
        assert report["run_id"] == run_id
        assert report["branch_id"] == branch_id
        assert report["recommendation"] in {"推荐继续", "谨慎继续", "建议归档"}
        assert (outputs / run_id / branch_id / "worldline_judgement.json").exists()

        fetched = get_worldline_judgement(run_id, branch_id, outputs_dir=outputs)
        assert fetched["run_id"] == run_id
        assert fetched["scores"]["overall"] == report["scores"]["overall"]

    def test_bad_run_id_rejected_before_path_use(self, isolated_outputs):
        with pytest.raises(WorldlineJudgeRequestError):
            judge_worldline(
                run_id="../outside",
                branch_id="branch_a",
                story_slug=BUILTIN_SLUG,
                outputs_dir=isolated_outputs,
            )

    def test_missing_branch_is_404_surface(self, isolated_outputs):
        with pytest.raises(FileNotFoundError):
            judge_worldline(
                run_id="run_missing",
                branch_id="branch_a",
                story_slug=BUILTIN_SLUG,
                outputs_dir=isolated_outputs,
            )

    def test_get_missing_report(self, isolated_outputs):
        _write_branch(isolated_outputs)
        with pytest.raises(FileNotFoundError):
            get_worldline_judgement(
                "run_judge_demo", "branch_a", outputs_dir=isolated_outputs
            )


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    projects.mkdir()
    outputs.mkdir()
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port, outputs
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
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


class TestHttp:
    def test_post_and_get_worldline_judgement(self, running_server):
        port, outputs = running_server
        run_id, branch_id = _write_branch(outputs)
        status, body = _post(
            port,
            f"/api/runs/{run_id}/branches/{branch_id}/worldline-judgement",
            {"story_slug": BUILTIN_SLUG},
        )
        assert status == 200
        assert body["kind"] == "worldline_judgement"
        assert body["scores"]["overall"] >= 0.0

        status, fetched = _get(
            port, f"/api/runs/{run_id}/branches/{branch_id}/worldline-judgement"
        )
        assert status == 200
        assert fetched["run_id"] == run_id

    def test_get_missing_worldline_judgement_404(self, running_server):
        port, outputs = running_server
        run_id, branch_id = _write_branch(outputs)
        status, _body = _get(
            port, f"/api/runs/{run_id}/branches/{branch_id}/worldline-judgement"
        )
        assert status == 404

    def test_bad_branch_id_400(self, running_server):
        port, _outputs = running_server
        status, _body = _post(
            port,
            "/api/runs/run_demo/branches/../worldline-judgement",
            {"story_slug": BUILTIN_SLUG},
        )
        assert status == 400

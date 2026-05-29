"""v0.7.4 Baseline & Canon Replay —— baseline service / holdout / replay evaluator + HTTP。

全程不打真实外网、不调用 LLM：baseline 走 mock；replay 为 deterministic 本地评估。
"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.canon_replay.evaluator import evaluate_replay
from living_novel_engine.service import (
    BaselineRequestError,
    HoldoutExistsError,
    HoldoutReadOnlyError,
    HoldoutRequestError,
    ReplayRequestError,
    generate_baseline,
    generate_story,
    get_baseline_report,
    get_canon_replay_report,
    get_holdout,
    run_canon_replay,
    write_holdout,
)

PREMISE = "一名守陵人发现先祖留下的禁忌封印松动，必须在城破之前找出真相。"
BUILTIN_SLUG = "tianhuang-night"


@pytest.fixture
def isolated_dirs(tmp_path, monkeypatch):
    """隔离 projects/outputs 目录，避免污染真实数据。"""
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    projects.mkdir()
    outputs.mkdir()
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    return projects, outputs


def _make_project(projects_dir, slug="canon-demo") -> str:
    generate_story(name=slug, premise=PREMISE, mock=True, projects_dir=projects_dir)
    return slug


# ── Baseline service ──────────────────────────────────────


class TestBaselineService:
    def test_builtin_baseline_success(self, isolated_dirs):
        _, outputs = isolated_dirs
        result = generate_baseline(story_slug=BUILTIN_SLUG, rounds=2, mock=True)
        assert result.story_slug == BUILTIN_SLUG
        assert result.branch_id == "baseline"
        assert result.report["kind"] == "baseline"
        assert result.report["no_intervention"] is True
        assert result.report["source_kind"] == "builtin"
        run_dir = outputs / result.run_id
        assert (run_dir / "baseline_report.json").exists()
        assert (run_dir / "baseline" / "chapter.md").exists()

    def test_baseline_no_intervention_artifacts(self, isolated_dirs):
        """无干预基线不得写 intervention.json / causal_diff.json。"""
        _, outputs = isolated_dirs
        result = generate_baseline(story_slug=BUILTIN_SLUG, rounds=2, mock=True)
        run_dir = outputs / result.run_id
        assert not (run_dir / "intervention.json").exists()
        for sub in run_dir.rglob("intervention.json"):
            raise AssertionError(f"baseline 不应包含 intervention.json: {sub}")
        for sub in run_dir.rglob("causal_diff.json"):
            raise AssertionError(f"baseline 不应包含 causal_diff.json: {sub}")

    def test_imported_baseline_success(self, isolated_dirs):
        projects, outputs = isolated_dirs
        slug = _make_project(projects)
        result = generate_baseline(story_slug=slug, rounds=2, mock=True)
        assert result.report["source_kind"] == "imported"
        assert (outputs / result.run_id / "baseline" / "state_snapshot.json").exists()

    def test_missing_story(self, isolated_dirs):
        with pytest.raises(FileNotFoundError):
            generate_baseline(story_slug="ghost-missing", mock=True)

    def test_empty_slug(self, isolated_dirs):
        with pytest.raises(BaselineRequestError):
            generate_baseline(story_slug="", mock=True)

    def test_bad_slug_rejected_before_path_use(self, isolated_dirs):
        with pytest.raises(BaselineRequestError):
            generate_baseline(story_slug="../evil", mock=True)

    def test_invalid_rounds(self, isolated_dirs):
        with pytest.raises(BaselineRequestError):
            generate_baseline(story_slug=BUILTIN_SLUG, rounds=0, mock=True)

    def test_from_run_without_branch(self, isolated_dirs):
        with pytest.raises(BaselineRequestError):
            generate_baseline(
                story_slug=BUILTIN_SLUG, mock=True, from_run_id="run_x"
            )

    def test_from_run_path_traversal_rejected(self, isolated_dirs):
        with pytest.raises(BaselineRequestError):
            generate_baseline(
                story_slug=BUILTIN_SLUG,
                mock=True,
                from_run_id="../outside",
                from_branch_id="baseline",
            )

    def test_get_report_roundtrip(self, isolated_dirs):
        _, outputs = isolated_dirs
        result = generate_baseline(story_slug=BUILTIN_SLUG, rounds=2, mock=True)
        report = get_baseline_report(result.run_id, outputs_dir=outputs)
        assert report["run_id"] == result.run_id
        assert report["kind"] == "baseline"

    def test_get_report_missing(self, isolated_dirs):
        _, outputs = isolated_dirs
        with pytest.raises(FileNotFoundError):
            get_baseline_report("run_does_not_exist", outputs_dir=outputs)

    def test_get_report_path_traversal_rejected(self, isolated_dirs):
        _, outputs = isolated_dirs
        with pytest.raises(BaselineRequestError):
            get_baseline_report("../outside", outputs_dir=outputs)


# ── Holdout service ───────────────────────────────────────


class TestHoldoutService:
    def test_write_and_read(self, isolated_dirs):
        projects, _ = isolated_dirs
        slug = _make_project(projects)
        manifest = write_holdout(
            slug,
            chapters=[{"chapter": 5, "title": "第五章 余烬", "content": "正史第五章内容。"}],
            projects_dir=projects,
        )
        assert manifest["chapter_count"] == 1
        assert manifest["available_chapters"] == [5]
        assert (projects / slug / "canon" / "holdout" / "chapter_005.md").exists()
        got = get_holdout(slug, projects_dir=projects)
        assert got["available_chapters"] == [5]
        assert got["chapters"][0]["path"] == "canon/holdout/chapter_005.md"

    def test_empty_manifest_when_none(self, isolated_dirs):
        projects, _ = isolated_dirs
        slug = _make_project(projects)
        got = get_holdout(slug, projects_dir=projects)
        assert got["chapter_count"] == 0
        assert got["available_chapters"] == []

    def test_force_false_conflict(self, isolated_dirs):
        projects, _ = isolated_dirs
        slug = _make_project(projects)
        write_holdout(
            slug, chapters=[{"chapter": 5, "content": "甲"}], projects_dir=projects
        )
        with pytest.raises(HoldoutExistsError):
            write_holdout(
                slug, chapters=[{"chapter": 5, "content": "乙"}], projects_dir=projects
            )

    def test_force_true_overwrite(self, isolated_dirs):
        projects, _ = isolated_dirs
        slug = _make_project(projects)
        write_holdout(
            slug, chapters=[{"chapter": 5, "content": "甲甲甲"}], projects_dir=projects
        )
        write_holdout(
            slug,
            chapters=[{"chapter": 5, "content": "乙乙"}],
            force=True,
            projects_dir=projects,
        )
        path = projects / slug / "canon" / "holdout" / "chapter_005.md"
        assert path.read_text(encoding="utf-8") == "乙乙"

    def test_builtin_read_only(self, isolated_dirs):
        with pytest.raises(HoldoutReadOnlyError):
            write_holdout(
                BUILTIN_SLUG, chapters=[{"chapter": 5, "content": "x"}]
            )

    def test_builtin_get_empty_ok(self, isolated_dirs):
        got = get_holdout(BUILTIN_SLUG)
        assert got["chapter_count"] == 0

    def test_empty_content_rejected(self, isolated_dirs):
        projects, _ = isolated_dirs
        slug = _make_project(projects)
        with pytest.raises(HoldoutRequestError):
            write_holdout(
                slug, chapters=[{"chapter": 5, "content": "   "}], projects_dir=projects
            )

    def test_bad_chapter_number(self, isolated_dirs):
        projects, _ = isolated_dirs
        slug = _make_project(projects)
        with pytest.raises(HoldoutRequestError):
            write_holdout(
                slug, chapters=[{"chapter": 0, "content": "x"}], projects_dir=projects
            )

    def test_bad_slug(self, isolated_dirs):
        with pytest.raises(HoldoutRequestError):
            get_holdout("Bad Slug!")

    def test_path_is_derived_not_user_controlled(self, isolated_dirs):
        """文件名由章号派生，用户提供的 title/path 不影响落盘路径。"""
        projects, _ = isolated_dirs
        slug = _make_project(projects)
        write_holdout(
            slug,
            chapters=[
                {"chapter": 7, "title": "../../evil", "content": "内容内容"}
            ],
            projects_dir=projects,
        )
        assert (projects / slug / "canon" / "holdout" / "chapter_007.md").exists()
        assert not (projects / "evil").exists()


# ── Replay evaluator (unit) ───────────────────────────────


class TestReplayEvaluator:
    def test_scores_in_range(self):
        ev = evaluate_replay(
            "林晚舟走进听雨轩，封印之谜逐渐揭开。",
            "林晚舟来到听雨轩，封印之谜的真相浮现。",
            entities=["林晚舟", "听雨轩"],
            threads=["封印之谜"],
            baseline_state={"characters": {"c1": {"name": "林晚舟"}}},
        )
        for v in (
            ev.lexical_overlap,
            ev.entity_overlap,
            ev.thread_overlap,
            ev.length_ratio,
            ev.state_consistency,
            ev.overall,
        ):
            assert 0.0 <= v <= 1.0

    def test_entity_match_and_missing(self):
        ev = evaluate_replay(
            "林晚舟独自前行。",
            "林晚舟与陆沉舟在听雨轩重逢。",
            entities=["林晚舟", "陆沉舟", "听雨轩"],
        )
        assert "林晚舟" in ev.matched_entities
        assert "陆沉舟" in ev.missing_entities
        assert "听雨轩" in ev.missing_entities

    def test_identical_high_overall(self):
        text = "林晚舟在听雨轩揭开封印之谜，城破之夜来临。"
        ev = evaluate_replay(
            text, text, entities=["林晚舟", "听雨轩"], threads=["封印之谜"]
        )
        assert ev.overall > 0.6
        assert ev.interpretation

    def test_empty_texts_warn(self):
        ev = evaluate_replay("", "")
        assert ev.overall == 0.0
        assert ev.warnings


# ── Replay service ────────────────────────────────────────


class TestReplayService:
    def _setup(self, projects, slug="replay-demo"):
        _make_project(projects, slug)
        write_holdout(
            slug,
            chapters=[{"chapter": 5, "title": "第五章", "content": "正史第五章的内容文本。"}],
            projects_dir=projects,
        )
        return slug

    def test_replay_writes_report(self, isolated_dirs):
        projects, outputs = isolated_dirs
        slug = self._setup(projects)
        baseline = generate_baseline(story_slug=slug, rounds=2, mock=True)
        report = run_canon_replay(
            story_slug=slug,
            baseline_run_id=baseline.run_id,
            baseline_branch_id="baseline",
            holdout_chapter=5,
            projects_dir=projects,
            outputs_dir=outputs,
        )
        assert report["kind"] == "canon_replay"
        assert report["holdout_chapter"] == 5
        assert 0.0 <= report["scores"]["overall"] <= 1.0
        assert (outputs / baseline.run_id / "canon_replay_report.json").exists()
        fetched = get_canon_replay_report(baseline.run_id, outputs_dir=outputs)
        assert fetched["baseline_run_id"] == baseline.run_id

    def test_missing_baseline_run(self, isolated_dirs):
        projects, outputs = isolated_dirs
        slug = self._setup(projects)
        with pytest.raises(FileNotFoundError):
            run_canon_replay(
                story_slug=slug,
                baseline_run_id="run_nope",
                holdout_chapter=5,
                projects_dir=projects,
                outputs_dir=outputs,
            )

    def test_bad_baseline_run_id_rejected(self, isolated_dirs):
        projects, outputs = isolated_dirs
        slug = self._setup(projects)
        with pytest.raises(ReplayRequestError):
            run_canon_replay(
                story_slug=slug,
                baseline_run_id="../outside",
                holdout_chapter=5,
                projects_dir=projects,
                outputs_dir=outputs,
            )

    def test_bad_baseline_branch_id_rejected(self, isolated_dirs):
        projects, outputs = isolated_dirs
        slug = self._setup(projects)
        baseline = generate_baseline(story_slug=slug, rounds=2, mock=True)
        with pytest.raises(ReplayRequestError):
            run_canon_replay(
                story_slug=slug,
                baseline_run_id=baseline.run_id,
                baseline_branch_id="../outside",
                holdout_chapter=5,
                projects_dir=projects,
                outputs_dir=outputs,
            )

    def test_missing_holdout(self, isolated_dirs):
        projects, outputs = isolated_dirs
        slug = _make_project(projects, "no-holdout")
        baseline = generate_baseline(story_slug=slug, rounds=2, mock=True)
        with pytest.raises(FileNotFoundError):
            run_canon_replay(
                story_slug=slug,
                baseline_run_id=baseline.run_id,
                holdout_chapter=5,
                projects_dir=projects,
                outputs_dir=outputs,
            )

    def test_bad_holdout_chapter(self, isolated_dirs):
        projects, outputs = isolated_dirs
        slug = self._setup(projects)
        baseline = generate_baseline(story_slug=slug, rounds=2, mock=True)
        with pytest.raises(ReplayRequestError):
            run_canon_replay(
                story_slug=slug,
                baseline_run_id=baseline.run_id,
                holdout_chapter=0,
                projects_dir=projects,
                outputs_dir=outputs,
            )

    def test_get_report_missing(self, isolated_dirs):
        _, outputs = isolated_dirs
        with pytest.raises(FileNotFoundError):
            get_canon_replay_report("run_nope", outputs_dir=outputs)

    def test_get_report_path_traversal_rejected(self, isolated_dirs):
        _, outputs = isolated_dirs
        with pytest.raises(ReplayRequestError):
            get_canon_replay_report("../outside", outputs_dir=outputs)


# ── HTTP ──────────────────────────────────────────────────


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
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port, projects, outputs
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
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def _seed_project(port: int, slug: str = "web-canon") -> str:
    _post(port, "/api/story-genesis", {"name": slug, "premise": PREMISE, "mock": True})
    return slug


class TestHttp:
    def test_baseline_post_and_get(self, running_server):
        port, _, _ = running_server
        slug = _seed_project(port)
        status, body = _post(
            port, f"/api/stories/{slug}/baseline", {"rounds": 2, "mock": True}
        )
        assert status == 200
        assert body["report"]["kind"] == "baseline"
        run_id = body["run_id"]
        status, report = _get(port, f"/api/runs/{run_id}/baseline")
        assert status == 200
        assert report["run_id"] == run_id

    def test_baseline_missing_story_404(self, running_server):
        port, _, _ = running_server
        status, _b = _post(port, "/api/stories/ghost/baseline", {"mock": True})
        assert status == 404

    def test_baseline_get_missing_404(self, running_server):
        port, _, _ = running_server
        status, _b = _get(port, "/api/runs/run_nope/baseline")
        assert status == 404

    def test_holdout_get_empty(self, running_server):
        port, _, _ = running_server
        slug = _seed_project(port)
        status, body = _get(port, f"/api/stories/{slug}/canon/holdout")
        assert status == 200
        assert body["chapter_count"] == 0

    def test_holdout_post_and_conflict(self, running_server):
        port, _, _ = running_server
        slug = _seed_project(port)
        status, body = _post(
            port,
            f"/api/stories/{slug}/canon/holdout",
            {"chapters": [{"chapter": 5, "content": "正史第五章。"}]},
        )
        assert status == 200
        assert body["available_chapters"] == [5]
        status, _b = _post(
            port,
            f"/api/stories/{slug}/canon/holdout",
            {"chapters": [{"chapter": 5, "content": "重复。"}]},
        )
        assert status == 409

    def test_holdout_builtin_readonly_400(self, running_server):
        port, _, _ = running_server
        status, _b = _post(
            port,
            f"/api/stories/{BUILTIN_SLUG}/canon/holdout",
            {"chapters": [{"chapter": 5, "content": "x"}]},
        )
        assert status == 400

    def test_replay_full_flow(self, running_server):
        port, _, _ = running_server
        slug = _seed_project(port)
        _post(
            port,
            f"/api/stories/{slug}/canon/holdout",
            {"chapters": [{"chapter": 5, "content": "林晚舟在听雨轩揭开封印之谜。"}]},
        )
        _, base = _post(
            port, f"/api/stories/{slug}/baseline", {"rounds": 2, "mock": True}
        )
        run_id = base["run_id"]
        status, report = _post(
            port,
            f"/api/stories/{slug}/canon/replay",
            {"baseline_run_id": run_id, "holdout_chapter": 5},
        )
        assert status == 200
        assert report["kind"] == "canon_replay"
        status, fetched = _get(port, f"/api/runs/{run_id}/canon-replay")
        assert status == 200
        assert fetched["baseline_run_id"] == run_id

    def test_replay_missing_baseline_404(self, running_server):
        port, _, _ = running_server
        slug = _seed_project(port)
        _post(
            port,
            f"/api/stories/{slug}/canon/holdout",
            {"chapters": [{"chapter": 5, "content": "内容。"}]},
        )
        status, _b = _post(
            port,
            f"/api/stories/{slug}/canon/replay",
            {"baseline_run_id": "run_nope", "holdout_chapter": 5},
        )
        assert status == 404

    def test_replay_get_missing_404(self, running_server):
        port, _, _ = running_server
        status, _b = _get(port, "/api/runs/run_nope/canon-replay")
        assert status == 404

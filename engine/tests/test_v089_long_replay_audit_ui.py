"""v0.8.9 Long Replay & Audit UI: range replay and audit workspace APIs."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import indexer, server
from living_novel_engine.service import (
    generate_baseline,
    import_novel_from_payload,
    run_canon_replay_range,
    write_holdout,
)


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i:03d}.md",
            "content": (
                f"第{i}章 回放审计\n"
                f"赵轩与沈冰月在第 {i} 章追查风鸣铃，归云斋暗线逐渐浮出水面。"
            ),
        }
        for i in range(1, n + 1)
    ]


def _make_project(projects, slug: str = "replay-audit-story") -> str:
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(6),
        mock=True,
        long_mode=True,
        projects_dir=projects,
    )
    write_holdout(
        slug,
        chapters=[
            {
                "chapter": 7,
                "title": "第七章 风鸣",
                "content": "赵轩与沈冰月在归云斋核对风鸣铃，旧案证据浮现。",
            },
            {
                "chapter": 8,
                "title": "第八章 暗线",
                "content": "沈冰月追问归云斋暗线，赵轩发现风鸣铃另有回响。",
            },
        ],
        projects_dir=projects,
    )
    return slug


@pytest.fixture
def isolated_dirs(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    projects.mkdir()
    outputs.mkdir()
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    return projects, outputs


def test_replay_range_writes_summary_and_entity_audit(isolated_dirs):
    projects, outputs = isolated_dirs
    slug = _make_project(projects)
    baseline = generate_baseline(story_slug=slug, rounds=2, mock=True)

    report = run_canon_replay_range(
        story_slug=slug,
        baseline_run_id=baseline.run_id,
        baseline_branch_id="baseline",
        chapter_start=7,
        chapter_end=8,
        projects_dir=projects,
        outputs_dir=outputs,
    )

    assert report["version"] == "v0.8.9"
    assert report["kind"] == "canon_replay_range"
    assert report["chapter_range"] == {"start": 7, "end": 8}
    assert [r["holdout_chapter"] for r in report["reports"]] == [7, 8]
    assert 0.0 <= report["summary"]["average_overall"] <= 1.0
    assert report["summary"]["risk_level"] in {"low", "medium", "high"}
    assert report["risk_dimensions"]
    assert "missing_entities_by_chapter" in report["entity_audit"]
    assert (outputs / baseline.run_id / "canon_replay_range_report.json").exists()


def test_replay_audit_workspace_collects_holdout_audit_aliases_and_range(
    isolated_dirs, monkeypatch
):
    projects, outputs = isolated_dirs
    slug = _make_project(projects)
    baseline = generate_baseline(story_slug=slug, rounds=2, mock=True)
    run_canon_replay_range(
        story_slug=slug,
        baseline_run_id=baseline.run_id,
        chapter_start=7,
        chapter_end=8,
        projects_dir=projects,
        outputs_dir=outputs,
    )
    monkeypatch.setattr(indexer, "projects_dir", lambda: projects)
    monkeypatch.setattr(indexer, "outputs_dir", lambda: outputs)

    workspace = indexer.get_replay_audit_workspace(slug)

    assert workspace["slug"] == slug
    assert workspace["holdout"]["available_chapters"] == [7, 8]
    assert workspace["baseline_runs"][0]["run_id"] == baseline.run_id
    assert workspace["audit"]["status"] == "ready"
    assert workspace["audit"]["dimensions"]
    assert workspace["entity_aliases"]["status"] == "ready"
    assert workspace["replay_ranges"][0]["summary"]["chapter_count"] == 2


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


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


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    projects.mkdir()
    outputs.mkdir()
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port, projects, outputs
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_http_replay_audit_workspace_and_range_statuses(running_server):
    port, projects, _ = running_server
    slug = _make_project(projects, "http-replay-audit")
    _, baseline = _post(
        port, f"/api/stories/{slug}/baseline", {"rounds": 2, "mock": True}
    )

    status, workspace = _get(port, f"/api/stories/{slug}/replay-audit")
    assert status == 200
    assert workspace["holdout"]["available_chapters"] == [7, 8]

    status, report = _post(
        port,
        f"/api/stories/{slug}/canon/replay-range",
        {
            "baseline_run_id": baseline["run_id"],
            "baseline_branch_id": "baseline",
            "chapter_start": 7,
            "chapter_end": 8,
        },
    )
    assert status == 200
    assert report["summary"]["chapter_count"] == 2

    bad_status, bad = _get(port, "/api/stories/..%2Fsecret/replay-audit")
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    missing_status, missing = _post(
        port,
        f"/api/stories/{slug}/canon/replay-range",
        {"baseline_run_id": "run_nope", "chapter_start": 7, "chapter_end": 8},
    )
    assert missing_status == 404
    assert "baseline" in missing["error"]

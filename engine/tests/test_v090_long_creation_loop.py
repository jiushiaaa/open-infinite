"""v0.9.0-alpha Long Novel Creation Loop: selected chapter export."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server


def _chapter_export_api():
    try:
        from living_novel_engine.service import (
            ChapterExportRequestError,
            build_chapter_export,
        )
    except ImportError as exc:  # pragma: no cover - red phase assertion
        pytest.fail(f"缺少章节导出服务: {exc}")
    return ChapterExportRequestError, build_chapter_export


def _write_branch(outputs, run_id: str = "run_v090_export", branch_id: str = "branch_a"):
    run_dir = outputs / run_id
    branch_dir = run_dir / branch_id
    branch_dir.mkdir(parents=True)
    (run_dir / "intervention.json").write_text(
        json.dumps(
            {
                "story_slug": "export-story",
                "source_kind": "imported",
                "target": "zhao_xuan",
                "content": "让赵轩提前核对风鸣铃线索",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "intervention_compilation.json").write_text(
        json.dumps(
            {
                "branch_axis": [
                    {
                        "branch_id": "branch_a",
                        "label": "提前查证",
                        "description": "赵轩提前核对风鸣铃线索。",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (branch_dir / "events.json").write_text(
        json.dumps({"theme": "提前查证"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (branch_dir / "state_snapshot.json").write_text(
        json.dumps({"characters": {"zhao_xuan": {"name": "赵轩"}}}, ensure_ascii=False),
        encoding="utf-8",
    )
    (branch_dir / "chapter.md").write_text(
        "# 第七章 风鸣旧案\n\n赵轩在归云斋前停步，先取出风鸣铃核对旧案线索。",
        encoding="utf-8",
    )
    (branch_dir / "worldline_judgement.json").write_text(
        json.dumps(
            {
                "recommendation": "推荐继续",
                "scores": {"overall": 0.82},
                "warnings": ["伏笔仍需后续兑现"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return run_id, branch_id


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


@pytest.fixture
def isolated_dirs(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
    return outputs


@pytest.fixture
def running_server(isolated_dirs):
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port, isolated_dirs
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_chapter_export_contains_source_ai_notice_and_judgement(isolated_dirs):
    _, build_chapter_export = _chapter_export_api()
    run_id, branch_id = _write_branch(isolated_dirs)

    export = build_chapter_export(
        run_id=run_id,
        branch_id=branch_id,
        outputs_dir=isolated_dirs,
    )

    assert export["version"] == "v0.9.0-alpha"
    assert export["kind"] == "chapter_export"
    assert export["story_slug"] == "export-story"
    assert export["filename"].endswith(".md")
    assert export["metadata"]["source_kind"] == "imported"
    assert export["metadata"]["branch_label"] == "提前查证"
    assert export["metadata"]["judgement_recommendation"] == "推荐继续"
    assert "AI 生成说明" in export["content_md"]
    assert "来源说明" in export["content_md"]
    assert "赵轩在归云斋前停步" in export["content_md"]


def test_chapter_export_rejects_bad_id_and_missing_chapter(isolated_dirs):
    ChapterExportRequestError, build_chapter_export = _chapter_export_api()

    with pytest.raises(ChapterExportRequestError):
        build_chapter_export(
            run_id="../outside",
            branch_id="branch_a",
            outputs_dir=isolated_dirs,
        )

    with pytest.raises(FileNotFoundError):
        build_chapter_export(
            run_id="run_missing",
            branch_id="branch_a",
            outputs_dir=isolated_dirs,
        )


def test_http_chapter_export_statuses(running_server):
    port, outputs = running_server
    run_id, branch_id = _write_branch(outputs)

    status, body = _get(port, f"/api/runs/{run_id}/branches/{branch_id}/chapter-export")
    assert status == 200
    assert body["kind"] == "chapter_export"
    assert "导出章节" in body["content_md"]

    bad_status, bad = _get(port, "/api/runs/..%2Foutside/branches/branch_a/chapter-export")
    assert bad_status == 400
    assert bad["error"] == "invalid run_id or branch_id"

    missing_status, missing = _get(
        port,
        "/api/runs/run_missing/branches/branch_a/chapter-export",
    )
    assert missing_status == 404
    assert "章节不存在" in missing["error"]

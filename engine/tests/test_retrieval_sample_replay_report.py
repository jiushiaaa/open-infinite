"""Retrieval Sample Replay Report MVP：失败样本复跑 case report。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml
from click.testing import CliRunner

from living_novel_engine.browser import server
from living_novel_engine.cli import main
from living_novel_engine.service import get_retrieval_sample_replay_report


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _make_project(
    projects: Path,
    slug: str = "replay-report-story",
    *,
    with_sample: bool = True,
) -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": "Replay 报告测试世界"})
    _write_yaml(project / "characters.yaml", {"characters": []})
    _write_jsonl(
        project / "memory" / "canon_ledger.jsonl",
        [
            {
                "id": "canon_000001",
                "type": "event",
                "chapter": 2,
                "scene": 1,
                "entities": ["mo_qing_yan", "retreat_bell"],
                "statement": "墨青烟确认退魂铃曾在听雨轩响过。",
                "truth_status": "canon",
                "source_ref": "source/chapter_002.md",
                "confidence": 0.92,
            }
        ],
    )
    _write_yaml(
        project / "memory" / "entity_aliases.yaml",
        {
            "version": "v0.8.x",
            "story_slug": slug,
            "entities": [
                {
                    "entity_id": "mo_qing_yan",
                    "canonical_name": "墨青烟",
                    "entity_type": "character",
                    "aliases": ["墨青烟", "墨姑娘"],
                },
                {
                    "entity_id": "retreat_bell",
                    "canonical_name": "退魂铃",
                    "entity_type": "item",
                    "aliases": ["退魂铃", "摄魂铃"],
                },
            ],
        },
    )
    if with_sample:
        _write_jsonl(
            project / "memory" / "retrieval_failure_samples.jsonl",
            [
                {
                    "id": "sample-001",
                    "created_at": "2026-06-01T19:00:00",
                    "query": "她必须追查那个遗失的关键物证",
                    "expected_entities": ["mo_qing_yan", "retreat_bell"],
                    "reason": "换说法后 BM25 未命中正史账本",
                    "current_chapter": 2,
                }
            ],
        )
    return project


def test_retrieval_sample_replay_report_tracks_current_case_status(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    _make_project(projects)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = get_retrieval_sample_replay_report(
        "replay-report-story",
        projects_dir=projects,
        now=datetime(2026, 6, 1, 19, 30, 0),
    )
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "retrieval-sample-replay-report-mvp"
    assert report["mode"] == "read_only_retrieval_sample_replay_report"
    assert report["status"] == "ready"
    assert report["summary"]["case_count"] == 1
    assert report["summary"]["still_failing_lexically_count"] == 1
    assert report["summary"]["invalid_case_count"] == 0
    assert report["replay_gate"]["passed"] is True
    assert report["cases"][0]["replay_status"] == "still_failing_lexically"
    assert report["cases"][0]["target_item_id"] == "canon_ledger:canon_000001"
    assert "仍是词面缺口" in report["report_md"]
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_retrieval_sample_replay_report_empty_needs_samples(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects, "replay-report-empty", with_sample=False)

    report = get_retrieval_sample_replay_report("replay-report-empty", projects_dir=projects)

    assert report["status"] == "empty"
    assert report["summary"]["case_count"] == 0
    assert report["replay_gate"]["passed"] is False
    assert report["replay_gate"]["status"] == "needs_samples"
    assert "暂无失败样本" in report["report_md"]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _request(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_retrieval_sample_replay_report_http_statuses(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    _make_project(projects)
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "outputs"))
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_MOCK", "1")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _request(
            port,
            "/api/stories/replay-report-story/retrieval-sample-replay-report",
        )
        bad_status, bad = _request(
            port,
            "/api/stories/..%2Fbad/retrieval-sample-replay-report",
        )
        missing_status, missing = _request(
            port,
            "/api/stories/missing-story/retrieval-sample-replay-report",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "ready"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404
    assert "error" in missing


def test_memory_cli_replay_report_requires_clean(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects, "replay-report-cli")
    env = {
        "LNE_PROJECTS_DIR": str(projects),
        "LNE_OUTPUTS_DIR": str(tmp_path / "outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "replay-report", "replay-report-cli", "--json", "--require-clean"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["replay_gate"]["passed"] is True
    assert body["summary"]["still_failing_lexically_count"] == 1

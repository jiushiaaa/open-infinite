"""Embedding Mock Evaluation Report MVP：失败样本批量对照报告。"""

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
from living_novel_engine.service import get_embedding_mock_evaluation_report


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
    slug: str = "mock-report-story",
    *,
    with_sample: bool = True,
) -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": "Mock 报告测试世界"})
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
                    "created_at": "2026-06-01T18:10:00",
                    "query": "她必须追查那个遗失的关键物证",
                    "expected_entities": ["mo_qing_yan", "retreat_bell"],
                    "reason": "换说法后 BM25 未命中正史账本",
                    "current_chapter": 2,
                }
            ],
        )
    return project


def test_embedding_mock_evaluation_report_marks_candidate(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    _make_project(projects)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = get_embedding_mock_evaluation_report(
        "mock-report-story",
        projects_dir=projects,
        now=datetime(2026, 6, 1, 18, 30, 0),
    )
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "embedding-mock-evaluation-report-mvp"
    assert report["mode"] == "read_only_embedding_mock_evaluation_report"
    assert report["status"] == "candidate"
    assert report["summary"]["sample_count"] == 1
    assert report["summary"]["lexical_gap_count"] == 1
    assert report["gate"]["passed"] is True
    assert report["gate"]["status"] == "candidate"
    assert report["buckets"]["lexical_gap"][0]["target_item_id"] == "canon_ledger:canon_000001"
    assert "她必须追查那个遗失的关键物证" in report["report_md"]
    assert "mock embedding 值得进入下一步评估" in report["report_md"]
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_embedding_mock_evaluation_report_empty_needs_samples(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects, "mock-report-empty", with_sample=False)

    report = get_embedding_mock_evaluation_report("mock-report-empty", projects_dir=projects)

    assert report["status"] == "empty"
    assert report["gate"]["passed"] is False
    assert report["gate"]["status"] == "needs_samples"
    assert report["summary"]["writes_artifacts"] is False
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


def test_embedding_mock_evaluation_report_http_statuses(tmp_path, monkeypatch):
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
            "/api/stories/mock-report-story/embedding-mock-evaluation-report",
        )
        bad_status, bad = _request(
            port,
            "/api/stories/..%2Fbad/embedding-mock-evaluation-report",
        )
        missing_status, missing = _request(
            port,
            "/api/stories/missing-story/embedding-mock-evaluation-report",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "candidate"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404
    assert "error" in missing


def test_memory_cli_mock_report_requires_candidate(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects, "mock-report-cli")
    env = {
        "LNE_PROJECTS_DIR": str(projects),
        "LNE_OUTPUTS_DIR": str(tmp_path / "outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "mock-report", "mock-report-cli", "--json", "--require-candidate"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["gate"]["passed"] is True
    assert body["summary"]["lexical_gap_count"] == 1

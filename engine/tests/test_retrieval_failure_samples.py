"""Retrieval Failure Sample Authoring MVP：本地失败样本追加。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from living_novel_engine.browser import server
from living_novel_engine.service import (
    RetrievalFailureSampleConflictError,
    RetrievalFailureSampleRequestError,
    add_retrieval_failure_sample,
    get_embedding_evaluation_samples,
    get_retrieval_failure_samples,
)


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _make_project(projects: Path, slug: str = "sample-story") -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": "样本测试世界"})
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
    return project


def test_add_retrieval_failure_sample_appends_normalized_jsonl(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    project = _make_project(projects)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = add_retrieval_failure_sample(
        "sample-story",
        {
            "query": "她必须追查那个遗失的关键物证",
            "expected_entities": "mo_qing_yan, retreat_bell",
            "reason": "换说法后 BM25 未命中正史账本",
            "current_chapter": 2,
            "actual_top_sources": ["runtime_memory", "chapter_brief"],
        },
        projects_dir=projects,
        now=datetime(2026, 6, 1, 16, 0, 0),
    )
    listing = get_retrieval_failure_samples("sample-story", projects_dir=projects)
    eval_report = get_embedding_evaluation_samples("sample-story", projects_dir=projects)
    text = json.dumps(report, ensure_ascii=False) + json.dumps(listing, ensure_ascii=False)

    assert report["status"] == "appended"
    assert report["sample"]["query"] == "她必须追查那个遗失的关键物证"
    assert report["sample"]["expected_entities"] == ["mo_qing_yan", "retreat_bell"]
    assert report["sample"]["expected_source"] == "canon_ledger"
    assert report["sample"]["created_at"] == "2026-06-01T16:00:00"
    assert listing["summary"]["sample_count"] == 1
    assert eval_report["summary"]["sample_count"] == 1
    assert (project / "memory" / "retrieval_failure_samples.jsonl").exists()
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_add_retrieval_failure_sample_rejects_secret_text(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects)

    with pytest.raises(RetrievalFailureSampleRequestError):
        add_retrieval_failure_sample(
            "sample-story",
            {
                "query": "sk-real-secret-7788",
                "expected_entities": ["mo_qing_yan"],
            },
            projects_dir=projects,
        )


def test_add_retrieval_failure_sample_rejects_builtin_sample(tmp_path):
    with pytest.raises(RetrievalFailureSampleConflictError):
        add_retrieval_failure_sample(
            "tianhuang-night",
            {
                "query": "样例不应写入",
                "expected_entities": ["sample_entity"],
            },
            projects_dir=tmp_path / "projects",
        )


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
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
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def _request(port: int, method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_retrieval_failure_sample_http_get_and_append(running_server):
    status, body = _request(
        running_server,
        "GET",
        "/api/stories/sample-story/retrieval-failure-samples",
    )
    assert status == 200
    assert body["status"] == "missing"

    status, body = _request(
        running_server,
        "POST",
        "/api/stories/sample-story/retrieval-failure-samples",
        {
            "query": "她必须追查那个遗失的关键物证",
            "expected_entities": ["mo_qing_yan", "retreat_bell"],
            "reason": "换说法后 BM25 未命中正史账本",
        },
    )
    assert status == 200
    assert body["status"] == "appended"
    assert body["sample"]["expected_entities"] == ["mo_qing_yan", "retreat_bell"]

    status, body = _request(
        running_server,
        "GET",
        "/api/stories/sample-story/retrieval-failure-samples",
    )
    assert status == 200
    assert body["summary"]["sample_count"] == 1


def test_retrieval_failure_sample_http_error_statuses(running_server):
    bad_status, bad = _request(
        running_server,
        "GET",
        "/api/stories/..%2Fbad/retrieval-failure-samples",
    )
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    invalid_status, invalid = _request(
        running_server,
        "POST",
        "/api/stories/sample-story/retrieval-failure-samples",
        {"query": "", "expected_entities": []},
    )
    assert invalid_status == 400
    assert "error" in invalid

    missing_status, missing = _request(
        running_server,
        "GET",
        "/api/stories/missing-story/retrieval-failure-samples",
    )
    assert missing_status == 404
    assert "error" in missing

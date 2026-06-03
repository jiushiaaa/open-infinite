"""Embedding Evaluation Samples MVP: mockable retrieval failure evaluation."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest
import yaml

from living_novel_engine.browser import server
from living_novel_engine.service import get_embedding_evaluation_samples


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_project(
    tmp_path: Path,
    slug: str,
    *,
    with_sample: bool = True,
) -> Path:
    project = tmp_path / slug
    memory = project / "memory"
    memory.mkdir(parents=True)
    (project / "world.yaml").write_text("name: 听雨轩\n", encoding="utf-8")
    (project / "story_contract.yaml").write_text("world_rules: []\n", encoding="utf-8")
    _write_json(
        project / "import_report.json",
        {"total_chapters": 12, "total_characters": 120_000},
    )
    ledger = {
        "id": "canon_000001",
        "type": "resource",
        "chapter": 2,
        "scene": 1,
        "entities": ["mo_qing_yan", "retreat_bell"],
        "statement": "墨青烟确认退魂铃曾在听雨轩响过。",
        "truth_status": "canon",
        "source_ref": "source/chapter_002.md",
        "confidence": 0.92,
    }
    (memory / "canon_ledger.jsonl").write_text(
        json.dumps(ledger, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (memory / "entity_aliases.yaml").write_text(
        yaml.safe_dump(
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
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    if with_sample:
        sample = {
            "query": "她必须追查那个遗失的关键物证",
            "expected_entities": ["mo_qing_yan", "retreat_bell"],
            "reason": "换说法后 BM25 未命中正史账本",
            "current_chapter": 2,
        }
        (memory / "retrieval_failure_samples.jsonl").write_text(
            json.dumps(sample, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return project


def test_embedding_evaluation_samples_reports_insufficient_samples(tmp_path):
    _make_project(tmp_path, "embed-empty", with_sample=False)

    report = get_embedding_evaluation_samples("embed-empty", projects_dir=tmp_path)

    assert report["version"] == "embedding-evaluation-samples-mvp"
    assert report["mode"] == "read_only_embedding_evaluation_samples"
    assert report["status"] == "insufficient_samples"
    assert report["summary"]["sample_count"] == 0
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["uses_embedding_provider"] is False
    assert report["summary"]["uses_vector_store"] is False
    assert any("先收集" in step for step in report["next_steps"])


def test_embedding_evaluation_samples_marks_lexical_gap_as_candidate(tmp_path):
    _make_project(tmp_path, "embed-candidate", with_sample=True)

    report = get_embedding_evaluation_samples("embed-candidate", projects_dir=tmp_path)

    assert report["status"] == "candidate"
    assert report["summary"]["sample_count"] == 1
    assert report["summary"]["bm25_hit_count"] == 0
    assert report["summary"]["mock_embedding_hit_count"] == 1
    assert report["summary"]["lexical_gap_count"] == 1
    sample = report["samples"][0]
    assert sample["query"] == "她必须追查那个遗失的关键物证"
    assert sample["bm25_hit"] is False
    assert sample["mock_embedding_hit"] is True
    assert sample["diagnosis"] == "lexical_gap"
    assert sample["target_item_id"] == "canon_ledger:canon_000001"
    assert any("mock embedding 对照" in step for step in report["next_steps"])


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "embed-http", with_sample=True)
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
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_embedding_evaluation_samples_http_statuses(running_server):
    status, body = _get(running_server, "/api/stories/embed-http/embedding-evaluation-samples")
    assert status == 200
    assert body["status"] == "candidate"

    bad_status, bad = _get(running_server, "/api/stories/..%2Fbad/embedding-evaluation-samples")
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    missing_status, _missing = _get(running_server, "/api/stories/ghost/embedding-evaluation-samples")
    assert missing_status == 404

"""Embedding / Vector Retrieval Readiness Probe: read-only trigger report."""

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
from living_novel_engine.service import get_vector_retrieval_readiness


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _make_project(
    tmp_path: Path,
    slug: str,
    *,
    chapters: int = 12,
    characters: int = 120_000,
    saved_failure: bool = False,
) -> Path:
    project = tmp_path / slug
    memory = project / "memory"
    memory.mkdir(parents=True)
    (project / "world.yaml").write_text("name: 听雨轩\n", encoding="utf-8")
    (project / "story_contract.yaml").write_text(
        "world_rules:\n  - 禁止让角色突然知道未曾获得的幕后真相\n",
        encoding="utf-8",
    )
    _write_json(
        project / "import_report.json",
        {
            "total_chapters": chapters,
            "total_characters": characters,
            "chapters": [{"index": i} for i in range(1, chapters + 1)],
        },
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
        "valid_from": 2,
        "valid_until": None,
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
                        "source_refs": ["characters.yaml"],
                    },
                    {
                        "entity_id": "retreat_bell",
                        "canonical_name": "退魂铃",
                        "entity_type": "item",
                        "aliases": ["退魂铃", "摄魂铃"],
                        "source_refs": ["memory/canon_ledger.jsonl"],
                    },
                ],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    if saved_failure:
        failure = {
            "query": "女主曾听见的那件会暴露旧案的法器",
            "expected_entities": ["mo_qing_yan", "retreat_bell"],
            "actual_top_sources": ["chapter_brief", "contract"],
            "reason": "换说法后 BM25 未命中正史账本",
        }
        (memory / "retrieval_failure_samples.jsonl").write_text(
            json.dumps(failure, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return project


def test_vector_retrieval_readiness_monitors_large_project_without_external_services(tmp_path):
    _make_project(tmp_path, "vector-large", chapters=55, characters=1_200_000)

    report = get_vector_retrieval_readiness("vector-large", projects_dir=tmp_path)

    assert report["version"] == "embedding-vector-readiness-probe-mvp"
    assert report["mode"] == "read_only_vector_retrieval_readiness"
    assert report["status"] == "monitor"
    assert report["summary"]["chapter_count"] == 55
    assert report["summary"]["character_count"] == 1_200_000
    assert report["summary"]["retrieval_probe_hit_rate"] == 1.0
    assert report["summary"]["saved_failure_sample_count"] == 0
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["uses_embedding"] is False
    assert report["summary"]["uses_vector_store"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert any(layer["id"] == "embedding" for layer in report["candidate_layers"])
    assert any("继续使用当前 BM25" in step for step in report["next_steps"])


def test_vector_retrieval_readiness_triggers_on_saved_bm25_failure_samples(tmp_path):
    _make_project(tmp_path, "vector-failure", saved_failure=True)

    report = get_vector_retrieval_readiness("vector-failure", projects_dir=tmp_path)

    assert report["status"] == "triggered"
    assert report["summary"]["saved_failure_sample_count"] == 1
    assert report["summary"]["retrieval_probe_hit_rate"] == 1.0
    assert report["failure_samples"][0]["query"] == "女主曾听见的那件会暴露旧案的法器"
    failure_signal = next(signal for signal in report["signals"] if signal["id"] == "saved_failure_samples")
    assert failure_signal["status"] == "attention"
    assert any("embedding / 向量库 spike" in step for step in report["next_steps"])
    assert any("不直接接生产向量库" in boundary for boundary in report["boundaries"])


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
    _make_project(tmp_path, "vector-http", saved_failure=True)
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


def test_vector_retrieval_readiness_http_statuses(running_server):
    status, body = _get(running_server, "/api/stories/vector-http/vector-retrieval-readiness")
    assert status == 200
    assert body["status"] == "triggered"

    bad_status, bad = _get(running_server, "/api/stories/..%2Fbad/vector-retrieval-readiness")
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    missing_status, _missing = _get(running_server, "/api/stories/ghost/vector-retrieval-readiness")
    assert missing_status == 404

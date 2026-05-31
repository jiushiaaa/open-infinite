"""v0.9.3 Retrieval Probe-B: evaluate current file memory retrieval first."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest
import yaml

from living_novel_engine.browser import server
from living_novel_engine.service import evaluate_retrieval_probes


def _make_project(tmp_path, slug: str, *, with_memory: bool = True):
    project = tmp_path / slug
    memory = project / "memory"
    memory.mkdir(parents=True)
    (project / "world.yaml").write_text("name: 听雨轩\n", encoding="utf-8")
    (project / "story_contract.yaml").write_text("world_rules: []\n", encoding="utf-8")
    if not with_memory:
        return project

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
    return project


def test_retrieval_probe_passes_alias_and_canon_ledger_sample(tmp_path):
    _make_project(tmp_path, "probe-story")

    report = evaluate_retrieval_probes("probe-story", projects_dir=tmp_path)

    assert report["version"] == "v0.9.3"
    assert report["status"] == "pass"
    assert report["metrics"]["sample_count"] == 1
    assert report["metrics"]["hit_count"] == 1
    assert report["failure_samples"] == []
    probe = report["probes"][0]
    assert probe["query"] == "墨姑娘 摄魂铃"
    assert probe["hit"] is True
    assert probe["top_item"]["source"] == "canon_ledger"
    assert probe["top_item"]["id"] == "canon_ledger:canon_000001"
    assert probe["expected_entities"] == ["mo_qing_yan", "retreat_bell"]


def test_retrieval_probe_reports_insufficient_samples(tmp_path):
    _make_project(tmp_path, "probe-empty", with_memory=False)

    report = evaluate_retrieval_probes("probe-empty", projects_dir=tmp_path)

    assert report["status"] == "insufficient_samples"
    assert report["metrics"]["sample_count"] == 0
    assert report["probes"] == []
    assert report["failure_samples"] == []
    assert any("代表性查询样本不足" in item for item in report["recommendations"])


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "probe-http")
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
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def test_retrieval_probe_http_statuses(running_server):
    port = running_server

    status, body = _get(port, "/api/stories/probe-http/retrieval-probes")
    assert status == 200
    assert body["status"] == "pass"

    bad_status, bad = _get(port, "/api/stories/..%2Fx/retrieval-probes")
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    missing_status, _missing = _get(port, "/api/stories/ghost/retrieval-probes")
    assert missing_status == 404

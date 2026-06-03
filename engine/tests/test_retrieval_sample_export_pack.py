"""Retrieval Sample Export Pack MVP：失败样本只读导出包。"""

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
from living_novel_engine.service import get_retrieval_sample_export_pack


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
    slug: str = "export-pack-story",
    *,
    with_sample: bool = True,
) -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": "导出包测试世界"})
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
                    "created_at": "2026-06-01T16:30:00",
                    "query": "她必须追查那个遗失的关键物证",
                    "expected_entities": ["mo_qing_yan", "retreat_bell"],
                    "reason": "换说法后 BM25 未命中正史账本",
                    "current_chapter": 2,
                }
            ],
        )
    return project


def test_retrieval_sample_export_pack_ready_markdown_and_manifest(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    _make_project(projects)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = get_retrieval_sample_export_pack(
        "export-pack-story",
        projects_dir=projects,
        now=datetime(2026, 6, 1, 17, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "retrieval-sample-export-pack-mvp"
    assert report["mode"] == "read_only_retrieval_sample_export_pack"
    assert report["status"] == "ready"
    assert report["filename"] == "export-pack-story-retrieval-samples.md"
    assert report["content_type"] == "text/markdown; charset=utf-8"
    assert report["summary"]["sample_count"] == 1
    assert report["summary"]["lexical_gap_count"] == 1
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["uses_embedding_provider"] is False
    assert report["summary"]["uses_vector_store"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["manifest"]["generated_at"] == "2026-06-01T17:00:00"
    assert report["manifest"]["samples"][0]["diagnosis"] == "lexical_gap"
    assert "她必须追查那个遗失的关键物证" in report["content_md"]
    assert "canon_ledger:canon_000001" in report["content_md"]
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_retrieval_sample_export_pack_empty_is_read_only(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects, "export-pack-empty", with_sample=False)

    report = get_retrieval_sample_export_pack("export-pack-empty", projects_dir=projects)

    assert report["status"] == "empty"
    assert report["summary"]["sample_count"] == 0
    assert report["summary"]["writes_artifacts"] is False
    assert "暂无失败样本" in report["content_md"]
    assert any("先记录" in step for step in report["next_steps"])


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


def test_retrieval_sample_export_pack_http_statuses(tmp_path, monkeypatch):
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
            "/api/stories/export-pack-story/retrieval-sample-export-pack",
        )
        bad_status, bad = _request(
            port,
            "/api/stories/..%2Fbad/retrieval-sample-export-pack",
        )
        missing_status, missing = _request(
            port,
            "/api/stories/missing-story/retrieval-sample-export-pack",
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


def test_memory_cli_export_samples_outputs_json(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects, "export-pack-cli")
    env = {
        "LNE_PROJECTS_DIR": str(projects),
        "LNE_OUTPUTS_DIR": str(tmp_path / "outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "export-samples", "export-pack-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["status"] == "ready"
    assert body["manifest"]["samples"][0]["diagnosis"] == "lexical_gap"
    assert "她必须追查那个遗失的关键物证" in body["content_md"]

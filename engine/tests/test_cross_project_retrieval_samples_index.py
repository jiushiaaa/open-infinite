"""Cross Project Retrieval Samples Index MVP：跨项目失败样本索引。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml
from click.testing import CliRunner

from living_novel_engine.browser import server
from living_novel_engine.cli import main
from living_novel_engine.service import get_cross_project_retrieval_samples_index


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _make_project(projects: Path, slug: str, *, with_sample: bool) -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": f"{slug} 测试世界"})
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
                    "created_at": "2026-06-01T23:00:00",
                    "query": "她必须追查那个遗失的关键物证",
                    "expected_entities": ["mo_qing_yan", "retreat_bell"],
                    "reason": "换说法后 BM25 未命中正史账本",
                    "current_chapter": 2,
                }
            ],
        )
    return project


def test_cross_project_retrieval_samples_index_summarizes_migration_packs(
    tmp_path, monkeypatch
):
    projects = tmp_path / "projects"
    _make_project(projects, "index-pack-a", with_sample=True)
    _make_project(projects, "index-pack-b", with_sample=False)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = get_cross_project_retrieval_samples_index(
        projects_dir=projects,
        now=datetime(2026, 6, 1, 23, 30, 0),
    )
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "cross-project-retrieval-samples-index-mvp"
    assert report["mode"] == "read_only_cross_project_retrieval_samples_index"
    assert report["status"] == "ready"
    assert report["summary"]["project_count"] == 2
    assert report["summary"]["ready_project_count"] == 1
    assert report["summary"]["empty_project_count"] == 1
    assert report["summary"]["record_count"] == 1
    assert report["projects"][0]["story_slug"] == "index-pack-a"
    assert report["projects"][0]["migration_gate_status"] == "ready"
    assert report["records"][0]["eval_id"] == "index-pack-a-retrieval-eval-001"
    assert "index-pack-a-retrieval-eval-001" in report["content_json"]
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_cross_project_retrieval_samples_index_empty_projects(tmp_path):
    report = get_cross_project_retrieval_samples_index(projects_dir=tmp_path / "projects")

    assert report["status"] == "empty"
    assert report["summary"]["project_count"] == 0
    assert report["summary"]["record_count"] == 0
    assert report["index_gate"]["passed"] is False
    assert report["index_gate"]["status"] == "needs_projects"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_cross_project_retrieval_samples_index_http(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    _make_project(projects, "index-pack-api", with_sample=True)
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
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/settings/retrieval-samples-index",
            timeout=10,
        ) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert body["status"] == "ready"
    assert body["summary"]["record_count"] == 1


def test_memory_cli_index_samples_json(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects, "index-pack-cli", with_sample=True)
    env = {
        "LNE_PROJECTS_DIR": str(projects),
        "LNE_OUTPUTS_DIR": str(tmp_path / "outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "index-samples", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["index_gate"]["passed"] is True
    assert body["summary"]["record_count"] == 1

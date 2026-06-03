"""Retrieval Sample Migration Pack MVP：失败样本迁移评测集包。"""

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
from living_novel_engine.service import get_retrieval_sample_migration_pack


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
    slug: str = "migration-pack-story",
    *,
    with_sample: bool = True,
) -> Path:
    project = projects / slug
    _write_yaml(project / "world.yaml", {"display_name": "迁移包测试世界"})
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
                    "created_at": "2026-06-01T21:00:00",
                    "query": "她必须追查那个遗失的关键物证",
                    "expected_entities": ["mo_qing_yan", "retreat_bell"],
                    "reason": "换说法后 BM25 未命中正史账本",
                    "current_chapter": 2,
                }
            ],
        )
    return project


def test_retrieval_sample_migration_pack_builds_stable_records(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    _make_project(projects)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    pack = get_retrieval_sample_migration_pack(
        "migration-pack-story",
        projects_dir=projects,
        now=datetime(2026, 6, 1, 21, 30, 0),
    )
    text = json.dumps(pack, ensure_ascii=False)

    assert pack["version"] == "retrieval-sample-migration-pack-mvp"
    assert pack["mode"] == "read_only_retrieval_sample_migration_pack"
    assert pack["status"] == "ready"
    assert pack["filename"] == "migration-pack-story-retrieval-migration-pack.json"
    assert pack["summary"]["record_count"] == 1
    assert pack["summary"]["migratable_count"] == 1
    assert pack["summary"]["skipped_count"] == 0
    assert pack["migration_gate"]["passed"] is True
    assert pack["records"][0]["eval_id"] == "migration-pack-story-retrieval-eval-001"
    assert pack["records"][0]["expected_item_id"] == "canon_ledger:canon_000001"
    assert pack["records"][0]["assertions"]["must_retrieve_item_id"] == "canon_ledger:canon_000001"
    assert "migration-pack-story-retrieval-eval-001" in pack["content_json"]
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_retrieval_sample_migration_pack_empty_needs_samples(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects, "migration-pack-empty", with_sample=False)

    pack = get_retrieval_sample_migration_pack("migration-pack-empty", projects_dir=projects)

    assert pack["status"] == "empty"
    assert pack["summary"]["record_count"] == 0
    assert pack["migration_gate"]["passed"] is False
    assert pack["migration_gate"]["status"] == "needs_samples"
    assert "records" in pack["manifest"]


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


def test_retrieval_sample_migration_pack_http_statuses(tmp_path, monkeypatch):
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
            "/api/stories/migration-pack-story/retrieval-sample-migration-pack",
        )
        bad_status, bad = _request(
            port,
            "/api/stories/..%2Fbad/retrieval-sample-migration-pack",
        )
        missing_status, missing = _request(
            port,
            "/api/stories/missing-story/retrieval-sample-migration-pack",
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


def test_memory_cli_migration_pack_json(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects, "migration-pack-cli")
    env = {
        "LNE_PROJECTS_DIR": str(projects),
        "LNE_OUTPUTS_DIR": str(tmp_path / "outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "migration-pack", "migration-pack-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["migration_gate"]["passed"] is True
    assert body["summary"]["migratable_count"] == 1

"""Memory CLI MVP：本地失败样本采集与复跑命令。"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from click.testing import CliRunner

from living_novel_engine.cli import main


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")


def _make_project(projects: Path, slug: str = "memory-cli-story") -> Path:
    project = projects / slug
    memory = project / "memory"
    memory.mkdir(parents=True)
    _write_yaml(project / "world.yaml", {"display_name": "记忆 CLI 测试"})
    _write_yaml(project / "characters.yaml", {"characters": []})
    ledger = {
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
    (memory / "canon_ledger.jsonl").write_text(
        json.dumps(ledger, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_yaml(
        memory / "entity_aliases.yaml",
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


def _env(tmp_path: Path) -> dict[str, str]:
    return {
        "LNE_PROJECTS_DIR": str(tmp_path / "projects"),
        "LNE_OUTPUTS_DIR": str(tmp_path / "outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }


def test_memory_cli_add_sample_then_samples_json(tmp_path):
    env = _env(tmp_path)
    _make_project(Path(env["LNE_PROJECTS_DIR"]))
    runner = CliRunner()

    added = runner.invoke(
        main,
        [
            "memory",
            "add-sample",
            "memory-cli-story",
            "--query",
            "她必须追查那个遗失的关键物证",
            "--entity",
            "mo_qing_yan",
            "--entity",
            "retreat_bell",
            "--reason",
            "换说法后 BM25 未命中正史账本",
            "--chapter",
            "2",
            "--json",
        ],
        env=env,
    )
    assert added.exit_code == 0, added.output
    add_body = json.loads(added.output)
    assert add_body["status"] == "appended"
    assert add_body["sample"]["expected_entities"] == ["mo_qing_yan", "retreat_bell"]

    replayed = runner.invoke(
        main,
        ["memory", "samples", "memory-cli-story", "--json", "--require-candidate"],
        env=env,
    )
    assert replayed.exit_code == 0, replayed.output
    replay_body = json.loads(replayed.output)
    assert replay_body["status"] == "candidate"
    assert replay_body["summary"]["sample_count"] == 1
    assert replay_body["samples"][0]["diagnosis"] == "lexical_gap"


def test_memory_cli_samples_require_candidate_fails_without_samples(tmp_path):
    env = _env(tmp_path)
    _make_project(Path(env["LNE_PROJECTS_DIR"]))

    result = CliRunner().invoke(
        main,
        ["memory", "samples", "memory-cli-story", "--require-candidate"],
        env=env,
    )

    assert result.exit_code != 0
    assert "未检测到可进入 embedding 对照的失败样本" in result.output


def test_memory_cli_add_sample_rejects_secret_text(tmp_path, monkeypatch):
    env = _env(tmp_path)
    _make_project(Path(env["LNE_PROJECTS_DIR"]))
    env["LLM_API_KEY"] = "sk-real-secret-7788"

    result = CliRunner().invoke(
        main,
        [
            "memory",
            "add-sample",
            "memory-cli-story",
            "--query",
            "sk-real-secret-7788",
            "--entity",
            "mo_qing_yan",
        ],
        env=env,
    )

    assert result.exit_code != 0
    assert "query 包含疑似密钥内容" in result.output
    assert "real-secret" not in result.output

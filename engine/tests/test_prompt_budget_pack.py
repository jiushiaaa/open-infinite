"""Prompt Budget Pack MVP: read-only compression of retrieval context."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import get_prompt_budget_pack


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _prepare_branch(outputs_dir: Path) -> None:
    branch = outputs_dir / "run_budget" / "branch_a"
    branch.mkdir(parents=True, exist_ok=True)
    (branch / "chapter.md").write_text("退魂铃在听雨轩再次响起。", encoding="utf-8")
    _write_json(
        branch / "retrieval_context.json",
        {
            "query": "退魂铃 墨青烟",
            "current_chapter": 8,
            "prompt_block": "旧 prompt block 会很长" * 20,
            "items": [
                {
                    "id": "chapter_brief:ch7",
                    "source": "chapter_brief",
                    "score": 0.6,
                    "text": "第七章里众人复核退魂铃，但没有解决来源。",
                },
                {
                    "id": "canon_ledger:ring",
                    "source": "canon_ledger",
                    "score": 0.9,
                    "text": "退魂铃属于墨青烟，响声会暴露听雨轩的旧案。",
                },
                {
                    "id": "contract:0",
                    "source": "contract",
                    "score": 0.3,
                    "text": "禁止让角色突然知道未曾获得的幕后真相。",
                },
                {
                    "id": "canon_ledger:ring-copy",
                    "source": "canon_ledger",
                    "score": 0.4,
                    "text": "退魂铃属于墨青烟，响声会暴露听雨轩的旧案。",
                },
                {
                    "id": "volume_brief:1",
                    "source": "volume_brief",
                    "score": 0.2,
                    "text": "第一卷主要围绕听雨轩旧案、退魂铃和赵轩的记录展开。",
                },
            ],
        },
    )
    _write_json(
        branch / "runtime_memory_context.json",
        {
            "consumed_layers": ["canon_ledger", "entity_aliases"],
            "prompt_block": "运行时记忆层：退魂铃、墨青烟、听雨轩。",
        },
    )


@pytest.fixture
def iso_env(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LNE_MOCK", "1")
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    _prepare_branch(outputs)
    return outputs


def test_prompt_budget_pack_dedupes_and_prioritizes_context(iso_env):
    report = get_prompt_budget_pack("run_budget", "branch_a", char_budget=120)
    sections = {section["id"]: section for section in report["sections"]}
    included_ids = [item["id"] for item in report["packed_items"]]

    assert report["version"] == "prompt-budget-pack-mvp"
    assert report["mode"] == "read_only_prompt_budget_pack"
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["uses_vector_store"] is False
    assert report["summary"]["deduped_item_count"] == 4
    assert report["summary"]["estimated_prompt_chars"] <= 120
    assert "contract:0" in included_ids
    assert "canon_ledger:ring" in included_ids
    assert "canon_ledger:ring-copy" not in included_ids
    assert sections["contract_constraints"]["item_count"] == 1
    assert sections["canon_facts"]["item_count"] >= 1
    assert "禁止让角色突然知道" in report["prompt_block"]


def test_prompt_budget_pack_damaged_retrieval_degrades(iso_env):
    branch = iso_env / "run_budget" / "branch_a"
    (branch / "retrieval_context.json").write_text("{bad-json}", encoding="utf-8")

    report = get_prompt_budget_pack("run_budget", "branch_a")

    assert report["status"] == "blocked"
    assert report["summary"]["source_item_count"] == 0
    assert any("retrieval_context.json 损坏" in item for item in report["warnings"])


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


@pytest.fixture
def running_server(iso_env):
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_prompt_budget_pack_http_statuses(running_server):
    status, body = _get(
        running_server,
        "/api/runs/run_budget/branches/branch_a/prompt-budget-pack?char_budget=120",
    )
    assert status == 200
    assert body["version"] == "prompt-budget-pack-mvp"
    assert body["summary"]["estimated_prompt_chars"] <= 120

    bad_status, bad = _get(
        running_server,
        "/api/runs/..%2Fbad/branches/branch_a/prompt-budget-pack",
    )
    assert bad_status == 400
    assert "invalid" in bad["error"]

    missing_status, missing = _get(
        running_server,
        "/api/runs/run_missing/branches/branch_a/prompt-budget-pack",
    )
    assert missing_status == 404
    assert "运行不存在" in missing["error"]

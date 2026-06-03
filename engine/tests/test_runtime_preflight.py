"""Runtime Preflight MVP: read-only project readiness before long creation."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import (
    get_runtime_preflight,
    import_novel_from_payload,
    select_worldline,
    write_project_copyright_statement,
    write_project_retention_policy,
)


def _chapters(n: int = 6) -> list[dict[str, str]]:
    return [
        {
            "filename": f"chapter_{i:03d}.md",
            "content": (
                f"第{i}章 运行前体检\n"
                f"墨青烟在听雨轩复核退魂铃线索，赵轩记录第 {i} 次回响。"
            ),
        }
        for i in range(1, n + 1)
    ]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _prepare_ready_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, slug: str) -> None:
    outputs = tmp_path / "_outputs"
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    write_project_copyright_statement(
        slug,
        {
            "source_title": "本地试写样例",
            "license_status": "owned_by_user",
            "permitted_uses": ["private_research", "local_export"],
            "attestation": "仅用于本地个人验证。",
        },
        projects_dir=tmp_path,
    )
    write_project_retention_policy(
        slug,
        {
            "project_retention": "keep_until_manual_delete",
            "uploaded_source_retention": "owner_private",
            "generated_artifact_retention": "keep_with_project",
            "holdout_retention": "evaluator_private_until_delete",
            "audit_log_retention": "append_only_until_project_delete",
            "ingest_chunk_retention": "expire_after_import",
        },
        projects_dir=tmp_path,
    )
    run_dir = outputs / "run_preflight"
    branch_dir = run_dir / "branch_a"
    _write_json(run_dir / "intervention.json", {"story_slug": slug})
    _write_json(branch_dir / "events.json", {"theme": "退魂铃余响"})
    (branch_dir / "chapter.md").write_text("退魂铃在听雨轩再次响起。", encoding="utf-8")
    _write_json(
        branch_dir / "state_execution_overlay.json",
        {
            "version": "v0.8.10-B",
            "kind": "state_execution_overlay",
            "mode": "overlay",
            "run_id": "run_preflight",
            "branch_id": "branch_a",
            "applied_candidate_ids": ["candidate-1"],
            "state_deltas": [],
            "state_overlay": {},
        },
    )
    select_worldline(
        story_slug=slug,
        run_id="run_preflight",
        branch_id="branch_a",
        note="体检样例",
    )


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
def iso_env(tmp_path, monkeypatch):
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    monkeypatch.setenv("LNE_MOCK", "1")
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    yield tmp_path


def test_runtime_preflight_aggregates_project_readiness_without_secrets(
    iso_env, monkeypatch
):
    tmp_path = iso_env
    monkeypatch.setenv("LLM_API_KEY", "sk-runtime-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-runtime-secret-8899")
    _prepare_ready_project(tmp_path, monkeypatch, "runtime-preflight-ready")

    report = get_runtime_preflight("runtime-preflight-ready", projects_dir=tmp_path)
    text = json.dumps(report, ensure_ascii=False)
    checkpoints = {item["id"]: item for item in report["checkpoints"]}

    assert report["version"] == "runtime-preflight-mvp"
    assert report["mode"] == "read_only_runtime_preflight"
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["checkpoint_count"] >= 11
    assert {
        "import_review",
        "master_setting",
        "canon_ledger",
        "entity_aliases",
        "retrieval_probe",
        "selected_worldline",
        "state_overlay",
        "copyright_statement",
        "retention_policy",
        "audit_log",
        "provider_status",
    }.issubset(checkpoints)
    assert checkpoints["state_overlay"]["status"] == "ready"
    assert checkpoints["retrieval_probe"]["source_endpoint"] == (
        "GET /api/stories/<slug>/retrieval-probes"
    )
    assert "runtime-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text


def test_runtime_preflight_degrades_damaged_artifacts(iso_env, monkeypatch):
    tmp_path = iso_env
    _prepare_ready_project(tmp_path, monkeypatch, "runtime-preflight-damaged")
    project = tmp_path / "runtime-preflight-damaged"
    (project / "memory" / "canon_ledger.jsonl").write_text("{bad-json}\n", encoding="utf-8")
    (project / "memory" / "entity_aliases.yaml").write_text("entities: [", encoding="utf-8")
    (project / "memory" / "master_setting.yaml").write_text("world_rules: [", encoding="utf-8")
    outputs = tmp_path / "_outputs"
    (outputs / "run_preflight" / "branch_a" / "state_execution_overlay.json").write_text(
        "{bad-json}",
        encoding="utf-8",
    )

    report = get_runtime_preflight("runtime-preflight-damaged", projects_dir=tmp_path)
    checkpoints = {item["id"]: item for item in report["checkpoints"]}

    assert report["status"] == "blocked"
    assert report["summary"]["blocked_count"] >= 3
    assert checkpoints["master_setting"]["status"] == "blocked"
    assert checkpoints["canon_ledger"]["status"] == "blocked"
    assert checkpoints["entity_aliases"]["status"] == "blocked"
    assert checkpoints["state_overlay"]["status"] == "blocked"
    assert any("损坏" in item for item in report["warnings"])


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    monkeypatch.setenv("LNE_MOCK", "1")
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    _prepare_ready_project(tmp_path, monkeypatch, "runtime-preflight-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_runtime_preflight_http_statuses(running_server):
    port = running_server

    status, body = _get(port, "/api/stories/runtime-preflight-http/runtime-preflight")
    assert status == 200
    assert body["version"] == "runtime-preflight-mvp"
    assert body["summary"]["checkpoint_count"] >= 11

    bad_status, bad = _get(port, "/api/stories/..%2Fbad/runtime-preflight")
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    missing_status, missing = _get(port, "/api/stories/missing/runtime-preflight")
    assert missing_status == 404
    assert "故事不存在" in missing["error"]

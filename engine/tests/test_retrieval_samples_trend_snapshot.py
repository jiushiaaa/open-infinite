"""Retrieval Samples Trend Snapshot MVP：跨项目检索样本趋势快照。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.request
from datetime import datetime

from click.testing import CliRunner

from living_novel_engine.browser import server
from living_novel_engine.cli import main
from living_novel_engine.service import get_retrieval_samples_trend_snapshot

from test_cross_project_retrieval_samples_index import _make_project


def test_retrieval_samples_trend_snapshot_summarizes_cross_project_signals(
    tmp_path, monkeypatch
):
    projects = tmp_path / "projects"
    _make_project(projects, "trend-pack-a", with_sample=True)
    _make_project(projects, "trend-pack-b", with_sample=False)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = get_retrieval_samples_trend_snapshot(
        projects_dir=projects,
        now=datetime(2026, 6, 2, 1, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    signals = {signal["id"]: signal for signal in report["signals"]}

    assert report["version"] == "retrieval-samples-trend-snapshot-mvp"
    assert report["mode"] == "read_only_retrieval_samples_trend_snapshot"
    assert report["status"] == "ready"
    assert report["summary"]["project_count"] == 2
    assert report["summary"]["record_count"] == 1
    assert report["summary"]["empty_project_count"] == 1
    assert report["trend_gate"]["passed"] is True
    assert signals["sample_coverage"]["status"] == "ready"
    assert signals["lexical_gap_pressure"]["status"] == "attention"
    assert signals["empty_project_pressure"]["status"] == "attention"
    assert signals["external_provider_pressure"]["status"] == "deferred"
    assert report["project_trends"][0]["story_slug"] == "trend-pack-a"
    assert report["project_trends"][0]["trend_bucket"] == "has_samples"
    assert "trend-pack-a-retrieval-eval-001" in report["content_json"]
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_retrieval_samples_trend_snapshot_empty_projects(tmp_path):
    report = get_retrieval_samples_trend_snapshot(projects_dir=tmp_path / "projects")

    assert report["status"] == "empty"
    assert report["summary"]["project_count"] == 0
    assert report["trend_gate"]["passed"] is False
    assert report["trend_gate"]["status"] == "needs_projects"
    assert report["signals"][0]["status"] == "attention"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_retrieval_samples_trend_snapshot_http(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    _make_project(projects, "trend-pack-api", with_sample=True)
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
            f"http://127.0.0.1:{port}/api/settings/retrieval-samples-trend-snapshot",
            timeout=10,
        ) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert body["status"] == "ready"
    assert body["summary"]["record_count"] == 1
    assert body["trend_gate"]["passed"] is True


def test_memory_cli_trend_snapshot_json(tmp_path):
    projects = tmp_path / "projects"
    _make_project(projects, "trend-pack-cli", with_sample=True)
    env = {
        "LNE_PROJECTS_DIR": str(projects),
        "LNE_OUTPUTS_DIR": str(tmp_path / "outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "trend-snapshot", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["trend_gate"]["passed"] is True
    assert body["summary"]["record_count"] == 1

"""Bundled Release / Desktop Packaging MVP: read-only packaging readiness."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from living_novel_engine.browser import server
import living_novel_engine.service as service


def _write(path: Path, content: str = "ok") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_ready_root(root: Path) -> None:
    _write(root / "scripts" / "start-local.ps1", "powershell startup")
    _write(root / "scripts" / "start-local.sh", "bash startup")
    _write(root / "engine" / "README.md", "本地启动脚本和模型配置说明")
    _write(root / "engine" / "pyproject.toml", "[project]\nname='living-novel-engine'")
    _write(root / "engine" / "ui" / "package.json", '{"scripts":{"build":"vite build"}}')
    _write(root / "engine" / "ui" / "dist" / "index.html", "<html></html>")


def test_bundled_release_readiness_is_secret_safe_and_read_only(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-release-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-release-secret-8899")
    _make_ready_root(tmp_path)

    get_readiness = getattr(service, "get_bundled_release_readiness", None)
    assert callable(get_readiness)
    report = get_readiness(root_dir=tmp_path)
    checks = {item["id"]: item for item in report["checks"]}
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "bundled-release-readiness-mvp"
    assert report["mode"] == "read_only_packaging_readiness"
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["summary"]["builds_package"] is False
    assert report["summary"]["bundles_runtime"] is False
    assert checks["windows_start_script"]["status"] == "ready"
    assert checks["unix_start_script"]["status"] == "ready"
    assert checks["frontend_dist"]["status"] == "ready"
    assert checks["backend_package"]["status"] == "ready"
    assert "release-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text


def test_bundled_release_readiness_degrades_missing_files(tmp_path):
    get_readiness = getattr(service, "get_bundled_release_readiness", None)
    assert callable(get_readiness)
    report = get_readiness(root_dir=tmp_path)
    checks = {item["id"]: item for item in report["checks"]}

    assert report["status"] == "attention"
    assert checks["windows_start_script"]["status"] == "attention"
    assert checks["frontend_dist"]["status"] == "attention"
    assert any(item["status"] == "deferred" for item in report["package_targets"])


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
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
        raw = exc.read().decode("utf-8")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"error": raw}
        return exc.code, body


def test_bundled_release_readiness_http_ok(running_server):
    status, body = _get(running_server, "/api/settings/packaging-readiness")

    assert status == 200
    assert body["version"] == "bundled-release-readiness-mvp"
    assert body["summary"]["check_count"] >= 6
    assert any(item["id"] == "desktop_shell" for item in body["package_targets"])

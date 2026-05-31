"""v1.0-beta Local Deployment Readiness-F：本地部署就绪清单。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

from living_novel_engine.browser import server
from living_novel_engine.service import get_local_deployment_readiness


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_local_deployment_readiness_is_secret_safe_and_actionable(
    tmp_path, monkeypatch
):
    static_root = tmp_path / "static"
    outputs_root = tmp_path / "outputs"
    projects_root = tmp_path / "projects"
    _write(static_root / "index.html", "<html></html>")
    _write(static_root / "app.js", "console.log('ok')")
    _write(static_root / "style.css", "body{}")
    outputs_root.mkdir()
    projects_root.mkdir()
    monkeypatch.setenv("LLM_API_KEY", "sk-deploy-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-deploy-secret-8899")
    monkeypatch.setenv("LNE_MOCK", "1")

    report = get_local_deployment_readiness(
        static_root=static_root,
        outputs_root=outputs_root,
        projects_root=projects_root,
    )
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "v1.0-beta-local-deployment-readiness-f"
    assert report["status"] == "ready"
    assert report["readiness"]["external_services_required"] is False
    assert report["readiness"]["frontend_static_ready"] is True
    assert report["environment"]["llm_key"]["present"] is True
    assert report["environment"]["seedream_key"]["masked"].endswith("8899")
    assert {item["id"] for item in report["checks"]} >= {
        "backend_http",
        "frontend_static",
        "runtime_environment",
        "data_directories",
        "api_smoke_plan",
    }
    routes = {route["path"] for route in report["api_smoke_plan"]}
    assert {
        "/api/stories",
        "/api/settings/runtime",
        "/api/settings/providers",
        "/api/settings/quota-observability",
    }.issubset(routes)
    assert any("lne browse" in step for step in report["run_steps"])
    assert any("pnpm run build" in step for step in report["verification_steps"])
    assert "deploy-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text


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


def test_local_deployment_readiness_http(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_MOCK", "1")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _get(port, "/api/settings/deployment-readiness")
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] in {"ready", "attention"}
    assert body["readiness"]["http_entrypoint"] == f"http://127.0.0.1:{port}/"
    assert body["observability"]["mode"] == "local_process"

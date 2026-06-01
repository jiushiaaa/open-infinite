"""D1 Local Run Script：本地一键运行脚本静态验收。"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_windows_local_start_script_bootstraps_and_runs_services():
    script = ROOT / "scripts" / "start-local.ps1"
    assert script.exists()
    text = script.read_text(encoding="utf-8")
    script.read_bytes().decode("ascii")

    assert "pip install" in text
    assert "install" in text and "pnpm" in text
    assert "-m living_novel_engine.cli browse" in text
    assert "pnpm run dev" in text
    assert "--host 127.0.0.1" in text
    assert "$BackendPort = 8765" in text
    assert "$FrontendPort = 5173" in text
    assert 'http://127.0.0.1:$FrontendPort/' in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text


def test_macos_local_start_script_bootstraps_and_runs_services():
    script = ROOT / "scripts" / "start-local.sh"
    assert script.exists()
    text = script.read_text(encoding="utf-8")

    assert "pip install" in text
    assert "pnpm install" in text
    assert "-m living_novel_engine.cli browse" in text
    assert "pnpm run dev" in text
    assert "--host 127.0.0.1" in text
    assert "BACKEND_PORT=8765" in text
    assert "FRONTEND_PORT=5173" in text
    assert "http://127.0.0.1:$FRONTEND_PORT/" in text
    assert "trap cleanup" in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text

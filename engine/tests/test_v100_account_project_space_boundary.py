"""v1.0-beta Account Project Space Boundary-H：账号与项目空间边界。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from pathlib import Path

from living_novel_engine.browser import server
from living_novel_engine.service import get_account_project_space_boundary


def _write(path: Path, payload: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def test_account_project_space_boundary_maps_local_spaces_without_auth_side_effects(
    tmp_path, monkeypatch
):
    projects = tmp_path / "projects"
    samples = tmp_path / "samples"
    outputs = tmp_path / "outputs"
    _write(projects / "story-a" / "world.yaml", "name: story-a")
    _write(projects / "story-b" / "import_report.json")
    _write(samples / "sample-one" / "world.yaml", "name: sample-one")
    _write(outputs / "run_001" / "branch_a" / "chapter.md", "chapter")
    _write(outputs / "story_selections" / "story-a" / "selected_worldline.json")
    monkeypatch.setenv("LLM_API_KEY", "sk-account-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-account-secret-8899")

    report = get_account_project_space_boundary(
        projects_root=projects,
        samples_root=samples,
        outputs_root=outputs,
    )
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "v1.0-beta-account-project-space-boundary-h"
    assert report["status"] == "boundary_defined"
    assert report["account_model"]["mode"] == "local_single_operator"
    assert report["enforcement"]["mode"] == "not_enforced"
    assert report["local_inventory"]["imported_project_count"] == 2
    assert report["local_inventory"]["sample_project_count"] == 1
    assert report["local_inventory"]["run_count"] == 1
    assert report["local_inventory"]["selection_count"] == 1
    space_ids = {item["id"] for item in report["project_spaces"]}
    assert {
        "imported_projects",
        "bundled_samples",
        "generated_runs",
        "selected_worldlines",
    }.issubset(space_ids)
    future_fields = {item["id"] for item in report["future_metadata_fields"]}
    assert {"owner_account_id", "team_id", "visibility"}.issubset(future_fields)
    boundary_ids = {item["id"] for item in report["migration_boundaries"]}
    assert {"slug_is_not_identity", "samples_are_read_only"}.issubset(boundary_ids)
    assert "account-secret" not in text
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


def test_account_project_space_boundary_http(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_MOCK", "1")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "outputs"))
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _get(port, "/api/settings/account-project-space-boundary")
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "boundary_defined"
    assert body["account_model"]["source_of_truth"] == "local_file_artifacts"
    assert body["next_steps"][0].startswith("先把")

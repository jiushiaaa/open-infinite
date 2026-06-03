"""Graph Memory Shadow Case Matrix MVP：只读 per-case 证据矩阵。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from datetime import datetime

from click.testing import CliRunner

from living_novel_engine.browser import server
from living_novel_engine.cli import main
from living_novel_engine.service import get_graph_memory_shadow_case_matrix

from test_cross_project_retrieval_samples_index import _make_project as _make_sample_project
from test_v093_graph_memory_trigger import _make_project as _make_graph_project


def _make_trigger_project(tmp_path):
    project_dir = _make_graph_project(tmp_path, "graph-cases-large", chapters=55)
    (project_dir / "memory" / "canon_ledger.jsonl").write_text("", encoding="utf-8")
    (project_dir / "memory" / "entity_aliases.yaml").unlink()
    _make_sample_project(tmp_path, "graph-cases-samples", with_sample=True)
    return project_dir


def test_graph_memory_shadow_case_matrix_expands_compare_pack(tmp_path, monkeypatch):
    _make_trigger_project(tmp_path)
    monkeypatch.setenv("LLM_API_KEY", "sk-real-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-real-secret-8899")

    report = get_graph_memory_shadow_case_matrix(
        "graph-cases-large",
        projects_dir=tmp_path,
        now=datetime(2026, 6, 2, 5, 0, 0),
    )
    text = json.dumps(report, ensure_ascii=False)
    cells = {(cell["case_id"], cell["layer_id"]): cell for cell in report["cells"]}

    assert report["version"] == "graph-memory-shadow-case-matrix-mvp"
    assert report["mode"] == "read_only_graph_memory_shadow_case_matrix"
    assert report["status"] == "ready"
    assert report["case_gate"]["passed"] is True
    assert report["case_gate"]["status"] == "case_matrix_ready"
    assert report["summary"]["source_compare_status"] == "ready_for_shadow_compare"
    assert report["summary"]["case_count"] == 1
    assert report["summary"]["layer_count"] >= 3
    assert report["summary"]["matrix_cell_count"] >= 3
    assert report["summary"]["candidate_cell_count"] >= 2
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["uses_graphrag"] is False
    assert report["summary"]["uses_zep"] is False
    assert report["summary"]["uses_embedding_provider"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["cases"][0]["eval_id"] == "graph-cases-samples-retrieval-eval-001"
    assert report["cases"][0]["query"] == "她必须追查那个遗失的关键物证"
    graph_cell = cells[("graph-cases-samples-retrieval-eval-001", "graphrag")]
    zep_cell = cells[("graph-cases-samples-retrieval-eval-001", "zep")]
    assert graph_cell["status"] == "candidate"
    assert graph_cell["evidence_status"] == "local_evidence_ready"
    assert graph_cell["shadow_question"].startswith("GraphRAG")
    assert any("retrieval_eval:" in ref for ref in graph_cell["evidence_refs"])
    assert zep_cell["decision"] in {"shadow_compare", "collect_foundation_evidence"}
    assert "graph-cases-samples-retrieval-eval-001" in report["content_json"]
    assert "real-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text
    assert str(tmp_path) not in text


def test_graph_memory_shadow_case_matrix_small_project_deferred(tmp_path):
    _make_graph_project(tmp_path, "graph-cases-small", chapters=3)

    report = get_graph_memory_shadow_case_matrix("graph-cases-small", projects_dir=tmp_path)

    assert report["status"] == "deferred"
    assert report["case_gate"]["passed"] is False
    assert report["case_gate"]["status"] == "deferred"
    assert report["summary"]["candidate_cell_count"] == 0
    assert all(cell["status"] == "deferred" for cell in report["cells"])


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


def test_graph_memory_shadow_case_matrix_http_statuses(tmp_path, monkeypatch):
    _make_graph_project(tmp_path, "graph-cases-http", chapters=3)
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_MOCK", "1")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _get(port, "/api/stories/graph-cases-http/graph-memory-shadow-case-matrix")
        bad_status, bad = _get(port, "/api/stories/..%2Fx/graph-memory-shadow-case-matrix")
        missing_status, _missing = _get(port, "/api/stories/ghost/graph-memory-shadow-case-matrix")
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["status"] == "deferred"
    assert bad_status == 400
    assert bad["error"] == "invalid slug"
    assert missing_status == 404


def test_memory_cli_graph_cases_json(tmp_path):
    _make_graph_project(tmp_path, "graph-cases-cli", chapters=3)
    env = {
        "LNE_PROJECTS_DIR": str(tmp_path),
        "LNE_OUTPUTS_DIR": str(tmp_path / "_outputs"),
        "LLM_API_KEY": "",
        "SEEDREAM_API_KEY": "",
        "LNE_MOCK": "1",
    }

    result = CliRunner().invoke(
        main,
        ["memory", "graph-cases", "graph-cases-cli", "--json"],
        env=env,
    )

    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["case_gate"]["status"] == "deferred"
    assert body["summary"]["story_slug"] == "graph-cases-cli"

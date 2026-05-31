"""v1.0-beta Quota & Observability Lite-E：本地配额与观测口径。"""

from __future__ import annotations

import json
import socket
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from living_novel_engine.browser import server
from living_novel_engine.service import JobStore, get_quota_observability_lite


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _seed_usage(outputs: Path) -> None:
    run_dir = outputs / "run_quota"
    _write_json(run_dir / "meta.json", {"story_slug": "quota-story"})
    _write_json(
        run_dir / "intervention_compilation.json",
        {
            "generation_meta": {
                "source": "llm",
                "model_name": "quota-model",
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 40,
                    "total_tokens": 140,
                },
            }
        },
    )


def _wait_job(store: JobStore, job_id: str) -> dict:
    for _ in range(50):
        rec = store.get(job_id)
        if rec and rec.status in {"succeeded", "failed"}:
            return rec.to_dict()
        time.sleep(0.02)
    rec = store.get(job_id)
    assert rec is not None
    return rec.to_dict()


def test_quota_observability_lite_aggregates_usage_and_jobs(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    _seed_usage(outputs)
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "sk-quota-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-quota-secret-8899")
    store = JobStore(max_jobs=5, max_workers=1)
    rec = store.submit("import_novel", lambda _update: {"ok": True})
    _wait_job(store, rec.job_id)

    report = get_quota_observability_lite(
        story_slug="quota-story",
        job_store=store,
    )
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "v1.0-beta-quota-observability-lite-e"
    assert report["status"] == "local_observability_ready"
    assert report["quota_policy"]["mode"] == "not_enforced"
    assert report["usage"]["totals"]["total_tokens"] == 140
    assert report["jobs"]["status_counts"]["succeeded"] == 1
    assert report["observability"]["external_monitoring"] == "not_configured"
    assert "真实计费" in " ".join(report["next_steps"])
    assert "quota-secret" not in text
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


def test_quota_observability_http(monkeypatch, tmp_path):
    outputs = tmp_path / "outputs"
    _seed_usage(outputs)
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_MOCK", "1")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _get(
            port,
            "/api/settings/quota-observability?story_slug=quota-story",
        )
        bad_status, bad = _get(
            port,
            "/api/settings/quota-observability?story_slug=../bad",
        )
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert status == 200
    assert body["usage"]["totals"]["total_tokens"] == 140
    assert body["jobs"]["retention"]["max_jobs"] == 100
    assert bad_status == 400
    assert bad["error"] == "invalid story_slug"

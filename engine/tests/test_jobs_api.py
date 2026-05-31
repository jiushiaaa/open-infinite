"""v0.7 第九刀：异步 Job / 进度轮询（service.jobs + /api/jobs/*）。"""

from __future__ import annotations

import json
import socket
import threading
import time
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import JobStore


# ── service 层：JobStore ──────────────────────────────────


def test_jobstore_runs_and_succeeds():
    store = JobStore(max_jobs=10)
    rec = store.submit("intervention", lambda update: (update(50, "x"), {"ok": True})[1])
    for _ in range(50):
        cur = store.get(rec.job_id)
        if cur.status in ("succeeded", "failed"):
            break
        time.sleep(0.02)
    cur = store.get(rec.job_id)
    assert cur.status == "succeeded"
    assert cur.progress == 100
    assert cur.result == {"ok": True}


def test_jobstore_captures_failure():
    store = JobStore(max_jobs=10)

    def boom(_update):
        raise ValueError("炸了")

    rec = store.submit("import_novel", boom)
    for _ in range(50):
        if store.get(rec.job_id).status in ("succeeded", "failed"):
            break
        time.sleep(0.02)
    cur = store.get(rec.job_id)
    assert cur.status == "failed"
    assert "炸了" in cur.error


def test_jobstore_unknown_kind():
    store = JobStore()
    with pytest.raises(ValueError):
        store.submit("nope", lambda u: {})


def test_jobstore_evicts_oldest():
    store = JobStore(max_jobs=3)
    ids = [store.submit("intervention", lambda u: {}).job_id for _ in range(5)]
    # 等待全部跑完，避免竞态
    time.sleep(0.2)
    assert store.count() <= 3
    # 最早两个应被清理
    assert store.get(ids[0]) is None
    assert store.get(ids[1]) is None
    assert store.get(ids[-1]) is not None


# ── HTTP ──────────────────────────────────────────────────


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_out"))
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path / "_proj"))
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def _post(port: int, path: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def _poll(port: int, job_id: str, timeout: float = 30.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        status, body = _get(port, f"/api/jobs/{job_id}")
        assert status == 200
        if body["status"] in ("succeeded", "failed"):
            return body
        time.sleep(0.1)
    raise AssertionError("job 未在超时内完成")


_CHAPTERS = [
    {"filename": "chapter_001.md", "content": "第一章\n少年踏入宗门，立志修行。" * 4},
    {"filename": "chapter_002.md", "content": "第二章\n初遇师姐，结下善缘。" * 4},
    {"filename": "chapter_003.md", "content": "第三章\n大比将至，暗流涌动。" * 4},
]


class TestHttp:
    def test_intervention_job_succeeds(self, running_server):
        status, body = _post(
            running_server,
            "/api/jobs/intervention",
            {
                "story_slug": "tianhuang-night",
                "target": "lin_wan_zhou",
                "content": "希望林晚舟今夜慎行。",
            },
        )
        assert status == 202
        job = _poll(running_server, body["job_id"])
        assert job["status"] == "succeeded"
        assert job["result"]["run_id"]
        assert job["result"]["primary_branch"]

    def test_resume_continue_job_succeeds(self, running_server):
        status, body = _post(
            running_server,
            "/api/jobs/intervention",
            {
                "story_slug": "tianhuang-night",
                "target": "lin_wan_zhou",
                "content": "希望林晚舟今夜慎行。",
                "branches": 2,
                "rounds": 1,
                "mock": True,
            },
        )
        assert status == 202
        parent_job = _poll(running_server, body["job_id"])
        assert parent_job["status"] == "succeeded"
        parent_result = parent_job["result"]

        status, body = _post(
            running_server,
            "/api/jobs/resume-continue",
            {
                "run_id": parent_result["run_id"],
                "branch_id": parent_result["primary_branch"],
                "rounds": 1,
                "mock": True,
            },
        )
        assert status == 202
        job = _poll(running_server, body["job_id"])
        assert job["status"] == "succeeded"
        assert job["result"]["parent_run_id"] == parent_result["run_id"]
        assert job["result"]["parent_branch_id"] == parent_result["primary_branch"]
        assert job["result"]["branch_id"] == "linear"
        assert job["result"]["run_id"]

        branch_status, branch = _get(
            running_server,
            f"/api/runs/{job['result']['run_id']}/branches/linear",
        )
        assert branch_status == 200
        assert branch["chapter_md"].strip()

    def test_resume_continue_job_rejects_bad_ids(self, running_server):
        status, body = _post(
            running_server,
            "/api/jobs/resume-continue",
            {"run_id": "../outside", "branch_id": "branch_a", "mock": True},
        )
        assert status == 400
        assert body["error"] == "invalid run_id or branch_id"

    def test_import_job_then_anchor(self, running_server):
        status, body = _post(
            running_server,
            "/api/jobs/import-novel",
            {"name": "job-import", "chapters": _CHAPTERS, "mock": True},
        )
        assert status == 202
        job = _poll(running_server, body["job_id"])
        assert job["status"] == "succeeded"
        slug = job["result"]["story_slug"]
        a_status, anchor = _get(running_server, f"/api/stories/{slug}/anchor")
        assert a_status == 200
        assert anchor["slug"] == slug

    def test_genesis_job_then_anchor(self, running_server):
        status, body = _post(
            running_server,
            "/api/jobs/story-genesis",
            {"name": "job-genesis", "premise": "一个少年在末法时代重燃灵气。", "mock": True},
        )
        assert status == 202
        job = _poll(running_server, body["job_id"])
        assert job["status"] == "succeeded"
        slug = job["result"]["story_slug"]
        a_status, anchor = _get(running_server, f"/api/stories/{slug}/anchor")
        assert a_status == 200
        assert anchor["slug"] == slug

    def test_job_failure_is_readable(self, running_server):
        # 缺 content → run_intervention 抛 InterventionRequestError → job failed
        status, body = _post(
            running_server,
            "/api/jobs/intervention",
            {"story_slug": "tianhuang-night", "target": "lin_wan_zhou", "content": ""},
        )
        assert status == 202
        job = _poll(running_server, body["job_id"])
        assert job["status"] == "failed"
        assert job["error"]

    def test_unknown_job_404(self, running_server):
        status, _b = _get(running_server, "/api/jobs/abcdef0123456789")
        assert status == 404

    def test_bad_job_id_400(self, running_server):
        status, _b = _get(running_server, "/api/jobs/@@bad")
        assert status == 400

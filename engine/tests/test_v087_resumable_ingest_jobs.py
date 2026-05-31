"""v0.8.7 Resumable Ingest Jobs: server-side chunk sessions."""

from __future__ import annotations

import base64
import hashlib
import json
import socket
import threading
import time
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service.ingest_sessions import (
    IngestSessionConflict,
    IngestSessionRequestError,
    build_upload_from_session,
    create_ingest_session,
    get_ingest_session,
    write_ingest_chunk,
)
from living_novel_engine.service.import_novel import import_novel_from_payload


def _novel_bytes(n: int = 5) -> bytes:
    text = "\n\n".join(
        f"第{i}章 雪夜旧案\n赵轩在归云斋翻检卷宗，沈冰月追问风鸣铃。这是第 {i} 章。"
        for i in range(1, n + 1)
    )
    return text.encode("utf-8")


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


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


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("LNE_INGEST_SESSIONS_DIR", str(tmp_path / "sessions"))
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_ingest_session_resumes_missing_chunks_and_builds_import_upload(tmp_path):
    raw = _novel_bytes(6)
    chunk_size = 31
    chunks = [raw[i : i + chunk_size] for i in range(0, len(raw), chunk_size)]
    created = create_ingest_session(
        name="resume-svc",
        filename="novel.txt",
        total_size=len(raw),
        chunk_size=chunk_size,
        file_sha256=_sha(raw),
        mock=True,
        force=False,
        long_mode=True,
        sessions_dir=tmp_path / "sessions",
    )
    sid = created["session_id"]

    first = write_ingest_chunk(
        sid,
        index=0,
        data_b64=_b64(chunks[0]),
        sha256=_sha(chunks[0]),
        sessions_dir=tmp_path / "sessions",
    )
    assert first["received_chunks"] == [0]
    assert first["missing_chunks"] == list(range(1, len(chunks)))

    duplicate = write_ingest_chunk(
        sid,
        index=0,
        data_b64=_b64(chunks[0]),
        sha256=_sha(chunks[0]),
        sessions_dir=tmp_path / "sessions",
    )
    assert duplicate["duplicate"] is True
    assert duplicate["received_chunks"] == [0]

    resumed = get_ingest_session(sid, sessions_dir=tmp_path / "sessions")
    assert resumed["missing_chunks"] == list(range(1, len(chunks)))

    for index, part in enumerate(chunks[1:], start=1):
        write_ingest_chunk(
            sid,
            index=index,
            data_b64=_b64(part),
            sha256=_sha(part),
            sessions_dir=tmp_path / "sessions",
        )

    upload = build_upload_from_session(sid, sessions_dir=tmp_path / "sessions")
    assert upload["filename"] == "novel.txt"
    assert upload["total_size"] == len(raw)
    assert len(upload["chunks"]) == len(chunks)

    result = import_novel_from_payload(
        name="resume-svc",
        chapters=[],
        upload=upload,
        mock=True,
        long_mode=True,
        projects_dir=tmp_path / "projects",
    )
    assert result.chapter_count == 6


def test_ingest_session_rejects_hash_mismatch_and_conflicting_duplicate(tmp_path):
    raw = _novel_bytes(3)
    created = create_ingest_session(
        name="hash-svc",
        filename="novel.txt",
        total_size=len(raw),
        chunk_size=64,
        sessions_dir=tmp_path / "sessions",
    )
    sid = created["session_id"]
    first = raw[:64]
    write_ingest_chunk(
        sid,
        index=0,
        data_b64=_b64(first),
        sha256=_sha(first),
        sessions_dir=tmp_path / "sessions",
    )

    with pytest.raises(IngestSessionConflict):
        write_ingest_chunk(
            sid,
            index=0,
            data_b64=_b64(b"x" * len(first)),
            sessions_dir=tmp_path / "sessions",
        )

    with pytest.raises(IngestSessionRequestError):
        write_ingest_chunk(
            sid,
            index=1,
            data_b64=_b64(raw[64:128]),
            sha256="0" * 64,
            sessions_dir=tmp_path / "sessions",
        )

    with pytest.raises(IngestSessionConflict):
        build_upload_from_session(sid, sessions_dir=tmp_path / "sessions")


def test_http_resumable_ingest_complete_starts_import_job(running_server):
    raw = _novel_bytes(5)
    chunk_size = 45
    chunks = [raw[i : i + chunk_size] for i in range(0, len(raw), chunk_size)]

    status, created = _post(
        running_server,
        "/api/ingest-sessions",
        {
            "name": "resume-http",
            "filename": "novel.txt",
            "total_size": len(raw),
            "chunk_size": chunk_size,
            "file_sha256": _sha(raw),
            "genre": "xianxia",
            "mock": True,
            "force": False,
            "long_mode": True,
        },
    )
    assert status == 201
    sid = created["session_id"]

    status, body = _post(
        running_server,
        f"/api/ingest-sessions/{sid}/chunks",
        {"index": 0, "data_b64": _b64(chunks[0]), "sha256": _sha(chunks[0])},
    )
    assert status == 200
    assert body["missing_chunks"] == list(range(1, len(chunks)))

    status, body = _get(running_server, f"/api/ingest-sessions/{sid}")
    assert status == 200
    assert body["received_chunks"] == [0]

    status, body = _post(
        running_server,
        f"/api/ingest-sessions/{sid}/chunks",
        {"index": 0, "data_b64": _b64(chunks[0]), "sha256": _sha(chunks[0])},
    )
    assert status == 200
    assert body["duplicate"] is True

    for index, part in enumerate(chunks[1:], start=1):
        status, _body = _post(
            running_server,
            f"/api/ingest-sessions/{sid}/chunks",
            {"index": index, "data_b64": _b64(part), "sha256": _sha(part)},
        )
        assert status == 200

    status, complete = _post(running_server, f"/api/ingest-sessions/{sid}/complete", {})
    assert status == 202
    job = _poll(running_server, complete["job_id"])
    assert job["status"] == "succeeded"
    assert job["result"]["story_slug"] == "resume-http"
    assert job["result"]["chapter_count"] == 5


def test_http_ingest_session_errors_are_400_404_409(running_server):
    status, body = _get(running_server, "/api/ingest-sessions/@@bad")
    assert status == 400
    assert "session" in body["error"].lower()

    status, _body = _get(running_server, "/api/ingest-sessions/abcdef0123456789")
    assert status == 404

    raw = _novel_bytes(3)
    status, created = _post(
        running_server,
        "/api/ingest-sessions",
        {
            "name": "incomplete-http",
            "filename": "novel.txt",
            "total_size": len(raw),
            "chunk_size": 30,
        },
    )
    assert status == 201
    status, body = _post(
        running_server,
        f"/api/ingest-sessions/{created['session_id']}/complete",
        {},
    )
    assert status == 409
    assert "缺失" in body["error"]

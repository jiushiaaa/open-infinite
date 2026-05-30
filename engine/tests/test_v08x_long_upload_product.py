"""v0.8.x long upload productization: chunked txt/zip/epub imports."""

from __future__ import annotations

import base64
import io
import json
import socket
import threading
import time
import urllib.error
import urllib.request
import zipfile

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import import_novel_from_payload


def _novel_text(n: int = 4) -> str:
    return "\n\n".join(
        f"第{i}章 风雪旧案\n赵轩在归云斋翻检卷宗，沈冰月追问风鸣铃。这是第 {i} 章。"
        for i in range(1, n + 1)
    )


def _chunk_upload(filename: str, raw: bytes, *, size: int = 37) -> dict:
    chunks = []
    for i in range(0, len(raw), size):
        part = raw[i : i + size]
        chunks.append(
            {
                "index": len(chunks),
                "data_b64": base64.b64encode(part).decode("ascii"),
            }
        )
    return {
        "filename": filename,
        "total_size": len(raw),
        "chunks": chunks,
    }


def _zip_bytes(files: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, text in files.items():
            zf.writestr(name, text)
    return buf.getvalue()


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
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_chunked_txt_upload_imports_long_mode_project(tmp_path):
    result = import_novel_from_payload(
        name="txt-upload",
        chapters=[],
        upload=_chunk_upload("novel.txt", _novel_text(12).encode("utf-8")),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )

    assert result.chapter_count == 12
    assert result.import_report["total_chapters"] == 12
    assert (tmp_path / "txt-upload" / "source_raw" / "chapter_012.md").exists()


def test_chunked_zip_upload_reads_txt_and_md_entries(tmp_path):
    raw = _zip_bytes(
        {
            "book/chapter_001.md": "第1章 雪夜\n赵轩出门。",
            "book/chapter_002.txt": "第2章 归云\n沈冰月问案。",
            "book/chapter_003.md": "第3章 风铃\n韩无归现身。",
        }
    )

    result = import_novel_from_payload(
        name="zip-upload",
        chapters=[],
        upload=_chunk_upload("novel.zip", raw),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )

    assert result.chapter_count == 3
    report = json.loads(
        (tmp_path / "zip-upload" / "import_report.json").read_text(encoding="utf-8")
    )
    assert report["chapters"][0]["source_filename"] == "book/chapter_001.md"


def test_epub_upload_job_succeeds_and_bad_zip_fails(running_server):
    epub = _zip_bytes(
        {
            "EPUB/chapter1.xhtml": "<h1>第1章 雪夜</h1><p>赵轩出门。</p>",
            "EPUB/chapter2.xhtml": "<h1>第2章 归云</h1><p>沈冰月问案。</p>",
            "EPUB/chapter3.xhtml": "<h1>第3章 风铃</h1><p>韩无归现身。</p>",
        }
    )
    status, body = _post(
        running_server,
        "/api/jobs/import-novel",
        {
            "name": "epub-upload",
            "chapters": [],
            "upload": _chunk_upload("novel.epub", epub),
            "mock": True,
            "long_mode": True,
        },
    )
    assert status == 202
    job = _poll(running_server, body["job_id"])
    assert job["status"] == "succeeded"
    assert job["result"]["chapter_count"] == 3

    status, body = _post(
        running_server,
        "/api/jobs/import-novel",
        {
            "name": "bad-upload",
            "chapters": [],
            "upload": _chunk_upload("broken.zip", b"not a zip"),
            "mock": True,
            "long_mode": True,
        },
    )
    assert status == 202
    failed = _poll(running_server, body["job_id"])
    assert failed["status"] == "failed"
    assert "无法解析" in failed["error"]

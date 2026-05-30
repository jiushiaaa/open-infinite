"""v0.8.6 Long Import Review: import report, previews, and error states."""

from __future__ import annotations

import base64
import io
import json
import socket
import threading
import urllib.error
import urllib.request
import zipfile

import pytest

from living_novel_engine.browser import indexer, server
from living_novel_engine.import_novel.report import build_import_report
from living_novel_engine.import_novel.splitter import SplitChapter
from living_novel_engine.service import import_novel_from_payload


def _chapters(n: int = 4) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i:03d}.md",
            "content": f"第{i}章 归云旧案\n赵轩在归云斋查看风鸣铃，沈冰月记录第 {i} 章线索。",
        }
        for i in range(1, n + 1)
    ]


def _upload(filename: str, raw: bytes) -> dict:
    return {
        "filename": filename,
        "total_size": len(raw),
        "chunks": [
            {
                "index": 0,
                "data_b64": base64.b64encode(raw).decode("ascii"),
            }
        ],
    }


def _zip_bytes(files: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def _post(port: int, path: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port, tmp_path
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_import_report_contains_review_fields():
    report = build_import_report(
        slug="review-story",
        chapters=[
            SplitChapter(index=1, title="同名章", content="第1章 正文？？？？？？？？"),
            SplitChapter(index=2, title="同名章", content="第2章 正文"),
        ],
        source_filenames=["chapter_001.md", "chapter_003.md"],
        long_mode=True,
        warnings=["zip 中跳过了非章节文件：cover.png"],
    )

    assert report["version"] == "v0.8.6"
    assert report["source"]["type"] == "manual"
    assert report["chapter_stats"]["average_characters"] > 0
    assert any(r["code"] == "duplicate_titles" for r in report["quality_risks"])
    assert any(r["code"] == "missing_chapter_numbers" for r in report["quality_risks"])
    assert report["parsing_warnings"] == ["zip 中跳过了非章节文件：cover.png"]
    assert any(a["kind"] == "review_chapters" for a in report["recommended_actions"])
    assert report["chapters"][0]["preview"]


def test_world_anchor_returns_import_review_preview_and_damaged_degrades(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "projects_dir", lambda: tmp_path)
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path / "_outputs")
    import_novel_from_payload(
        name="review-anchor",
        chapters=_chapters(4),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )

    anchor = indexer.get_world_anchor("review-anchor")
    review = anchor["import_review"]
    assert review["status"] == "ready"
    assert review["summary"]["total_chapters"] == 4
    assert review["chapter_previews"][0]["preview"]
    assert review["recommended_actions"]

    (tmp_path / "review-anchor" / "import_report.json").write_text(
        "{not json", encoding="utf-8"
    )
    damaged = indexer.get_world_anchor("review-anchor")["import_review"]
    assert damaged["status"] == "damaged"
    assert damaged["chapter_previews"][0]["title"]
    assert damaged["summary"]["total_chapters"] == 4
    assert damaged["warnings"]


def test_import_errors_are_clear_for_bad_archives_and_empty_files(running_server):
    port, _ = running_server
    cases = [
        ("bad-zip", "broken.zip", b"not a zip", "zip 文件无法解析或已损坏"),
        ("bad-epub", "broken.epub", b"not an epub", "epub 文件无法解析或已损坏"),
        ("empty-txt", "empty.txt", b"", "上传文件为空"),
        (
            "few-chapters",
            "few.zip",
            _zip_bytes(
                {
                    "chapter_001.md": "第1章 风雪\n赵轩出门。",
                    "chapter_002.md": "第2章 归云\n沈冰月问案。",
                }
            ),
            "至少需要 3 章",
        ),
    ]

    for slug, filename, raw, expected in cases:
        status, body = _post(
            port,
            "/api/import-novel",
            {
                "name": slug,
                "chapters": [],
                "upload": _upload(filename, raw),
                "mock": True,
                "long_mode": True,
            },
        )
        assert status == 400
        assert expected in body["error"]


def test_http_anchor_import_review_missing_and_ready_states(running_server):
    port, tmp_path = running_server
    status, body = _post(
        port,
        "/api/import-novel",
        {
            "name": "http-review",
            "chapters": _chapters(4),
            "mock": True,
            "long_mode": True,
        },
    )
    assert status == 200
    assert body["import_report"]["quality_risks"] == []
    assert body["import_report"]["recommended_actions"]

    status, anchor = _get(port, "/api/stories/http-review/anchor")
    assert status == 200
    assert anchor["import_review"]["status"] == "ready"
    assert anchor["import_review"]["chapter_previews"]

    (tmp_path / "http-review" / "import_report.json").unlink()
    status, missing = _get(port, "/api/stories/http-review/anchor")
    assert status == 200
    assert missing["import_review"]["status"] == "missing"
    assert missing["import_review"]["chapter_previews"]

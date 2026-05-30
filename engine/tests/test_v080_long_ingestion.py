"""v0.8.0-A Long Novel Ingestion：导入报告与长篇原文落盘。"""

from __future__ import annotations

import json
import socket
import threading
import time
import urllib.request
import urllib.error

import pytest

from living_novel_engine.browser import server
from living_novel_engine.service import ImportRequestError, import_novel_from_payload


def _chapters(n: int, *, gap: bool = False, garbled: bool = False) -> list[dict]:
    items: list[dict] = []
    for i in range(n):
        chapter_no = i + 1
        filename_no = chapter_no + 1 if gap and chapter_no >= 2 else chapter_no
        title = "重复章名" if chapter_no in (2, 3) else f"第{chapter_no}章 长篇测试"
        body = "林凡沿着旧案线索继续追查，退魂铃的余波仍在。" * 8
        if garbled and chapter_no == 2:
            body += "���????"
        items.append({
            "filename": f"chapter_{filename_no:03d}.md",
            "content": f"{title}\n{body}",
        })
    return items


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


class TestLongIngestionReport:
    def test_long_mode_writes_source_raw_and_report(self, tmp_path):
        result = import_novel_from_payload(
            name="long-ingest",
            chapters=_chapters(25),
            mock=True,
            long_mode=True,
            projects_dir=tmp_path,
        )

        project_dir = tmp_path / "long-ingest"
        report_path = project_dir / "import_report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))

        assert result.chapter_count == 25
        assert result.import_report["total_chapters"] == 25
        assert report["version"] == "v0.8.0"
        assert report["total_chapters"] == 25
        assert report["playable_chapter_limit"] == 20
        assert report["partial_ready"] is True
        assert report["total_characters"] > 1000
        assert len(list((project_dir / "source_raw").glob("chapter_*.md"))) == 25
        assert len(list((project_dir / "source").glob("chapter_*.md"))) == 25

    def test_legacy_import_still_rejects_more_than_ten(self, tmp_path):
        with pytest.raises(ImportRequestError, match="最多 10 章"):
            import_novel_from_payload(
                name="legacy-limit",
                chapters=_chapters(11),
                mock=True,
                projects_dir=tmp_path,
            )

    def test_report_flags_garbled_duplicates_and_missing_chapter(self, tmp_path):
        result = import_novel_from_payload(
            name="risk-report",
            chapters=_chapters(4, gap=True, garbled=True),
            mock=True,
            long_mode=True,
            projects_dir=tmp_path,
        )

        risks = result.import_report["risks"]
        assert risks["garbled_chapters"] == [2]
        assert risks["duplicate_titles"] == ["重复章名"]
        assert risks["missing_chapter_numbers"] == [2]
        assert result.warnings


class TestLongIngestionHttp:
    def test_import_job_returns_report_summary(self, running_server):
        status, body = _post(
            running_server,
            "/api/jobs/import-novel",
            {
                "name": "job-long-ingest",
                "chapters": _chapters(12),
                "mock": True,
                "long_mode": True,
            },
        )

        assert status == 202
        job = _poll(running_server, body["job_id"])
        assert job["status"] == "succeeded"
        summary = job["result"]["import_report"]
        assert summary["total_chapters"] == 12
        assert summary["playable_chapter_limit"] == 12
        assert summary["partial_ready"] is False

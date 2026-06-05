"""World Sandbox Loop v8: author adoption desk."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

from living_novel_engine.browser import server
from living_novel_engine.service import import_novel_from_payload
from living_novel_engine.service.author_adoption import record_author_adoption
from living_novel_engine.service.character_lens import generate_character_lens_briefs


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 作者采纳台\n"
                "赵轩追查风鸣铃，沈冰月守住苍澜派规矩，韩无归逼问旧案。"
            ),
        }
        for idx in range(1, n + 1)
    ]


def _make_project(tmp_path, slug: str = "adoption-story"):
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    return tmp_path / slug


def test_author_adoption_writes_ledger_and_export_brief(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃现世，赵轩选择隐瞒。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )

    report = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="partial",
        original_outline="赵轩按旧大纲公开风鸣铃线索，苍澜派保持稳定。",
        author_note="保留隐瞒动作，但不立刻推翻苍澜派。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    run_dir = outputs_dir / report["run_id"]
    ledger_path = tmp_path / "adoption-story" / "author_adoption_ledger.jsonl"

    assert report["version"] == "author-adoption-desk-v1"
    assert report["decision"] == "partial"
    assert report["artifact"] == "author_adoption_record.json"
    assert report["comparison"]["original_outline"]
    assert "风鸣铃" in report["comparison"]["sandbox_emergence"]
    assert report["adoption_entry"]["source_run_id"] == lens["run_id"]
    assert ledger_path.exists()
    assert (run_dir / "author_adoption_record.json").exists()
    assert (run_dir / "author_adoption_brief.md").exists()
    assert "部分采纳" in (run_dir / "author_adoption_brief.md").read_text(
        encoding="utf-8"
    )
    rows = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows[-1]["decision"] == "partial"


def test_author_adoption_feeds_next_chapter_brief_and_worldline_continuation(tmp_path):
    project_dir = _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"
    lens = generate_character_lens_briefs(
        "adoption-story",
        source_event="风鸣铃现世，赵轩选择隐瞒，沈冰月误判他的真实立场。",
        character_id="zhao_xuan",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )

    report = record_author_adoption(
        "adoption-story",
        source_run_id=lens["run_id"],
        decision="adopted",
        original_outline="赵轩公开消息，沈冰月继续相信他。",
        author_note="采纳误判，让下一章从两人的信息差开场。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
        worldline_id="branch_from_sandbox",
    )
    run_dir = outputs_dir / report["run_id"]
    state_path = project_dir / "worldlines" / "branch_from_sandbox" / "worldline_state.json"

    assert report["artifacts"]["next_chapter_brief"] == "next_chapter_brief.json"
    assert (run_dir / "next_chapter_brief.json").exists()
    assert report["next_chapter_brief"]["opening_scene"]
    assert report["next_chapter_brief"]["sandbox_inputs"]["major_event"]
    assert report["next_chapter_brief"]["sandbox_inputs"]["worldline_id"] == "branch_from_sandbox"
    assert report["outline_diff"]["status"] in {"aligned", "diverged", "partially_aligned"}
    assert report["foreshadowing_adjustments"]
    assert report["reviewer_suggestions"]
    assert report["continuation_effect"]["affects_future_sandbox"] is True
    assert state_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["author_adoption"]["latest_decision"] == "adopted"
    assert state["next_chapter_brief"]["source_run_id"] == report["run_id"]


def test_author_adoption_supports_allowed_decisions(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    for decision in ("adopted", "partial", "new_branch", "export_brief"):
        report = record_author_adoption(
            "adoption-story",
            source_event="风鸣铃现世。",
            sandbox_summary="赵轩隐瞒消息，沈冰月开始怀疑。",
            decision=decision,
            original_outline="赵轩公开消息。",
            projects_dir=tmp_path,
            outputs_dir=outputs_dir,
        )
        assert report["decision"] == decision
        assert report["adoption_entry"]["mode_label"]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _post(port: int, path: str, body: dict) -> tuple[int, dict]:
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_author_adoption_http_statuses(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "adoption-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _post(
            port,
            "/api/stories/adoption-http/author-adoption",
            {
                "source_event": "风鸣铃现世。",
                "sandbox_summary": "赵轩隐瞒消息。",
                "decision": "adopted",
                "original_outline": "赵轩公开消息。",
            },
        )
        assert status == 200
        assert body["artifact"] == "author_adoption_record.json"
        assert body["decision"] == "adopted"

        bad_status, bad = _post(
            port,
            "/api/stories/..%2Fbad/author-adoption",
            {"source_event": "风鸣铃现世。"},
        )
        assert bad_status == 400
        assert bad["error"] == "invalid slug"

        invalid_status, invalid = _post(
            port,
            "/api/stories/adoption-http/author-adoption",
            {"source_event": "风鸣铃现世。", "decision": "overwrite"},
        )
        assert invalid_status == 400
        assert "decision" in invalid["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()

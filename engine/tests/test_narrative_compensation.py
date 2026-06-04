"""World Sandbox Loop v5: narrative compensation and Tianming delta."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

from living_novel_engine.browser import server
from living_novel_engine.service import import_novel_from_payload
from living_novel_engine.service.narrative_compensation import (
    run_narrative_compensation,
)
from living_novel_engine.service.tianming import (
    confirm_tianming_book,
    generate_tianming_book,
)


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 代偿\n"
                "赵轩追查风鸣铃，沈冰月守住苍澜派规矩，韩无归逼问旧案。"
            ),
        }
        for idx in range(1, n + 1)
    ]


def _make_project(tmp_path, slug: str = "compensation-story"):
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    generate_tianming_book(slug, projects_dir=tmp_path)
    confirm_tianming_book(slug, confirm=True, projects_dir=tmp_path)


def test_narrative_compensation_writes_tianming_delta_and_world_pressure(tmp_path):
    _make_project(tmp_path)
    outputs_dir = tmp_path / "_outputs"

    report = run_narrative_compensation(
        "compensation-story",
        trigger_event="赵轩拒绝追查风鸣铃，并试图离开云城。",
        projects_dir=tmp_path,
        outputs_dir=outputs_dir,
    )
    delta_path = outputs_dir / report["run_id"] / "tianming_delta.json"
    saved = json.loads(delta_path.read_text(encoding="utf-8"))

    assert report["version"] == "narrative-compensation-v1"
    assert report["artifact"] == "tianming_delta.json"
    assert delta_path.exists()
    assert saved["anchor_transfer"]["status"] in {"stable", "transferring", "unanchored"}
    assert saved["replacement_anchor_candidates"]
    assert saved["causal_debt_diffusion"]
    assert saved["world_pressure_events"]
    assert all(event["mode"] != "admin_erasure" for event in saved["world_pressure_events"])
    assert any(event["domain"] in {"politics", "relationship", "faction", "environment"} for event in saved["world_pressure_events"])


def test_narrative_compensation_marks_unanchored_when_anchor_removed(tmp_path):
    _make_project(tmp_path)

    report = run_narrative_compensation(
        "compensation-story",
        trigger_event="赵轩死亡，风鸣铃失去主锚点，云城谣言四起。",
        projects_dir=tmp_path,
        outputs_dir=tmp_path / "_outputs",
    )

    assert report["anchor_transfer"]["status"] == "unanchored"
    assert report["anchor_transfer"]["next_anchor_candidate"]
    assert report["causal_debt_diffusion"]["level"] == "high"


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


def test_narrative_compensation_http_statuses(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "compensation-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _post(
            port,
            "/api/stories/compensation-http/narrative-compensation/run",
            {"trigger_event": "赵轩摆烂，沈冰月被迫接过线索。"},
        )
        assert status == 200
        assert body["artifact"] == "tianming_delta.json"

        bad_status, bad = _post(
            port,
            "/api/stories/..%2Fbad/narrative-compensation/run",
            {"trigger_event": "赵轩摆烂。"},
        )
        assert bad_status == 400
        assert bad["error"] == "invalid slug"

        empty_status, empty = _post(
            port,
            "/api/stories/compensation-http/narrative-compensation/run",
            {"trigger_event": ""},
        )
        assert empty_status == 400
        assert "trigger_event" in empty["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()

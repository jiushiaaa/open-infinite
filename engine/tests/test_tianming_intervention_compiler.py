"""World Sandbox Loop v4: intervention compiler reads Tianming book."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

from living_novel_engine.browser import server
from living_novel_engine.service import import_novel_from_payload
from living_novel_engine.service.tianming import (
    confirm_tianming_book,
    generate_tianming_book,
)
from living_novel_engine.service.tianming_intervention_compiler import (
    compile_intervention_against_tianming,
)


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{idx:03d}.md",
            "content": (
                f"第{idx}章 干预编译\n"
                "赵轩追查风鸣铃，沈冰月守住苍澜派规矩，韩无归逼问旧案。"
            ),
        }
        for idx in range(1, n + 1)
    ]


def _make_project(tmp_path, slug: str = "compiler-story"):
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    generate_tianming_book(slug, projects_dir=tmp_path)
    confirm_tianming_book(slug, confirm=True, projects_dir=tmp_path)
    return tmp_path / slug


def test_compile_intervention_reads_tianming_and_preserves_book(tmp_path):
    project_dir = _make_project(tmp_path)
    before = (project_dir / "tianming.json").read_text(encoding="utf-8")

    report = compile_intervention_against_tianming(
        "compiler-story",
        content="给赵轩一封来自未来的大纲信，告诉他韩无归下一章会叛逃。",
        target="zhao_xuan",
        projects_dir=tmp_path,
    )
    after = (project_dir / "tianming.json").read_text(encoding="utf-8")

    assert before == after
    assert report["version"] == "tianming-intervention-compiler-v1"
    assert report["tianming"]["status"] == "confirmed"
    assert report["intervention_type"] == "information"
    assert report["intervention_level"] in {"L2", "L3"}
    assert report["compatibility"]["status"] in {"compatible", "strained"}
    assert report["translation_strategy"]
    assert report["worldline_judgement"]["kind"] in {"divergent", "au"}
    assert report["branch_axis"]
    assert report["causal_debt"]["level"] in {"low", "medium", "high"}
    assert report["ordinary_intervention_mutates_tianming"] is False


def test_compile_rule_rewrite_marks_au_and_requires_audit(tmp_path):
    _make_project(tmp_path)

    report = compile_intervention_against_tianming(
        "compiler-story",
        content="把这个世界改成所有人都必须听命于读者的系统，风鸣铃规则永久失效。",
        target="zhao_xuan",
        projects_dir=tmp_path,
    )

    assert report["intervention_type"] == "rule_rewrite"
    assert report["intervention_level"] in {"L4", "L5"}
    assert report["worldline_judgement"]["kind"] == "au"
    assert report["audit"]["required"] is True
    assert report["audit"]["can_mutate_tianming_snapshot"] is True


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


def test_tianming_intervention_compiler_http_statuses(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "compiler-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _post(
            port,
            "/api/stories/compiler-http/tianming/intervention-compile",
            {"content": "给赵轩一枚能够偷听宗门密谈的铜铃。", "target": "zhao_xuan"},
        )
        assert status == 200
        assert body["intervention_type"] == "resource_injection"
        assert body["tianming"]["artifact"] == "tianming.json"

        bad_status, bad = _post(
            port,
            "/api/stories/..%2Fbad/tianming/intervention-compile",
            {"content": "给赵轩密信。"},
        )
        assert bad_status == 400
        assert bad["error"] == "invalid slug"

        empty_status, empty = _post(
            port,
            "/api/stories/compiler-http/tianming/intervention-compile",
            {"content": ""},
        )
        assert empty_status == 400
        assert "content" in empty["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()

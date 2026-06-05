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


def test_l5_intervention_writes_worldline_tianming_snapshot_without_root_mutation(tmp_path):
    project_dir = _make_project(tmp_path)
    before = (project_dir / "tianming.json").read_text(encoding="utf-8")

    report = compile_intervention_against_tianming(
        "compiler-story",
        content="永久改写世界规则：所有角色都知道自己是小说人物，并必须回应读者。",
        target="zhao_xuan",
        projects_dir=tmp_path,
        worldline_id="reader_au",
    )
    after = (project_dir / "tianming.json").read_text(encoding="utf-8")
    snapshot_path = project_dir / "worldlines" / "reader_au" / "tianming_snapshot.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))

    assert before == after
    assert snapshot_path.exists()
    assert report["worldline_tianming_snapshot"]["artifact"] == (
        "worldlines/reader_au/tianming_snapshot.json"
    )
    assert report["worldline_tianming_snapshot"]["status"] == "draft_snapshot"
    assert snapshot["status"] == "draft_snapshot"
    assert snapshot["worldline_id"] == "reader_au"
    assert snapshot["root_tianming_mutated"] is False
    assert snapshot["snapshot_reason"]["intervention_level"] == "L5"
    assert snapshot["contract_pressure"]["active_tier"] == "collapse"
    assert snapshot["contract_pressure"]["score"] >= 12


def test_ak47_intervention_can_choose_immersive_translation_or_wild_au(tmp_path):
    project_dir = _make_project(tmp_path)
    before = (project_dir / "tianming.json").read_text(encoding="utf-8")

    immersive = compile_intervention_against_tianming(
        "compiler-story",
        content="给赵轩投放一把 AK47 和三十发子弹。",
        target="zhao_xuan",
        projects_dir=tmp_path,
        worldline_id="ak47_line",
        projection_mode="immersive",
    )

    assert immersive["projection_mode"] == "immersive"
    assert immersive["intervention_type"] == "resource_injection"
    assert immersive["compatibility"]["foreign_object_intrusion"] is True
    assert immersive["translation_strategy"]["mode"] == "local_reinterpretation"
    assert immersive["worldline_judgement"]["kind"] == "divergent"
    assert immersive["worldline_tianming_snapshot"] is None
    assert (project_dir / "tianming.json").read_text(encoding="utf-8") == before

    wild = compile_intervention_against_tianming(
        "compiler-story",
        content="给赵轩投放一把 AK47 和三十发子弹。",
        target="zhao_xuan",
        projects_dir=tmp_path,
        worldline_id="ak47_au",
        projection_mode="wild_au",
    )

    assert wild["projection_mode"] == "wild_au"
    assert wild["intervention_type"] == "resource_injection"
    assert wild["compatibility"]["foreign_object_intrusion"] is True
    assert wild["translation_strategy"]["mode"] == "wild_au_intrusion"
    assert wild["worldline_judgement"]["kind"] == "au"
    assert wild["audit"]["required"] is True
    assert wild["audit"]["can_mutate_tianming_snapshot"] is True
    assert wild["worldline_tianming_snapshot"]["artifact"] == (
        "worldlines/ak47_au/tianming_snapshot.json"
    )
    assert (project_dir / "worldlines" / "ak47_au" / "tianming_snapshot.json").exists()
    assert (project_dir / "tianming.json").read_text(encoding="utf-8") == before


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

        snapshot_status, snapshot_body = _post(
            port,
            "/api/stories/compiler-http/tianming/intervention-compile",
            {
                "content": "永久改写世界规则，让所有角色知道自己是小说人物。",
                "target": "zhao_xuan",
                "worldline_id": "http_au",
            },
        )
        assert snapshot_status == 200
        assert snapshot_body["worldline_tianming_snapshot"]["artifact"] == (
            "worldlines/http_au/tianming_snapshot.json"
        )
        assert (
            tmp_path
            / "compiler-http"
            / "worldlines"
            / "http_au"
            / "tianming_snapshot.json"
        ).exists()

        wild_status, wild_body = _post(
            port,
            "/api/stories/compiler-http/tianming/intervention-compile",
            {
                "content": "给赵轩投放一把 AK47 和三十发子弹。",
                "target": "zhao_xuan",
                "worldline_id": "ak47_http_au",
                "projection_mode": "wild_au",
            },
        )
        assert wild_status == 200
        assert wild_body["projection_mode"] == "wild_au"
        assert wild_body["compatibility"]["foreign_object_intrusion"] is True
        assert wild_body["worldline_judgement"]["kind"] == "au"
        assert wild_body["worldline_tianming_snapshot"]["artifact"] == (
            "worldlines/ak47_http_au/tianming_snapshot.json"
        )

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

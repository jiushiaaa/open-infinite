"""v0.9.0-alpha Long Novel Creation Loop: export and checklist slices."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import indexer, server
from living_novel_engine.service import import_novel_from_payload, run_intervention, write_holdout


def _chapter_export_api():
    try:
        from living_novel_engine.service import (
            ChapterExportRequestError,
            build_chapter_export,
            build_chapter_collection_export,
        )
    except ImportError as exc:  # pragma: no cover - red phase assertion
        pytest.fail(f"缺少章节导出服务: {exc}")
    return (
        ChapterExportRequestError,
        build_chapter_export,
        build_chapter_collection_export,
    )


def _resume_continue_api():
    try:
        from living_novel_engine.service import (
            ResumeContinueRequestError,
            run_resume_continue,
        )
    except ImportError as exc:  # pragma: no cover - red phase assertion
        pytest.fail(f"缺少续章服务: {exc}")
    return ResumeContinueRequestError, run_resume_continue


def _worldline_selection_api():
    try:
        from living_novel_engine.service import (
            WorldlineSelectionRequestError,
            get_selected_worldline,
            select_worldline,
        )
    except ImportError as exc:  # pragma: no cover - red phase assertion
        pytest.fail(f"缺少世界线选择服务: {exc}")
    return WorldlineSelectionRequestError, get_selected_worldline, select_worldline


def _write_branch(
    outputs,
    run_id: str = "run_v090_export",
    branch_id: str = "branch_a",
    *,
    with_judgement: bool = True,
):
    run_dir = outputs / run_id
    branch_dir = run_dir / branch_id
    branch_dir.mkdir(parents=True)
    (run_dir / "intervention.json").write_text(
        json.dumps(
            {
                "story_slug": "export-story",
                "source_kind": "imported",
                "target": "zhao_xuan",
                "content": "让赵轩提前核对风鸣铃线索",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "intervention_compilation.json").write_text(
        json.dumps(
            {
                "branch_axis": [
                    {
                        "branch_id": "branch_a",
                        "label": "提前查证",
                        "description": "赵轩提前核对风鸣铃线索。",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (branch_dir / "events.json").write_text(
        json.dumps({"theme": "提前查证"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (branch_dir / "state_snapshot.json").write_text(
        json.dumps({"characters": {"zhao_xuan": {"name": "赵轩"}}}, ensure_ascii=False),
        encoding="utf-8",
    )
    (branch_dir / "chapter.md").write_text(
        "# 第七章 风鸣旧案\n\n赵轩在归云斋前停步，先取出风鸣铃核对旧案线索。",
        encoding="utf-8",
    )
    if with_judgement:
        (branch_dir / "worldline_judgement.json").write_text(
            json.dumps(
                {
                    "recommendation": "推荐继续",
                    "scores": {"overall": 0.82},
                    "warnings": ["伏笔仍需后续兑现"],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    return run_id, branch_id


def _write_causal_diff(outputs, run_id: str, branch_id: str):
    branch_dir = outputs / run_id / branch_id
    (branch_dir / "causal_diff.json").write_text(
        json.dumps(
            {
                "status": "ready",
                "blocks": [
                    {
                        "id": "wind-bell",
                        "title": "风鸣铃提前曝光",
                        "risk": "medium",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _write_replay_range(
    outputs,
    *,
    risk_level: str = "medium",
    missing_entities: list[str] | None = None,
):
    missing = ["风鸣铃"] if missing_entities is None else missing_entities
    baseline_dir = outputs / "run_v090_baseline"
    baseline_dir.mkdir()
    (baseline_dir / "meta.json").write_text(
        json.dumps(
            {"story_slug": "export-story", "source_kind": "imported"},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (baseline_dir / "baseline_report.json").write_text(
        json.dumps(
            {
                "story_slug": "export-story",
                "branch_id": "baseline",
                "summary": "无干预基线已生成。",
                "created_at": "2026-05-31T12:00:00Z",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (baseline_dir / "canon_replay_range_report.json").write_text(
        json.dumps(
            {
                "chapter_range": {"start": 1, "end": 2},
                "available_chapters": [1, 2, 3],
                "summary": {
                    "chapter_count": 2,
                    "average_overall": 0.92 if risk_level == "low" else 0.74,
                    "risk_level": risk_level,
                    "weakest_chapter": 2,
                    "warning_count": 0 if not missing else 1,
                },
                "risk_dimensions": []
                if not missing
                else [
                    {
                        "key": "entity_missing",
                        "label": "实体缺失",
                        "level": risk_level,
                        "detail": "风鸣铃在回放中缺失。",
                    }
                ],
                "entity_audit": {
                    "matched_entities": ["赵轩"],
                    "missing_entities": missing,
                    "missing_entities_by_chapter": [
                        {"chapter": 2, "entities": ["风鸣铃"]}
                    ]
                    if missing
                    else [],
                },
                "created_at": "2026-05-31T12:01:00Z",
            },
            ensure_ascii=False,
        ),
            encoding="utf-8",
        )


def _write_baseline_run(outputs):
    baseline_dir = outputs / "run_v090_baseline"
    baseline_dir.mkdir()
    (baseline_dir / "meta.json").write_text(
        json.dumps(
            {"story_slug": "export-story", "source_kind": "imported"},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (baseline_dir / "baseline_report.json").write_text(
        json.dumps(
            {
                "story_slug": "export-story",
                "branch_id": "baseline",
                "summary": "无干预基线已生成。",
                "created_at": "2026-05-31T12:00:00Z",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _write_clean_consistency_report(projects):
    report_path = projects / "export-story" / "memory" / "consistency_report.json"
    report_path.write_text(
        json.dumps(
            {
                "version": "test-clean",
                "summary": {"issue_count": 0, "risk_level": "low"},
                "persona_drift": [],
                "timeline_conflicts": [],
                "resource_conflicts": [],
                "contract_violations": [],
                "forgotten_threads": [],
                "repair_suggestions": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _write_child_continue_run(outputs, parent_run_id: str, parent_branch_id: str):
    child_run_id = "run_v090_child"
    run_dir = outputs / child_run_id
    branch_dir = run_dir / "linear"
    branch_dir.mkdir(parents=True)
    (run_dir / "meta.json").write_text(
        json.dumps(
            {
                "kind": "resume_continue",
                "story_slug": "export-story",
                "source_kind": "imported",
                "parent_run_id": parent_run_id,
                "parent_branch": parent_branch_id,
                "current_chapter": 8,
                "lineage": [parent_run_id, child_run_id],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (branch_dir / "events.json").write_text(
        json.dumps({"theme": "顺势续写"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (branch_dir / "state_snapshot.json").write_text(
        json.dumps({"characters": {"zhao_xuan": {"name": "赵轩"}}}, ensure_ascii=False),
        encoding="utf-8",
    )
    (branch_dir / "chapter.md").write_text(
        "# 第八章 风声入卷\n\n赵轩循着风鸣铃余音，写下第二条证词。",
        encoding="utf-8",
    )
    return child_run_id, "linear"


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i:03d}.md",
            "content": (
                f"第{i}章 创作闭环\n"
                f"赵轩在归云斋整理第 {i} 章线索，沈冰月记录风鸣铃的回响。"
            ),
        }
        for i in range(1, n + 1)
    ]


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
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


@pytest.fixture
def isolated_dirs(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
    return outputs


@pytest.fixture
def isolated_story_dirs(tmp_path, monkeypatch):
    projects = tmp_path / "projects"
    outputs = tmp_path / "outputs"
    projects.mkdir()
    outputs.mkdir()
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(projects))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setattr(indexer, "projects_dir", lambda: projects)
    monkeypatch.setattr(indexer, "outputs_dir", lambda: outputs)
    return projects, outputs


@pytest.fixture
def running_server(isolated_dirs):
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port, isolated_dirs
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_chapter_export_contains_source_ai_notice_and_judgement(isolated_dirs):
    _, build_chapter_export, _ = _chapter_export_api()
    run_id, branch_id = _write_branch(isolated_dirs)

    export = build_chapter_export(
        run_id=run_id,
        branch_id=branch_id,
        outputs_dir=isolated_dirs,
    )

    assert export["version"] == "v0.9.0-alpha"
    assert export["kind"] == "chapter_export"
    assert export["story_slug"] == "export-story"
    assert export["filename"].endswith(".md")
    assert export["metadata"]["source_kind"] == "imported"
    assert export["metadata"]["branch_label"] == "提前查证"
    assert export["metadata"]["judgement_recommendation"] == "推荐继续"
    assert "AI 生成说明" in export["content_md"]
    assert "来源说明" in export["content_md"]
    assert "版权与分享边界" in export["content_md"]
    assert export["share_guard"]["public_share_allowed"] is False
    assert export["share_guard"]["requires_rights_confirmation"] is True
    assert "赵轩在归云斋前停步" in export["content_md"]


def test_chapter_export_rejects_bad_id_and_missing_chapter(isolated_dirs):
    ChapterExportRequestError, build_chapter_export, _ = _chapter_export_api()

    with pytest.raises(ChapterExportRequestError):
        build_chapter_export(
            run_id="../outside",
            branch_id="branch_a",
            outputs_dir=isolated_dirs,
        )

    with pytest.raises(FileNotFoundError):
        build_chapter_export(
            run_id="run_missing",
            branch_id="branch_a",
            outputs_dir=isolated_dirs,
        )


def test_chapter_collection_export_orders_parent_and_child_chapters(isolated_dirs):
    _, _, build_chapter_collection_export = _chapter_export_api()
    parent_run_id, parent_branch_id = _write_branch(isolated_dirs)
    child_run_id, child_branch_id = _write_child_continue_run(
        isolated_dirs,
        parent_run_id,
        parent_branch_id,
    )

    export = build_chapter_collection_export(
        run_id=child_run_id,
        branch_id=child_branch_id,
        outputs_dir=isolated_dirs,
    )

    assert export["kind"] == "chapter_collection_export"
    assert export["chapter_count"] == 2
    assert export["chapters"][0]["run_id"] == parent_run_id
    assert export["chapters"][1]["run_id"] == child_run_id
    assert export["content_md"].find("第七章 风鸣旧案") < export["content_md"].find(
        "第八章 风声入卷"
    )
    assert "AI 生成说明" in export["content_md"]
    assert "版权与分享边界" in export["content_md"]
    assert "不导出上传原作全文" in export["content_md"]
    assert export["share_guard"]["public_share_allowed"] is False
    assert export["share_guard"]["requires_rights_confirmation"] is True


def test_http_chapter_export_statuses(running_server):
    port, outputs = running_server
    run_id, branch_id = _write_branch(outputs)

    status, body = _get(port, f"/api/runs/{run_id}/branches/{branch_id}/chapter-export")
    assert status == 200
    assert body["kind"] == "chapter_export"
    assert "导出章节" in body["content_md"]

    bad_status, bad = _get(port, "/api/runs/..%2Foutside/branches/branch_a/chapter-export")
    assert bad_status == 400
    assert bad["error"] == "invalid run_id or branch_id"

    missing_status, missing = _get(
        port,
        "/api/runs/run_missing/branches/branch_a/chapter-export",
    )
    assert missing_status == 404
    assert "章节不存在" in missing["error"]


def test_http_chapter_collection_export_statuses(running_server):
    port, outputs = running_server
    parent_run_id, parent_branch_id = _write_branch(outputs)
    child_run_id, child_branch_id = _write_child_continue_run(
        outputs,
        parent_run_id,
        parent_branch_id,
    )

    status, body = _get(
        port,
        f"/api/runs/{child_run_id}/branches/{child_branch_id}/chapter-collection-export",
    )
    assert status == 200
    assert body["kind"] == "chapter_collection_export"
    assert body["chapter_count"] == 2

    bad_status, bad = _get(
        port,
        "/api/runs/..%2Foutside/branches/branch_a/chapter-collection-export",
    )
    assert bad_status == 400
    assert bad["error"] == "invalid run_id or branch_id"


def test_project_workspace_creation_loop_recommends_exportable_worldline(
    isolated_story_dirs,
):
    projects, outputs = isolated_story_dirs
    import_novel_from_payload(
        name="export-story",
        chapters=_chapters(6),
        mock=True,
        long_mode=True,
        projects_dir=projects,
    )
    run_id, branch_id = _write_branch(outputs)

    workspace = indexer.get_project_workspace("export-story")
    loop = workspace["creation_loop"]

    assert loop["version"] == "v0.9.0-alpha"
    assert loop["status"] == "ready"
    assert loop["recommended"]["run_id"] == run_id
    assert loop["recommended"]["branch_id"] == branch_id
    assert loop["recommended"]["has_export"] is True
    assert loop["recommended"]["has_judgement"] is True
    assert loop["recommended"]["overall_score"] == 0.82
    assert loop["recommended"]["continue_hint"].startswith("lne resume continue")
    assert loop["checklist"][0]["status"] == "done"
    assert any(step["id"] == "chapter_export" for step in loop["checklist"])
    assert any(step["id"] == "export_share_guard" for step in loop["checklist"])
    assert loop["completion"]["kind"] == "creation_loop_completion"
    assert loop["completion"]["status"] == "todo"
    assert "选择后审计" in loop["completion"]["blocking_labels"]
    closeout = loop["closeout"]
    assert closeout["kind"] == "creation_loop_alpha_closeout"
    assert closeout["status"] == "not_ready"
    assert closeout["can_close_alpha"] is False
    assert "选择后审计" in closeout["remaining_blockers"]
    evidence = loop["completion"]["evidence"]
    assert [item["id"] for item in evidence] == [
        item["id"] for item in loop["checklist"]
    ]
    judgement_evidence = next(
        item for item in evidence if item["id"] == "worldline_judgement"
    )
    export_evidence = next(item for item in evidence if item["id"] == "chapter_export")
    audit_evidence = next(item for item in evidence if item["id"] == "post_run_audit")
    assert judgement_evidence["source"] == "artifact"
    assert judgement_evidence["ref"] == "worldline_judgement.json"
    assert export_evidence["source"] == "api"
    assert export_evidence["ref"].endswith("/chapter-export")
    assert audit_evidence["source"] == "route"
    assert audit_evidence["ref"] == "#/anchor/export-story"
    assert any("继续推荐世界线" in step for step in loop["next_steps"])


def test_creation_loop_completion_exposes_actions_for_blockers(
    isolated_story_dirs,
):
    projects, outputs = isolated_story_dirs
    import_novel_from_payload(
        name="export-story",
        chapters=_chapters(6),
        mock=True,
        long_mode=True,
        projects_dir=projects,
    )
    run_id, branch_id = _write_branch(
        outputs,
        run_id="run_v090_needs_actions",
        with_judgement=False,
    )

    loop = indexer.get_project_workspace("export-story")["creation_loop"]
    actions = loop["completion"]["actions"]

    judgement = next(action for action in actions if action["id"] == "worldline_judgement")
    selection = next(action for action in actions if action["id"] == "select_worldline")
    replay = next(action for action in actions if action["id"] == "replay_audit")
    assert judgement["status"] == "available"
    assert judgement["method"] == "POST"
    assert judgement["api_path"] == (
        f"/api/runs/{run_id}/branches/{branch_id}/worldline-judgement"
    )
    assert selection["api_path"] == "/api/stories/export-story/selected-worldline"
    assert replay["route_hash"] == "#/anchor/export-story"
    judgement_evidence = next(
        item
        for item in loop["completion"]["evidence"]
        if item["id"] == "worldline_judgement"
    )
    assert judgement_evidence["source"] == "api"
    assert judgement_evidence["ref"] == judgement["api_path"]


def test_creation_loop_offers_replay_range_action_after_selection(
    isolated_story_dirs,
):
    projects, outputs = isolated_story_dirs
    import_novel_from_payload(
        name="export-story",
        chapters=_chapters(6),
        mock=True,
        long_mode=True,
        projects_dir=projects,
    )
    run_id, branch_id = _write_branch(outputs)
    _write_causal_diff(outputs, run_id, branch_id)
    _write_baseline_run(outputs)
    write_holdout(
        "export-story",
        chapters=[
            {"chapter": 7, "title": "第七章 正史", "content": "赵轩追查风鸣铃。"},
            {"chapter": 8, "title": "第八章 正史", "content": "风鸣铃牵出旧案。"},
        ],
        projects_dir=projects,
    )
    _, _, select_worldline = _worldline_selection_api()
    select_worldline(story_slug="export-story", run_id=run_id, branch_id=branch_id)

    loop = indexer.get_project_workspace("export-story")["creation_loop"]
    actions = loop["completion"]["actions"]
    replay = next(action for action in actions if action["id"] == "run_replay_range")

    assert replay["method"] == "POST"
    assert replay["api_path"] == "/api/stories/export-story/canon/replay-range"
    assert replay["payload"] == {
        "baseline_run_id": "run_v090_baseline",
        "baseline_branch_id": "baseline",
        "chapter_start": 7,
        "chapter_end": 8,
    }


def test_resume_continue_service_writes_linear_child_run(isolated_dirs, monkeypatch):
    monkeypatch.setenv("LNE_MOCK", "1")
    ResumeContinueRequestError, run_resume_continue = _resume_continue_api()

    parent = run_intervention(
        story_slug="tianhuang-night",
        target="lin_wan_zhou",
        content="愿你今夜慎行。",
        branches=2,
        rounds=1,
        mock=True,
    )

    result = run_resume_continue(
        run_id=parent.run_id,
        branch_id=parent.branch_ids[0],
        rounds=1,
        mock=True,
    )

    assert result.parent_run_id == parent.run_id
    assert result.parent_branch_id == parent.branch_ids[0]
    assert result.branch_id == "linear"
    assert result.story_slug == "tianhuang-night"
    assert result.chapter_number >= 14
    assert (result.run_dir / "meta.json").exists()
    assert (result.run_dir / "linear" / "chapter.md").read_text(encoding="utf-8").strip()
    assert not (result.run_dir / "intervention.json").exists()

    with pytest.raises(ResumeContinueRequestError):
        run_resume_continue(run_id="../outside", branch_id="branch_a", mock=True)


def test_worldline_selection_persists_into_creation_loop(isolated_story_dirs):
    projects, outputs = isolated_story_dirs
    import_novel_from_payload(
        name="export-story",
        chapters=_chapters(6),
        mock=True,
        long_mode=True,
        projects_dir=projects,
    )
    run_id, branch_id = _write_branch(outputs)
    WorldlineSelectionRequestError, get_selected_worldline, select_worldline = (
        _worldline_selection_api()
    )

    selection = select_worldline(
        story_slug="export-story",
        run_id=run_id,
        branch_id=branch_id,
        note="继续赵轩提前查证这条线。",
    )

    assert selection["status"] == "ready"
    assert selection["run_id"] == run_id
    assert selection["branch_id"] == branch_id
    assert selection["branch_label"] == "提前查证"
    assert "继续赵轩" in selection["note"]

    stored = get_selected_worldline("export-story")
    assert stored["run_id"] == run_id
    workspace = indexer.get_project_workspace("export-story")
    assert workspace["creation_loop"]["selected"]["run_id"] == run_id
    assert workspace["creation_loop"]["selected"]["branch_id"] == branch_id

    with pytest.raises(WorldlineSelectionRequestError):
        select_worldline(
            story_slug="export-story",
            run_id="../outside",
            branch_id=branch_id,
        )


def test_creation_loop_surfaces_selected_worldline_post_run_audit(
    isolated_story_dirs,
):
    projects, outputs = isolated_story_dirs
    import_novel_from_payload(
        name="export-story",
        chapters=_chapters(6),
        mock=True,
        long_mode=True,
        projects_dir=projects,
    )
    run_id, branch_id = _write_branch(outputs)
    _write_causal_diff(outputs, run_id, branch_id)
    _write_replay_range(outputs)
    _, _, select_worldline = _worldline_selection_api()
    select_worldline(
        story_slug="export-story",
        run_id=run_id,
        branch_id=branch_id,
        note="先围绕风鸣铃线继续。",
    )

    loop = indexer.get_project_workspace("export-story")["creation_loop"]
    post_audit = loop["post_run_audit"]

    assert post_audit["status"] == "warn"
    assert post_audit["selected_run_id"] == run_id
    assert post_audit["selected_branch_id"] == branch_id
    assert post_audit["has_range_replay"] is True
    assert post_audit["risk_level"] == "medium"
    assert post_audit["missing_entities"] == ["风鸣铃"]
    assert post_audit["review_hash"] == "#/anchor/export-story"
    assert any("回放与审计" in action for action in post_audit["next_actions"])
    assert any(item["id"] == "post_run_audit" for item in loop["checklist"])
    completion = loop["completion"]
    assert completion["status"] == "warn"
    assert completion["done_count"] < completion["total_count"]
    assert "选择后审计" in completion["blocking_labels"]
    assert completion["can_mark_alpha_complete"] is False


def test_creation_loop_ready_state_marks_alpha_closeable(isolated_story_dirs):
    projects, outputs = isolated_story_dirs
    import_novel_from_payload(
        name="export-story",
        chapters=_chapters(6),
        mock=True,
        long_mode=True,
        projects_dir=projects,
    )
    run_id, branch_id = _write_branch(outputs)
    _write_causal_diff(outputs, run_id, branch_id)
    _write_clean_consistency_report(projects)
    _write_replay_range(outputs, risk_level="low", missing_entities=[])
    _, _, select_worldline = _worldline_selection_api()
    select_worldline(
        story_slug="export-story",
        run_id=run_id,
        branch_id=branch_id,
        note="低风险世界线可进入 alpha 收口。",
    )

    loop = indexer.get_project_workspace("export-story")["creation_loop"]
    completion = loop["completion"]
    closeout = loop["closeout"]

    assert completion["status"] == "ready"
    assert completion["done_count"] == completion["total_count"]
    assert completion["blocking_ids"] == []
    assert completion["actions"] == []
    assert completion["can_mark_alpha_complete"] is True
    assert closeout["kind"] == "creation_loop_alpha_closeout"
    assert closeout["status"] == "ready"
    assert closeout["can_close_alpha"] is True
    assert closeout["ready_count"] == closeout["required_count"]
    assert closeout["remaining_blockers"] == []
    assert [item["id"] for item in closeout["evidence"]] == [
        item["id"] for item in loop["checklist"]
    ]


def test_http_worldline_selection_statuses(isolated_story_dirs):
    projects, outputs = isolated_story_dirs
    import_novel_from_payload(
        name="export-story",
        chapters=_chapters(6),
        mock=True,
        long_mode=True,
        projects_dir=projects,
    )
    run_id, branch_id = _write_branch(outputs)
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _post(
            port,
            "/api/stories/export-story/selected-worldline",
            {"run_id": run_id, "branch_id": branch_id, "note": "设为下一章起点"},
        )
        assert status == 200
        assert body["selection"]["run_id"] == run_id
        assert body["selection"]["branch_label"] == "提前查证"

        get_status, selected = _get(port, "/api/stories/export-story/selected-worldline")
        assert get_status == 200
        assert selected["selection"]["branch_id"] == branch_id

        bad_status, bad = _post(
            port,
            "/api/stories/export-story/selected-worldline",
            {"run_id": "../outside", "branch_id": branch_id},
        )
        assert bad_status == 400
        assert "run_id" in bad["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()

"""v0.9.2 MasterSetting Workspace Lite: safe master_setting.yaml edits."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest
import yaml

from living_novel_engine.browser import server
from living_novel_engine.service import (
    MasterSettingConflictError,
    MasterSettingUpdateError,
    get_project_audit_log,
    import_novel_from_payload,
    update_master_setting,
)


def _chapters(n: int = 6) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i:03d}.md",
            "content": f"第{i}章 设定轻编辑\n赵轩在归云斋记录第 {i} 条世界规则。",
        }
        for i in range(1, n + 1)
    ]


def _patch() -> dict:
    return {
        "display_name": "归云斋异闻录",
        "genre": "东方玄幻",
        "world_rules": ["角色不得无故 OOC", "新增设定必须能追溯到已导入章节"],
        "power_system_limits": ["凡人不可正面击败高境修士"],
        "forbidden_additions": ["系统", "穿越", "前世记忆"],
    }


def _make_project(tmp_path, slug: str = "master-edit"):
    import_novel_from_payload(
        name=slug,
        chapters=_chapters(),
        mock=True,
        long_mode=True,
        projects_dir=tmp_path,
    )
    return tmp_path / slug


def test_update_master_setting_writes_backup_and_report(tmp_path):
    project_dir = _make_project(tmp_path)

    result = update_master_setting("master-edit", _patch(), projects_dir=tmp_path)

    assert result.changed == [
        "display_name",
        "genre",
        "world_rules",
        "power_system_limits",
        "forbidden_additions",
    ]
    assert result.backup_dir is not None
    assert (result.backup_dir / "memory" / "master_setting.yaml").exists()

    data = yaml.safe_load(
        (project_dir / "memory" / "master_setting.yaml").read_text(encoding="utf-8")
    )
    assert data["display_name"] == "归云斋异闻录"
    assert data["world_rules"] == ["角色不得无故 OOC", "新增设定必须能追溯到已导入章节"]

    report = json.loads(
        (project_dir / "memory" / "master_setting_update_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["version"] == "v0.9.2"
    assert report["status"] == "saved"
    assert report["changed"] == result.changed
    assert report["backup"].endswith("/memory/master_setting.yaml")


def test_update_master_setting_appends_audit_event(tmp_path):
    _make_project(tmp_path, "master-audit")

    update_master_setting("master-audit", _patch(), projects_dir=tmp_path)
    audit = get_project_audit_log("master-audit", projects_dir=tmp_path)

    event = next(
        event
        for event in audit["events"]
        if event["action"] == "master_setting_updated"
        and event["artifact"] == "memory/project_audit_log.jsonl"
    )
    assert event["metadata"]["artifact_path"] == "memory/master_setting.yaml"
    assert event["metadata"]["changed"] == [
        "display_name",
        "genre",
        "world_rules",
        "power_system_limits",
        "forbidden_additions",
    ]


def test_update_master_setting_rejects_uneditable_payload(tmp_path):
    _make_project(tmp_path, "master-nochange")

    with pytest.raises(MasterSettingUpdateError):
        update_master_setting(
            "master-nochange",
            {"source_refs": ["hacked.yaml"]},
            projects_dir=tmp_path,
        )


def test_update_master_setting_rejects_damaged_yaml_without_report(tmp_path):
    project_dir = _make_project(tmp_path, "master-damaged")
    (project_dir / "memory" / "master_setting.yaml").write_text(
        "world_rules: [", encoding="utf-8"
    )

    with pytest.raises(MasterSettingConflictError):
        update_master_setting("master-damaged", _patch(), projects_dir=tmp_path)

    assert not (project_dir / "memory" / "master_setting_update_report.json").exists()


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LNE_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(tmp_path / "_outputs"))
    _make_project(tmp_path, "master-http")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port, tmp_path
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
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def test_master_setting_update_http_success(running_server):
    port, _ = running_server

    status, body = _post(port, "/api/stories/master-http/master-setting", _patch())

    assert status == 200
    assert body["changed"]
    assert body["backup"]
    master = body["master_setting_workspace"]
    assert master["status"] == "ready"
    assert master["mode"] == "lite_edit"
    assert master["capabilities"]["can_edit"] is True
    assert master["world"]["display_name"] == "归云斋异闻录"
    assert master["summary"]["world_rule_count"] == 2


def test_master_setting_update_http_statuses(running_server):
    port, tmp_path = running_server

    bad_status, bad = _post(port, "/api/stories/..%2Fx/master-setting", _patch())
    assert bad_status == 400
    assert bad["error"] == "invalid slug"

    missing_status, _missing = _post(port, "/api/stories/ghost/master-setting", _patch())
    assert missing_status == 404

    (tmp_path / "master-http" / "memory" / "master_setting.yaml").write_text(
        "world_rules: [", encoding="utf-8"
    )
    damaged_status, damaged = _post(
        port, "/api/stories/master-http/master-setting", _patch()
    )
    assert damaged_status == 409
    assert "master_setting.yaml" in damaged["error"]

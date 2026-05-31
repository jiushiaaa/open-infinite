"""v1.0-beta Permission Matrix Draft-C：只读权限矩阵草案。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.request

from living_novel_engine.browser import server
from living_novel_engine.service import get_permission_matrix_draft


def test_permission_matrix_declares_roles_resources_and_no_enforcement(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-permission-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-permission-secret-8899")

    matrix = get_permission_matrix_draft()
    text = json.dumps(matrix, ensure_ascii=False)

    assert matrix["version"] == "v1.0-beta-permission-matrix-draft-c"
    assert matrix["status"] == "draft"
    assert matrix["enforcement"]["mode"] == "not_enforced"
    assert {role["id"] for role in matrix["roles"]} == {"owner", "editor", "viewer"}
    resource_ids = {resource["id"] for resource in matrix["resources"]}
    assert {
        "project_workspace",
        "master_setting",
        "worldline_selection",
        "generation_actions",
        "audit_log",
        "exports",
    }.issubset(resource_ids)

    by_resource = {resource["id"]: resource for resource in matrix["resources"]}
    assert by_resource["master_setting"]["permissions"]["viewer"] == ["read"]
    assert "write" not in by_resource["master_setting"]["permissions"]["viewer"]
    assert "write" in by_resource["master_setting"]["permissions"]["editor"]
    assert by_resource["generation_actions"]["permissions"]["viewer"] == ["read_status"]
    assert "permission-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_permission_matrix_http(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    monkeypatch.setenv("LNE_MOCK", "1")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/settings/permission-matrix",
            timeout=10,
        ) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert body["version"] == "v1.0-beta-permission-matrix-draft-c"
    assert body["enforcement"]["mode"] == "not_enforced"
    assert any(item["id"] == "audit_log" for item in body["resources"])

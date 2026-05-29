"""v0.7 第三刀：Causal Diff 确立/抹除/回滚（service + POST /api/diffs/action）。"""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import indexer, server
from living_novel_engine.service import (
    DiffActionError,
    DiffNotFoundError,
    apply_diff_action,
)

_DIFF = {
    "diff_id": "diff_abc123",
    "branch_id": "branch_a",
    "lineage_type": "divergent_worldline",
    "diff_mode": "local_divergence",
    "status": "proposed",
    "intervention_summary": {"intervention_type": "forced_action"},
    "affected_scope": {"characters": ["lin_wan_zhou"]},
    "blocks": [
        {"id": "branch_a_blk_0", "op": "replace", "old_text": "旧", "new_text": "新"},
        {"id": "branch_a_blk_1", "op": "insert", "old_text": "", "new_text": "增"},
    ],
    "reason": "",
    "created_at": "2026-05-29T10:00:00",
    "compiler_version": "v0.7.1-C",
    "accepted_at": None,
    "rejected_at": None,
    "reverted_from": None,
    "parent_diff_id": None,
}


def _write_diff(outputs_dir, run_id="run_x", branch_id="branch_a", diff=None):
    bdir = outputs_dir / run_id / branch_id
    bdir.mkdir(parents=True)
    (bdir / "causal_diff.json").write_text(
        json.dumps(diff or _DIFF, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return bdir / "causal_diff.json"


# ── service 层 ────────────────────────────────────────────


class TestService:
    def test_accept(self, tmp_path):
        path = _write_diff(tmp_path)
        art = apply_diff_action(
            outputs_dir=tmp_path, run_id="run_x", branch_id="branch_a", action="accept"
        )
        assert art["status"] == "accepted"
        assert art["accepted_at"]
        # 旧字段保留
        assert art["diff_id"] == "diff_abc123"
        assert len(art["blocks"]) == 2
        # 落盘一致
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        assert on_disk["status"] == "accepted"

    def test_reject(self, tmp_path):
        _write_diff(tmp_path)
        art = apply_diff_action(
            outputs_dir=tmp_path, run_id="run_x", branch_id="branch_a", action="reject"
        )
        assert art["status"] == "rejected"
        assert art["rejected_at"]

    def test_revert_points_to_diff_id(self, tmp_path):
        _write_diff(tmp_path)
        art = apply_diff_action(
            outputs_dir=tmp_path, run_id="run_x", branch_id="branch_a", action="revert"
        )
        assert art["status"] == "reverted"
        assert art["reverted_from"] == "diff_abc123"

    def test_block_level_only(self, tmp_path):
        _write_diff(tmp_path)
        art = apply_diff_action(
            outputs_dir=tmp_path,
            run_id="run_x",
            branch_id="branch_a",
            action="accept",
            block_id="branch_a_blk_1",
        )
        # 整体状态不变，仅块级改
        assert art["status"] == "proposed"
        blk = next(b for b in art["blocks"] if b["id"] == "branch_a_blk_1")
        assert blk["status"] == "accepted"

    def test_unknown_block(self, tmp_path):
        _write_diff(tmp_path)
        with pytest.raises(DiffActionError):
            apply_diff_action(
                outputs_dir=tmp_path,
                run_id="run_x",
                branch_id="branch_a",
                action="accept",
                block_id="nope",
            )

    def test_bad_action(self, tmp_path):
        _write_diff(tmp_path)
        with pytest.raises(DiffActionError):
            apply_diff_action(
                outputs_dir=tmp_path, run_id="run_x", branch_id="branch_a", action="explode"
            )

    def test_missing_diff(self, tmp_path):
        with pytest.raises(DiffNotFoundError):
            apply_diff_action(
                outputs_dir=tmp_path, run_id="run_x", branch_id="branch_a", action="accept"
            )


# ── HTTP POST /api/diffs/action ───────────────────────────


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(tmp_path, monkeypatch):
    monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
    _write_diff(tmp_path)
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port, tmp_path
    finally:
        httpd.shutdown()
        httpd.server_close()


def _post(port: int, payload: dict) -> tuple[int, dict]:
    url = f"http://127.0.0.1:{port}/api/diffs/action"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


class TestPostApi:
    def test_accept_success(self, running_server):
        port, base = running_server
        status, body = _post(port, {"run_id": "run_x", "branch_id": "branch_a", "action": "accept"})
        assert status == 200, body
        assert body["causal_diff"]["status"] == "accepted"
        on_disk = json.loads((base / "run_x" / "branch_a" / "causal_diff.json").read_text("utf-8"))
        assert on_disk["status"] == "accepted"

    def test_missing_diff_404(self, running_server):
        port, _ = running_server
        status, body = _post(port, {"run_id": "run_x", "branch_id": "branch_z", "action": "accept"})
        assert status == 404
        assert "error" in body

    def test_bad_action_400(self, running_server):
        port, _ = running_server
        status, body = _post(port, {"run_id": "run_x", "branch_id": "branch_a", "action": "nuke"})
        assert status == 400
        assert "action" in body["error"]

    def test_path_traversal_rejected(self, running_server):
        port, _ = running_server
        status, body = _post(port, {"run_id": "..", "branch_id": "branch_a", "action": "accept"})
        assert status == 400
        assert "invalid" in body["error"].lower()

    def test_get_still_works(self, running_server):
        port, _ = running_server
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/stories", timeout=5) as resp:
            assert resp.status == 200

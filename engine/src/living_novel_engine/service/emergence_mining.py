"""v0.8+ Emergence Mining service.

读取 run 目录下的既有 artifact，写/读 ``emergence_nodes.json``。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from living_novel_engine.emergence_mining import write_emergence_nodes

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_REPORT_NAME = "emergence_nodes.json"


class EmergenceMiningRequestError(ValueError):
    """入参非法或报告损坏 —— 映射为 HTTP 400。"""


def _validate_identifier(value: str | None, label: str) -> str:
    ident = (value or "").strip()
    if not ident:
        raise EmergenceMiningRequestError(f"缺少 {label}")
    if ".." in ident or not _SAFE_ID_RE.match(ident):
        raise EmergenceMiningRequestError(f"{label} 非法")
    return ident


def _outputs_root(outputs_dir: Path | None) -> Path:
    if outputs_dir is not None:
        return outputs_dir
    from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir

    return default_outputs_dir()


def mine_run_emergence(run_id: str, *, outputs_dir: Path | None = None) -> dict:
    rid = _validate_identifier(run_id, "run_id")
    run_dir = _outputs_root(outputs_dir) / rid
    if not run_dir.is_dir():
        raise FileNotFoundError(f"run 不存在: {rid}")
    return write_emergence_nodes(run_dir)


def get_emergence_nodes(run_id: str, *, outputs_dir: Path | None = None) -> dict:
    rid = _validate_identifier(run_id, "run_id")
    path = _outputs_root(outputs_dir) / rid / _REPORT_NAME
    if not path.exists():
        raise FileNotFoundError(f"涌现节点报告不存在: {rid}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise EmergenceMiningRequestError(f"涌现节点报告损坏: {rid}") from exc
    return data if isinstance(data, dict) else {}

"""v0.7 第三刀：Causal Diff 确立 / 抹除 / 回滚（artifact 状态写回）。

只改 `causal_diff.json` 的状态字段，**不重写 chapter.md 正文、不改 state_snapshot.json、
不做文本合并、不删 run**。读原始 dict 后原地改键再 dump，保证旧字段全部保留。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

VALID_ACTIONS = ("accept", "reject", "revert")

_STATUS_BY_ACTION = {
    "accept": "accepted",
    "reject": "rejected",
    "revert": "reverted",
}
_TIMESTAMP_FIELD = {
    "accept": "accepted_at",
    "reject": "rejected_at",
}


class DiffActionError(ValueError):
    """入参非法（未知 action / 未知 block_id / 损坏 JSON）——映射为 HTTP 400。"""


class DiffNotFoundError(FileNotFoundError):
    """run / branch / causal_diff.json 不存在——映射为 HTTP 404。"""


def apply_diff_action(
    *,
    outputs_dir: Path,
    run_id: str,
    branch_id: str,
    action: str,
    block_id: str | None = None,
) -> dict[str, Any]:
    """对一个分支的 causal_diff.json 施加状态写回，返回更新后的 artifact dict。"""
    if not run_id or not branch_id:
        raise DiffActionError("缺少 run_id 或 branch_id")
    if action not in VALID_ACTIONS:
        raise DiffActionError(
            f"未知 action: {action!r}，应为 {', '.join(VALID_ACTIONS)}"
        )

    path = outputs_dir / run_id / branch_id / "causal_diff.json"
    if not path.exists():
        raise DiffNotFoundError(f"未找到 causal_diff: {run_id}/{branch_id}")

    try:
        artifact: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise DiffActionError(f"causal_diff.json 无法读取或损坏：{exc}") from exc
    if not isinstance(artifact, dict):
        raise DiffActionError("causal_diff.json 结构异常（顶层非对象）")

    status = _STATUS_BY_ACTION[action]
    now = datetime.now().isoformat()

    if block_id:
        _apply_to_block(artifact, block_id, status)
    else:
        _apply_to_artifact(artifact, action, status, now)

    path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return artifact


def _apply_to_block(artifact: dict[str, Any], block_id: str, status: str) -> None:
    blocks = artifact.get("blocks")
    block = None
    if isinstance(blocks, list):
        block = next(
            (b for b in blocks if isinstance(b, dict) and b.get("id") == block_id),
            None,
        )
    if block is None:
        raise DiffActionError(f"未知 block_id: {block_id}")
    # 仅改块级状态，保留 artifact 级状态（单块采纳不代表整条世界线被确立）。
    block["status"] = status


def _apply_to_artifact(
    artifact: dict[str, Any], action: str, status: str, now: str
) -> None:
    artifact["status"] = status
    ts_field = _TIMESTAMP_FIELD.get(action)
    if ts_field:
        artifact[ts_field] = now
    if action == "revert":
        # reverted_from 指向自身 diff_id（记录被回滚的来源）。
        artifact["reverted_from"] = artifact.get("diff_id")

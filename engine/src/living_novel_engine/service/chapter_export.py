"""v0.9.0-alpha: export a selected worldline chapter as Markdown."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id

BRANCH_ORDER = ("branch_a", "branch_b", "branch_c", "branch_d")


class ChapterExportRequestError(ValueError):
    """Invalid export request, mapped to HTTP 400."""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _branch_label(
    *,
    branch_id: str,
    theme: str,
    compilation: dict[str, Any],
) -> str:
    axis = compilation.get("branch_axis")
    if isinstance(axis, list):
        for item in axis:
            if isinstance(item, dict) and item.get("branch_id") == branch_id:
                return str(item.get("label") or theme or branch_id)
        try:
            idx = BRANCH_ORDER.index(branch_id)
        except ValueError:
            idx = -1
        if 0 <= idx < len(axis):
            item = axis[idx]
            if isinstance(item, dict):
                return str(item.get("label") or theme or branch_id)
    return theme or ("顺势续写" if branch_id == "linear" else branch_id)


def _share_guard(source_kind: str) -> dict[str, Any]:
    normalized = (source_kind or "unknown").lower()
    source_warning = (
        "来源包含用户上传或未知文本，默认不提供公开分享授权。"
        if normalized not in {"builtin", "genesis"}
        else "来源为内置样例或生成内容时，公开分享前仍需确认素材授权和平台规则。"
    )
    return {
        "kind": "export_share_guard",
        "status": "rights_confirmation_required",
        "source_kind": source_kind or "unknown",
        "private_use_allowed": True,
        "public_share_allowed": False,
        "requires_rights_confirmation": True,
        "notice": "当前导出仅用于本地个人评估；公开分享、发布或商用前必须确认上传文本、生成内容和素材来源均已获得授权。",
        "warnings": [
            source_warning,
            "不要冒充原作者，不要公开分发受保护原文或可替代原作阅读的内容。",
        ],
    }


def build_chapter_export(
    *,
    run_id: str,
    branch_id: str,
    outputs_dir: Path | None = None,
) -> dict[str, Any]:
    """Build a self-contained Markdown export for one selected branch.

    This is a read-only product export layer. It does not write an artifact,
    mutate ``chapter.md``, or change runner behavior.
    """

    rid = safe_id(run_id)
    bid = safe_id(branch_id)
    if rid is None or bid is None:
        raise ChapterExportRequestError("invalid run_id or branch_id")

    root = outputs_dir or default_outputs_dir()
    run_dir = root / rid
    branch_dir = run_dir / bid
    chapter_path = branch_dir / "chapter.md"
    if not chapter_path.exists():
        raise FileNotFoundError(f"章节不存在: {rid}/{bid}")

    chapter_md = chapter_path.read_text(encoding="utf-8")
    intervention = _read_json(run_dir / "intervention.json")
    meta = _read_json(run_dir / "meta.json")
    events = _read_json(branch_dir / "events.json")
    compilation = _read_json(run_dir / "intervention_compilation.json")
    judgement = _read_json(branch_dir / "worldline_judgement.json")
    causal_diff = _read_json(branch_dir / "causal_diff.json")
    overlay = _read_json(branch_dir / "state_execution_overlay.json")

    story_slug = str(
        intervention.get("story_slug")
        or intervention.get("sample_slug")
        or meta.get("story_slug")
        or meta.get("sample_slug")
        or "unknown-story"
    )
    source_kind = str(
        intervention.get("source_kind") or meta.get("source_kind") or "unknown"
    )
    theme = str(events.get("theme") or "")
    branch_label = _branch_label(
        branch_id=bid,
        theme=theme,
        compilation=compilation,
    )
    recommendation = str(judgement.get("recommendation") or "未生成评审")
    overall = judgement.get("scores", {}).get("overall") if isinstance(
        judgement.get("scores"), dict
    ) else None
    ai_notice = (
        "本文件包含 Living Novel Engine 基于本地故事锚定、角色状态、"
        "读者干预与运行时记忆生成或推演的内容；公开使用前请自行核对版权、事实与来源。"
    )
    source_notice = (
        "本次导出只包含所选世界线的生成章节与必要元数据，不导出上传原作全文或隐藏评估集正文。"
    )
    share_guard = _share_guard(source_kind)
    safe_story_slug = safe_id(story_slug) or "story"
    filename = f"{safe_story_slug}_{rid}_{bid}_chapter.md"
    exported_at = datetime.now().isoformat(timespec="seconds")

    lines = [
        f"# 导出章节：{branch_label}",
        "",
        "## 导出信息",
        "",
        f"- 故事：`{story_slug}`",
        f"- 运行：`{rid}`",
        f"- 世界线：`{bid}`（{branch_label}）",
        f"- 来源类型：{source_kind}",
        f"- 世界线评审：{recommendation}",
    ]
    if isinstance(overall, int | float):
        lines.append(f"- 评审总分：{overall:.2f}")
    if causal_diff:
        lines.append(f"- 时空 Diff 状态：{causal_diff.get('status', '未记录')}")
    if overlay:
        lines.append("- 状态覆盖层：已显式应用低风险状态")
    lines.extend(
        [
            f"- 导出时间：{exported_at}",
            "",
            "## 来源说明",
            "",
            source_notice,
            "",
            "## AI 生成说明",
            "",
            ai_notice,
            "",
            "## 版权与分享边界",
            "",
            share_guard["notice"],
            "",
        ]
    )
    lines.extend(f"- {warning}" for warning in share_guard["warnings"])
    lines.extend(
        [
            "",
            "## 章节正文",
            "",
            chapter_md.strip(),
            "",
        ]
    )

    return {
        "version": "v0.9.0-alpha",
        "kind": "chapter_export",
        "run_id": rid,
        "branch_id": bid,
        "story_slug": story_slug,
        "filename": filename,
        "content_type": "text/markdown; charset=utf-8",
        "content_md": "\n".join(lines),
        "share_guard": share_guard,
        "metadata": {
            "source_kind": source_kind,
            "branch_label": branch_label,
            "judgement_recommendation": recommendation,
            "judgement_overall": overall,
            "causal_diff_status": causal_diff.get("status") if causal_diff else None,
            "state_overlay_applied": bool(overlay),
            "ai_notice": ai_notice,
            "source_notice": source_notice,
            "exported_at": exported_at,
        },
    }


def _story_source_for_run(run_dir: Path) -> tuple[str, str]:
    intervention = _read_json(run_dir / "intervention.json")
    meta = _read_json(run_dir / "meta.json")
    story_slug = str(
        intervention.get("story_slug")
        or intervention.get("sample_slug")
        or meta.get("story_slug")
        or meta.get("sample_slug")
        or "unknown-story"
    )
    source_kind = str(
        intervention.get("source_kind") or meta.get("source_kind") or "unknown"
    )
    return story_slug, source_kind


def _collection_item(
    *,
    run_id: str,
    branch_id: str,
    root: Path,
) -> dict[str, Any]:
    run_dir = root / run_id
    branch_dir = run_dir / branch_id
    chapter_path = branch_dir / "chapter.md"
    if not chapter_path.exists():
        raise FileNotFoundError(f"章节不存在: {run_id}/{branch_id}")
    events = _read_json(branch_dir / "events.json")
    compilation = _read_json(run_dir / "intervention_compilation.json")
    theme = str(events.get("theme") or "")
    return {
        "run_id": run_id,
        "branch_id": branch_id,
        "branch_label": _branch_label(
            branch_id=branch_id,
            theme=theme,
            compilation=compilation,
        ),
        "chapter_md": chapter_path.read_text(encoding="utf-8").strip(),
    }


def _parent_ref(run_dir: Path) -> tuple[str, str] | None:
    meta = _read_json(run_dir / "meta.json")
    parent_run_id = safe_id(str(meta.get("parent_run_id") or ""))
    parent_branch_id = safe_id(str(meta.get("parent_branch") or ""))
    if parent_run_id and parent_branch_id:
        return parent_run_id, parent_branch_id
    return None


def build_chapter_collection_export(
    *,
    run_id: str,
    branch_id: str,
    outputs_dir: Path | None = None,
) -> dict[str, Any]:
    """Build a Markdown collection along a run/branch parent chain.

    The collection is read-only. It follows ``meta.parent_run_id`` /
    ``meta.parent_branch`` backward, then renders chapters in chronological
    order. Missing ancestors degrade to warnings after the requested branch has
    been included.
    """

    rid = safe_id(run_id)
    bid = safe_id(branch_id)
    if rid is None or bid is None:
        raise ChapterExportRequestError("invalid run_id or branch_id")

    root = outputs_dir or default_outputs_dir()
    current: tuple[str, str] | None = (rid, bid)
    seen: set[tuple[str, str]] = set()
    items: list[dict[str, Any]] = []
    warnings: list[str] = []
    story_slug = "unknown-story"
    source_kind = "unknown"

    while current is not None and len(items) < 24:
        cur_run_id, cur_branch_id = current
        if current in seen:
            warnings.append("检测到父链循环，合集已在安全位置截断。")
            break
        seen.add(current)
        run_dir = root / cur_run_id
        if not run_dir.is_dir():
            if not items:
                raise FileNotFoundError(f"运行不存在: {cur_run_id}")
            warnings.append(f"父运行不存在，已停止回溯：{cur_run_id}")
            break
        try:
            items.append(
                _collection_item(
                    run_id=cur_run_id,
                    branch_id=cur_branch_id,
                    root=root,
                )
            )
        except FileNotFoundError:
            if not items:
                raise
            warnings.append(f"父分支章节缺失，已停止回溯：{cur_run_id}/{cur_branch_id}")
            break
        story_slug, source_kind = _story_source_for_run(run_dir)
        current = _parent_ref(run_dir)

    items.reverse()
    safe_story_slug = safe_id(story_slug) or "story"
    filename = f"{safe_story_slug}_{rid}_{bid}_collection.md"
    exported_at = datetime.now().isoformat(timespec="seconds")
    ai_notice = (
        "本合集包含 Living Novel Engine 沿所选世界线父链生成或推演的章节；"
        "公开使用前请自行核对版权、事实与来源。"
    )
    source_notice = (
        "本次合集只包含世界线父链中的生成章节与必要元数据，不导出上传原作全文或隐藏评估集正文。"
    )
    share_guard = _share_guard(source_kind)

    lines = [
        f"# 导出合集：{items[-1]['branch_label'] if items else bid}",
        "",
        "## 导出信息",
        "",
        f"- 故事：`{story_slug}`",
        f"- 起点：`{items[0]['run_id']}/{items[0]['branch_id']}`" if items else "",
        f"- 终点：`{rid}/{bid}`",
        f"- 来源类型：{source_kind}",
        f"- 章节数：{len(items)}",
        f"- 导出时间：{exported_at}",
    ]
    if warnings:
        lines.extend(["", "## 导出提示", ""])
        lines.extend(f"- {warning}" for warning in warnings)
    lines.extend(
        [
            "",
            "## 来源说明",
            "",
            source_notice,
            "",
            "## AI 生成说明",
            "",
            ai_notice,
            "",
            "## 版权与分享边界",
            "",
            share_guard["notice"],
            "",
        ]
    )
    lines.extend(f"- {warning}" for warning in share_guard["warnings"])
    lines.append("")
    for idx, item in enumerate(items, start=1):
        lines.extend(
            [
                f"## 第 {idx} 节 · {item['branch_label']}",
                "",
                f"> 来源：`{item['run_id']}/{item['branch_id']}`",
                "",
                item["chapter_md"],
                "",
            ]
        )

    return {
        "version": "v0.9.0-alpha",
        "kind": "chapter_collection_export",
        "run_id": rid,
        "branch_id": bid,
        "story_slug": story_slug,
        "filename": filename,
        "content_type": "text/markdown; charset=utf-8",
        "content_md": "\n".join(line for line in lines if line is not None),
        "chapter_count": len(items),
        "chapters": [
            {
                "run_id": item["run_id"],
                "branch_id": item["branch_id"],
                "branch_label": item["branch_label"],
            }
            for item in items
        ],
        "warnings": warnings,
        "share_guard": share_guard,
        "metadata": {
            "source_kind": source_kind,
            "ai_notice": ai_notice,
            "source_notice": source_notice,
            "exported_at": exported_at,
        },
    }

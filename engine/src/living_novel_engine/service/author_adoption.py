"""World Sandbox Loop v8: author adoption desk."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.project_health import resolve_story_path
from living_novel_engine.service.worldline_state import (
    apply_author_adoption_to_worldline_state,
)

VERSION = "author-adoption-desk-v1"
ARTIFACT = "author_adoption_record.json"
BRIEF_ARTIFACT = "author_adoption_brief.md"
NEXT_CHAPTER_ARTIFACT = "next_chapter_brief.json"
LEDGER = "author_adoption_ledger.jsonl"

_DECISIONS = {
    "adopted": "采纳",
    "partial": "部分采纳",
    "new_branch": "另开分支",
    "export_brief": "导出 brief",
}


class AuthorAdoptionRequestError(ValueError):
    """Invalid author adoption request."""


def record_author_adoption(
    story_slug: str,
    *,
    decision: str,
    original_outline: str = "",
    sandbox_summary: str = "",
    source_event: str = "",
    source_run_id: str = "",
    author_note: str = "",
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
    worldline_id: str = "main",
) -> dict[str, Any]:
    """Record an author adoption decision for emergent sandbox material."""

    sid = _checked_id(story_slug, "story_slug")
    wid = _checked_id(worldline_id, "worldline_id")
    decision_key = str(decision or "").strip()
    if decision_key not in _DECISIONS:
        raise AuthorAdoptionRequestError(
            "decision 必须是 adopted、partial、new_branch 或 export_brief"
        )
    story_path, source_kind = resolve_story_path(sid, projects_dir)
    root = outputs_dir or default_outputs_dir()
    source = _source_material(
        source_run_id=source_run_id,
        source_event=source_event,
        sandbox_summary=sandbox_summary,
        outputs_dir=root,
    )
    if not source["sandbox_emergence"]:
        raise AuthorAdoptionRequestError("缺少 sandbox_summary 或可读取的 source_run_id")

    now = datetime.now().isoformat(timespec="seconds")
    run_id = _new_run_id()
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    comparison = {
        "original_outline": _clean(original_outline) or "原大纲未填写。",
        "sandbox_emergence": source["sandbox_emergence"],
        "difference": _difference(original_outline, source["sandbox_emergence"]),
    }
    entry = {
        "version": VERSION,
        "created_at": now,
        "story_slug": sid,
        "source_kind": source_kind,
        "worldline_id": wid,
        "decision": decision_key,
        "mode_label": _DECISIONS[decision_key],
        "source_run_id": source.get("source_run_id") or "",
        "source_event": source.get("source_event") or "",
        "original_outline": comparison["original_outline"],
        "sandbox_emergence": comparison["sandbox_emergence"],
        "author_note": _clean(author_note),
    }
    _append_ledger(story_path / LEDGER, entry)
    next_chapter_brief = _next_chapter_brief(
        story_slug=sid,
        worldline_id=wid,
        decision=decision_key,
        source=source,
        comparison=comparison,
        author_note=_clean(author_note),
    )
    outline_diff = _outline_diff(decision_key, comparison)
    foreshadowing_adjustments = _foreshadowing_adjustments(
        comparison,
        decision_key,
    )
    reviewer_suggestions = _reviewer_suggestions(
        comparison,
        next_chapter_brief,
    )
    worldline_state = apply_author_adoption_to_worldline_state(
        story_path=story_path,
        worldline_id=wid,
        decision=decision_key,
        source_run_id=run_id,
        next_chapter_brief=next_chapter_brief,
    )

    report = {
        "version": VERSION,
        "artifact": ARTIFACT,
        "run_id": run_id,
        "story_slug": sid,
        "source_kind": source_kind,
        "worldline_id": wid,
        "created_at": now,
        "decision": decision_key,
        "mode_label": _DECISIONS[decision_key],
        "comparison": comparison,
        "outline_diff": outline_diff,
        "foreshadowing_adjustments": foreshadowing_adjustments,
        "reviewer_suggestions": reviewer_suggestions,
        "next_chapter_brief": next_chapter_brief,
        "continuation_effect": {
            "affects_future_sandbox": decision_key in {"adopted", "partial", "new_branch"},
            "worldline_state_artifact": worldline_state.get("artifact") or "",
            "next_sandbox_entry": next_chapter_brief["sandbox_inputs"],
        },
        "adoption_entry": entry,
        "artifacts": {
            "author_adoption_record": ARTIFACT,
            "author_adoption_brief": BRIEF_ARTIFACT,
            "next_chapter_brief": NEXT_CHAPTER_ARTIFACT,
            "ledger": LEDGER,
        },
        "boundaries": [
            "作者采纳台只追加 adoption ledger，不自动覆盖正史或原大纲。",
            "另开分支只是作者决策记录，后续分支创建仍需显式操作。",
            "不调用外部 provider，不改 run_scene 默认行为。",
        ],
        "next_steps": [
            "可把采纳记录接入章节 brief 生成。",
            "后续沙盘可读取 worldline_state.json 中的 next_chapter_brief。",
        ],
    }
    (run_dir / ARTIFACT).write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / BRIEF_ARTIFACT).write_text(
        _brief_markdown(report),
        encoding="utf-8",
    )
    (run_dir / NEXT_CHAPTER_ARTIFACT).write_text(
        json.dumps(next_chapter_brief, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def _next_chapter_brief(
    *,
    story_slug: str,
    worldline_id: str,
    decision: str,
    source: dict[str, str],
    comparison: dict[str, str],
    author_note: str,
) -> dict[str, Any]:
    emergence = comparison["sandbox_emergence"]
    event = source.get("source_event") or _first_sentence(emergence)
    opening = (
        f"下一章从“{event}”之后开场：角色先按沙盘涌现剧情承担误会与因果债，"
        "再让原大纲中仍可保留的目标以伏笔形式回流。"
    )
    if decision == "new_branch":
        opening = f"另开分支后，下一章以“{event}”作为分歧点，明确标记原大纲已退为参照。"
    if decision == "export_brief":
        opening = f"导出 brief 后，下一章暂不写入主线，只把“{event}”整理为作者可选素材。"
    return {
        "version": VERSION,
        "story_slug": story_slug,
        "worldline_id": worldline_id,
        "decision": decision,
        "opening_scene": opening,
        "chapter_goal": "把沙盘涌现剧情写成可继续运行的一章，而不是孤立摘要。",
        "conflict_focus": _conflict_focus(emergence),
        "sandbox_inputs": {
            "major_event": event or "作者采纳后的世界线继续运转。",
            "worldline_id": worldline_id,
            "author_note": author_note,
        },
        "must_preserve": [
            "角色主观记忆和信息差",
            "世界状态 delta 和因果债",
            "作者对原大纲的采纳范围",
        ],
    }


def _outline_diff(decision: str, comparison: dict[str, str]) -> dict[str, str]:
    difference = comparison["difference"]
    if "基本贴合" in difference:
        status = "aligned"
    elif decision == "partial":
        status = "partially_aligned"
    else:
        status = "diverged"
    return {
        "status": status,
        "summary": difference,
        "original_outline": comparison["original_outline"],
        "sandbox_emergence": comparison["sandbox_emergence"],
    }


def _foreshadowing_adjustments(
    comparison: dict[str, str],
    decision: str,
) -> list[dict[str, str]]:
    return [
        {
            "type": "preserve",
            "text": "保留原大纲中仍成立的目标，但把达成路径改为沙盘涌现后的代价链。",
        },
        {
            "type": "add",
            "text": "补一处角色误会或隐瞒的伏笔，让下一轮主观记忆继续驱动行动。",
        },
        {
            "type": "branch" if decision == "new_branch" else "adjust",
            "text": "标记原大纲与沙盘涌现剧情的差异，避免下一章忽略世界线偏移。",
        },
    ]


def _reviewer_suggestions(
    comparison: dict[str, str],
    next_chapter_brief: dict[str, Any],
) -> list[str]:
    return [
        "开章先写角色行动，不要先解释系统规则。",
        "至少保留一个角色不知道的正史事实，形成信息差。",
        f"下一章冲突焦点应落在：{next_chapter_brief['conflict_focus']}。",
    ]


def _first_sentence(text: str) -> str:
    clean = _clean(text)
    for sep in ("。", "\n", "；"):
        if sep in clean:
            return clean.split(sep)[0]
    return clean[:80]


def _conflict_focus(text: str) -> str:
    if "隐瞒" in text or "误判" in text:
        return "隐瞒与误判如何改变关系信任"
    if "因果债" in text:
        return "因果债如何压向当前锚点"
    return "原大纲目标与沙盘涌现选择之间的偏移"


def _source_material(
    *,
    source_run_id: str,
    source_event: str,
    sandbox_summary: str,
    outputs_dir: Path,
) -> dict[str, str]:
    rid = str(source_run_id or "").strip()
    if rid:
        checked = _checked_id(rid, "source_run_id")
        lens_path = outputs_dir / checked / "character_lens_briefs.json"
        if not lens_path.exists():
            raise FileNotFoundError(f"采纳来源不存在: {checked}")
        raw = _read_json(lens_path)
        return {
            "source_run_id": checked,
            "source_event": str(raw.get("source", {}).get("source_event") or ""),
            "sandbox_emergence": _summarize_lens(raw),
        }
    return {
        "source_run_id": "",
        "source_event": _clean(source_event),
        "sandbox_emergence": _clean(sandbox_summary),
    }


def _summarize_lens(raw: dict[str, Any]) -> str:
    briefs = raw.get("briefs") if isinstance(raw.get("briefs"), list) else []
    parts = []
    for brief in briefs[:4]:
        if isinstance(brief, dict):
            title = str(brief.get("title") or brief.get("lens_type") or "卷宗")
            body = str(brief.get("body") or "")
            if body:
                parts.append(f"{title}：{body}")
    return "\n".join(parts)


def _difference(original_outline: str, sandbox_emergence: str) -> str:
    original = _clean(original_outline)
    emergence = _clean(sandbox_emergence)
    if not original:
        return "暂无原大纲，只记录沙盘涌现材料。"
    if original in emergence:
        return "沙盘涌现剧情基本贴合原大纲。"
    return "沙盘涌现剧情与原大纲出现偏移，需要作者决定采纳范围。"


def _append_ledger(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _brief_markdown(report: dict[str, Any]) -> str:
    comparison = report["comparison"]
    return "\n".join(
        [
            "# 作者采纳 brief",
            "",
            f"- 决策：{report['mode_label']}",
            f"- 来源：{report['adoption_entry'].get('source_run_id') or '手动输入'}",
            "",
            "## 原大纲",
            "",
            comparison["original_outline"],
            "",
            "## 沙盘涌现剧情",
            "",
            comparison["sandbox_emergence"],
            "",
            "## 对照判断",
            "",
            comparison["difference"],
            "",
            "## 下一章可写方案",
            "",
            report["next_chapter_brief"]["opening_scene"],
            "",
            "## Reviewer 建议",
            "",
            "\n".join(f"- {item}" for item in report["reviewer_suggestions"]),
            "",
            "## 作者备注",
            "",
            report["adoption_entry"].get("author_note") or "无",
            "",
        ]
    )


def _read_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthorAdoptionRequestError(f"{path.name} 无法解析：{exc}") from exc
    return raw if isinstance(raw, dict) else {}


def _clean(value: object) -> str:
    return " ".join(str(value or "").split())


def _new_run_id() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"adoption_{ts}_{uuid.uuid4().hex[:6]}"


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise AuthorAdoptionRequestError(f"{label} 无效")
    return checked

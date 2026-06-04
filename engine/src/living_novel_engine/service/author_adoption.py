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

VERSION = "author-adoption-desk-v1"
ARTIFACT = "author_adoption_record.json"
BRIEF_ARTIFACT = "author_adoption_brief.md"
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
        "adoption_entry": entry,
        "artifacts": {
            "author_adoption_record": ARTIFACT,
            "author_adoption_brief": BRIEF_ARTIFACT,
            "ledger": LEDGER,
        },
        "boundaries": [
            "作者采纳台只追加 adoption ledger，不自动覆盖正史或原大纲。",
            "另开分支只是作者决策记录，后续分支创建仍需显式操作。",
            "不调用外部 provider，不改 run_scene 默认行为。",
        ],
        "next_steps": [
            "可把采纳记录接入章节 brief 生成。",
            "可在作者模式展示原大纲与沙盘涌现剧情的持续对照。",
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
    return report


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

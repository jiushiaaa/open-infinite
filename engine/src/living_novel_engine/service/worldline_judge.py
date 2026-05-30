"""v0.7.5 Worldline Judge service.

读取既有 branch artifact，写出 branch-level ``worldline_judgement.json``。
不调用 LLM、不改 runner、不改既有 artifact 契约。
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.story_loader import load_story
from living_novel_engine.worldline_judge.evaluator import evaluate_worldline

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_REPORT_NAME = "worldline_judgement.json"


class WorldlineJudgeRequestError(ValueError):
    """入参非法或 artifact 损坏 —— 映射为 HTTP 400。"""


def _validate_identifier(value: str | None, label: str) -> str:
    ident = (value or "").strip()
    if not ident:
        raise WorldlineJudgeRequestError(f"缺少 {label}")
    if ".." in ident or not _SAFE_ID_RE.match(ident):
        raise WorldlineJudgeRequestError(f"{label} 非法")
    return ident


def _outputs_root(outputs_dir: Path | None) -> Path:
    if outputs_dir is not None:
        return outputs_dir
    from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir

    return default_outputs_dir()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise WorldlineJudgeRequestError(f"{path.name} 读取失败") from exc


def _read_json_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise WorldlineJudgeRequestError(f"{path.name} 损坏，无法解析") from exc
    return data if isinstance(data, dict) else {}


def _infer_story_slug(
    explicit: str | None, run_dir: Path, meta: dict[str, Any] | None, intervention: dict[str, Any] | None
) -> str:
    if explicit:
        return _validate_identifier(explicit, "story_slug")
    for payload in (meta, intervention):
        if not isinstance(payload, dict):
            continue
        slug = payload.get("story_slug") or payload.get("sample_slug")
        if slug:
            return _validate_identifier(str(slug), "story_slug")
    baseline = _read_json_optional(run_dir / "baseline_report.json")
    if baseline and baseline.get("story_slug"):
        return _validate_identifier(str(baseline["story_slug"]), "story_slug")
    raise WorldlineJudgeRequestError("缺少 story_slug，无法定位故事锚定")


def _collect_character_names(bundle, state_snapshot: dict[str, Any] | None) -> list[str]:
    names = [c.name for c in bundle.characters if c.name]
    chars = (state_snapshot or {}).get("characters") or {}
    if isinstance(chars, dict):
        for cid, cs in chars.items():
            if isinstance(cs, dict) and cs.get("name"):
                names.append(str(cs["name"]))
            else:
                names.append(str(cid))
    return list(dict.fromkeys(n for n in names if n))


def _collect_threads(bundle) -> list[str]:
    titles: list[str] = []
    for thread in getattr(bundle.world, "open_threads", []) or []:
        title = getattr(thread, "title", "")
        if title:
            titles.append(title)
    return list(dict.fromkeys(titles))


def judge_worldline(
    *,
    run_id: str,
    branch_id: str,
    story_slug: str | None = None,
    outputs_dir: Path | None = None,
) -> dict:
    """Generate and persist ``worldline_judgement.json`` for one branch."""
    rid = _validate_identifier(run_id, "run_id")
    bid = _validate_identifier(branch_id, "branch_id")
    root = _outputs_root(outputs_dir)
    run_dir = root / rid
    branch_dir = run_dir / bid
    if not branch_dir.is_dir():
        raise FileNotFoundError(f"分支不存在: {rid}/{bid}")

    chapter_path = branch_dir / "chapter.md"
    if not chapter_path.exists():
        raise FileNotFoundError(f"分支正文不存在: {rid}/{bid}")

    meta = _read_json_optional(run_dir / "meta.json")
    intervention = _read_json_optional(run_dir / "intervention.json")
    compilation = _read_json_optional(run_dir / "intervention_compilation.json")
    events = _read_json_optional(branch_dir / "events.json")
    state = _read_json_optional(branch_dir / "state_snapshot.json")
    causal_diff = _read_json_optional(branch_dir / "causal_diff.json")

    slug = _infer_story_slug(story_slug, run_dir, meta, intervention)
    bundle = load_story(slug)

    report = evaluate_worldline(
        chapter_text=_read_text(chapter_path),
        summary_text=_read_text(branch_dir / "summary.md")
        if (branch_dir / "summary.md").exists()
        else "",
        events=events,
        state_snapshot=state,
        known_character_names=_collect_character_names(bundle, state),
        world_rules=getattr(bundle.world, "rules", []) or [],
        open_threads=_collect_threads(bundle),
        causal_diff=causal_diff,
        intervention=intervention,
        compilation=compilation,
    )
    report.story_slug = slug
    report.source_kind = "builtin" if bundle.source_kind == "builtin" else "imported"
    report.run_id = rid
    report.branch_id = bid
    report.created_at = datetime.now().isoformat()

    payload = report.model_dump(mode="json")
    (branch_dir / _REPORT_NAME).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload


def get_worldline_judgement(
    run_id: str,
    branch_id: str,
    *,
    outputs_dir: Path | None = None,
) -> dict:
    """Read branch-level ``worldline_judgement.json``."""
    rid = _validate_identifier(run_id, "run_id")
    bid = _validate_identifier(branch_id, "branch_id")
    path = _outputs_root(outputs_dir) / rid / bid / _REPORT_NAME
    if not path.exists():
        raise FileNotFoundError(f"世界线评审报告不存在: {rid}/{bid}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise WorldlineJudgeRequestError(f"世界线评审报告损坏: {rid}/{bid}") from exc
    return data if isinstance(data, dict) else {}

"""Persist the user's selected worldline for the long creation loop."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir
from living_novel_engine.story_loader import load_story

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_VERSION = "v0.9.0-alpha"


class WorldlineSelectionRequestError(ValueError):
    """Invalid selected-worldline request, mapped to HTTP 400."""


def _validate_identifier(value: str | None, label: str) -> str:
    ident = (value or "").strip()
    if not ident:
        raise WorldlineSelectionRequestError(f"缺少 {label}")
    if ".." in ident or not _SAFE_ID_RE.match(ident):
        raise WorldlineSelectionRequestError(f"{label} 非法")
    return ident


def _safe_note(note: str | None) -> str:
    return (note or "").strip()[:280]


def _selection_path(story_slug: str, *, project_dir: Path | None = None) -> Path:
    if project_dir is not None:
        return project_dir / "selected_worldline.json"
    bundle = load_story(story_slug)
    if bundle.project_dir:
        return bundle.project_dir / "selected_worldline.json"
    return outputs_dir() / "story_selections" / story_slug / "selected_worldline.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _infer_run_story_slug(run_dir: Path) -> str:
    for name in ("meta.json", "intervention.json"):
        path = run_dir / name
        if not path.exists():
            continue
        data = _read_json(path)
        slug = str(data.get("story_slug") or data.get("sample_slug") or "")
        if slug:
            return slug
    return "tianhuang-night"


def _branch_label(branch_dir: Path, branch_id: str) -> str:
    events_path = branch_dir / "events.json"
    if events_path.exists():
        events = _read_json(events_path)
        theme = str(events.get("theme") or "").strip()
        if theme:
            return theme
    return branch_id


def _selection_missing(story_slug: str) -> dict[str, Any]:
    return {
        "version": _VERSION,
        "kind": "selected_worldline",
        "status": "missing",
        "story_slug": story_slug,
    }


def get_selected_worldline(
    story_slug: str,
    *,
    project_dir: Path | None = None,
) -> dict[str, Any]:
    """Read the persisted selection, returning a stable empty state when absent."""
    slug = _validate_identifier(story_slug, "story_slug")
    path = _selection_path(slug, project_dir=project_dir)
    if not path.exists():
        return _selection_missing(slug)
    try:
        data = _read_json(path)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {
            "version": _VERSION,
            "kind": "selected_worldline",
            "status": "damaged",
            "story_slug": slug,
            "warning": str(exc),
        }
    data.setdefault("version", _VERSION)
    data.setdefault("kind", "selected_worldline")
    data.setdefault("status", "ready")
    data.setdefault("story_slug", slug)
    return data


def select_worldline(
    *,
    story_slug: str,
    run_id: str,
    branch_id: str,
    note: str | None = None,
) -> dict[str, Any]:
    """Persist a selected branch as the next long-creation starting point."""
    slug = _validate_identifier(story_slug, "story_slug")
    rid = _validate_identifier(run_id, "run_id")
    bid = _validate_identifier(branch_id, "branch_id")
    # Raises FileNotFoundError for unknown story; caller maps to 404.
    path = _selection_path(slug)

    run_dir = outputs_dir() / rid
    branch_dir = run_dir / bid
    if not run_dir.is_dir():
        raise FileNotFoundError(f"运行目录不存在: {rid}")
    if not branch_dir.is_dir():
        raise FileNotFoundError(f"分支不存在: {rid}/{bid}")
    run_story_slug = _infer_run_story_slug(run_dir)
    if run_story_slug != slug:
        raise WorldlineSelectionRequestError(
            f"run_id 不属于故事 {slug}: {run_story_slug}"
        )

    chapter_path = branch_dir / "chapter.md"
    chapter_chars = len(chapter_path.read_text(encoding="utf-8")) if chapter_path.exists() else 0
    selection = {
        "version": _VERSION,
        "kind": "selected_worldline",
        "status": "ready",
        "story_slug": slug,
        "run_id": rid,
        "branch_id": bid,
        "branch_label": _branch_label(branch_dir, bid),
        "chapter_chars": chapter_chars,
        "export_api_path": f"/api/runs/{rid}/branches/{bid}/chapter-export"
        if chapter_chars > 0
        else "",
        "note": _safe_note(note),
        "selected_at": datetime.now().isoformat(timespec="seconds"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(selection, ensure_ascii=False, indent=2), encoding="utf-8")
    return selection

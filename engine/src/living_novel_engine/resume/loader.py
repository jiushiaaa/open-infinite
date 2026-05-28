from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from living_novel_engine.models import CharacterAgent
from living_novel_engine.samples import load_sample


def _outputs_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "outputs"

DEFAULT_SAMPLE_SLUG = "tianhuang-night"
DEFAULT_PARENT_CHAPTER = 13


@dataclass
class ParentSnapshot:
    run_id: str
    branch_id: str
    sample_slug: str
    chapter_number: int
    snapshot: dict[str, Any]
    chapter_text: str
    summary_text: str
    events: dict[str, Any]
    scene_flags: dict[str, Any] = field(default_factory=dict)
    location: str = ""
    time: str = ""
    branch_seed: str = ""
    branch_theme: str = ""


def _resolve_run_dir(run_id: str) -> Path:
    run_dir = Path(run_id)
    if not run_dir.is_absolute():
        run_dir = _outputs_dir() / run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"运行目录不存在: {run_dir}")
    return run_dir


def _infer_sample_slug(run_dir: Path) -> str:
    intervention_path = run_dir / "intervention.json"
    if intervention_path.exists():
        data = json.loads(intervention_path.read_text(encoding="utf-8"))
        slug = data.get("sample_slug") or data.get("world_slug")
        if slug:
            return str(slug)
    meta_path = run_dir / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("sample_slug"):
            return str(meta["sample_slug"])
    return DEFAULT_SAMPLE_SLUG


def _chapter_number_from_run(run_dir: Path, meta: dict[str, Any] | None) -> int:
    if meta and meta.get("current_chapter"):
        return int(meta["current_chapter"])
    if meta and meta.get("parent_chapter"):
        return int(meta["parent_chapter"])
    if (run_dir / "intervention.json").exists():
        return DEFAULT_PARENT_CHAPTER
    if meta and meta.get("kind") == "resume_continue":
        return int(meta.get("current_chapter", DEFAULT_PARENT_CHAPTER))
    return DEFAULT_PARENT_CHAPTER


def load_parent_snapshot(run_id: str, branch_id: str) -> ParentSnapshot:
    run_dir = _resolve_run_dir(run_id)
    branch_dir = run_dir / branch_id
    if not branch_dir.is_dir():
        raise FileNotFoundError(f"分支不存在: {branch_id}（路径 {branch_dir}）")

    snapshot_path = branch_dir / "state_snapshot.json"
    chapter_path = branch_dir / "chapter.md"
    events_path = branch_dir / "events.json"
    summary_path = branch_dir / "summary.md"

    if not snapshot_path.exists():
        raise FileNotFoundError(f"缺少 state_snapshot.json: {snapshot_path}")

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    chapter_text = chapter_path.read_text(encoding="utf-8") if chapter_path.exists() else ""
    summary_text = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""
    events = (
        json.loads(events_path.read_text(encoding="utf-8")) if events_path.exists() else {}
    )

    meta: dict[str, Any] | None = None
    meta_path = run_dir / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

    sample_slug = _infer_sample_slug(run_dir)
    chapter_number = _chapter_number_from_run(run_dir, meta)

    scene_flags = dict(snapshot.get("scene_flags") or {})
    return ParentSnapshot(
        run_id=run_dir.name,
        branch_id=branch_id,
        sample_slug=sample_slug,
        chapter_number=chapter_number,
        snapshot=snapshot,
        chapter_text=chapter_text,
        summary_text=summary_text,
        events=events,
        scene_flags=scene_flags,
        location=str(snapshot.get("location", "")),
        time=str(snapshot.get("time", "")),
        branch_seed=str(snapshot.get("branch_seed", "")),
        branch_theme=str(snapshot.get("branch_theme", "")),
    )


def build_seed_scene_state(parent: ParentSnapshot) -> dict[str, Any]:
    """从父快照构造 scene_runner 初始 scene_state（resume continue → linear）。"""
    state = dict(parent.scene_flags)
    if parent.location:
        state["location"] = parent.location
    if parent.time:
        state["time"] = parent.time
    state["branch_seed"] = "linear"
    state.setdefault("intervention_target", "")
    return state


def build_seed_scene_state_for_intervene(
    parent: ParentSnapshot,
    intervention_target: str,
) -> dict[str, Any]:
    """从父快照构造 scene_runner 初始 scene_state（resume intervene → 三分支）。"""
    state = dict(parent.scene_flags)
    if parent.location:
        state["location"] = parent.location
    if parent.time:
        state["time"] = parent.time
    state["intervention_target"] = intervention_target
    state.pop("branch_seed", None)
    return state


def project_characters_from_parent(
    parent: ParentSnapshot,
) -> tuple[list[CharacterAgent], Any]:
    bundle = load_sample(parent.sample_slug)
    chars = copy.deepcopy(bundle.characters)
    snap_chars = parent.snapshot.get("characters") or {}

    parent_summary = (parent.summary_text or "").strip()[:200]
    memory_note = f"第{parent.chapter_number}章续前：{parent_summary}" if parent_summary else ""

    for char in chars:
        cs = snap_chars.get(char.id)
        if not cs:
            continue
        if cs.get("location"):
            char.current_state.location = str(cs["location"])
        if cs.get("emotion"):
            char.current_state.emotion = str(cs["emotion"])
        if cs.get("resources"):
            char.current_state.resources = list(cs["resources"])
        if memory_note:
            char.memory.append(memory_note)

    return chars, bundle.world

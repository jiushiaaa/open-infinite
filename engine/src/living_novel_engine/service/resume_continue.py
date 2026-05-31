"""console-free resume continue service for v0.9.0-alpha.

This mirrors the CLI ``lne resume continue`` path so the Web UI can trigger
the same opt-in continuation job without changing ``run_scene`` defaults.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from living_novel_engine.fourth_wall import fourth_wall_enabled
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import build_continuation_spec
from living_novel_engine.output.writer import load_lineage_ledger, write_resume_output
from living_novel_engine.resume import (
    build_seed_scene_state,
    load_parent_snapshot,
    project_characters_from_parent,
)
from living_novel_engine.runtime_memory import build_runtime_memory_context
from living_novel_engine.service.intervene import resolve_llm_quietly
from living_novel_engine.story_loader import load_story

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class ResumeContinueRequestError(ValueError):
    """Invalid resume continue request, mapped to HTTP 400."""


@dataclass
class ResumeContinueServiceResult:
    run_id: str
    run_dir: Path
    branch_id: str
    story_slug: str
    source_kind: str
    parent_run_id: str
    parent_branch_id: str
    chapter_number: int
    llm_mock: bool
    fallback_reason: str | None = None
    extra: dict[str, object] = field(default_factory=dict)


def _validate_identifier(value: str | None, label: str) -> str:
    ident = (value or "").strip()
    if not ident:
        raise ResumeContinueRequestError(f"缺少 {label}")
    if ".." in ident or not _SAFE_ID_RE.match(ident):
        raise ResumeContinueRequestError(f"{label} 非法")
    return ident


def _prepare_retrieval(bundle, query: str, source_type: str, *, current_chapter: int):
    if bundle.project_dir and source_type != "builtin_sample":
        ctx = build_runtime_memory_context(
            bundle.project_dir,
            query,
            current_chapter=current_chapter,
        )
        return ctx.as_prompt_block(), ctx.retrieval.to_artifact(), ctx.to_artifact()
    return "", None, None


def _load_ledger_for_resume(parent_run_id: str):
    if not fourth_wall_enabled():
        return None
    return load_lineage_ledger(parent_run_id)


def run_resume_continue(
    *,
    run_id: str,
    branch_id: str,
    rounds: int = 4,
    mock: bool = False,
    runner_name: str | None = None,
) -> ResumeContinueServiceResult:
    """Continue a selected branch into a new ``linear`` child run."""
    parent_run_id = _validate_identifier(run_id, "run_id")
    parent_branch_id = _validate_identifier(branch_id, "branch_id")
    if not isinstance(rounds, int) or rounds < 1 or rounds > 12:
        raise ResumeContinueRequestError("rounds 必须为 1-12 的整数")

    llm, used_mock = resolve_llm_quietly(mock)
    try:
        parent = load_parent_snapshot(parent_run_id, parent_branch_id)
    except FileNotFoundError as exc:
        raise FileNotFoundError(str(exc)) from exc

    characters, world = project_characters_from_parent(parent)
    bundle = load_story(parent.story_slug)
    parent_seed = parent.branch_seed or "unknown"
    spec = build_continuation_spec(parent_seed, parent.branch_id)
    next_chapter = parent.chapter_number + 1

    seed_state = build_seed_scene_state(parent)
    prologue = bundle.prologue
    if parent.summary_text.strip():
        prologue = (
            f"{prologue}\n\n【第{parent.chapter_number}章已发生】\n"
            f"{parent.summary_text.strip()}"
        )

    query = parent.summary_text[:200] if parent.summary_text else parent.branch_theme
    retrieved_ctx, retrieval_record, runtime_memory_record = _prepare_retrieval(
        bundle,
        query,
        parent.source_type,
        current_chapter=next_chapter,
    )

    ledger = _load_ledger_for_resume(parent.run_id)
    result = run_scene(
        world,
        characters,
        None,
        spec,
        llm,
        max_rounds=rounds,
        canon_excerpt=parent.chapter_text,
        prologue=prologue,
        canon_opening=bundle.canon_opening,
        canon_chapter=parent.chapter_text,
        seed_scene_state=seed_state,
        seed_characters=characters,
        chapter_number=next_chapter,
        source_type=parent.source_type,
        retrieved_context=retrieved_ctx,
        ledger=ledger,
        runner_name=runner_name,
    )
    if retrieval_record is not None:
        result.retrieval_record = retrieval_record
    if runtime_memory_record is not None:
        result.runtime_memory_record = runtime_memory_record

    output = write_resume_output(parent, result, ledger=ledger)
    return ResumeContinueServiceResult(
        run_id=output.run_id,
        run_dir=output.run_dir,
        branch_id=result.worldline_id,
        story_slug=parent.story_slug,
        source_kind=parent.source_kind,
        parent_run_id=parent.run_id,
        parent_branch_id=parent.branch_id,
        chapter_number=next_chapter,
        llm_mock=used_mock,
    )

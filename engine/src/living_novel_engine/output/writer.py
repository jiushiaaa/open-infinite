from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from living_novel_engine.fourth_wall import FourthWallLedger, load_ledger, save_ledger, should_persist_ledger
from living_novel_engine.models import Intervention
from living_novel_engine.models.events import SimulationResult

if TYPE_CHECKING:
    from living_novel_engine.intervention_compiler.models import InterventionCompilation
    from living_novel_engine.resume.loader import ParentSnapshot


def _write_compilation(run_dir: Path, compilation: "InterventionCompilation | None") -> None:
    """写入 Intervention Compiler artifact（None 时不写，保持向后兼容）。"""
    if compilation is None:
        return
    with open(run_dir / "intervention_compilation.json", "w", encoding="utf-8") as f:
        json.dump(
            compilation.model_dump(mode="json"),
            f,
            ensure_ascii=False,
            indent=2,
            default=str,
        )


def _write_causal_diff(
    branch_dir: Path,
    result: SimulationResult,
    *,
    old_text: str | None,
    new_text: str | None,
    compilation: "InterventionCompilation",
    chapter_number: int,
) -> None:
    """写入 v0.7.1-C Causal Diff artifact（仅 intervene/resume intervene 分支）。"""
    from living_novel_engine.causal_diff import build_causal_diff

    artifact = build_causal_diff(
        branch_id=result.worldline_id,
        old_text=old_text,
        new_text=new_text,
        compilation=compilation,
        chapter_number=chapter_number,
    )
    with open(branch_dir / "causal_diff.json", "w", encoding="utf-8") as f:
        json.dump(
            artifact.model_dump(mode="json"),
            f,
            ensure_ascii=False,
            indent=2,
            default=str,
        )


def _outputs_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "outputs"


def _ledger_path(run_dir: Path) -> Path:
    return run_dir / "fourth_wall.json"


def load_run_ledger(run_id: str) -> FourthWallLedger:
    """读取某个 run 的第四面墙账本（缺失/损坏时返回空账本）。"""
    return load_ledger(_outputs_dir() / run_id / "fourth_wall.json")


def load_lineage_ledger(run_id: str) -> FourthWallLedger:
    """沿 meta.json 父链向上查找最近一份有实质内容的 fourth_wall.json。

    用于 resume：关闭第四面墙期间不写账本的 run 不会截断 lineage，
    重新开启后可继承关闭前的觉察状态，但不会继承关闭期间的新干预。
    """
    run_dir = _outputs_dir() / run_id
    path = _ledger_path(run_dir)
    if path.exists():
        ledger = load_ledger(path)
        if ledger.traces or ledger.awareness:
            return ledger.model_copy(update={"enabled": True})

    meta_path = run_dir / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        parent_id = meta.get("parent_run_id")
        if parent_id:
            return load_lineage_ledger(str(parent_id))

    return FourthWallLedger(enabled=True)


def _maybe_save_ledger(run_dir: Path, ledger: FourthWallLedger | None) -> None:
    if should_persist_ledger(ledger):
        save_ledger(_ledger_path(run_dir), ledger)  # type: ignore[arg-type]


def _infer_chapter_from_result(result: SimulationResult) -> int:
    for evt in result.accepted_events:
        if getattr(evt, "chapter", None):
            return int(evt.chapter)
    snap = result.state_snapshot or {}
    return int(snap.get("chapter") or 13)


@dataclass
class RunOutput:
    run_id: str
    run_dir: Path
    intervention: Intervention
    results: list[SimulationResult] = field(default_factory=list)


def write_run_output(
    intervention: Intervention,
    results: list[SimulationResult],
    *,
    run_id: str | None = None,
    ledger: FourthWallLedger | None = None,
    compilation: "InterventionCompilation | None" = None,
    old_text: str | None = None,
) -> RunOutput:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = run_id or f"run_{ts}_{uuid.uuid4().hex[:6]}"
    run_dir = _outputs_dir() / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    if ledger is not None:
        _maybe_save_ledger(run_dir, ledger)
    _write_compilation(run_dir, compilation)

    intervention_payload = intervention.model_dump(mode="json")
    if intervention.contract_audit:
        intervention_payload["contract_audit"] = intervention.contract_audit.model_dump()
    slug = (
        intervention.story_slug
        or intervention_payload.get("story_slug")
        or intervention_payload.get("sample_slug")
        or "tianhuang-night"
    )
    intervention_payload["story_slug"] = slug
    intervention_payload["sample_slug"] = slug
    if intervention.source_kind:
        intervention_payload["source_kind"] = intervention.source_kind
    elif slug == "tianhuang-night":
        intervention_payload["source_kind"] = "builtin"
    elif not intervention_payload.get("source_kind"):
        intervention_payload["source_kind"] = "imported"

    with open(run_dir / "intervention.json", "w", encoding="utf-8") as f:
        json.dump(intervention_payload, f, ensure_ascii=False, indent=2, default=str)

    for result in results:
        _write_branch_outputs(
            run_dir / result.worldline_id,
            result,
            chapter_number=_infer_chapter_from_result(result),
            old_text=old_text,
            compilation=compilation,
        )

    compare_md = _build_compare_md(results, intervention=intervention)
    (run_dir / "compare.md").write_text(compare_md, encoding="utf-8")

    return RunOutput(run_id=run_id, run_dir=run_dir, intervention=intervention, results=results)


def _build_compare_md(
    results: list[SimulationResult],
    intervention: Intervention | None = None,
) -> str:
    from living_novel_engine.orchestrator.narrative_constraints import summary_from_snapshot

    lines = ["# 世界线对比\n", f"生成时间: {datetime.now().isoformat()}\n"]
    if intervention:
        target = intervention.target
        content = (intervention.content or "")[:120]
        lines.append(f"**本次干预**（对 `{target}`）：{content}\n")
    lines.append("| 世界线 | 主题 | 种子 | 终止原因 | 下一章钩子 |")
    lines.append("| --- | --- | --- | --- | --- |")
    for r in results:
        snap = r.state_snapshot or {}
        hook = str(snap.get("next_chapter_hook", ""))[:80]
        lines.append(
            f"| {r.worldline_id} | {r.theme} | {r.branch_seed} | {r.termination_reason} | {hook} |"
        )
    lines.append("\n## 分歧要点（由 state_snapshot 生成）\n")
    for r in results:
        lines.append(f"### {r.worldline_id}: {r.theme}\n")
        summary = summary_from_snapshot(r.theme, r)
        lines.append(summary + "\n")
        snap = r.state_snapshot or {}
        flags = snap.get("scene_flags") or {}
        loc = (snap.get("characters") or {}).get("lin_wan_zhou", {}).get("location", "")
        if loc:
            lines.append(f"- 林晚舟位置：`{loc}`\n")
        if flags.get("bamboo_grove_triggered"):
            lines.append("- 场景标志：城外竹林已触发\n")
        elif flags.get("investigating"):
            lines.append("- 场景标志：留城调查/拖延\n")
        hook = snap.get("next_chapter_hook")
        if hook:
            lines.append(f"**下一章钩子**: {hook}\n")
    return "\n".join(lines)


@dataclass
class ResumeRunOutput:
    run_id: str
    run_dir: Path
    parent: ParentSnapshot
    result: SimulationResult


@dataclass
class ResumeInterveneOutput:
    run_id: str
    run_dir: Path
    parent: ParentSnapshot
    intervention: Intervention
    results: list[SimulationResult] = field(default_factory=list)


def _build_resume_meta(parent: "ParentSnapshot", kind: str) -> dict[str, object]:
    current_chapter = parent.chapter_number + 1
    lineage_entry = f"{parent.run_id}:{parent.branch_id}"
    parent_meta_path = _outputs_dir() / parent.run_id / "meta.json"
    lineage: list[str] = [lineage_entry]
    branch_seed_lineage: list[str] = []
    if parent.branch_seed:
        branch_seed_lineage.append(parent.branch_seed)
    if parent_meta_path.exists():
        prev_meta = json.loads(parent_meta_path.read_text(encoding="utf-8"))
        lineage = list(prev_meta.get("lineage", [])) + [lineage_entry]
        branch_seed_lineage = list(prev_meta.get("branch_seed_lineage", []))
        if parent.branch_seed and parent.branch_seed not in branch_seed_lineage:
            branch_seed_lineage.append(parent.branch_seed)
    return {
        "kind": kind,
        "parent_run_id": parent.run_id,
        "parent_branch": parent.branch_id,
        "parent_chapter": parent.chapter_number,
        "current_chapter": current_chapter,
        "story_slug": parent.story_slug,
        "source_kind": parent.source_kind,
        "sample_slug": parent.story_slug,
        "branch_seed_lineage": branch_seed_lineage,
        "lineage": lineage,
    }


def _write_parent_artifacts(run_dir: Path, parent: "ParentSnapshot") -> None:
    (run_dir / "parent_snapshot.json").write_text(
        json.dumps(parent.snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / "parent_chapter.md").write_text(parent.chapter_text, encoding="utf-8")


def _write_branch_outputs(
    branch_dir: Path,
    result: SimulationResult,
    *,
    chapter_number: int | None = None,
    old_text: str | None = None,
    compilation: "InterventionCompilation | None" = None,
) -> None:
    branch_dir.mkdir(parents=True, exist_ok=True)
    snapshot = result.state_snapshot or result.final_scene_state

    events_payload: dict = {
        "worldline_id": result.worldline_id,
        "theme": result.theme,
        "branch_seed": result.branch_seed,
        "termination_reason": result.termination_reason,
        "runner": result.runner_name,
        "accepted_events": [e.model_dump() for e in result.accepted_events],
        "state_deltas": [d.model_dump() for d in result.state_deltas],
        "final_scene_state": result.final_scene_state,
    }
    if chapter_number is not None:
        events_payload["chapter"] = chapter_number

    with open(branch_dir / "events.json", "w", encoding="utf-8") as f:
        json.dump(events_payload, f, ensure_ascii=False, indent=2, default=str)

    from living_novel_engine.orchestrator.narrative_constraints import (
        chapter_from_snapshot_and_events,
        is_structured_chapter_fallback,
        summary_from_snapshot,
    )

    summary_text = summary_from_snapshot(result.theme, result)

    chapter_text = (result.chapter_text or "").strip()
    ch_num = chapter_number or _infer_chapter_from_result(result)
    if not chapter_text:
        chapter_text = chapter_from_snapshot_and_events(
            result, snapshot, chapter_number=ch_num, include_dev_notice=False
        )
    elif is_structured_chapter_fallback(chapter_text):
        chapter_text = chapter_from_snapshot_and_events(
            result, snapshot, chapter_number=ch_num, include_dev_notice=False
        )

    (branch_dir / "summary.md").write_text(summary_text, encoding="utf-8")
    (branch_dir / "chapter.md").write_text(chapter_text, encoding="utf-8")

    if compilation is not None:
        _write_causal_diff(
            branch_dir,
            result,
            old_text=old_text,
            new_text=chapter_text,
            compilation=compilation,
            chapter_number=ch_num,
        )

    with open(branch_dir / "state_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2, default=str)

    if result.retrieval_record is not None:
        with open(branch_dir / "retrieval_context.json", "w", encoding="utf-8") as f:
            json.dump(
                result.retrieval_record,
                f,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

    if result.multi_agent_trace is not None:
        with open(branch_dir / "multi_agent_trace.json", "w", encoding="utf-8") as f:
            json.dump(
                result.multi_agent_trace,
                f,
                ensure_ascii=False,
                indent=2,
                default=str,
            )


def write_resume_output(
    parent: "ParentSnapshot",
    result: SimulationResult,
    *,
    kind: str = "resume_continue",
    ledger: FourthWallLedger | None = None,
) -> ResumeRunOutput:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"run_{ts}_{uuid.uuid4().hex[:6]}_continue_{parent.branch_id}"
    run_dir = _outputs_dir() / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    if ledger is not None:
        _maybe_save_ledger(run_dir, ledger)

    meta = _build_resume_meta(parent, kind)
    current_chapter = int(meta["current_chapter"])
    with open(run_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    _write_parent_artifacts(run_dir, parent)
    _write_branch_outputs(
        run_dir / result.worldline_id, result, chapter_number=current_chapter
    )

    return ResumeRunOutput(
        run_id=run_id, run_dir=run_dir, parent=parent, result=result
    )


def write_resume_intervene_output(
    parent: "ParentSnapshot",
    intervention: Intervention,
    results: list[SimulationResult],
    *,
    ledger: FourthWallLedger | None = None,
    compilation: "InterventionCompilation | None" = None,
) -> ResumeInterveneOutput:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"run_{ts}_{uuid.uuid4().hex[:6]}_resume_intervene_{parent.branch_id}"
    run_dir = _outputs_dir() / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    if ledger is not None:
        _maybe_save_ledger(run_dir, ledger)
    _write_compilation(run_dir, compilation)

    meta = _build_resume_meta(parent, "resume_intervene")
    current_chapter = int(meta["current_chapter"])
    with open(run_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    _write_parent_artifacts(run_dir, parent)

    intervention_payload = intervention.model_dump(mode="json")
    if intervention.contract_audit:
        intervention_payload["contract_audit"] = intervention.contract_audit.model_dump()
    intervention_payload["story_slug"] = parent.story_slug
    intervention_payload["source_kind"] = parent.source_kind
    intervention_payload["sample_slug"] = parent.story_slug
    intervention_payload["resume_parent_run_id"] = parent.run_id
    intervention_payload["resume_parent_branch"] = parent.branch_id
    intervention_payload["resume_parent_chapter"] = parent.chapter_number
    with open(run_dir / "intervention.json", "w", encoding="utf-8") as f:
        json.dump(intervention_payload, f, ensure_ascii=False, indent=2, default=str)

    for result in results:
        _write_branch_outputs(
            run_dir / result.worldline_id,
            result,
            chapter_number=current_chapter,
            old_text=parent.chapter_text,
            compilation=compilation,
        )

    compare_md = _build_compare_md(results, intervention=intervention)
    (run_dir / "compare.md").write_text(compare_md, encoding="utf-8")

    return ResumeInterveneOutput(
        run_id=run_id,
        run_dir=run_dir,
        parent=parent,
        intervention=intervention,
        results=results,
    )


def load_run_for_compare(run_path: str | Path) -> str:
    run_dir = Path(run_path)
    compare_file = run_dir / "compare.md"
    if compare_file.exists():
        return compare_file.read_text(encoding="utf-8")
    results = []
    for branch in sorted(run_dir.glob("branch_*")):
        summary = (branch / "summary.md").read_text(encoding="utf-8")
        results.append(f"## {branch.name}\n\n{summary}\n")
    return "\n".join(results) if results else "未找到可对比的世界线输出"

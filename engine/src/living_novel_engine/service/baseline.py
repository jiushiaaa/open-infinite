"""console-free 无干预基线服务（v0.7.4 Baseline Worldline）。

为任意故事生成一条"无高维干预"的基线世界线，作为干预世界线的对照组：
- 不改变 run_scene 默认行为（intervention=None，沿 linear 自然推进语义）。
- 不写 intervention.json / contract_audit / causal_diff，artifact 全部 additive。
- 缺 from_run/from_branch：从故事锚定状态生成基线。
- 有 from_run/from_branch：从该分支快照继续无干预基线，用于与干预分支对照。

所有失败降级为明确错误（400/404），不白屏、不 500。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from living_novel_engine.baseline.models import (
    BASELINE_VERSION,
    BaselineReport,
    CharacterStateChange,
)
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import build_baseline_spec
from living_novel_engine.output.writer import write_baseline_output
from living_novel_engine.runtime_memory import build_runtime_memory_context
from living_novel_engine.service.intervene import resolve_llm_quietly
from living_novel_engine.story_loader import load_story

_MAX_DEV_POINTS = 6
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class BaselineRequestError(ValueError):
    """入参非法（坏 slug、缺故事、参数错误）——映射为 HTTP 400。"""


@dataclass
class BaselineServiceResult:
    run_id: str
    run_dir: Path
    branch_id: str
    story_slug: str
    summary: str
    report: dict
    extra: dict[str, object] = field(default_factory=dict)


def _validate_identifier(value: str | None, label: str) -> str:
    ident = (value or "").strip()
    if not ident:
        raise BaselineRequestError(f"缺少 {label}")
    if ".." in ident or not _SAFE_ID_RE.match(ident):
        raise BaselineRequestError(f"{label} 非法")
    return ident


def _outputs_root() -> Path:
    from living_novel_engine.browser.paths import outputs_dir

    return outputs_dir()


def _collect_dev_points(result) -> list[str]:
    points: list[str] = []
    for scene in result.scenes or []:
        summ = (getattr(scene, "summary", "") or "").strip()
        if summ and summ not in points:
            points.append(summ)
        if len(points) >= _MAX_DEV_POINTS:
            break
    if not points:
        for evt in (result.accepted_events or [])[:_MAX_DEV_POINTS]:
            narr = (getattr(evt, "narrative", "") or "").strip()
            if narr and narr not in points:
                points.append(narr)
    return points[:_MAX_DEV_POINTS]


def _collect_state_changes(result, char_map) -> list[CharacterStateChange]:
    snapshot = result.state_snapshot or {}
    snap_chars = snapshot.get("characters") or {}
    changes: list[CharacterStateChange] = []
    for cid, cs in snap_chars.items():
        if not isinstance(cs, dict):
            continue
        char = char_map.get(cid)
        changes.append(
            CharacterStateChange(
                character_id=cid,
                name=char.name if char else str(cs.get("name") or cid),
                location=str(cs.get("location") or ""),
                emotion=str(cs.get("emotion") or ""),
            )
        )
    return changes


def _collect_threads_touched(world, chapter_text: str) -> list[str]:
    text = chapter_text or ""
    touched: list[str] = []
    for thread in getattr(world, "open_threads", []) or []:
        title = (getattr(thread, "title", "") or "").strip()
        if not title:
            continue
        # 命中规则：标题整体出现，或标题里的较长词块出现在正文中。
        hit = title in text
        if not hit:
            for token in title.replace("，", " ").replace("、", " ").split():
                if len(token) >= 2 and token in text:
                    hit = True
                    break
        if hit and title not in touched:
            touched.append(title)
    return touched


def _build_report(
    *,
    story_slug: str,
    source_kind: str,
    run_id: str,
    from_run_id: str | None,
    from_branch_id: str | None,
    chapter_number: int,
    runner: str,
    mock: bool,
    result,
    char_map,
    world,
) -> BaselineReport:
    chapter_text = (result.chapter_text or "").strip()
    summary = (result.summary_text or "").strip()
    if not summary:
        summary = chapter_text[:200]
    return BaselineReport(
        version=BASELINE_VERSION,
        story_slug=story_slug,
        source_kind="builtin" if source_kind == "builtin" else "imported",
        run_id=run_id,
        branch_id="baseline",
        from_run_id=from_run_id,
        from_branch_id=from_branch_id,
        chapter_number=chapter_number,
        runner=runner,
        mock=mock,
        no_intervention=True,
        summary=summary,
        natural_development_points=_collect_dev_points(result),
        character_state_changes=_collect_state_changes(result, char_map),
        open_threads_touched=_collect_threads_touched(world, chapter_text),
        created_at=datetime.now().isoformat(),
    )


def _run_from_anchor(bundle, llm, *, rounds: int, runner_name: str | None):
    spec = build_baseline_spec()
    source_type = bundle.world.source_type
    query = bundle.world.display_name or bundle.world.title
    retrieved_ctx, retrieval_record, runtime_memory_record = "", None, None
    if bundle.project_dir and source_type != "builtin_sample":
        ctx = build_runtime_memory_context(
            bundle.project_dir, query, current_chapter=bundle.intervention_chapter()
        )
        retrieved_ctx = ctx.as_prompt_block()
        retrieval_record = ctx.retrieval.to_artifact()
        runtime_memory_record = ctx.to_artifact()

    result = run_scene(
        bundle.world,
        bundle.characters,
        None,
        spec,
        llm,
        max_rounds=rounds,
        canon_excerpt=bundle.canon_context_for_narrator(),
        prologue=bundle.prologue,
        canon_opening=bundle.canon_opening,
        canon_chapter=bundle.canon_chapter,
        source_type=source_type,
        retrieved_context=retrieved_ctx,
        runner_name=runner_name,
    )
    if retrieval_record is not None:
        result.retrieval_record = retrieval_record
    if runtime_memory_record is not None:
        result.runtime_memory_record = runtime_memory_record
    chapter_number = next(
        (int(e.chapter) for e in result.accepted_events if getattr(e, "chapter", None)),
        13,
    )
    return result, chapter_number


def _run_from_parent(
    bundle, llm, *, from_run_id: str, from_branch_id: str, rounds: int, runner_name: str | None
):
    from living_novel_engine.resume.loader import (
        build_seed_scene_state,
        load_parent_snapshot,
        project_characters_from_parent,
    )

    try:
        parent = load_parent_snapshot(from_run_id, from_branch_id)
    except FileNotFoundError as exc:
        raise BaselineRequestError(str(exc)) from exc

    characters, world = project_characters_from_parent(parent)
    spec = build_baseline_spec()
    next_chapter = parent.chapter_number + 1
    seed_state = build_seed_scene_state(parent)

    prologue = bundle.prologue
    if parent.summary_text.strip():
        prologue = (
            f"{prologue}\n\n【第{parent.chapter_number}章已发生】\n"
            f"{parent.summary_text.strip()}"
        )

    retrieved_ctx, retrieval_record, runtime_memory_record = "", None, None
    if bundle.project_dir and parent.source_type != "builtin_sample":
        query = parent.summary_text[:200] if parent.summary_text else parent.branch_theme
        ctx = build_runtime_memory_context(
            bundle.project_dir,
            query,
            current_chapter=next_chapter,
        )
        retrieved_ctx = ctx.as_prompt_block()
        retrieval_record = ctx.retrieval.to_artifact()
        runtime_memory_record = ctx.to_artifact()

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
        runner_name=runner_name,
    )
    if retrieval_record is not None:
        result.retrieval_record = retrieval_record
    if runtime_memory_record is not None:
        result.runtime_memory_record = runtime_memory_record
    return result, next_chapter, world


def generate_baseline(
    *,
    story_slug: str,
    rounds: int = 4,
    mock: bool = True,
    runner_name: str | None = None,
    from_run_id: str | None = None,
    from_branch_id: str | None = None,
) -> BaselineServiceResult:
    """生成一条无干预基线世界线，写出 baseline run，返回 run 信息与报告。"""
    slug = _validate_identifier(story_slug, "story_slug")
    if not isinstance(rounds, int) or rounds < 1 or rounds > 12:
        raise BaselineRequestError("rounds 必须为 1-12 的整数")
    if bool(from_run_id) != bool(from_branch_id):
        raise BaselineRequestError("from_run_id 与 from_branch_id 必须同时提供或同时缺省")
    if from_run_id:
        from_run_id = _validate_identifier(from_run_id, "from_run_id")
    if from_branch_id:
        from_branch_id = _validate_identifier(from_branch_id, "from_branch_id")

    # 缺故事让 FileNotFoundError 透传（→ HTTP 404）；坏 slug 已在上方校验。
    bundle = load_story(slug)

    llm, used_mock = resolve_llm_quietly(mock)
    runner = runner_name or "lightweight"

    if from_run_id and from_branch_id:
        result, chapter_number, world = _run_from_parent(
            bundle,
            llm,
            from_run_id=from_run_id,
            from_branch_id=from_branch_id,
            rounds=rounds,
            runner_name=runner_name,
        )
        char_map = {c.id: c for c in bundle.characters}
    else:
        result, chapter_number = _run_from_anchor(
            bundle, llm, rounds=rounds, runner_name=runner_name
        )
        world = bundle.world
        char_map = bundle.character_map()

    # worldline_id 标记为 baseline，确保分支目录与 events.worldline_id 一致。
    result.worldline_id = "baseline"

    report = _build_report(
        story_slug=slug,
        source_kind=bundle.source_kind,
        run_id="",  # 写盘后回填
        from_run_id=from_run_id,
        from_branch_id=from_branch_id,
        chapter_number=chapter_number,
        runner=result.runner_name or runner,
        mock=used_mock,
        result=result,
        char_map=char_map,
        world=world,
    )

    meta = {
        "kind": "baseline",
        "story_slug": slug,
        "source_kind": "builtin" if bundle.source_kind == "builtin" else "imported",
        "baseline": True,
        "no_intervention": True,
        "parent_run_id": from_run_id,
        "parent_branch_id": from_branch_id,
        "current_chapter": chapter_number,
        "runner": result.runner_name or runner,
        "created_at": report.created_at,
    }
    baseline_meta = {
        "branch_id": "baseline",
        "story_slug": slug,
        "source_kind": meta["source_kind"],
        "chapter_number": chapter_number,
        "no_intervention": True,
        "from_run_id": from_run_id,
        "from_branch_id": from_branch_id,
        "runner": result.runner_name or runner,
        "created_at": report.created_at,
    }

    output = write_baseline_output(
        result=result,
        report=report.model_dump(mode="json"),
        meta=meta,
        baseline_meta=baseline_meta,
    )

    # 回填 run_id 并重写 baseline_report.json，确保报告内 run_id 准确。
    report.run_id = output.run_id
    report_path = output.run_dir / "baseline_report.json"
    import json

    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report_dict = report.model_dump(mode="json")
    return BaselineServiceResult(
        run_id=output.run_id,
        run_dir=output.run_dir,
        branch_id="baseline",
        story_slug=slug,
        summary=report.summary,
        report=report_dict,
        extra={"llm_mock": used_mock},
    )


def get_baseline_report(run_id: str, *, outputs_dir: Path | None = None) -> dict:
    """读取某个 baseline run 的 baseline_report.json（不存在抛 FileNotFoundError → 404）。"""
    import json

    rid = _validate_identifier(run_id, "run_id")
    root = outputs_dir or _outputs_root()
    path = root / rid / "baseline_report.json"
    if not path.exists():
        raise FileNotFoundError(f"baseline 报告不存在: {rid}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise BaselineRequestError(f"baseline 报告损坏: {rid}") from exc

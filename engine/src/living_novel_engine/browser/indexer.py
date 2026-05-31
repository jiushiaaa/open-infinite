"""Index projects/ and outputs/ for the read-only worldline browser."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

from living_novel_engine.entity_aliases import load_entity_aliases
from living_novel_engine.browser.paths import outputs_dir, projects_dir, samples_dir
from living_novel_engine.import_novel.report import (
    REPORT_VERSION,
    chapter_previews_from_report,
    summarize_import_report,
)
from living_novel_engine.samples import list_samples
from living_novel_engine.service.worldline_selection import get_selected_worldline

RunKind = Literal["intervene", "resume_continue", "resume_intervene", "unknown"]
BRANCH_IDS = ("branch_a", "branch_b", "branch_c", "linear")


@dataclass
class BranchSummary:
    id: str
    theme: str
    termination_reason: str = ""
    chapter_chars: int = 0
    has_state: bool = False
    has_retrieval: bool = False
    retrieval_count: int = 0
    has_runtime_memory: bool = False
    runtime_memory_layer_count: int = 0
    has_multi_agent_trace: bool = False
    multi_agent_trace_count: int = 0
    has_causal_diff: bool = False
    causal_diff_count: int = 0


@dataclass
class RunSummary:
    run_id: str
    kind: RunKind
    story_slug: str
    source_kind: str
    branches: list[BranchSummary] = field(default_factory=list)
    parent_run_id: str | None = None
    parent_branch: str | None = None
    current_chapter: int | None = None
    has_compare: bool = False
    has_intervention: bool = False
    intervention_preview: str = ""
    lineage: list[str] = field(default_factory=list)


@dataclass
class StorySummary:
    slug: str
    display_name: str
    source_kind: Literal["builtin", "imported"]
    run_count: int = 0


def _read_json(path: Path) -> dict[str, Any]:
    """Read JSON; return {} on any read/parse failure (browser is read-only & defensive)."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _read_optional_json(path: Path) -> dict[str, Any] | None:
    """Read JSON if the file exists; None when absent, {} when corrupt (defensive)."""
    if not path.exists():
        return None
    return _read_json(path)


def _read_yaml(path: Path) -> Any:
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (OSError, yaml.YAMLError, UnicodeDecodeError):
        return None


def _read_text(path: Path, limit: int | None = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if limit is not None and len(text) > limit:
        return text[:limit]
    return text


def _infer_run_kind(run_dir: Path, meta: dict[str, Any] | None) -> RunKind:
    if meta and meta.get("kind") in (
        "resume_continue",
        "resume_intervene",
        "intervene",
    ):
        return meta["kind"]  # type: ignore[return-value]
    if (run_dir / "intervention.json").exists() and not (run_dir / "meta.json").exists():
        return "intervene"
    if meta and meta.get("kind") == "resume_continue":
        return "resume_continue"
    if (run_dir / "linear").is_dir():
        return "resume_continue"
    if (run_dir / "intervention.json").exists() and (run_dir / "meta.json").exists():
        return "resume_intervene"
    if any((run_dir / b).is_dir() for b in ("branch_a", "branch_b", "branch_c")):
        return "intervene"
    return "unknown"


def _branch_theme(branch_dir: Path, events: dict[str, Any] | None) -> str:
    if events and events.get("theme"):
        return str(events["theme"])
    snap_path = branch_dir / "state_snapshot.json"
    if snap_path.exists():
        snap = _read_json(snap_path)
        if snap.get("branch_theme"):
            return str(snap["branch_theme"])
    return branch_dir.name


def _list_len_in_json(path: Path, key: str) -> tuple[bool, int]:
    """(exists, len(json[key])) ；缺失返回 (False, 0)，损坏/非列表返回 (True, 0)。"""
    if not path.exists():
        return False, 0
    value = _read_json(path).get(key)
    return True, len(value) if isinstance(value, list) else 0


def _scan_branch(branch_dir: Path) -> BranchSummary:
    events: dict[str, Any] | None = None
    events_path = branch_dir / "events.json"
    if events_path.exists():
        events = _read_json(events_path)

    chapter_path = branch_dir / "chapter.md"
    chapter_chars = len(chapter_path.read_text(encoding="utf-8")) if chapter_path.exists() else 0
    termination = str(events.get("termination_reason", "")) if events else ""

    has_retrieval, retrieval_count = _list_len_in_json(
        branch_dir / "retrieval_context.json", "items"
    )
    has_runtime_memory, runtime_memory_layer_count = _list_len_in_json(
        branch_dir / "runtime_memory_context.json", "consumed_layers"
    )
    has_trace, trace_count = _list_len_in_json(
        branch_dir / "multi_agent_trace.json", "turn_plans"
    )
    has_diff, diff_count = _list_len_in_json(
        branch_dir / "causal_diff.json", "blocks"
    )

    return BranchSummary(
        id=branch_dir.name,
        theme=_branch_theme(branch_dir, events),
        termination_reason=termination,
        chapter_chars=chapter_chars,
        has_state=(branch_dir / "state_snapshot.json").exists(),
        has_retrieval=has_retrieval,
        retrieval_count=retrieval_count,
        has_runtime_memory=has_runtime_memory,
        runtime_memory_layer_count=runtime_memory_layer_count,
        has_multi_agent_trace=has_trace,
        multi_agent_trace_count=trace_count,
        has_causal_diff=has_diff,
        causal_diff_count=diff_count,
    )


def _list_branch_dirs(run_dir: Path) -> list[Path]:
    found: list[Path] = []
    for name in BRANCH_IDS:
        p = run_dir / name
        if p.is_dir() and (
            (p / "chapter.md").exists()
            or (p / "state_snapshot.json").exists()
            or (p / "events.json").exists()
        ):
            found.append(p)
    if found:
        return found
    return [
        p
        for p in run_dir.iterdir()
        if p.is_dir()
        and p.name not in ("source", "canon")
        and (
            (p / "chapter.md").exists()
            or (p / "state_snapshot.json").exists()
        )
    ]


def index_run(run_dir: Path) -> RunSummary | None:
    try:
        if not run_dir.is_dir() or not run_dir.name.startswith("run_"):
            return None
    except OSError:
        return None

    meta: dict[str, Any] = {}
    meta_path = run_dir / "meta.json"
    if meta_path.exists():
        meta = _read_json(meta_path)

    kind = _infer_run_kind(run_dir, meta or None)
    story_slug = "tianhuang-night"
    source_kind = "builtin"

    intervention_path = run_dir / "intervention.json"
    intervention_preview = ""
    if intervention_path.exists():
        inv = _read_json(intervention_path)
        story_slug = str(
            inv.get("story_slug") or inv.get("sample_slug") or story_slug
        )
        if inv.get("source_kind") in ("builtin", "imported"):
            source_kind = inv["source_kind"]
        target = inv.get("target", "")
        content = str(inv.get("content", ""))[:80]
        intervention_preview = f"{target}: {content}" if target else content

    if meta:
        story_slug = str(meta.get("story_slug") or meta.get("sample_slug") or story_slug)
        if meta.get("source_kind") in ("builtin", "imported"):
            source_kind = meta["source_kind"]

    try:
        branches = [_scan_branch(b) for b in _list_branch_dirs(run_dir)]
    except OSError:
        branches = []

    parent_run_id = None
    parent_branch = None
    current_chapter = None
    lineage: list[str] = []
    if meta:
        parent_run_id = meta.get("parent_run_id")
        parent_branch = meta.get("parent_branch")
        if meta.get("current_chapter") is not None:
            current_chapter = int(meta["current_chapter"])
        lineage = list(meta.get("lineage", []))

    return RunSummary(
        run_id=run_dir.name,
        kind=kind,
        story_slug=story_slug,
        source_kind=source_kind,
        branches=branches,
        parent_run_id=str(parent_run_id) if parent_run_id else None,
        parent_branch=str(parent_branch) if parent_branch else None,
        current_chapter=current_chapter,
        has_compare=(run_dir / "compare.md").exists(),
        has_intervention=intervention_path.exists(),
        intervention_preview=intervention_preview,
        lineage=lineage,
    )


def _quick_story_slug(run_dir: Path) -> str | None:
    """Cheaply infer run story_slug before scanning branch folders.

    ``index_run`` reads every branch to populate tree badges. Story-filtered
    calls can skip most runs by consulting root-level metadata first.
    """
    for name in ("meta.json", "intervention.json", "baseline_report.json"):
        path = run_dir / name
        if not path.exists():
            continue
        try:
            data = _read_json(path)
        except Exception:
            continue
        slug = data.get("story_slug") or data.get("sample_slug")
        if slug:
            return str(slug)
    return "tianhuang-night" if run_dir.name.startswith("run_") else None


def list_runs(*, story_slug: str | None = None) -> list[RunSummary]:
    out_dir = outputs_dir()
    if not out_dir.exists():
        return []

    runs: list[RunSummary] = []
    try:
        entries = sorted(out_dir.iterdir(), reverse=True)
    except OSError:
        return []
    for run_dir in entries:
        try:
            if not run_dir.is_dir():
                continue
        except OSError:
            continue
        if story_slug:
            quick_slug = _quick_story_slug(run_dir)
            if quick_slug is not None and quick_slug != story_slug:
                continue
        try:
            summary = index_run(run_dir)
        except Exception:
            continue
        if summary is None:
            continue
        if story_slug and summary.story_slug != story_slug:
            continue
        runs.append(summary)
    return runs


def get_run(run_id: str) -> dict[str, Any]:
    run_dir = outputs_dir() / run_id
    if not run_dir.is_dir():
        raise FileNotFoundError(f"运行不存在: {run_id}")

    summary = index_run(run_dir)
    if summary is None:
        raise FileNotFoundError(f"无效运行目录: {run_id}")

    payload: dict[str, Any] = asdict(summary)
    if summary.has_compare:
        payload["compare_md"] = _read_text(run_dir / "compare.md")
    if summary.has_intervention:
        payload["intervention"] = _read_json(run_dir / "intervention.json")
    compilation = _read_optional_json(run_dir / "intervention_compilation.json")
    if compilation is not None:
        payload["intervention_compilation"] = compilation
    if (run_dir / "meta.json").exists():
        payload["meta"] = _read_json(run_dir / "meta.json")
    if (run_dir / "parent_chapter.md").exists():
        payload["parent_chapter_preview"] = _read_text(
            run_dir / "parent_chapter.md", limit=500
        )
    payload["cli_hints"] = _cli_hints(summary)
    return payload


def get_branch(run_id: str, branch_id: str) -> dict[str, Any]:
    run_dir = outputs_dir() / run_id
    branch_dir = run_dir / branch_id
    if not branch_dir.is_dir():
        raise FileNotFoundError(f"分支不存在: {run_id}/{branch_id}")

    chapter = _read_text(branch_dir / "chapter.md")
    summary = _read_text(branch_dir / "summary.md")
    state = _read_optional_json(branch_dir / "state_snapshot.json")
    events = _read_optional_json(branch_dir / "events.json")
    retrieval = _read_optional_json(branch_dir / "retrieval_context.json")
    runtime_memory = _read_optional_json(branch_dir / "runtime_memory_context.json")
    multi_agent_trace = _read_optional_json(branch_dir / "multi_agent_trace.json")
    causal_diff = _read_optional_json(branch_dir / "causal_diff.json")
    act_director_plan = _read_optional_json(run_dir / "act_director_plan.json")
    dynamic_action_registry = _read_yaml(run_dir / "dynamic_action_registry.yaml")
    narrative_diagnostics = _read_optional_json(
        branch_dir / "narrative_diagnostics.json"
    )
    emergence_nodes = _read_optional_json(run_dir / "emergence_nodes.json")
    runner_state_execution_report = _read_optional_json(
        run_dir / "runner_state_execution_report.json"
    )
    runner_state_execution_apply_report = _read_optional_json(
        run_dir / "runner_state_execution_apply_report.json"
    )
    runner_state_execution_rollback_report = _read_optional_json(
        run_dir / "runner_state_execution_rollback_report.json"
    )
    state_execution_overlay = _read_optional_json(
        branch_dir / "state_execution_overlay.json"
    )

    run_summary = index_run(run_dir)
    child_runs: list[str] = []
    if run_summary:
        for r in list_runs(story_slug=run_summary.story_slug):
            if r.parent_run_id == run_id and r.parent_branch == branch_id:
                child_runs.append(r.run_id)

    hints: list[str] = []
    if run_summary:
        if branch_id != "linear":
            hints.append(
                f"lne resume continue {run_id} --branch {branch_id} --mock"
            )
        else:
            hints.append(
                f"lne resume intervene {run_id} --branch linear "
                f"--target <char_id> --content \"...\" --mock"
            )

    return {
        "run_id": run_id,
        "branch_id": branch_id,
        "theme": _branch_theme(branch_dir, events),
        "chapter_md": chapter,
        "summary_md": summary,
        "state_snapshot": state,
        "events": events,
        "retrieval": retrieval,
        "runtime_memory_context": runtime_memory,
        "act_director_plan": act_director_plan,
        "dynamic_action_registry": dynamic_action_registry,
        "narrative_diagnostics": narrative_diagnostics,
        "emergence_nodes": emergence_nodes,
        "runner_state_execution_report": runner_state_execution_report,
        "runner_state_execution_apply_report": runner_state_execution_apply_report,
        "runner_state_execution_rollback_report": runner_state_execution_rollback_report,
        "state_execution_overlay": state_execution_overlay,
        "multi_agent_trace": multi_agent_trace,
        "causal_diff": causal_diff,
        "child_runs": child_runs,
        "cli_hints": hints,
    }


def _cli_hints(run: RunSummary) -> list[str]:
    hints: list[str] = []
    if run.kind == "intervene" and run.branches:
        hints.append(f"lne compare outputs/{run.run_id}")
        for b in run.branches[:1]:
            hints.append(
                f"lne resume continue {run.run_id} --branch {b.id} --mock"
            )
    elif run.kind == "resume_continue":
        hints.append(
            f"lne resume intervene {run.run_id} --branch linear "
            f"--target <char_id> --content \"...\" --mock"
        )
    return hints


def list_stories() -> list[StorySummary]:
    stories: dict[str, StorySummary] = {}

    for slug in list_samples():
        try:
            from living_novel_engine.samples import load_sample

            bundle = load_sample(slug)
            stories[slug] = StorySummary(
                slug=slug,
                display_name=bundle.display_name,
                source_kind="builtin",
            )
        except Exception:
            stories[slug] = StorySummary(
                slug=slug, display_name=slug, source_kind="builtin"
            )

    proj_root = projects_dir()
    if proj_root.exists():
        try:
            entries = sorted(proj_root.iterdir())
        except OSError:
            entries = []
        for pdir in entries:
            if not pdir.is_dir() or not (pdir / "world.yaml").exists():
                continue
            slug = pdir.name
            w = _read_yaml(pdir / "world.yaml") or {}
            display = w.get("display_name") or w.get("title") or slug
            stories[slug] = StorySummary(
                slug=slug, display_name=display, source_kind="imported"
            )

    runs = list_runs()
    run_counts: dict[str, int] = defaultdict(int)
    for r in runs:
        run_counts[r.story_slug] += 1

    result = list(stories.values())
    for s in result:
        s.run_count = run_counts.get(s.slug, 0)
    result.sort(key=lambda s: (-s.run_count, s.slug))
    return result


def get_story(slug: str) -> dict[str, Any]:
    story_path: Path | None = None
    source_kind: Literal["builtin", "imported"] = "builtin"

    sample_path = samples_dir() / slug
    project_path = projects_dir() / slug
    if project_path.exists() and (project_path / "world.yaml").exists():
        story_path = project_path
        source_kind = "imported"
    elif sample_path.exists() and (sample_path / "world.yaml").exists():
        story_path = sample_path
        source_kind = "builtin"
    else:
        raise FileNotFoundError(f"故事不存在: {slug}")

    assert story_path is not None
    world = _read_yaml(story_path / "world.yaml") or {}

    characters: list[dict[str, Any]] = []
    chars_path = story_path / "characters.yaml"
    if chars_path.exists():
        data = _read_yaml(chars_path) or {}
        characters = list(data.get("characters", []) or [])

    payload: dict[str, Any] = {
        "slug": slug,
        "source_kind": source_kind,
        "display_name": world.get("display_name") or world.get("title") or slug,
        "divergence_point": world.get("divergence_point", ""),
        "rules": world.get("rules", []),
        "characters": [
            {
                "id": c.get("id"),
                "name": c.get("name"),
                "narrative_role": c.get("narrative_role"),
                "present_in_scene": c.get("present_in_scene", False),
            }
            for c in characters
        ],
        "runs": [asdict(r) for r in list_runs(story_slug=slug)],
    }

    contract_path = story_path / "story_contract.yaml"
    if contract_path.exists():
        contract = _read_yaml(contract_path)
        if contract is not None:
            payload["story_contract"] = contract

    facts_path = story_path / "canon" / "facts.jsonl"
    if facts_path.exists():
        facts: list[dict[str, Any]] = []
        try:
            for line in facts_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    facts.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            payload["facts"] = facts
        except OSError:
            pass

    summaries_dir = story_path / "summaries"
    if summaries_dir.exists():
        summaries: list[Any] = []
        for sp in sorted(summaries_dir.glob("chapter_*.yaml")):
            data = _read_yaml(sp)
            if data is not None:
                summaries.append(data)
        if summaries:
            payload["summaries"] = summaries

    import_meta = story_path / "import_meta.json"
    if import_meta.exists():
        payload["import_meta"] = _read_json(import_meta)
    if source_kind == "imported":
        payload["import_review"] = _import_review(story_path)

    return payload


def _resolve_story_path(slug: str) -> tuple[Path, Literal["builtin", "imported"]]:
    """定位故事目录并判定来源；projects 优先于同名 sample。"""
    project_path = projects_dir() / slug
    if project_path.exists() and (project_path / "world.yaml").exists():
        return project_path, "imported"
    sample_path = samples_dir() / slug
    if sample_path.exists() and (sample_path / "world.yaml").exists():
        return sample_path, "builtin"
    raise FileNotFoundError(f"故事不存在: {slug}")


def _anchor_characters(story_path: Path) -> list[dict[str, Any]]:
    chars_path = story_path / "characters.yaml"
    if not chars_path.exists():
        return []
    data = _read_yaml(chars_path) or {}
    out: list[dict[str, Any]] = []
    for c in data.get("characters", []) or []:
        if not isinstance(c, dict):
            continue
        persona = c.get("persona", {}) or {}
        state = c.get("current_state", {}) or {}
        out.append(
            {
                "id": c.get("id"),
                "name": c.get("name"),
                "narrative_role": c.get("narrative_role", "supporting"),
                "gender": c.get("gender", ""),
                "present_in_scene": bool(c.get("present_in_scene", True)),
                "persona": {
                    "traits": list(persona.get("traits", []) or []),
                    "desires": list(persona.get("desires", []) or []),
                    "fears": list(persona.get("fears", []) or []),
                    "boundaries": list(persona.get("boundaries", []) or []),
                },
                "current_state": {
                    "location": state.get("location", ""),
                    "emotion": state.get("emotion", ""),
                    "resources": list(state.get("resources", []) or []),
                },
                "memory": list(c.get("memory", []) or []),
                "relationships": dict(c.get("relationships", {}) or {}),
                "address_rules": list(c.get("address_rules", []) or []),
            }
        )
    return out


def _anchor_open_threads(story_path: Path, world: dict[str, Any]) -> list[dict[str, Any]]:
    ot_path = story_path / "open_threads.yaml"
    raw: Any
    if ot_path.exists():
        raw = _read_yaml(ot_path) or []
    else:
        raw = world.get("open_threads", []) or []
    threads: list[dict[str, Any]] = []
    for i, t in enumerate(raw):
        if isinstance(t, dict):
            threads.append(
                {
                    "id": t.get("id", str(i)),
                    "title": t.get("title", ""),
                    "description": t.get("description", ""),
                    "status": t.get("status", "open"),
                }
            )
        else:
            threads.append({"id": str(i), "title": str(t), "description": "", "status": "open"})
    return threads


def _anchor_summaries(story_path: Path) -> list[dict[str, Any]]:
    summaries_dir = story_path / "summaries"
    if not summaries_dir.exists():
        return []
    out: list[dict[str, Any]] = []
    for sp in sorted(summaries_dir.glob("chapter_*.yaml")):
        data = _read_yaml(sp)
        if not isinstance(data, dict):
            continue
        out.append(
            {
                "chapter": data.get("chapter"),
                "title": data.get("title", ""),
                "summary": data.get("summary", ""),
                "key_events": list(data.get("key_events", []) or []),
                "characters_present": list(data.get("characters_present", []) or []),
            }
        )
    return out


def _entity_alias_summary(story_path: Path) -> dict[str, Any]:
    return load_entity_aliases(story_path).to_summary()


def _read_import_report_with_status(path: Path) -> tuple[str, dict[str, Any]]:
    if not path.exists():
        return "missing", {}
    try:
        return "ready", json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return "damaged", {}


def _source_chapter_previews(story_path: Path, *, limit: int = 8) -> list[dict[str, Any]]:
    source_dir = story_path / "source"
    if not source_dir.exists():
        return []
    try:
        paths = sorted(source_dir.glob("chapter_*.md"))
    except OSError:
        return []
    previews: list[dict[str, Any]] = []
    for index, path in enumerate(paths[:limit], start=1):
        text = _read_text(path, limit=600).strip()
        if not text:
            continue
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        title = lines[0][:60] if lines else path.stem
        preview = " ".join(lines)[:160]
        previews.append(
            {
                "index": index,
                "title": title,
                "characters": len(text),
                "preview": preview,
                "source_path": f"source/{path.name}",
                "source_filename": path.name,
            }
        )
    return previews


def _fallback_import_summary(status: str, previews: list[dict[str, Any]]) -> dict[str, Any]:
    total_chars = sum(int(p.get("characters") or 0) for p in previews)
    lengths = [int(p.get("characters") or 0) for p in previews]
    warnings = [
        "导入报告缺失，已仅用章节文件生成预览。"
        if status == "missing"
        else "导入报告无法解析，已仅用章节文件生成预览。"
    ]
    return {
        "version": REPORT_VERSION,
        "status": status,
        "source": {"type": "unknown"},
        "total_chapters": len(previews),
        "total_characters": total_chars,
        "chapter_stats": {
            "min_characters": min(lengths, default=0),
            "max_characters": max(lengths, default=0),
            "average_characters": round(total_chars / len(lengths), 1)
            if lengths
            else 0,
            "short_chapters": [],
        },
        "playable_chapter_limit": min(20, len(previews)),
        "partial_ready": len(previews) > 20,
        "risks": {},
        "quality_risks": [],
        "recommended_actions": [
            {
                "kind": "regenerate_import_report",
                "label": "重新生成导入报告",
                "description": "报告缺失或损坏时，先重新导入或覆盖项目，再继续长篇审查。",
            }
        ],
        "warnings": warnings,
    }


def _import_review(story_path: Path) -> dict[str, Any]:
    status, report = _read_import_report_with_status(story_path / "import_report.json")
    fallback_previews = _source_chapter_previews(story_path)
    if status == "ready":
        previews = chapter_previews_from_report(report) or fallback_previews
        return {
            "status": "ready",
            "summary": summarize_import_report(report),
            "quality_risks": list(report.get("quality_risks", []) or []),
            "recommended_actions": list(report.get("recommended_actions", []) or []),
            "warnings": list(report.get("warnings", []) or []),
            "chapter_previews": previews,
        }

    summary = _fallback_import_summary(status, fallback_previews)
    return {
        "status": status,
        "summary": summary,
        "quality_risks": [],
        "recommended_actions": summary["recommended_actions"],
        "warnings": summary["warnings"],
        "chapter_previews": fallback_previews,
    }


def _read_json_with_status(path: Path) -> tuple[str, dict[str, Any]]:
    if not path.exists():
        return "missing", {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return "damaged", {}
    return ("ready", data) if isinstance(data, dict) else ("damaged", {})


def _memory_summary(story_path: Path) -> dict[str, Any]:
    status, manifest = _read_json_with_status(
        story_path / "memory" / "memory_manifest.json"
    )
    if status != "ready":
        warning = (
            "分层记忆清单缺失。"
            if status == "missing"
            else "分层记忆清单无法解析。"
        )
        return {
            "status": status,
            "version": "",
            "layer_count": 0,
            "layers": [],
            "warnings": [warning],
        }

    raw_layers = manifest.get("layers", {}) or {}
    layers = []
    if isinstance(raw_layers, dict):
        for name, raw in raw_layers.items():
            if not isinstance(raw, dict):
                continue
            layers.append(
                {
                    "name": name,
                    "path": raw.get("path", ""),
                    "count": int(raw.get("count") or 0),
                }
            )
    return {
        "status": "ready",
        "version": manifest.get("version", ""),
        "created_at": manifest.get("created_at", ""),
        "layer_count": len(layers),
        "layers": layers,
        "warnings": [],
    }


def _canon_ledger_summary(story_path: Path) -> dict[str, Any]:
    path = story_path / "memory" / "canon_ledger.jsonl"
    if not path.exists():
        return {
            "status": "missing",
            "entry_count": 0,
            "type_counts": {},
            "samples": [],
            "warnings": ["正史账本缺失。"],
        }

    records: list[dict[str, Any]] = []
    type_counts: dict[str, int] = defaultdict(int)
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                continue
            records.append(record)
            type_counts[str(record.get("type") or "unknown")] += 1
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {
            "status": "damaged",
            "entry_count": 0,
            "type_counts": {},
            "samples": [],
            "warnings": ["正史账本无法解析，已停止展示样例。"],
        }

    samples = [
        {
            "id": r.get("id", ""),
            "type": r.get("type", ""),
            "chapter": r.get("chapter"),
            "source_ref": r.get("source_ref", ""),
            "statement": str(r.get("statement") or "")[:160],
        }
        for r in records[:6]
    ]
    return {
        "status": "ready",
        "entry_count": len(records),
        "type_counts": dict(sorted(type_counts.items())),
        "samples": samples,
        "warnings": [],
    }


def _audit_summary(story_path: Path) -> dict[str, Any]:
    status, report = _read_json_with_status(
        story_path / "memory" / "consistency_report.json"
    )
    if status != "ready":
        warning = (
            "一致性审计报告缺失。"
            if status == "missing"
            else "一致性审计报告无法解析。"
        )
        return {
            "status": status,
            "version": "",
            "summary": {"issue_count": 0, "risk_level": "unknown"},
            "dimensions": [],
            "issues": [],
            "repair_suggestions": [],
            "warnings": [warning],
        }

    issue_groups = [
        "persona_drift",
        "timeline_conflicts",
        "resource_conflicts",
        "contract_violations",
        "forgotten_threads",
    ]
    issues: list[dict[str, Any]] = []
    dimensions: list[dict[str, Any]] = []
    for group in issue_groups:
        raw_items = report.get(group, []) or []
        if not isinstance(raw_items, list):
            continue
        severity_counts: dict[str, int] = defaultdict(int)
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            severity_counts[str(item.get("severity") or "unknown")] += 1
            issues.append(
                {
                    "category": group,
                    "kind": item.get("kind", ""),
                    "severity": item.get("severity", ""),
                    "detail": item.get("detail", ""),
                    "evidence": item.get("evidence", ""),
                }
            )
        dimensions.append(
            {
                "key": group,
                "label": _audit_dimension_label(group),
                "issue_count": len(raw_items),
                "severity_counts": dict(sorted(severity_counts.items())),
            }
        )

    return {
        "status": "ready",
        "version": report.get("version", ""),
        "created_at": report.get("created_at", ""),
        "summary": report.get("summary", {"issue_count": len(issues)}),
        "dimensions": dimensions,
        "issues": issues[:10],
        "repair_suggestions": list(report.get("repair_suggestions", []) or []),
        "warnings": [],
    }


def _audit_dimension_label(key: str) -> str:
    labels = {
        "persona_drift": "人设漂移",
        "timeline_conflicts": "时间线",
        "resource_conflicts": "资源/文本",
        "contract_violations": "合约风险",
        "forgotten_threads": "开放伏笔",
    }
    return labels.get(key, key)


def _retrieval_summary(slug: str) -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    total = 0
    for run in list_runs(story_slug=slug)[:20]:
        for branch in run.branches:
            total += int(branch.retrieval_count or 0)
            if branch.retrieval_count <= 0:
                continue
            data = _read_optional_json(
                outputs_dir() / run.run_id / branch.id / "retrieval_context.json"
            )
            items = data.get("items", []) if isinstance(data, dict) else []
            if not isinstance(items, list):
                continue
            for item in items[:3]:
                if not isinstance(item, dict):
                    continue
                hits.append(
                    {
                        "run_id": run.run_id,
                        "branch_id": branch.id,
                        "source": item.get("source", ""),
                        "source_ref": item.get("source_ref", ""),
                        "score": item.get("score"),
                        "preview": str(
                            item.get("text")
                            or item.get("statement")
                            or item.get("summary")
                            or ""
                        )[:160],
                    }
                )
                if len(hits) >= 8:
                    break
            if len(hits) >= 8:
                break
        if len(hits) >= 8:
            break

    return {
        "status": "ready" if total else "missing",
        "hit_count": total,
        "samples": hits,
        "warnings": [] if total else ["尚无运行检索命中；先发起基线或干预后再查看。"],
    }


def _score_value(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _check_item(
    *,
    item_id: str,
    label: str,
    status: str,
    detail: str,
) -> dict[str, str]:
    return {"id": item_id, "label": label, "status": status, "detail": detail}


def _creation_loop_completion(checklist: list[dict[str, str]]) -> dict[str, Any]:
    total_count = len(checklist)
    done_count = sum(1 for item in checklist if item.get("status") == "done")
    blocking_items = [item for item in checklist if item.get("status") != "done"]
    has_todo = any(item.get("status") == "todo" for item in blocking_items)
    if total_count == 0 or has_todo:
        status = "todo"
        summary = "长篇共创闭环尚未完成，先补齐阻塞步骤。"
    elif blocking_items:
        status = "warn"
        summary = "长篇共创主链路已串起，但仍有风险项需要复盘。"
    else:
        status = "ready"
        summary = "长篇共创闭环已具备 alpha 收口条件。"
    return {
        "kind": "creation_loop_completion",
        "status": status,
        "done_count": done_count,
        "total_count": total_count,
        "blocking_ids": [str(item.get("id") or "") for item in blocking_items],
        "blocking_labels": [str(item.get("label") or "") for item in blocking_items],
        "summary": summary,
        "can_mark_alpha_complete": status == "ready",
    }


def _creation_loop_actions(
    *,
    slug: str,
    recommended: dict[str, Any] | None,
    selected: dict[str, Any],
    post_run_audit: dict[str, Any],
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    if recommended:
        run_id = str(recommended.get("run_id") or "")
        branch_id = str(recommended.get("branch_id") or "")
        if not recommended.get("has_judgement"):
            actions.append(
                {
                    "id": "worldline_judgement",
                    "label": "生成世界线评审",
                    "status": "available",
                    "kind": "api",
                    "method": "POST",
                    "api_path": (
                        f"/api/runs/{run_id}/branches/{branch_id}/worldline-judgement"
                    ),
                    "detail": "补齐推荐世界线的评审报告。",
                }
            )
        if (
            selected.get("status") != "ready"
            or selected.get("run_id") != run_id
            or selected.get("branch_id") != branch_id
        ):
            actions.append(
                {
                    "id": "select_worldline",
                    "label": "设为下一章起点",
                    "status": "available",
                    "kind": "api",
                    "method": "POST",
                    "api_path": f"/api/stories/{slug}/selected-worldline",
                    "detail": "把推荐世界线记录为后续续写起点。",
                }
            )
    if post_run_audit.get("status") != "ready":
        replay_payload = (
            _replay_range_quick_payload(slug)
            if selected.get("status") == "ready"
            and not post_run_audit.get("has_range_replay")
            else None
        )
        if replay_payload:
            actions.append(
                {
                    "id": "run_replay_range",
                    "label": "运行范围回放",
                    "status": "available",
                    "kind": "api",
                    "method": "POST",
                    "api_path": f"/api/stories/{slug}/canon/replay-range",
                    "payload": replay_payload,
                    "detail": "使用最新基线和已录入 holdout 直接补齐范围回放。",
                }
            )
        else:
            actions.append(
                {
                    "id": "replay_audit",
                    "label": "查看回放与审计",
                    "status": "available",
                    "kind": "route",
                    "method": "NAVIGATE",
                    "route_hash": f"#/anchor/{slug}",
                    "detail": "补齐范围回放或复盘现有风险。",
                }
            )
    return actions


def _replay_range_quick_payload(slug: str) -> dict[str, Any] | None:
    baselines = _baseline_run_summaries(slug)
    if not baselines:
        return None
    try:
        from living_novel_engine.service import get_holdout

        holdout = get_holdout(slug, projects_dir=projects_dir())
    except Exception:
        return None
    chapters = sorted(
        {
            int(chapter)
            for chapter in (holdout.get("available_chapters") or [])
            if isinstance(chapter, int) and chapter > 0
        }
    )
    if not chapters:
        return None
    baseline = baselines[0]
    return {
        "baseline_run_id": str(baseline.get("run_id") or ""),
        "baseline_branch_id": str(baseline.get("branch_id") or "baseline"),
        "chapter_start": chapters[0],
        "chapter_end": chapters[-1],
    }


def _creation_loop_evidence(
    *,
    slug: str,
    checklist: list[dict[str, str]],
    recommended: dict[str, Any] | None,
    post_run_audit: dict[str, Any],
) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    run_id = str((recommended or {}).get("run_id") or "")
    branch_id = str((recommended or {}).get("branch_id") or "")
    export_api_path = str((recommended or {}).get("export_api_path") or "")
    has_judgement = bool((recommended or {}).get("has_judgement"))

    for item in checklist:
        item_id = str(item.get("id") or "")
        source = "state"
        ref = item_id
        detail = str(item.get("detail") or "")
        if item_id == "import_review":
            source = "route"
            ref = f"#/anchor/{slug}"
            detail = "世界锚定页会展示导入检查与章节片段。"
        elif item_id == "branch_run" and recommended:
            source = "artifact"
            ref = f"run:{run_id}/branch:{branch_id}"
            detail = "推荐世界线已有可阅读分支输出。"
        elif item_id == "worldline_judgement" and recommended:
            if has_judgement:
                source = "artifact"
                ref = "worldline_judgement.json"
                detail = "推荐世界线已有评审 artifact。"
            else:
                source = "api"
                ref = f"/api/runs/{run_id}/branches/{branch_id}/worldline-judgement"
                detail = "可用快捷动作生成推荐世界线评审。"
        elif item_id == "replay_audit":
            source = "route"
            ref = f"#/anchor/{slug}"
            detail = "回放与审计页提供范围回放和静态风险维度。"
        elif item_id == "post_run_audit":
            source = "route"
            ref = str(post_run_audit.get("review_hash") or f"#/anchor/{slug}")
            detail = str(post_run_audit.get("summary") or detail)
        elif item_id in {"chapter_export", "export_share_guard"} and export_api_path:
            source = "api"
            ref = export_api_path
            detail = (
                "章节导出接口会返回正文、来源说明和版权边界。"
                if item_id == "chapter_export"
                else "导出负载内含 share_guard 版权边界。"
            )
        evidence.append(
            {
                "id": item_id,
                "label": str(item.get("label") or ""),
                "status": str(item.get("status") or ""),
                "source": source,
                "ref": ref,
                "detail": detail,
            }
        )
    return evidence


def _as_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    return 0


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _post_run_audit_summary(
    *,
    slug: str,
    selected: dict[str, Any],
    candidates: list[dict[str, Any]],
    audit: dict[str, Any],
) -> dict[str, Any]:
    review_hash = f"#/anchor/{slug}"
    if selected.get("status") != "ready":
        return {
            "status": "todo",
            "selected_run_id": "",
            "selected_branch_id": "",
            "selected_label": "",
            "summary": "先选择一条世界线，再核对审计与回放状态。",
            "review_hash": review_hash,
            "has_range_replay": False,
            "risk_level": "unknown",
            "static_issue_count": _as_int((audit.get("summary") or {}).get("issue_count")),
            "risk_dimensions": [],
            "missing_entities": [],
            "next_actions": ["先在候选世界线中设为起点。"],
        }

    selected_run_id = str(selected.get("run_id") or "")
    selected_branch_id = str(selected.get("branch_id") or "")
    candidate = next(
        (
            item
            for item in candidates
            if item.get("run_id") == selected_run_id
            and item.get("branch_id") == selected_branch_id
        ),
        None,
    )
    replay_ranges = _replay_range_reports(slug)
    latest_range = replay_ranges[0] if replay_ranges else None
    range_summary = (
        latest_range.get("summary", {})
        if isinstance(latest_range, dict) and latest_range
        else {}
    )
    risk_level = str(
        range_summary.get("risk_level")
        or (audit.get("summary") or {}).get("risk_level")
        or "unknown"
    )
    entity_audit = (
        latest_range.get("entity_audit", {})
        if isinstance(latest_range, dict) and latest_range
        else {}
    )
    missing_entities = [
        str(item) for item in _as_list(entity_audit.get("missing_entities"))
    ][:8]
    static_issue_count = _as_int((audit.get("summary") or {}).get("issue_count"))
    has_judgement = bool(candidate and candidate.get("has_judgement"))
    has_causal_diff = bool(candidate and candidate.get("has_causal_diff"))
    has_range_replay = latest_range is not None

    next_actions: list[str] = []
    if not has_judgement:
        next_actions.append("先运行世界线评审，确认这条线是否值得继续。")
    if not has_causal_diff:
        next_actions.append("先核对 Causal Diff，确认干预造成的偏移边界。")
    if not has_range_replay:
        next_actions.append("进入回放与审计，运行章节范围回放。")
    if static_issue_count > 0 or risk_level in {"medium", "high"} or missing_entities:
        next_actions.append("回放与审计中仍有风险，继续前先处理高影响项。")
    if not next_actions:
        next_actions.append("审计入口已补齐，可以继续生成下一章或导出留档。")

    if candidate is None:
        status = "warn"
        summary = "已选世界线不在当前候选列表中，先重新打开项目工作台确认。"
    elif not has_range_replay:
        status = "todo"
        summary = "已选世界线尚未完成范围回放，继续前建议先补审计。"
    elif (
        static_issue_count > 0
        or risk_level in {"medium", "high"}
        or missing_entities
        or not has_judgement
        or not has_causal_diff
    ):
        status = "warn"
        summary = "已选世界线有审计提示，继续前建议先复盘风险。"
    else:
        status = "ready"
        summary = "已选世界线的评审、Diff 与范围回放均可复盘。"

    risk_dimensions = []
    if isinstance(latest_range, dict):
        for item in _as_list(latest_range.get("risk_dimensions"))[:5]:
            if isinstance(item, dict):
                risk_dimensions.append(item)

    return {
        "status": status,
        "selected_run_id": selected_run_id,
        "selected_branch_id": selected_branch_id,
        "selected_label": str(selected.get("branch_label") or ""),
        "summary": summary,
        "review_hash": review_hash,
        "has_range_replay": has_range_replay,
        "risk_level": risk_level,
        "static_issue_count": static_issue_count,
        "risk_dimensions": risk_dimensions,
        "missing_entities": missing_entities,
        "range_replay": latest_range,
        "next_actions": next_actions,
    }


def _creation_loop_summary(
    *,
    slug: str,
    source_kind: str,
    story_path: Path,
    import_review: dict[str, Any] | None,
    audit: dict[str, Any],
    runs: list[RunSummary],
) -> dict[str, Any]:
    """v0.9.0-alpha：项目级创作闭环清单，不写 artifact。"""

    selected = get_selected_worldline(
        slug,
        project_dir=story_path if source_kind != "builtin" else None,
    )
    child_counts: dict[tuple[str, str], int] = defaultdict(int)
    for run in runs:
        if run.parent_run_id and run.parent_branch:
            child_counts[(run.parent_run_id, run.parent_branch)] += 1

    candidates: list[dict[str, Any]] = []
    for run in runs:
        run_dir = outputs_dir() / run.run_id
        for branch in run.branches:
            branch_dir = run_dir / branch.id
            judgement = _read_optional_json(branch_dir / "worldline_judgement.json")
            judgement_ready = bool(judgement)
            scores = judgement.get("scores", {}) if isinstance(judgement, dict) else {}
            overall_score = (
                _score_value(scores.get("overall")) if isinstance(scores, dict) else None
            )
            recommendation = (
                str(judgement.get("recommendation") or "") if judgement_ready else ""
            )
            causal_diff = _read_optional_json(branch_dir / "causal_diff.json")
            overlay = _read_optional_json(branch_dir / "state_execution_overlay.json")
            has_export = (branch_dir / "chapter.md").exists() and branch.chapter_chars > 0
            continue_hint = (
                f"lne resume continue {run.run_id} --branch {branch.id} --mock"
                if branch.id != "linear"
                else (
                    f"lne resume intervene {run.run_id} --branch linear "
                    '--target <char_id> --content "..." --mock'
                )
            )
            candidates.append(
                {
                    "run_id": run.run_id,
                    "branch_id": branch.id,
                    "run_kind": run.kind,
                    "branch_label": branch.theme or branch.id,
                    "chapter_chars": branch.chapter_chars,
                    "has_export": has_export,
                    "export_api_path": (
                        f"/api/runs/{run.run_id}/branches/{branch.id}/chapter-export"
                    )
                    if has_export
                    else "",
                    "has_judgement": judgement_ready,
                    "recommendation": recommendation or "未评审",
                    "overall_score": overall_score,
                    "has_causal_diff": bool(causal_diff),
                    "causal_diff_status": causal_diff.get("status")
                    if isinstance(causal_diff, dict) and causal_diff
                    else None,
                    "state_overlay_applied": bool(overlay),
                    "child_run_count": child_counts.get((run.run_id, branch.id), 0),
                    "continue_hint": continue_hint,
                    "is_selected": selected.get("status") == "ready"
                    and selected.get("run_id") == run.run_id
                    and selected.get("branch_id") == branch.id,
                }
            )

    recommendation_rank = {"推荐继续": 3, "谨慎继续": 2, "建议归档": 1}
    ranked_candidates = sorted(
        candidates,
        key=lambda item: (
            bool(item.get("has_export")),
            recommendation_rank.get(str(item.get("recommendation")), 0),
            float(item.get("overall_score") or 0),
            int(item.get("chapter_chars") or 0),
        ),
        reverse=True,
    )
    recommended = ranked_candidates[0] if ranked_candidates else None
    post_run_audit = _post_run_audit_summary(
        slug=slug,
        selected=selected,
        candidates=candidates,
        audit=audit,
    )

    if source_kind == "imported":
        review_status = str((import_review or {}).get("status") or "missing")
        import_status = "done" if review_status == "ready" else "warn"
        import_detail = (
            "导入检查报告可用。"
            if review_status == "ready"
            else "导入检查缺失或损坏，先回到世界锚定页确认来源与章节。"
        )
    else:
        import_status = "done"
        import_detail = "内置样例无需长篇导入检查。"

    has_judgement = any(bool(c.get("has_judgement")) for c in candidates)
    has_export = any(bool(c.get("has_export")) for c in candidates)
    audit_status = str(audit.get("status") or "missing")
    issue_count = int((audit.get("summary") or {}).get("issue_count") or 0)
    if audit_status == "ready" and issue_count == 0:
        audit_item_status = "done"
    elif audit_status in ("ready", "damaged"):
        audit_item_status = "warn"
    else:
        audit_item_status = "todo"

    checklist = [
        _check_item(
            item_id="import_review",
            label="确认导入质量",
            status=import_status,
            detail=import_detail,
        ),
        _check_item(
            item_id="branch_run",
            label="生成候选世界线",
            status="done" if candidates else "todo",
            detail="已有可阅读分支。" if candidates else "先发起基线或干预生成世界线。",
        ),
        _check_item(
            item_id="worldline_judgement",
            label="评审世界线",
            status="done" if has_judgement else "todo",
            detail="已有世界线评审。" if has_judgement else "先运行世界线评审再决定继续。",
        ),
        _check_item(
            item_id="replay_audit",
            label="核对审计风险",
            status=audit_item_status,
            detail=(
                "静态审计未发现问题。"
                if audit_item_status == "done"
                else "结合一致性审计与回放结果检查偏移风险。"
            ),
        ),
        _check_item(
            item_id="post_run_audit",
            label="选择后审计",
            status=(
                "done"
                if post_run_audit["status"] == "ready"
                else "todo"
                if post_run_audit["status"] == "todo"
                else "warn"
            ),
            detail=str(post_run_audit.get("summary") or ""),
        ),
        _check_item(
            item_id="chapter_export",
            label="导出当前章节",
            status="done" if has_export else "todo",
            detail="至少一条世界线可导出章节。" if has_export else "生成章节后再导出。",
        ),
        _check_item(
            item_id="export_share_guard",
            label="确认版权边界",
            status="done" if has_export else "todo",
            detail=(
                "导出前会提示版权与分享边界。"
                if has_export
                else "生成可导出章节后再确认版权与分享边界。"
            ),
        ),
    ]
    completion = _creation_loop_completion(checklist)
    completion["evidence"] = _creation_loop_evidence(
        slug=slug,
        checklist=checklist,
        recommended=recommended,
        post_run_audit=post_run_audit,
    )
    completion["actions"] = _creation_loop_actions(
        slug=slug,
        recommended=recommended,
        selected=selected,
        post_run_audit=post_run_audit,
    )

    next_steps: list[str] = []
    if recommended:
        next_steps.append(
            f"继续推荐世界线：{recommended['branch_label']}，先核对评审与 Diff，再导出或续写。"
        )
        if not recommended.get("has_judgement"):
            next_steps.append("该候选尚未评审，先运行世界线评审。")
        if recommended.get("has_export"):
            next_steps.append("可先导出章节留档，再决定是否继续生成下一章。")
    else:
        next_steps.append("先从项目工作台发起基线或干预，生成至少一条世界线。")
    if audit_item_status != "done":
        next_steps.append("继续前建议查看回放与审计，确认没有高风险冲突。")
    if post_run_audit["status"] != "ready":
        next_steps.extend(post_run_audit.get("next_actions", [])[:2])

    return {
        "version": "v0.9.0-alpha",
        "status": "ready" if recommended else "empty",
        "recommended": recommended,
        "selected": selected if selected.get("status") == "ready" else None,
        "post_run_audit": post_run_audit,
        "candidates": ranked_candidates[:6],
        "checklist": checklist,
        "completion": completion,
        "next_steps": next_steps,
    }


def get_project_workspace(slug: str) -> dict[str, Any]:
    """v0.8.8 长篇项目工作台：汇总导入、记忆、正史、审计与运行入口。"""

    story_path, source_kind = _resolve_story_path(slug)
    world = _read_yaml(story_path / "world.yaml") or {}
    import_review = _import_review(story_path) if source_kind == "imported" else None
    previews = (
        list(import_review.get("chapter_previews", []) or [])
        if import_review
        else _source_chapter_previews(story_path)
    )
    review_summary = import_review.get("summary", {}) if import_review else {}
    audit = _audit_summary(story_path)
    runs = list_runs(story_slug=slug)

    return {
        "version": "v0.9.0-alpha",
        "slug": slug,
        "source_kind": source_kind,
        "display_name": world.get("display_name") or world.get("title") or slug,
        "source": (review_summary.get("source") or {"type": source_kind})
        if isinstance(review_summary, dict)
        else {"type": source_kind},
        "chapter_overview": {
            "total_chapters": int(review_summary.get("total_chapters") or len(previews))
            if isinstance(review_summary, dict)
            else len(previews),
            "total_characters": int(review_summary.get("total_characters") or 0)
            if isinstance(review_summary, dict)
            else 0,
            "playable_chapter_limit": int(
                review_summary.get("playable_chapter_limit") or len(previews)
            )
            if isinstance(review_summary, dict)
            else len(previews),
            "partial_ready": bool(review_summary.get("partial_ready", False))
            if isinstance(review_summary, dict)
            else False,
            "previews": previews,
        },
        "import_review": import_review,
        "memory": _memory_summary(story_path),
        "canon_ledger": _canon_ledger_summary(story_path),
        "entity_aliases": _entity_alias_summary(story_path),
        "retrieval": _retrieval_summary(slug),
        "audit": audit,
        "run_count": len(runs),
        "creation_loop": _creation_loop_summary(
            slug=slug,
            source_kind=source_kind,
            story_path=story_path,
            import_review=import_review,
            audit=audit,
            runs=runs,
        ),
        "actions": {
            "anchor_hash": f"#/anchor/{slug}",
            "workspace_hash": f"#/workspace/{slug}",
            "can_start_baseline": True,
            "can_start_intervention": True,
            "next_steps": [
                "先核对章节与导入风险。",
                "再进入世界锚定页检查角色、规则与开放伏笔。",
                "确认无误后生成无干预基线，或选择世界线发起干预。",
            ],
        },
    }


def _baseline_run_summaries(slug: str) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for run in list_runs(story_slug=slug):
        report = _read_optional_json(outputs_dir() / run.run_id / "baseline_report.json")
        if not isinstance(report, dict) or not report:
            continue
        runs.append(
            {
                "run_id": run.run_id,
                "branch_id": report.get("branch_id", "baseline"),
                "chapter_number": report.get("chapter_number"),
                "summary": report.get("summary", ""),
                "created_at": report.get("created_at", ""),
                "from_run_id": report.get("from_run_id"),
                "from_branch_id": report.get("from_branch_id"),
            }
        )
    runs.sort(key=lambda r: str(r.get("run_id") or ""), reverse=True)
    return runs


def _replay_range_reports(slug: str) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for baseline in _baseline_run_summaries(slug):
        run_id = str(baseline.get("run_id") or "")
        report = _read_optional_json(
            outputs_dir() / run_id / "canon_replay_range_report.json"
        )
        if not isinstance(report, dict) or not report:
            continue
        reports.append(
            {
                "run_id": run_id,
                "status": "ready",
                "chapter_range": report.get("chapter_range", {}),
                "available_chapters": report.get("available_chapters", []),
                "summary": report.get("summary", {}),
                "risk_dimensions": report.get("risk_dimensions", []),
                "entity_audit": report.get("entity_audit", {}),
                "created_at": report.get("created_at", ""),
            }
        )
    return reports


def get_replay_audit_workspace(slug: str) -> dict[str, Any]:
    """v0.8.9 长篇回放与审计工作台数据。"""

    story_path, source_kind = _resolve_story_path(slug)
    world = _read_yaml(story_path / "world.yaml") or {}
    holdout: dict[str, Any]
    try:
        from living_novel_engine.service import get_holdout

        holdout = get_holdout(slug, projects_dir=projects_dir())
    except Exception as exc:
        holdout = {
            "version": "",
            "story_slug": slug,
            "chapters": [],
            "chapter_count": 0,
            "available_chapters": [],
            "warnings": [str(exc)],
        }
    return {
        "version": "v0.8.9",
        "slug": slug,
        "source_kind": source_kind,
        "display_name": world.get("display_name") or world.get("title") or slug,
        "holdout": holdout,
        "baseline_runs": _baseline_run_summaries(slug),
        "replay_ranges": _replay_range_reports(slug),
        "audit": _audit_summary(story_path),
        "entity_aliases": _entity_alias_summary(story_path),
        "next_steps": [
            "先录入或确认正史 holdout 章节范围。",
            "生成无干预基线后，选择章节范围运行正史回放。",
            "结合风险维度、缺失实体和一致性审计决定是否继续该世界线。",
        ],
    }


def get_world_anchor(slug: str) -> dict[str, Any]:
    """v0.7 第四刀：世界锚定页数据（world/characters/contract/threads/summaries）。

    builtin sample 与 imported project 均可读；缺文件返回 null/[]，不抛 500。
    """
    from living_novel_engine.story_loader import intervention_chapter_from_project

    story_path, source_kind = _resolve_story_path(slug)
    world = _read_yaml(story_path / "world.yaml") or {}

    current_chapter = None
    if source_kind == "imported":
        current_chapter = intervention_chapter_from_project(story_path)

    contract_path = story_path / "story_contract.yaml"
    story_contract = _read_yaml(contract_path) if contract_path.exists() else None

    payload: dict[str, Any] = {
        "slug": slug,
        "source_kind": source_kind,
        "display_name": world.get("display_name") or world.get("title") or slug,
        "divergence_point": world.get("divergence_point", ""),
        "world": {
            "display_name": world.get("display_name") or world.get("title") or slug,
            "source_type": world.get("source_type", source_kind),
            "canonical_place_name": world.get("canonical_place_name", ""),
            "worldline_policy": world.get("worldline_policy", ""),
            "scene_description": world.get("scene_description", ""),
            "current_chapter": current_chapter,
            "rules": list(world.get("rules", []) or []),
            "locations": list(world.get("locations", []) or []),
            "factions": list(world.get("factions", []) or []),
            "timeline": list(world.get("timeline", []) or []),
        },
        "characters": _anchor_characters(story_path),
        "story_contract": story_contract,
        "open_threads": _anchor_open_threads(story_path, world),
        "summaries": _anchor_summaries(story_path),
        "entity_aliases": _entity_alias_summary(story_path),
        "import_review": _import_review(story_path)
        if source_kind == "imported"
        else None,
        "run_count": len(list_runs(story_slug=slug)),
    }
    return payload


def build_worldline_tree(*, story_slug: str | None = None) -> list[dict[str, Any]]:
    """Build nested run trees keyed by parent (run_id, branch_id).

    Sorting contract (stable across multiple stories / roots / orphans):

    - Roots are returned in descending ``run_id`` order. Because ``run_id``
      is timestamp-prefixed (``run_YYYYMMDD_HHMMSS_xxx``) this is equivalent
      to newest-first, and the lexicographic order is total/deterministic.
    - ``is_orphan`` marks a root whose declared ``parent_run_id`` points to
      a run that does not exist in the current index (e.g. archived parent).
      Orphans appear alongside genuine roots; the flag lets the UI label
      them so users do not mistake them for fresh top-level interventions.
    - Children of a branch are also sorted by descending ``run_id``.
    """
    runs = list_runs(story_slug=story_slug)
    by_id = {r.run_id: r for r in runs}
    children_map: dict[tuple[str, str], list[str]] = defaultdict(list)
    child_ids: set[str] = set()

    for r in runs:
        if r.parent_run_id and r.parent_branch and r.parent_run_id in by_id:
            children_map[(r.parent_run_id, r.parent_branch)].append(r.run_id)
            child_ids.add(r.run_id)

    def branch_node(run_id: str, branch: BranchSummary) -> dict[str, Any]:
        child_run_ids = children_map.get((run_id, branch.id), [])
        return {
            "branch_id": branch.id,
            "theme": branch.theme,
            "chapter_chars": branch.chapter_chars,
            "retrieval_count": branch.retrieval_count,
            "has_runtime_memory": branch.has_runtime_memory,
            "runtime_memory_layer_count": branch.runtime_memory_layer_count,
            "has_multi_agent_trace": branch.has_multi_agent_trace,
            "multi_agent_trace_count": branch.multi_agent_trace_count,
            "has_causal_diff": branch.has_causal_diff,
            "causal_diff_count": branch.causal_diff_count,
            "child_runs": [
                run_node(cid) for cid in sorted(child_run_ids, reverse=True)
            ],
        }

    def run_node(run_id: str) -> dict[str, Any]:
        r = by_id[run_id]
        is_orphan = bool(r.parent_run_id) and r.parent_run_id not in by_id
        return {
            "run_id": r.run_id,
            "kind": r.kind,
            "story_slug": r.story_slug,
            "source_kind": r.source_kind,
            "intervention_preview": r.intervention_preview,
            "current_chapter": r.current_chapter,
            "branches": [branch_node(run_id, b) for b in r.branches],
            "parent_run_id": r.parent_run_id,
            "parent_branch": r.parent_branch,
            "is_orphan": is_orphan,
        }

    roots = [r for r in runs if r.run_id not in child_ids]
    roots.sort(key=lambda r: r.run_id, reverse=True)
    return [run_node(r.run_id) for r in roots]

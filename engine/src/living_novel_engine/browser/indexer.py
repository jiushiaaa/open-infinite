"""Index projects/ and outputs/ for the read-only worldline browser."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

from living_novel_engine.browser.paths import outputs_dir, projects_dir, samples_dir
from living_novel_engine.samples import list_samples

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
    branch_dir = outputs_dir() / run_id / branch_id
    if not branch_dir.is_dir():
        raise FileNotFoundError(f"分支不存在: {run_id}/{branch_id}")

    chapter = _read_text(branch_dir / "chapter.md")
    summary = _read_text(branch_dir / "summary.md")
    state = _read_optional_json(branch_dir / "state_snapshot.json")
    events = _read_optional_json(branch_dir / "events.json")
    retrieval = _read_optional_json(branch_dir / "retrieval_context.json")
    multi_agent_trace = _read_optional_json(branch_dir / "multi_agent_trace.json")
    causal_diff = _read_optional_json(branch_dir / "causal_diff.json")

    run_summary = index_run(outputs_dir() / run_id)
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

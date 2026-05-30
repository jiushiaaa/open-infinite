"""console-free 正史回放服务（v0.7.4 Canon Replay）。

两部分：
1. 正史 holdout 读写：把完结小说后续章节作为隐藏评估集存盘，仅 imported/genesis
   可写，builtin 只读。文件名由章号派生，用户不可控制路径。
2. 正史回放评估：读取 baseline 续写章节与 holdout 章节，做 deterministic 轻量
   评估，写 canon_replay_report.json。

边界：
- 不打 LLM、不做语义评估、不公开分享受版权保护文本。
- holdout 文本只给 evaluator，不进入角色 / narrator / retrieval。
- 所有失败降级为明确错误（400/404/409），不白屏、不 500。
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path

from living_novel_engine.canon_replay.evaluator import evaluate_replay
from living_novel_engine.canon_replay.models import (
    CANON_REPLAY_VERSION,
    CanonReplayReport,
    HoldoutChapter,
    HoldoutManifest,
    ReplayScores,
)
from living_novel_engine.story_loader import load_story

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_MANIFEST_NAME = "holdout_manifest.json"
_VISIBILITY_MANIFEST_NAME = "visibility_manifest.json"
_HOLDOUT_DIRNAME = "holdout"
_HOLDOUT_PRIVATE_DIRNAME = "holdout_private"
_CANON_DIRNAME = "canon"
_REPLAY_REPORT_NAME = "canon_replay_report.json"
_VISIBILITY_VERSION = "v0.8.5"
_MAX_CHAPTER = 100000


class HoldoutRequestError(ValueError):
    """入参非法（坏 slug、空内容、非法章号）——映射为 HTTP 400。"""


class HoldoutReadOnlyError(ValueError):
    """builtin 样例不可写 holdout——映射为 HTTP 400。"""


class HoldoutExistsError(ValueError):
    """同章 holdout 已存在且 force=False——映射为 HTTP 409。"""


class ReplayRequestError(ValueError):
    """回放入参非法或 artifact 损坏——映射为 HTTP 400。"""


# ── 路径与校验 ────────────────────────────────────────────


def _projects_dir(projects_dir: Path | None) -> Path:
    if projects_dir is not None:
        return projects_dir
    env = os.environ.get("LNE_PROJECTS_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3] / "projects"


def _outputs_root(outputs_dir: Path | None) -> Path:
    if outputs_dir is not None:
        return outputs_dir
    from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir

    return default_outputs_dir()


def _validate_slug(slug: str) -> str:
    slug = (slug or "").strip()
    if not _SLUG_RE.match(slug):
        raise HoldoutRequestError("故事标识非法（须为英文小写字母+数字+连字符）")
    return slug


def _validate_identifier(value: str | None, label: str) -> str:
    ident = (value or "").strip()
    if not ident:
        raise ReplayRequestError(f"缺少 {label}")
    if ".." in ident or not _SAFE_ID_RE.match(ident):
        raise ReplayRequestError(f"{label} 非法")
    return ident


def _canon_dir(slug: str, projects_dir: Path | None) -> Path:
    return _projects_dir(projects_dir) / slug / _CANON_DIRNAME


def _project_dir(slug: str, projects_dir: Path | None) -> Path:
    return _projects_dir(projects_dir) / slug


def _holdout_dir(slug: str, projects_dir: Path | None) -> Path:
    return _canon_dir(slug, projects_dir) / _HOLDOUT_DIRNAME


def _holdout_private_dir(slug: str, projects_dir: Path | None) -> Path:
    return _project_dir(slug, projects_dir) / _HOLDOUT_PRIVATE_DIRNAME


def _chapter_filename(chapter: int) -> str:
    return f"chapter_{chapter:03d}.md"


def _chapter_rel_path(chapter: int) -> str:
    return f"{_CANON_DIRNAME}/{_HOLDOUT_DIRNAME}/{_chapter_filename(chapter)}"


def _private_chapter_rel_path(chapter: int) -> str:
    return f"{_HOLDOUT_PRIVATE_DIRNAME}/{_chapter_filename(chapter)}"


# ── manifest 读写 ────────────────────────────────────────


def _load_manifest(slug: str, projects_dir: Path | None) -> HoldoutManifest:
    path = _canon_dir(slug, projects_dir) / _MANIFEST_NAME
    if not path.exists():
        return HoldoutManifest(story_slug=slug)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        manifest = HoldoutManifest.model_validate(data)
    except Exception:
        return HoldoutManifest(story_slug=slug)
    if not manifest.story_slug:
        manifest.story_slug = slug
    return manifest


def _save_manifest(slug: str, manifest: HoldoutManifest, projects_dir: Path | None) -> None:
    canon_dir = _canon_dir(slug, projects_dir)
    canon_dir.mkdir(parents=True, exist_ok=True)
    path = canon_dir / _MANIFEST_NAME
    path.write_text(
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _runtime_visible_chapters(slug: str, projects_dir: Path | None) -> list[dict]:
    source_dir = _project_dir(slug, projects_dir) / "source"
    chapters: list[dict] = []
    if not source_dir.is_dir():
        return chapters
    for fp in sorted(source_dir.glob("chapter_*.md")):
        match = re.search(r"chapter_(\d+)", fp.name)
        if not match:
            continue
        try:
            chapter = int(match.group(1))
            chars = len(fp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        chapters.append({
            "chapter": chapter,
            "path": f"source/{fp.name}",
            "chars": chars,
        })
    return chapters


def _build_visibility_manifest(
    slug: str,
    holdout_manifest: HoldoutManifest,
    projects_dir: Path | None,
) -> dict:
    runtime_visible = _runtime_visible_chapters(slug, projects_dir)
    private_chapters = [
        {
            "chapter": ch.chapter,
            "title": ch.title,
            "path": _private_chapter_rel_path(ch.chapter),
            "chars": ch.chars,
        }
        for ch in holdout_manifest.chapters
    ]
    return {
        "version": _VISIBILITY_VERSION,
        "story_slug": slug,
        "created_at": datetime.now().isoformat(),
        "runtime_visible": {
            "dir": "source",
            "chapter_count": len(runtime_visible),
            "available_chapters": [c["chapter"] for c in runtime_visible],
            "chapters": runtime_visible,
        },
        "holdout_private": {
            "dir": _HOLDOUT_PRIVATE_DIRNAME,
            "chapter_count": len(private_chapters),
            "available_chapters": [c["chapter"] for c in private_chapters],
            "chapters": private_chapters,
        },
        "rules": [
            "holdout_private 不得进入 retrieval、character_agent、narrator 或 multi_agent_runner prompt",
            "holdout_private 仅允许 evaluator 在 Canon Replay 阶段读取",
        ],
    }


def _save_visibility_manifest(
    slug: str,
    holdout_manifest: HoldoutManifest,
    projects_dir: Path | None,
) -> dict:
    manifest = _build_visibility_manifest(slug, holdout_manifest, projects_dir)
    canon_dir = _canon_dir(slug, projects_dir)
    canon_dir.mkdir(parents=True, exist_ok=True)
    (canon_dir / _VISIBILITY_MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def _load_visibility_manifest(slug: str, projects_dir: Path | None) -> dict:
    path = _canon_dir(slug, projects_dir) / _VISIBILITY_MANIFEST_NAME
    if not path.exists():
        return _build_visibility_manifest(slug, _load_manifest(slug, projects_dir), projects_dir)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _build_visibility_manifest(slug, _load_manifest(slug, projects_dir), projects_dir)
    return data if isinstance(data, dict) else {}


def _normalise_chapter_payload(raw: object) -> tuple[int, str, str]:
    if not isinstance(raw, dict):
        raise HoldoutRequestError("章节项必须为对象")
    try:
        chapter = int(raw.get("chapter"))
    except (TypeError, ValueError) as exc:
        raise HoldoutRequestError("章号非法（须为整数）") from exc
    if chapter < 1 or chapter > _MAX_CHAPTER:
        raise HoldoutRequestError(f"章号超出范围（1-{_MAX_CHAPTER}）")
    content = str(raw.get("content") or "").strip()
    if not content:
        raise HoldoutRequestError(f"第 {chapter} 章内容为空")
    title = str(raw.get("title") or "").strip()
    return chapter, title, content


def write_holdout(
    slug: str,
    *,
    chapters: list,
    force: bool = False,
    projects_dir: Path | None = None,
) -> dict:
    """写入正史 holdout 章节并更新 manifest。

    - 坏 slug / 空内容 / 非法章号 → HoldoutRequestError（400）。
    - 缺故事 → FileNotFoundError（404）。
    - builtin 样例 → HoldoutReadOnlyError（400）。
    - 同章已存在且 force=False → HoldoutExistsError（409）。
    """
    slug = _validate_slug(slug)
    bundle = load_story(slug)  # 缺故事抛 FileNotFoundError
    if bundle.source_kind == "builtin":
        raise HoldoutReadOnlyError("内置样例为只读，不能写入正史 holdout")
    if not isinstance(chapters, list) or not chapters:
        raise HoldoutRequestError("chapters 须为非空数组")

    parsed = [_normalise_chapter_payload(c) for c in chapters]

    holdout_dir = _holdout_dir(slug, projects_dir)
    manifest = _load_manifest(slug, projects_dir)
    existing = {c.chapter for c in manifest.chapters}

    if not force:
        for chapter, _, _ in parsed:
            file_exists = (holdout_dir / _chapter_filename(chapter)).exists()
            if chapter in existing or file_exists:
                raise HoldoutExistsError(
                    f"第 {chapter} 章 holdout 已存在（force=true 可覆盖）"
                )

    holdout_dir.mkdir(parents=True, exist_ok=True)
    private_dir = _holdout_private_dir(slug, projects_dir)
    private_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now().isoformat()
    by_chapter = {c.chapter: c for c in manifest.chapters}
    for chapter, title, content in parsed:
        (holdout_dir / _chapter_filename(chapter)).write_text(content, encoding="utf-8")
        (private_dir / _chapter_filename(chapter)).write_text(
            content, encoding="utf-8"
        )
        by_chapter[chapter] = HoldoutChapter(
            chapter=chapter,
            title=title,
            path=_chapter_rel_path(chapter),
            chars=len(content),
        )

    manifest.story_slug = slug
    manifest.chapters = [by_chapter[k] for k in sorted(by_chapter)]
    if not manifest.created_at:
        manifest.created_at = now
    manifest.updated_at = now
    _save_manifest(slug, manifest, projects_dir)
    visibility = _save_visibility_manifest(slug, manifest, projects_dir)

    return _manifest_response(manifest, visibility_manifest=visibility)


def _manifest_response(
    manifest: HoldoutManifest, *, visibility_manifest: dict | None = None
) -> dict:
    payload = manifest.model_dump(mode="json")
    payload["chapter_count"] = len(manifest.chapters)
    payload["available_chapters"] = manifest.chapter_numbers()
    if visibility_manifest is not None:
        payload["visibility_manifest"] = visibility_manifest
    return payload


def get_holdout(slug: str, *, projects_dir: Path | None = None) -> dict:
    """读取正史 holdout manifest（无 holdout → 空 manifest，不 404）。

    - 坏 slug → HoldoutRequestError（400）。
    - 缺故事 → FileNotFoundError（404）。
    """
    slug = _validate_slug(slug)
    load_story(slug)  # 仅校验故事存在
    manifest = _load_manifest(slug, projects_dir)
    visibility = _load_visibility_manifest(slug, projects_dir)
    return _manifest_response(manifest, visibility_manifest=visibility)


# ── 回放评估 ─────────────────────────────────────────────


def _read_text_strict(path: Path, what: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReplayRequestError(f"{what}读取失败") from exc


def _read_json_strict(path: Path, what: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ReplayRequestError(f"{what}损坏，无法解析") from exc
    return data if isinstance(data, dict) else {}


def _collect_entities(bundle) -> list[str]:
    entities: list[str] = []
    for char in bundle.characters:
        if char.name:
            entities.append(char.name)
    for loc in getattr(bundle.world, "locations", []) or []:
        if getattr(loc, "name", ""):
            entities.append(loc.name)
    for faction in getattr(bundle.world, "factions", []) or []:
        if faction:
            entities.append(str(faction))
    return list(dict.fromkeys(entities))


def _collect_threads(bundle) -> list[str]:
    titles = []
    for thread in getattr(bundle.world, "open_threads", []) or []:
        title = getattr(thread, "title", "")
        if title:
            titles.append(title)
    return list(dict.fromkeys(titles))


def run_canon_replay(
    *,
    story_slug: str,
    baseline_run_id: str,
    baseline_branch_id: str = "baseline",
    holdout_chapter: int,
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
) -> dict:
    """对比无干预基线续写与正史 holdout 某章，写 canon_replay_report.json。

    - 入参非法 / artifact 损坏 → ReplayRequestError（400）。
    - 无 baseline run / 无 holdout → FileNotFoundError（404）。
    """
    slug = _validate_slug(story_slug)
    baseline_run_id = _validate_identifier(baseline_run_id, "baseline_run_id")
    baseline_branch_id = _validate_identifier(
        baseline_branch_id or "baseline", "baseline_branch_id"
    )
    if not isinstance(holdout_chapter, int) or holdout_chapter < 1:
        raise ReplayRequestError("holdout_chapter 必须为 >=1 的整数")

    bundle = load_story(slug)  # 缺故事 → FileNotFoundError（404）

    out_root = _outputs_root(outputs_dir)
    branch_dir = out_root / baseline_run_id / baseline_branch_id
    chapter_path = branch_dir / "chapter.md"
    if not chapter_path.exists():
        raise FileNotFoundError(
            f"未找到 baseline 续写章节: {baseline_run_id}/{baseline_branch_id}"
        )
    baseline_text = _read_text_strict(chapter_path, "baseline 续写章节")

    holdout_path = _holdout_dir(slug, projects_dir) / _chapter_filename(holdout_chapter)
    if not holdout_path.exists():
        raise FileNotFoundError(f"未找到正史 holdout 第 {holdout_chapter} 章")
    holdout_text = _read_text_strict(holdout_path, "正史 holdout 章节")

    snapshot_path = branch_dir / "state_snapshot.json"
    baseline_state = (
        _read_json_strict(snapshot_path, "baseline state_snapshot")
        if snapshot_path.exists()
        else {}
    )

    evaluation = evaluate_replay(
        baseline_text,
        holdout_text,
        entities=_collect_entities(bundle),
        threads=_collect_threads(bundle),
        baseline_state=baseline_state,
    )

    report = CanonReplayReport(
        version=CANON_REPLAY_VERSION,
        story_slug=slug,
        baseline_run_id=baseline_run_id,
        baseline_branch_id=baseline_branch_id,
        holdout_chapter=holdout_chapter,
        scores=ReplayScores(
            lexical_overlap=evaluation.lexical_overlap,
            entity_overlap=evaluation.entity_overlap,
            thread_overlap=evaluation.thread_overlap,
            length_ratio=evaluation.length_ratio,
            state_consistency=evaluation.state_consistency,
            overall=evaluation.overall,
        ),
        matched_entities=evaluation.matched_entities,
        missing_entities=evaluation.missing_entities,
        matched_threads=evaluation.matched_threads,
        warnings=evaluation.warnings,
        interpretation=evaluation.interpretation,
        created_at=datetime.now().isoformat(),
    )

    report_path = out_root / baseline_run_id / _REPLAY_REPORT_NAME
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report.model_dump(mode="json")


def get_canon_replay_report(
    run_id: str, *, outputs_dir: Path | None = None
) -> dict:
    """读取 canon_replay_report.json（不存在 404，损坏 400，不 500）。"""
    rid = _validate_identifier(run_id, "run_id")
    path = _outputs_root(outputs_dir) / rid / _REPLAY_REPORT_NAME
    if not path.exists():
        raise FileNotFoundError(f"正史回放报告不存在: {rid}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ReplayRequestError(f"正史回放报告损坏: {rid}") from exc

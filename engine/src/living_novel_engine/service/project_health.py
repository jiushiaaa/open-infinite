"""console-free 项目健康检查（v0.7 第七刀：世界锚定轻编辑前置）。

检查 world.yaml / characters.yaml / open_threads.yaml / story_contract.yaml
是否能解析；解析失败不抛 500，而是定位到具体文件并返回 errors/warnings。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml

from living_novel_engine.browser.paths import samples_dir
from living_novel_engine.import_novel.validator import validate_project
from living_novel_engine.import_novel.writer import _default_projects_dir

# 参与健康检查的 YAML 文件（按重要性）。
_HEALTH_FILES = (
    "world.yaml",
    "characters.yaml",
    "open_threads.yaml",
    "story_contract.yaml",
)

HealthStatus = Literal["ok", "warning", "error"]


@dataclass
class HealthReport:
    slug: str
    status: HealthStatus
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)  # filename -> ok|missing|error
    source_kind: str = "imported"

    def as_dict(self) -> dict:
        return {
            "slug": self.slug,
            "status": self.status,
            "errors": self.errors,
            "warnings": self.warnings,
            "files": self.files,
            "source_kind": self.source_kind,
        }


def resolve_story_path(
    slug: str, projects_dir: Path | None = None
) -> tuple[Path, Literal["builtin", "imported"]]:
    """定位故事目录并判定来源；projects 优先于同名 sample。

    与 indexer._resolve_story_path 同义，但允许显式传入 projects_dir（便于测试）。
    """
    pdir = projects_dir or _default_projects_dir()
    project_path = pdir / slug
    if project_path.exists() and (project_path / "world.yaml").exists():
        return project_path, "imported"
    sample_path = samples_dir() / slug
    if sample_path.exists() and (sample_path / "world.yaml").exists():
        return sample_path, "builtin"
    raise FileNotFoundError(f"故事不存在: {slug}")


def _parse_files(story_path: Path) -> tuple[dict[str, str], list[str]]:
    """逐个 parse YAML，返回 (files 状态映射, parse 错误列表)。"""
    files: dict[str, str] = {}
    errors: list[str] = []
    for fname in _HEALTH_FILES:
        fpath = story_path / fname
        if not fpath.exists():
            files[fname] = "missing"
            continue
        try:
            with open(fpath, encoding="utf-8") as f:
                yaml.safe_load(f)
            files[fname] = "ok"
        except (yaml.YAMLError, UnicodeDecodeError, OSError) as exc:
            files[fname] = "error"
            errors.append(f"{fname} 解析失败：{exc}")
    return files, errors


def check_project_health(
    slug: str, projects_dir: Path | None = None
) -> HealthReport:
    """检查项目 YAML 健康度；任何解析失败均被捕获，不抛 500。"""
    story_path, source_kind = resolve_story_path(slug, projects_dir)

    files, parse_errors = _parse_files(story_path)
    errors = list(parse_errors)
    warnings: list[str] = []

    # 仅当核心文件可解析时再跑结构校验，避免重复报 parse 错误。
    if files.get("world.yaml") != "error" and files.get("characters.yaml") != "error":
        vr = validate_project(story_path)
        errors.extend(vr.errors)
        warnings.extend(vr.warnings)

    if errors:
        status: HealthStatus = "error"
    elif warnings:
        status = "warning"
    else:
        status = "ok"

    return HealthReport(
        slug=slug,
        status=status,
        errors=errors,
        warnings=warnings,
        files=files,
        source_kind=source_kind,
    )

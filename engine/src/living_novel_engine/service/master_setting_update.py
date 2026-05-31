"""v0.9.2 MasterSetting Workspace Lite safe edit service.

Only a small whitelist in memory/master_setting.yaml is writable here. The
service backs up the original file before saving and writes a tiny audit report.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from living_novel_engine.import_novel.writer import _write_yaml
from living_novel_engine.service.project_health import resolve_story_path


class MasterSettingUpdateError(ValueError):
    """Invalid payload or no whitelisted field."""


class MasterSettingReadOnlyError(ValueError):
    """Builtin samples are read-only."""


class MasterSettingConflictError(ValueError):
    """Current master_setting.yaml cannot be safely edited."""


@dataclass
class MasterSettingUpdateResult:
    slug: str
    project_dir: Path
    backup_dir: Path | None
    report_path: Path
    changed: list[str]


_STRING_FIELDS = {"display_name": 80, "genre": 40}
_LIST_FIELDS = {
    "world_rules": (20, 160),
    "power_system_limits": (12, 160),
    "forbidden_additions": (20, 80),
}


def _load_master(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise MasterSettingConflictError("memory/master_setting.yaml 缺失，无法保存设定")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, UnicodeDecodeError, OSError) as exc:
        raise MasterSettingConflictError(
            f"memory/master_setting.yaml 解析失败，已拒绝保存：{exc}"
        ) from exc
    if not isinstance(data, dict):
        raise MasterSettingConflictError("memory/master_setting.yaml 结构异常，已拒绝保存")
    return data


def _clean_text(value: object, max_len: int) -> str:
    text = str(value).strip()
    if not text:
        return ""
    return text[:max_len]


def _clean_list(value: object, max_items: int, max_len: int) -> list[str] | None:
    if not isinstance(value, list):
        return None
    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = _clean_text(item, max_len)
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
        if len(out) >= max_items:
            break
    return out


def _apply_patch(master: dict[str, Any], patch: dict[str, Any]) -> list[str]:
    changed: list[str] = []
    for field, max_len in _STRING_FIELDS.items():
        if field not in patch:
            continue
        value = _clean_text(patch[field], max_len)
        if value:
            master[field] = value
            changed.append(field)
    for field, limits in _LIST_FIELDS.items():
        if field not in patch:
            continue
        value = _clean_list(patch[field], *limits)
        if value is not None:
            master[field] = value
            changed.append(field)
    return changed


def _backup_master(project_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_dir = project_dir / "backups" / ts / "memory"
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        project_dir / "memory" / "master_setting.yaml",
        backup_dir / "master_setting.yaml",
    )
    return backup_dir.parent


def _report_path(project_dir: Path) -> Path:
    return project_dir / "memory" / "master_setting_update_report.json"


def _relative_posix(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def update_master_setting(
    slug: str, patch: dict, projects_dir: Path | None = None
) -> MasterSettingUpdateResult:
    """Safely update a tiny whitelist in memory/master_setting.yaml.

    This edits imported projects only. It does not synchronize world.yaml,
    characters, timeline, plot threads, or runner artifacts.
    """
    if not isinstance(patch, dict):
        raise MasterSettingUpdateError("patch 须为对象")

    project_dir, source_kind = resolve_story_path(slug, projects_dir)
    if source_kind == "builtin":
        raise MasterSettingReadOnlyError("内置样例只读，请先导入或创世为可编辑项目")

    master_path = project_dir / "memory" / "master_setting.yaml"
    master = _load_master(master_path)
    changed = _apply_patch(master, patch)
    if not changed:
        raise MasterSettingUpdateError("没有可写回的设定白名单字段")

    backup_dir = _backup_master(project_dir)
    _write_yaml(master_path, master)

    report = {
        "version": "v0.9.2",
        "status": "saved",
        "story_slug": slug,
        "changed": changed,
        "backup": _relative_posix(
            backup_dir / "memory" / "master_setting.yaml", project_dir
        ),
        "warnings": [
            "本次轻编辑仅写 memory/master_setting.yaml，不同步 world.yaml 或 runner artifact。"
        ],
    }
    report_path = _report_path(project_dir)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return MasterSettingUpdateResult(
        slug=slug,
        project_dir=project_dir,
        backup_dir=backup_dir,
        report_path=report_path,
        changed=changed,
    )

"""视觉资产本地存储：artifact 读写 + 图片落盘 + 安全路径解析。

设计要点：
- 缺 artifact → 返回 status=none 的空清单，不抛错。
- artifact 损坏 → 同样安全降级为空清单，不抛错（调用方不应 500）。
- 图片只写入 <story_dir>/assets/ 下，禁止路径穿越。
- JSON 用 ensure_ascii=False 落盘，便于人读。
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import VisualAssets

VISUAL_ASSETS_FILENAME = "visual_assets.json"
ASSETS_DIRNAME = "assets"


def artifact_path(story_dir: Path) -> Path:
    return story_dir / VISUAL_ASSETS_FILENAME


def assets_dir(story_dir: Path) -> Path:
    return story_dir / ASSETS_DIRNAME


def load(story_dir: Path, slug: str = "") -> VisualAssets:
    """读取 visual_assets.json；缺失或损坏一律安全降级为空清单。"""
    path = artifact_path(story_dir)
    if not path.exists():
        return VisualAssets(story_slug=slug, status="none")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        va = VisualAssets.model_validate(data)
    except Exception:
        # 损坏降级：返回空清单，绝不外溢异常。
        return VisualAssets(story_slug=slug, status="none")
    if slug and not va.story_slug:
        va.story_slug = slug
    return va


def save(story_dir: Path, va: VisualAssets) -> Path:
    story_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_path(story_dir)
    path.write_text(
        json.dumps(va.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def _safe_target(story_dir: Path, rel_under_assets: str) -> Path:
    """把 assets 内相对路径解析为绝对路径，拒绝穿越。"""
    base = assets_dir(story_dir).resolve()
    target = (base / rel_under_assets).resolve()
    if target != base and base not in target.parents:
        raise ValueError("不安全的资产路径")
    return target


def write_image(story_dir: Path, rel_under_assets: str, data: bytes) -> str:
    """把图片字节写入 assets/<rel>，返回相对故事目录的路径（assets/...）。"""
    target = _safe_target(story_dir, rel_under_assets)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return f"{ASSETS_DIRNAME}/{rel_under_assets}".replace(os.sep, "/")


def resolve_asset_file(story_dir: Path, rel_under_assets: str) -> Path | None:
    """供静态服务用：解析 assets 下文件路径。

    - 穿越 → 抛 ValueError（调用方映射 403）。
    - 不存在 → None（调用方映射 404）。
    """
    target = _safe_target(story_dir, rel_under_assets)
    return target if target.is_file() else None

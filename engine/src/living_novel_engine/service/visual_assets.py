"""console-free 视觉资产服务（v0.7.3 Visual Asset Generation）。

职责：
- 读取项目级 visual_assets artifact（缺失/损坏安全降级）。
- 生成封面 / 角色头像 / 场景背景；无 Key 或 mock 时落占位条目，不打外网。
- 安全解析 assets 下文件路径，供 HTTP 静态服务。

边界：
- 不改 run_scene、不改既有 chapter/events/state/trace/diff 契约。
- 视觉资产目录统一落在 projects/<slug>/（gitignored），即便故事来自 samples/，
  也只把元数据与图片写到 projects/<slug>/，绝不污染 git 跟踪的样例目录。
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

from living_novel_engine.models import CharacterAgent, StoryWorld
from living_novel_engine.story_loader import load_story
from living_novel_engine.visual_assets import prompt_builder, store
from living_novel_engine.visual_assets.models import AssetEntry, VisualAssets
from living_novel_engine.visual_assets.seedream_client import SeedreamClient

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_VALID_KINDS = ("cover", "characters", "scenes")
_DEFAULT_SCENE_ID = "main"


class VisualAssetRequestError(ValueError):
    """入参非法（坏 slug、非法 kinds）——映射为 HTTP 400。"""


class VisualAssetPathError(ValueError):
    """资产路径穿越——映射为 HTTP 403。"""


def _projects_dir(projects_dir: Path | None) -> Path:
    if projects_dir is not None:
        return projects_dir
    env = os.environ.get("LNE_PROJECTS_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3] / "projects"


def _asset_dir(slug: str, projects_dir: Path | None) -> Path:
    """视觉资产目录：统一落在 projects/<slug>/（不依赖 world.yaml 是否在此）。"""
    return _projects_dir(projects_dir) / slug


def _validate_slug(slug: str) -> str:
    slug = (slug or "").strip()
    if not _SLUG_RE.match(slug):
        raise VisualAssetRequestError("故事标识非法（须为英文小写字母+数字+连字符）")
    return slug


def get_visual_assets(slug: str, *, projects_dir: Path | None = None) -> VisualAssets:
    """返回项目级视觉资产清单。

    - 坏 slug → VisualAssetRequestError（400）。
    - 缺故事 → FileNotFoundError（404）。
    - 缺 artifact / 损坏 → 返回 status=none 占位清单，不报错。
    """
    slug = _validate_slug(slug)
    load_story(slug)  # 仅用于校验故事存在；不存在抛 FileNotFoundError
    return store.load(_asset_dir(slug, projects_dir), slug)


def resolve_asset_path(
    slug: str, rel_under_assets: str, *, projects_dir: Path | None = None
) -> Path | None:
    """解析 assets 下文件路径供静态服务。

    - 坏 slug → VisualAssetRequestError（400）。
    - 穿越 → VisualAssetPathError（403）。
    - 不存在 → None（404）。
    """
    slug = _validate_slug(slug)
    try:
        return store.resolve_asset_file(_asset_dir(slug, projects_dir), rel_under_assets)
    except ValueError as exc:
        raise VisualAssetPathError(str(exc)) from exc


def _normalise_kinds(kinds: list[str] | None) -> list[str]:
    if not kinds:
        return list(_VALID_KINDS)
    out: list[str] = []
    for k in kinds:
        if k not in _VALID_KINDS:
            raise VisualAssetRequestError(
                f"未知资产类型: {k!r}；可用: {', '.join(_VALID_KINDS)}"
            )
        if k not in out:
            out.append(k)
    return out


def _make_entry(
    *,
    asset_dir: Path,
    kind: str,
    asset_id: str,
    prompt: str,
    rel_stem: str,
    client: SeedreamClient,
    effective_mock: bool,
    now: str,
) -> AssetEntry:
    """生成单个条目：mock/不可用 → 占位；否则调用 client，失败 → failed。"""
    if effective_mock:
        return AssetEntry(
            asset_id=asset_id,
            kind=kind,  # type: ignore[arg-type]
            prompt=prompt,
            status="placeholder",
            path="",
            created_at=now,
        )
    result = client.generate_image(prompt)
    if result.ok and result.data:
        rel = f"{rel_stem}.{result.ext}"
        path = store.write_image(asset_dir, rel, result.data)
        return AssetEntry(
            asset_id=asset_id,
            kind=kind,  # type: ignore[arg-type]
            prompt=prompt,
            status="ready",
            path=path,
            created_at=now,
        )
    return AssetEntry(
        asset_id=asset_id,
        kind=kind,  # type: ignore[arg-type]
        prompt=prompt,
        status="failed",
        path="",
        created_at=now,
        error=result.error,
    )


def _keep_existing(entry: AssetEntry | None, force: bool) -> bool:
    return (not force) and entry is not None and entry.status == "ready"


def generate_visual_assets(
    slug: str,
    *,
    kinds: list[str] | None = None,
    character_ids: list[str] | None = None,
    force: bool = False,
    mock: bool = False,
    client: SeedreamClient | None = None,
    projects_dir: Path | None = None,
) -> VisualAssets:
    """生成视觉资产并落盘，返回更新后的清单。

    - 坏 slug / 非法 kinds → VisualAssetRequestError（400）。
    - 缺故事 → FileNotFoundError（404）。
    - Seedream 不可用 / mock → 落占位条目，不打外网，不抛错。
    """
    slug = _validate_slug(slug)
    requested = _normalise_kinds(kinds)
    bundle = load_story(slug)  # 缺故事抛 FileNotFoundError
    world: StoryWorld = bundle.world
    char_map: dict[str, CharacterAgent] = bundle.character_map()

    asset_dir = _asset_dir(slug, projects_dir)
    va = store.load(asset_dir, slug)

    client = client or SeedreamClient(mock=mock)
    effective_mock = mock or (not client.available)
    now = datetime.now().isoformat()

    if "cover" in requested and not _keep_existing(va.cover, force):
        va.cover = _make_entry(
            asset_dir=asset_dir,
            kind="story_cover",
            asset_id=f"{slug}_cover",
            prompt=prompt_builder.build_cover_prompt(world),
            rel_stem="cover",
            client=client,
            effective_mock=effective_mock,
            now=now,
        )

    if "characters" in requested:
        target_ids = character_ids or list(char_map.keys())
        for cid in target_ids:
            character = char_map.get(cid)
            if character is None:
                continue  # 未知角色 id 直接跳过，不报错
            if _keep_existing(va.characters.get(cid), force):
                continue
            va.characters[cid] = _make_entry(
                asset_dir=asset_dir,
                kind="character_avatar",
                asset_id=f"{slug}_char_{cid}",
                prompt=prompt_builder.build_character_prompt(world, character),
                rel_stem=f"characters/{cid}",
                client=client,
                effective_mock=effective_mock,
                now=now,
            )

    if "scenes" in requested and not _keep_existing(
        va.scenes.get(_DEFAULT_SCENE_ID), force
    ):
        va.scenes[_DEFAULT_SCENE_ID] = _make_entry(
            asset_dir=asset_dir,
            kind="scene_background",
            asset_id=f"{slug}_scene_{_DEFAULT_SCENE_ID}",
            prompt=prompt_builder.build_scene_prompt(world),
            rel_stem=f"scenes/{_DEFAULT_SCENE_ID}",
            client=client,
            effective_mock=effective_mock,
            now=now,
        )

    va.story_slug = slug
    va.recompute_status()
    store.save(asset_dir, va)
    return va

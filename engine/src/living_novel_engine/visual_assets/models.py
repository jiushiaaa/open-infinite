"""v0.7.3 视觉资产 artifact 契约（additive、可缓存、不含二进制）。

JSON 只保存相对路径与元数据；图片二进制单独存放在 assets/ 目录。
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

VISUAL_ASSETS_VERSION = "v0.7.3"

AssetStatus = Literal["ready", "failed", "placeholder"]
AssetKind = Literal[
    "story_cover",
    "character_avatar",
    "scene_background",
    "worldline_node",
]
OverallStatus = Literal["none", "partial", "ready", "failed"]


class AssetEntry(BaseModel):
    """单个视觉资产条目。"""

    asset_id: str
    kind: AssetKind
    prompt: str = ""
    status: AssetStatus = "placeholder"
    path: str = ""  # 相对故事目录的路径，如 assets/characters/hero.png；占位时为空
    created_at: str = ""
    error: str = ""


class VisualAssets(BaseModel):
    """项目级视觉资产清单（写入 projects/<slug>/visual_assets.json）。"""

    version: str = VISUAL_ASSETS_VERSION
    story_slug: str = ""
    provider: str = "seedream"
    status: OverallStatus = "none"
    cover: AssetEntry | None = None
    characters: dict[str, AssetEntry] = Field(default_factory=dict)
    scenes: dict[str, AssetEntry] = Field(default_factory=dict)
    worldline_nodes: dict[str, AssetEntry] = Field(default_factory=dict)

    def all_entries(self) -> list[AssetEntry]:
        entries: list[AssetEntry] = []
        if self.cover is not None:
            entries.append(self.cover)
        entries.extend(self.characters.values())
        entries.extend(self.scenes.values())
        entries.extend(self.worldline_nodes.values())
        return entries

    def recompute_status(self) -> "VisualAssets":
        entries = self.all_entries()
        if not entries:
            self.status = "none"
            return self
        readys = [e for e in entries if e.status == "ready"]
        fails = [e for e in entries if e.status == "failed"]
        if readys and len(readys) == len(entries):
            self.status = "ready"
        elif readys:
            self.status = "partial"
        elif fails:
            self.status = "failed"
        else:
            self.status = "none"  # 仅占位，尚无真实资产
        return self

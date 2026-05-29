"""v0.7.3 Visual Asset Generation —— Seedream 视觉资产增强层。

视觉资产是「增强层」，不是核心文字运行时依赖：
- 未配置 Key / 关闭开关 / 生成失败时全程稳定降级。
- 所有 artifact additive，不改既有契约。
"""

from __future__ import annotations

from .models import (
    VISUAL_ASSETS_VERSION,
    AssetEntry,
    AssetKind,
    AssetStatus,
    VisualAssets,
)
from .seedream_client import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    ImageResult,
    SeedreamClient,
    SeedreamSettings,
)

__all__ = [
    "VISUAL_ASSETS_VERSION",
    "AssetEntry",
    "AssetKind",
    "AssetStatus",
    "VisualAssets",
    "SeedreamClient",
    "SeedreamSettings",
    "ImageResult",
    "DEFAULT_BASE_URL",
    "DEFAULT_MODEL",
]

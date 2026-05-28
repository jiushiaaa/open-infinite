"""Chapter distance decay — 章节距离衰减函数。"""

from __future__ import annotations


def distance_decay(
    current_chapter: int,
    item_chapter: int,
    alpha: float = 0.2,
) -> float:
    """越接近当前章节权重越高，远章不会完全消失。

    alpha 越大衰减越快；alpha=0 时无衰减。
    """
    return 1.0 / (1.0 + abs(current_chapter - item_chapter) * alpha)

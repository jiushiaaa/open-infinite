from __future__ import annotations

from .models import CompilerInterventionType

# 规则改写型标记：系统、穿越、重生、金手指、现代/未来武器等改写世界前提的元素
RULE_REWRITE_MARKERS: tuple[str, ...] = (
    "系统", "系統", "金手指", "外挂", "面板", "签到", "升级面板", "数据面板",
    "穿越", "穿越者", "重生", "前世记忆", "夺舍", "无敌", "秒杀全场",
    "召唤神龙", "时空门", "诸天万界",
    "ak47", "ak-47", "步枪", "机枪", "手枪", "枪械", "子弹", "手雷", "炸药",
    "导弹", "核弹", "坦克", "无人机", "激光", "电磁炮", "现代武器", "热武器",
)

# 资源/物品注入型标记：让角色获得/捡到某件物品或资源
RESOURCE_MARKERS: tuple[str, ...] = (
    "捡到", "拾得", "拾到", "获得", "得到", "掉落", "出现一", "凭空多出",
    "塞给", "赠予", "交给他", "交给她", "送他", "送她",
    "一把", "一柄", "一枚", "一颗", "一本", "一卷", "一枚丹", "宝物", "至宝",
    "丹药", "秘籍", "符箓", "灵剑", "法器", "灵石", "玉佩", "令牌",
)

# 强制行动型标记：要求角色某时某刻必须做/不做某事
FORCED_ACTION_MARKERS: tuple[str, ...] = (
    "必须", "务必", "一定要", "立刻", "马上", "强行", "强制", "命令",
    "不得", "不准", "不要去", "别去", "禁止他", "禁止她", "让他去", "让她去",
    "逼", "拖住", "拦下", "留下", "带走", "去做", "去找", "去杀",
)

# 信息型标记：告诉角色未来/真相/预兆（用于在歧义时倾向 information）
INFORMATION_MARKERS: tuple[str, ...] = (
    "告诉", "提醒", "预知", "未来", "将会", "会发生", "其实", "真相",
    "梦", "低语", "预兆", "异象", "提前", "得知", "知道",
)


def _hits(text: str, markers: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [m for m in markers if m in text or m in lowered]


def classify(
    raw_input: str,
    declared_type: CompilerInterventionType | None = None,
) -> tuple[CompilerInterventionType, list[str]]:
    """把自由输入分类成四类干预之一，并返回命中的标记（供解释）。

    优先级：规则改写 > 资源注入 > 强制行动 > 信息型（默认）。
    规则改写最危险，必须最先识别，避免被伪装成普通分叉。
    """
    text = raw_input or ""

    if declared_type:
        return declared_type, _collect_markers(text)

    rule_hits = _hits(text, RULE_REWRITE_MARKERS)
    if rule_hits:
        return "rule_rewrite", rule_hits

    resource_hits = _hits(text, RESOURCE_MARKERS)
    forced_hits = _hits(text, FORCED_ACTION_MARKERS)

    # 物品注入与强制行动可能共现（"让他捡起那把剑"）；
    # 若同时命中，以"获得物品"语义优先归为 resource_injection。
    if resource_hits and not _is_pure_movement(forced_hits, text):
        return "resource_injection", resource_hits

    if forced_hits:
        return "forced_action", forced_hits

    if resource_hits:
        return "resource_injection", resource_hits

    return "information", _hits(text, INFORMATION_MARKERS)


def _is_pure_movement(forced_hits: list[str], text: str) -> bool:
    """强制行动是"去/不去某地"而非获得物品时返回 True。"""
    movement = ("不要去", "别去", "去找", "去做", "去杀", "拦下", "拖住", "留下")
    return bool(forced_hits) and any(m in text for m in movement) and not any(
        item in text for item in ("捡", "拾", "获得", "得到", "掉落")
    )


def _collect_markers(text: str) -> list[str]:
    hits: list[str] = []
    for markers in (
        RULE_REWRITE_MARKERS,
        RESOURCE_MARKERS,
        FORCED_ACTION_MARKERS,
        INFORMATION_MARKERS,
    ):
        hits.extend(_hits(text, markers))
    return hits

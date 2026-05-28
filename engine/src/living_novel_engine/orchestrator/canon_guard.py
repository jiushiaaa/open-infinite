from __future__ import annotations

import re
from typing import Any

from living_novel_engine.models import StoryWorld

# 样例未声明的设定，正文中禁止新增
FORBIDDEN_TROPES: tuple[str, ...] = (
    "重生",
    "穿越",
    "系统面板",
    "系统提示",
    "前世记忆",
    "前世",
    "读档",
    "金手指",
    "轮回记忆",
    "二次人生",
)

# 退魂铃来源漂移（canonical：墨青烟十年前乱葬岗所赠）
SOUL_BELL_ORIGIN_DRIFT: tuple[str, ...] = (
    "青云宗至宝",
    "宗门至宝",
    "宗门长辈所赐",
    "师门长辈所赐",
    "师门所赐",
    "青云宗长辈",
    "宗门赐予",
    "长老所赐",
    "掌门所赐",
)

# 角色名 exact match 纠错表（错字 -> 正字）
CHARACTER_NAME_CORRECTIONS: dict[str, str] = {
    "莫青烟": "墨青烟",
}

SECT_TERM_NORMALIZE: dict[str, str] = {
    "戒律堂": "执法堂",
}

# 传讯玉简术语漂移（jade_slip_used 时墨色竹简也视为示警物漂移）
JADE_SLIP_TERM_DRIFT: tuple[str, ...] = (
    "保命竹简",
    "外门竹简",
    "外门应急竹简",
    "应急竹简",
    "师门唯一的竹简",
    "师门最后一张竹简",
    "唯一的保命竹简",
    "最后一张保命竹简",
    "封好的竹简",
    "那枚已经封好的竹简",
)

JADE_SLIP_DRIFT_WHEN_USED: tuple[str, ...] = (
    "墨色竹简",
)

SOUL_BELL_CANON_LINE = (
    "退魂铃：十年前乱葬岗由墨青烟亲手赠予林晚舟，称护神魂、铃在人在；"
    "不得改写为青云宗至宝、宗门长辈所赐或师门赐予。"
)


def build_canon_constraints(world: StoryWorld | None = None) -> str:
    lines = [
        "【正史锁·禁止设定漂移】",
        "- 禁止新增样例未声明设定：重生、穿越、系统、前世记忆、金手指等。",
        f"- {SOUL_BELL_CANON_LINE}",
        "- 角色名必须精确：墨青烟（禁止写成莫青烟等错字）。",
        (
            "- 林凡所持为「传讯玉简」；禁止漂成应急竹简、墨色竹简、保命竹简等。"
            "玉简已碎后林晚舟只闻耳畔传讯余韵，禁止写她手持/放下传讯玉简或任何竹简。"
        ),
    ]
    if world and world.canonical_place_name:
        lines.append(f"- 城名：{world.canonical_place_name}（青云宗为宗门名可保留）。")
    return "\n".join(lines)


def validate_canon_consistency(text: str) -> list[str]:
    violations: list[str] = []
    if not text:
        return violations

    for trope in FORBIDDEN_TROPES:
        if trope in text:
            violations.append(f"禁止未声明设定「{trope}」")

    if "退魂铃" in text or "魂铃" in text:
        for drift in SOUL_BELL_ORIGIN_DRIFT:
            if drift in text:
                violations.append(
                    f"退魂铃来源漂移：出现「{drift}」，应保持墨青烟十年前所赠设定"
                )

    for wrong, right in CHARACTER_NAME_CORRECTIONS.items():
        if wrong in text:
            violations.append(f"角色名错字：应写「{right}」，非「{wrong}」")

    if "林凡重生" in text or "重生的记忆" in text:
        violations.append("林凡无重生设定，禁止写重生记忆")

    for drift in JADE_SLIP_TERM_DRIFT + JADE_SLIP_DRIFT_WHEN_USED:
        if drift in text:
            violations.append(f"术语漂移：应使用「传讯玉简」，非「{drift}」")
    if (
        re.search(r"师门[^。，；\n]{0,12}竹简", text)
        and "传讯玉简" not in text
        and "墨色竹简" not in text
    ):
        violations.append("术语漂移：师门竹简应写为「传讯玉简」")

    if re.search(
        r"林晚舟[^。，；\n]{0,24}(手中的|握着|捏着|拿起|放到|置于|凝视着那枚)[^。，；\n]{0,16}"
        r"(传讯玉简|竹简|应急)",
        text,
    ):
        violations.append("传讯玉简仅林凡持有；林晚舟不得手持/放下竹简或传讯玉简")

    return violations


def normalize_jade_slip_terms(text: str, *, jade_slip_used: bool = False) -> str:
    if not text:
        return text
    repl = "传讯玉简（已碎）" if jade_slip_used else "传讯玉简"
    echo = "耳畔传讯神念余韵" if jade_slip_used else repl

    for drift in JADE_SLIP_TERM_DRIFT:
        text = text.replace(drift, repl)
    if jade_slip_used:
        for drift in JADE_SLIP_DRIFT_WHEN_USED:
            text = text.replace(drift, echo)
    text = re.sub(r"外门[^。，；\n]{0,6}应急[^。，；\n]{0,4}竹简", repl, text)
    text = re.sub(
        r"师门[^。，；\n]{0,12}竹简",
        repl,
        text,
    )
    if jade_slip_used:
        text = re.sub(r"凝视着那枚[^，。]{0,14}竹简", echo, text)
        text = re.sub(r"[^，。]{0,6}竹简[^，。]{0,8}放到案", echo, text)
        text = re.sub(
            r"林晚舟[^。]{0,16}(握着|拿起|手持)[^。]{0,12}竹简",
            "林晚舟侧耳听着传讯余韵",
            text,
        )
    return text


def normalize_sect_terms(text: str) -> str:
    if not text:
        return text
    for wrong, right in SECT_TERM_NORMALIZE.items():
        text = text.replace(wrong, right)
    return text


def normalize_canon_text(text: str, *, jade_slip_used: bool = False) -> str:
    """事件/正文统一纠错（写盘前）。"""
    if not text:
        return text
    for wrong, right in CHARACTER_NAME_CORRECTIONS.items():
        text = text.replace(wrong, right)
    text = normalize_sect_terms(text)
    return normalize_jade_slip_terms(text, jade_slip_used=jade_slip_used)


def polish_canon_in_chapter(text: str, *, jade_slip_used: bool = False) -> str:
    """章节正文后处理：错字 + 明显来源漂移句式。"""
    text = normalize_canon_text(text, jade_slip_used=jade_slip_used)
    for drift in SOUL_BELL_ORIGIN_DRIFT:
        if drift in text and ("退魂铃" in text or "魂铃" in text):
            text = text.replace(
                drift,
                "墨青烟十年前所赠、称护神魂的那枚退魂铃",
            )
    text = re.sub(r"林凡重生的记忆", "林凡昨夜偷听所得", text)
    text = re.sub(r"重生[^。，；\n]{0,8}记忆", "旧事记忆", text)
    return text


def validate_full_chapter(chapter_text: str, snapshot: dict[str, Any]) -> list[str]:
    from living_novel_engine.orchestrator.narrative_constraints import (
        validate_chapter_against_snapshot,
    )

    return validate_chapter_against_snapshot(chapter_text, snapshot) + validate_canon_consistency(
        chapter_text
    )

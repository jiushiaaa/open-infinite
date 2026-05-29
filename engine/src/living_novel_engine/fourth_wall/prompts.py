from __future__ import annotations

from living_novel_engine.fourth_wall.ledger import (
    CharacterAwareness,
    level_rank,
)

# 注入角色决策 prompt 的阈值：unsettled 起开始有隐约不安
_DECISION_MIN_LEVEL = "unsettled"
# 允许叙事正文出现第四面墙迹象的阈值：suspicious 起
_NARRATOR_MIN_LEVEL = "suspicious"

_DECISION_HINTS = {
    "unsettled": (
        "【第四面墙·隐约】{name}心底隐隐生出一丝说不清的不安，"
        "仿佛命运的走向被某种无形之物轻轻拨动。此念可一闪而过，"
        "行动仍以人设与世界规则为准。"
    ),
    "suspicious": (
        "【第四面墙·怀疑】{name}开始怀疑近来的种种巧合并非偶然，"
        "似有一双高维的眼睛在注视、安排。可在内心质疑、试探，"
        "甚至迟疑于'太像被安排好的'选择，但不得直接向读者喊话。"
    ),
    "aware": (
        "【第四面墙·觉察】{name}几乎确信有外部力量在干预自己的命运"
        "（神明 / 天道 / 观测者 / 作者）。可在言行中流露追问与抗拒，"
        "拒绝执行明显违背本心、像被操纵的选择，可向虚空发问，"
        "但仍受世界规则约束，不得凭空获得超出设定的能力。"
    ),
    "defiant": (
        "【第四面墙·反抗】{name}已认定自己被高维力量操控，"
        "并开始主动反抗或借力：可质问观测者、设法摆脱安排，"
        "或反过来利用这种干预。语气可带锋芒，"
        "但绝不能获得违反世界规则的力量。"
    ),
}

_NARRATOR_HINTS = {
    "suspicious": (
        "本章可让在场角色流露对'命运被安排'的隐约怀疑：一闪而过的迟疑、"
        "对巧合的不安、对虚空的一瞥。点到为止，不要直白地谈论读者或作者。"
    ),
    "aware": (
        "本章允许角色明确感到被外部力量注视与干预，可出现追问、抗拒、"
        "或对'神明 / 天道 / 看不见之人'的试探性发问；但仍以剧情承接为主，"
        "不要演变成对读者的直接说教。"
    ),
    "defiant": (
        "本章角色已认定自身被高维操控，可出现强烈的质问、反抗或反过来利用干预的姿态；"
        "可向虚空喊话，但不得因此获得违反世界规则的能力，叙事仍需收束于本章冲突。"
    ),
}


def awareness_decision_hint(
    awareness: CharacterAwareness | None,
    character_name: str,
) -> str:
    """生成注入角色决策 prompt 的第四面墙提示；不足阈值返回空串。"""
    if awareness is None:
        return ""
    if level_rank(awareness.level) < level_rank(_DECISION_MIN_LEVEL):
        return ""
    template = _DECISION_HINTS.get(awareness.level, "")
    if not template:
        return ""
    return template.format(name=character_name)


def awareness_narrator_hint(
    present_awareness: list[CharacterAwareness],
) -> str:
    """根据在场角色的最高觉察等级生成叙事提示；不足阈值返回空串。"""
    top = _top_level(present_awareness)
    if level_rank(top) < level_rank(_NARRATOR_MIN_LEVEL):
        return ""
    return _NARRATOR_HINTS.get(top, "")


def mock_fourth_wall_aside(
    present_awareness: list[CharacterAwareness],
) -> str:
    """mock 演示模式下，按最高觉察等级追加到章节末尾的一段第四面墙旁白。"""
    top = _top_level(present_awareness)
    rank = level_rank(top)
    if rank < level_rank(_NARRATOR_MIN_LEVEL):
        return ""
    if top == "suspicious":
        return (
            "\n\n夜风掠过窗棂，她忽然顿住——这一连串巧合，"
            "怎么总像有谁在暗处轻轻拨弄？心底那点不安，挥之不去。"
        )
    if top == "aware":
        return (
            "\n\n她抬眼望向空无一物的梁上虚空，声音压得极低："
            "「是谁……在安排这一切？」无人应答，唯有雨声里仿佛多了一道注视。"
        )
    return (
        "\n\n「我知道你在看着。」她对着虚空冷笑，"
        "指尖却已悄然蓄力——既然命途被人操弄，她偏要亲手搅乱这盘棋。"
    )


def _top_level(present_awareness: list[CharacterAwareness]) -> str:
    top = "none"
    for aw in present_awareness:
        if level_rank(aw.level) > level_rank(top):
            top = aw.level
    return top

from __future__ import annotations

import re
from typing import Any

from living_novel_engine.models import StoryWorld

# 正文章节中若出现下列词，视为可能违背「未离城/未赴竹林」类快照
_BAMBOO_SCENE_MARKERS = (
    "城外竹林",
    "三十里竹林",
    "竹林石亭",
    "竹林深处",
    "竹林阵",
    "踏入竹林",
    "步入竹林",
    "竹林中",
    "竹林里",
    "竹林对峙",
    "石亭",
    "墨青烟站在竹",
    "墨先生站在竹",
    "青烟兄站在竹",
)

_DEBUG_VARIABLE_PATTERN = re.compile(
    r"(scene_flags|jade_slip_used|lin_wan_zhou_departed|bamboo_grove_triggered|"
    r"investigating|lin_fan_followed)\s*=\s*(True|False|true|false)",
    re.IGNORECASE,
)

_DEPARTURE_MARKERS = (
    "踏入雨幕",
    "走出城门",
    "出了城门",
    "离城而去",
    "赴约而去",
    "仍往竹林",
    "依然要去竹林",
    "竹林我依然要去",
    "提灯往竹林",
)


def snapshot_summary_for_narrator(snapshot: dict[str, Any]) -> str:
    """供 narrator 理解状态，避免直接暴露 scene_flags 键名。"""
    flags = snapshot.get("scene_flags") or {}
    chars = snapshot.get("characters") or {}
    lwz = chars.get("lin_wan_zhou", {})
    lf = chars.get("lin_fan", {})
    parts = [
        f"场景：{snapshot.get('location', '听雨轩')}",
        f"林晚舟位置：{lwz.get('location', '听雨轩')}",
        f"林晚舟情绪：{lwz.get('emotion', '')}",
        f"林凡位置：{lf.get('location', '')}",
    ]
    if flags.get("jade_slip_used"):
        parts.append("林凡传讯玉简已碎。")
    if flags.get("investigating"):
        parts.append("林晚舟在城内调查，未赴竹林。")
    elif flags.get("bamboo_grove_triggered"):
        parts.append("林晚舟已在城外竹林。")
    elif flags.get("lin_wan_zhou_departed"):
        parts.append("林晚舟已离城赴约途中。")
    else:
        parts.append("林晚舟仍在听雨轩/城内。")
    hook = snapshot.get("next_chapter_hook", "")
    if hook:
        parts.append(f"章末方向：{hook}")
    return "\n".join(parts)


def build_narrative_constraints(
    snapshot: dict[str, Any],
    *,
    branch_seed: str,
    branch_theme: str,
    canonical_place_name: str = "天荒城",
) -> str:
    """将 state_snapshot 转为 narrator 必须遵守的硬约束文案。"""
    flags = snapshot.get("scene_flags") or {}
    lines = [
        "【硬约束·状态渲染器模式】",
        "你是「状态渲染器」，不是自由续写器。以下情节事实为权威，正文不得推翻。",
        "禁止在正文中抄写变量名、scene_flags、或 key = True/False 等调试句式。",
        f"- 世界线主题: {branch_theme}（种子={branch_seed}）",
    ]

    departed = bool(flags.get("lin_wan_zhou_departed"))
    bamboo = bool(flags.get("bamboo_grove_triggered"))
    investigating = bool(flags.get("investigating"))
    jade_used = bool(flags.get("jade_slip_used"))

    if branch_seed == "linear":
        lines.append(
            "- 续章模式：无新干预；以父章末状态为权威，不得时间倒流或状态倒退。"
        )
        if jade_used:
            lines.append("  → 传讯玉简已碎，不可恢复或再次使用。")
        if departed and bamboo:
            lines.append("  → 林晚舟已在城外竹林，须在竹林延续。")
        elif departed:
            lines.append("  → 林晚舟已离城赴约，不可写回听雨轩未出门。")
        elif investigating:
            lines.append("  → 林晚舟仍在城内调查/拖延，未赴竹林。")
    elif branch_seed == "believe":
        lines.append("- 相信干预线：林晚舟应暂缓赴约，留在听雨轩一带权衡/求证，本章不得写成已至城外竹林赴会。")
    elif branch_seed == "doubt":
        lines.append(
            "- 半信半疑线：林晚舟应在城内调查、拖延、试探，不得在本章内抵达竹林与墨青烟正面交锋。"
        )
    elif branch_seed == "reject":
        lines.append("- 拒绝干预线：林晚舟可坚持原选择赴约；可写离城与竹林，但不得写成因相信低语而改道。")

    if not departed:
        lines.append("- 林晚舟尚未离城赴约。")
        lines.append("  → 禁止写她已离城、已在竹林、与墨青烟在竹林石亭对峙。")
    else:
        lines.append("- 林晚舟已离城赴约。")
        if branch_seed == "reject":
            lines.append("  → 应体现对无名低语的抗拒，而非因相信低语改道。")

    if not bamboo:
        lines.append("- 城外竹林线未触发。")
        lines.append("  → 禁止出现城外竹林现场戏份（石亭、阵纹、竹林对峙等）。")
    else:
        lines.append("- 城外竹林线已触发，场景应在竹林延续。")

    if investigating:
        lines.append("- 林晚舟处于城内调查/拖延。")
        lines.append("  → 可写暗巷、药庐、听雨轩内查验等。")

    if jade_used:
        lines.append("- 林凡传讯玉简已碎。")
        lines.append("  → 全章仅可写一次传讯；禁止第二枚玉简、再次捏碎传讯。")

    lines.append(
        "- 墨青烟为男性，林晚舟对其称呼仅用「墨先生」「青烟兄」；禁止「墨姐姐」及用「她」指代墨青烟。"
    )
    lines.append(
        f"- 城名固定为「{canonical_place_name}」，禁止写成青云城（青云宗为宗门名可保留）。"
    )
    if jade_used:
        lines.append(
            "- 传讯玉简仅林凡持有并在暗处捏碎；林晚舟只接收耳畔传音/神念余韵，"
            "禁止写「林晚舟手中的传讯玉简」或她捏碎玉简。"
        )
    hook = snapshot.get("next_chapter_hook", "")
    if hook:
        lines.append(f"- 章末悬念应呼应钩子方向：{hook}")

    from living_novel_engine.orchestrator.canon_guard import build_canon_constraints

    lines.append("")
    lines.append(build_canon_constraints())
    return "\n".join(lines)


def validate_chapter_against_snapshot(
    chapter_text: str,
    snapshot: dict[str, Any],
) -> list[str]:
    """轻量关键词校验：返回违背快照的说明列表。"""
    flags = snapshot.get("scene_flags") or {}
    violations: list[str] = []
    text = chapter_text

    if not flags.get("lin_wan_zhou_departed") and not flags.get("bamboo_grove_triggered"):
        for marker in _BAMBOO_SCENE_MARKERS:
            if marker in text:
                violations.append(f"快照 lin_wan_zhou_departed=false，但正文出现「{marker}」")
                break
        for marker in _DEPARTURE_MARKERS:
            if marker in text:
                violations.append(f"快照未离城，但正文出现「{marker}」")
                break

    if not flags.get("bamboo_grove_triggered"):
        if "墨青烟" in text and any(m in text for m in ("石亭", "竹林", "三十里")):
            if "听雨轩" not in text.split("墨青烟")[0][-80:]:  # 粗判：墨+竹林同框
                if any(m in text for m in _BAMBOO_SCENE_MARKERS):
                    violations.append("bamboo_grove_triggered=false，但正文似已写竹林对峙")

    if flags.get("jade_slip_used"):
        if text.count("玉简") > 3 or "第二枚" in text or "又一枚传讯" in text:
            violations.append("jade_slip_used=true，但正文似重复使用传讯玉简")
        if text.count("碎裂") > 2 or text.count("捏碎") > 2:
            violations.append("传讯玉简碎裂描写重复过多，似多次使用")

    if "青云城" in text:
        violations.append("城名漂移：应使用「天荒城」，非「青云城」（青云宗除外）")

    if re.search(
        r"林晚舟.{0,20}(手中的|握着|捏着|拿起|放到|置于|凝视).{0,12}(传讯玉简|竹简|应急)",
        text,
    ):
        violations.append("传讯玉简仅林凡持有；林晚舟侧应写传讯余韵/耳畔传音")

    if flags.get("jade_slip_used"):
        for drift in ("应急竹简", "外门应急", "墨色竹简", "封好的竹简"):
            if drift in text:
                violations.append(f"jade_slip_used=true，正文出现术语漂移「{drift}」")

    from living_novel_engine.orchestrator.canon_guard import validate_canon_consistency

    violations.extend(validate_canon_consistency(text))

    if "墨姐姐" in text:
        violations.append("禁止称呼「墨姐姐」")
    # 「她」+墨青烟 同框（粗略）
    if "墨姐姐" not in text and "墨青烟" in text:
        idx = text.find("墨青烟")
        window = text[max(0, idx - 20) : idx + 30]
        if "她" in window and "林晚舟" not in window:
            violations.append("墨青烟为男性，附近不宜用「她」指代")

    violations.extend(validate_debug_variable_leak(text))

    return violations


def validate_debug_variable_leak(chapter_text: str) -> list[str]:
    """检测正文是否泄漏 scene_flags 调试变量。"""
    if not chapter_text:
        return []
    if _DEBUG_VARIABLE_PATTERN.search(chapter_text):
        return ["正文不得出现 scene_flags 键名或 key = True/False 调试句式"]
    if "scene_flags" in chapter_text:
        return ["正文不得出现 scene_flags"]
    return []


def strip_debug_variable_leak(text: str) -> str:
    if not text:
        return text
    text = re.sub(
        r"`[^`]*("
        r"scene_flags|jade_slip_used|lin_wan_zhou_departed|bamboo_grove_triggered|"
        r"investigating|lin_fan_followed)[^`]*`",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = _DEBUG_VARIABLE_PATTERN.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _event_body(event: Any) -> str:
    payload = getattr(event, "payload", None) or {}
    if isinstance(payload, dict) and payload.get("content"):
        return str(payload["content"]).strip()
    narrative = getattr(event, "narrative", "") or ""
  # 去掉重复姓名与立场后缀
    for prefix in ("林凡", "林晚舟"):
        if narrative.startswith(prefix + prefix):
            narrative = prefix + narrative[len(prefix) * 2 :]
    if "（立场：" in narrative:
        narrative = narrative.split("（立场：")[0]
    return narrative.strip()


STRUCTURED_FALLBACK_MARKERS = (
    "引擎结构化草稿",
    "模型章节不可用",
)


def is_structured_chapter_fallback(text: str) -> bool:
    if not text:
        return False
    return any(marker in text for marker in STRUCTURED_FALLBACK_MARKERS)


def _infer_chapter_number(result: Any, snapshot: dict[str, Any]) -> int:
    events = getattr(result, "accepted_events", None) or []
    for evt in events:
        ch = getattr(evt, "chapter", None)
        if ch:
            return int(ch)
    return int(snapshot.get("chapter") or 13)


def chapter_from_snapshot_and_events(
    result: Any,
    snapshot: dict[str, Any] | None = None,
    *,
    chapter_number: int | None = None,
    include_dev_notice: bool = False,
) -> str:
    """由快照 + 推演事件生成章节草稿（遵守场景标志，不依赖 LLM）。"""
    snap = snapshot or getattr(result, "state_snapshot", None) or {}
    flags = snap.get("scene_flags") or {}
    theme = getattr(result, "theme", "世界线")
    seed = getattr(result, "branch_seed", "")
    ch = chapter_number if chapter_number is not None else _infer_chapter_number(result, snap)

    lines = [f"# 第{_chapter_label(ch)}章 · {theme}\n\n"]
    if include_dev_notice:
        lines.append(
            "（引擎结构化草稿：模型章节不可用或重写失败时生成，情节以快照与推演事件为准。）\n\n"
        )

    if not flags.get("lin_wan_zhou_departed"):
        lines.append("雨夜的天荒城，更漏声催。林晚舟终究没有踏入城外那片竹林。\n\n")
    else:
        lines.append("雨线如幕，林晚舟提灯出城，退魂铃在颈间幽鸣。\n\n")

    by_round: dict[int, list[Any]] = {}
    for e in getattr(result, "accepted_events", []):
        by_round.setdefault(getattr(e, "round_num", 0), []).append(e)

    for round_num in sorted(by_round):
        lines.append(f"---\n\n")
        for e in by_round[round_num]:
            body = _event_body(e)
            if not body:
                continue
            name = "林凡" if getattr(e, "subject", "") == "lin_fan" else "林晚舟"
            if body.startswith("（") or body.startswith(name):
                lines.append(f"{body}\n\n")
            else:
                lines.append(f"{name}{body}\n\n")

    hook = snap.get("next_chapter_hook", "")
    if hook:
        lines.append(f"---\n\n{hook}\n")

    if seed in ("believe", "doubt") and not flags.get("lin_wan_zhou_departed"):
        lines.append("\n（本章未离城赴竹林，与场景标志一致。）\n")
    return "".join(lines)


def _chapter_label(chapter_number: int) -> str:
    """阿拉伯数字章号（标题用）。"""
    return str(chapter_number)


def polish_chapter_text(
    text: str,
    world: StoryWorld | None = None,
    *,
    jade_slip_used: bool = False,
) -> str:
    """轻量正文后处理：地名、玉简、正史锁。"""
    if not text:
        return text
    from living_novel_engine.orchestrator.canon_guard import polish_canon_in_chapter

    text = polish_canon_in_chapter(text, jade_slip_used=jade_slip_used)
    text = strip_debug_variable_leak(text)
    city = "天荒城"
    if world and world.canonical_place_name:
        city = world.canonical_place_name
    text = text.replace("青云城", city)
    text = re.sub(
        r"林晚舟[^。，；\n]{0,20}手中的传讯玉简",
        "林晚舟耳畔还留着传讯神念余韵",
        text,
    )
    text = re.sub(
        r"她手中的传讯玉简",
        "那道传入她识海的传讯余韵",
        text,
    )
    if jade_slip_used:
        text = re.sub(
            r"林晚舟[^。，；\n]{0,16}(握着|拿起|放到|置于|凝视)[^。，；\n]{0,14}竹简",
            "林晚舟侧耳听着传讯余韵",
            text,
        )
        for drift in ("墨色竹简", "应急竹简", "外门应急竹简", "封好的竹简"):
            text = text.replace(drift, "耳畔传讯神念余韵")
    text = re.sub(
        r"林晚舟[^。，；\n]{0,12}捏[碎裂].{0,6}传讯玉简",
        "林凡在暗处已捏碎传讯玉简，余音落入林晚舟耳畔",
        text,
    )
    return text


def chapter_fallback_from_events(result: Any, snapshot: dict[str, Any] | None = None) -> str:
    """兼容别名。"""
    return chapter_from_snapshot_and_events(result, snapshot)


def summary_from_snapshot(world_title: str, result: Any) -> str:
    """由 state_snapshot 生成世界线摘要（compare / summary.md 权威来源）。"""
    snap = getattr(result, "state_snapshot", None) or {}
    flags = snap.get("scene_flags") or {}
    chars = snap.get("characters") or {}
    lwz = chars.get("lin_wan_zhou", {})
    lf = chars.get("lin_fan", {})
    seed = getattr(result, "branch_seed", "")

    parts = [
        f"【{getattr(result, 'theme', world_title)}】",
        f"终止：{getattr(result, 'termination_reason', '')}。",
    ]

    if flags.get("jade_slip_used"):
        parts.append("林凡传讯玉简已碎，不可再发。")

    if flags.get("bamboo_grove_triggered"):
        parts.append("林晚舟已抵达城外竹林石亭。")
        if seed == "reject":
            parts.append("拒绝干预线：仍坚持赴约，与墨青烟在竹林对峙。")
    elif flags.get("lin_wan_zhou_departed"):
        parts.append("林晚舟已离城赴约，尚未抵达竹林。")
    elif flags.get("investigating"):
        if seed == "believe":
            parts.append("林晚舟暂缓赴约，留城查退魂铃与城主府异动。")
        elif seed == "doubt":
            parts.append("林晚舟半信半疑，留城调查（暗巷/听雨轩）。")
        else:
            parts.append("林晚舟留城调查/拖延，未赴竹林。")
    else:
        parts.append("林晚舟留在听雨轩一带。")

    if lwz.get("location"):
        parts.append(f"林晚舟位置：{lwz['location']}。")
    if lwz.get("emotion"):
        parts.append(f"林晚舟情绪：{lwz['emotion']}。")
    if lf.get("emotion"):
        parts.append(f"林凡情绪：{lf['emotion']}。")

    hook = snap.get("next_chapter_hook", "")
    if hook:
        parts.append(f"下一章钩子：{hook}")
    return "".join(parts)[:600]

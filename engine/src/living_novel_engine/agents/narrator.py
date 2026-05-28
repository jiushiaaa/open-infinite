from __future__ import annotations

import os
from pathlib import Path

from typing import Any

from living_novel_engine.llm.client import LLMClient
from living_novel_engine.models import StoryWorld
from living_novel_engine.models.events import SimulationResult
from living_novel_engine.orchestrator.narrative_constraints import (
    build_narrative_constraints,
    chapter_from_snapshot_and_events,
    is_structured_chapter_fallback,
    polish_chapter_text,
    snapshot_summary_for_narrator,
    strip_debug_variable_leak,
    summary_from_snapshot,
    validate_chapter_against_snapshot,
    validate_debug_variable_leak,
)

_BUILTIN_STYLE_PATH = (
    Path(__file__).resolve().parents[1] / "resources" / "style_fallback_xianxia.md"
)


def _builtin_style_hint() -> str:
    if _BUILTIN_STYLE_PATH.exists():
        return _BUILTIN_STYLE_PATH.read_text(encoding="utf-8")
    return (
        "修真网文：短句、张力、留白；情绪用动作与器物呈现；"
        "对话带身份差；章末留悬念。"
    )


def _optional_external_style_hint() -> str | None:
    """仅当用户显式配置 WEBNOVEL_GENRE_TEMPLATE 且文件可读时采用，失败则忽略。"""
    env_path = os.environ.get("WEBNOVEL_GENRE_TEMPLATE", "").strip()
    if not env_path:
        return None
    path = Path(env_path)
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        return text[:3000] + ("\n...(截断)" if len(text) > 3000 else "")
    except OSError:
        return None


def genre_style_hint() -> str:
    external = _optional_external_style_hint()
    if external:
        return f"【可选外部风格参考】\n{external}\n\n【内置 fallback】\n{_builtin_style_hint()}"
    return _builtin_style_hint()


def render_summary(
    world: StoryWorld,
    result: SimulationResult,
    llm: LLMClient,
) -> str:
    events_text = "\n".join(
        f"- 第{e.round_num}轮 [{e.event_type}] {e.subject}: {e.narrative}"
        for e in result.accepted_events
    )
    system = "你是叙事编辑，将推演事件整理为 200-400 字世界线摘要，突出分歧点与角色命运变化。"
    user = (
        f"世界: {world.display_name or world.title}\n"
        f"主题: {result.theme}\n"
        f"分支种子: {result.branch_seed}\n"
        f"终止原因: {result.termination_reason}\n"
        f"事件:\n{events_text}"
    )
    if llm.mock:
        return summary_from_snapshot(world.display_name or world.title, result)
    text = llm.chat(system, user, temperature=0.5, max_tokens=800)
    if not (text or "").strip():
        text = summary_from_snapshot(world.display_name or world.title, result)
    return text.strip()


def _strip_leading_h1(text: str) -> str:
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).strip()
    return text.strip()


def _mock_chapter_body(
    world: StoryWorld,
    result: SimulationResult,
    prologue: str,
    canon_opening: str,
    canon_chapter: str,
    *,
    chapter_number: int = 13,
) -> str:
    """Mock 演示：从前情与第一章写起，再衔接干预章与分叉续写。"""
    prologue_block = _strip_leading_h1(prologue) if prologue else "（暂无前情提要）"
    opening_block = _strip_leading_h1(canon_opening) if canon_opening else ""
    intervention_tail = canon_chapter.strip()[-600:] if canon_chapter else ""

    lines = [
        "# 前情提要\n",
        prologue_block,
        "\n\n---\n\n",
    ]
    if opening_block:
        lines.extend(["# 第一章 边城雨至（原作节选）\n\n", opening_block, "\n\n---\n\n"])
    if intervention_tail:
        lines.extend(
            [
                "# 第十二章 子时将至（干预节点·节选）\n\n",
                intervention_tail,
                "\n\n---\n\n",
            ]
        )
    lines.extend(
        [
            f"# 第{chapter_number}章 雨线分叉（干预后·本世界线）\n\n",
            "雨夜未歇。林晚舟在听雨轩廊下停住脚步，灯笼的光在雨丝里摇晃。",
            "若那低语为真，城外竹林便是杀局；若为假，她便辜负了十年恩义故友。",
            "林凡在暗处咬破舌尖，传讯玉简在袖中发烫，终究没有捏碎。",
            "子时更漏已尽，竹林方向传来一声极轻的铃响——退魂铃，还是杀机？\n\n",
            f"（本世界线：{result.theme}）\n",
            f"（演示模式：完整阅读请配置 LLM_API_KEY 后去掉 --mock）",
        ]
    )
    return "".join(lines)


def _recover_chapter_after_failed_repair(
    llm: LLMClient,
    *,
    short_system: str,
    simple_user: str,
    first_draft: str,
    result: SimulationResult,
    snap: dict[str, Any],
    chapter_number: int,
) -> str:
    """重写失败时：先简易再生成，再保留首稿，最后才用事件草稿。"""
    retry = llm.chat(short_system, simple_user, temperature=0.55, max_tokens=4096)
    if retry.strip() and not is_structured_chapter_fallback(retry):
        return retry.strip()

    draft = (first_draft or "").strip()
    if (
        len(draft) > 400
        and not is_structured_chapter_fallback(draft)
        and not validate_debug_variable_leak(draft)
    ):
        return draft

    return chapter_from_snapshot_and_events(
        result, snap, chapter_number=chapter_number, include_dev_notice=False
    )


def render_chapter(
    world: StoryWorld,
    result: SimulationResult,
    canon_excerpt: str,
    llm: LLMClient,
    *,
    prologue: str = "",
    canon_opening: str = "",
    canon_chapter: str = "",
    state_snapshot: dict[str, Any] | None = None,
    chapter_number: int = 13,
) -> str:
    events_text = "\n".join(
        f"第{e.round_num}轮 {e.subject}: {e.narrative}" for e in result.accepted_events
    )
    style = genre_style_hint()
    length_hint = "1500-2500 字" if not llm.mock else "300-600 字（mock 演示）"
    snap = state_snapshot or {}
    constraints = ""
    if snap:
        constraints = build_narrative_constraints(
            snap,
            branch_seed=result.branch_seed,
            branch_theme=result.theme,
            canonical_place_name=world.canonical_place_name or "天荒城",
        )

    system = f"""你是网文「状态渲染器」，将已锁定的推演状态写成小说章节正文。
要求：
- {length_hint}
- **权威事实以【场景状态摘要】与【硬约束】为准**；不得为戏剧张力改写离城/赴竹林/玉简次数
- 保持人设一致，遵守世界规则与角色称谓规则
- 承接原作语气，但不要照抄原作
- 不要打破第四面墙
- **禁止**在正文中出现 scene_flags、变量名、或 `key = True/False` 等调试句式

题材风格参考：
{style}
"""
    context = canon_excerpt if canon_excerpt else ""
    snap_summary = snapshot_summary_for_narrator(snap) if snap else ""
    user = (
        f"【原作上下文（含前情与干预节点）】\n{context[-3500:]}\n\n"
        f"【世界规则】\n{world.rules_text()}\n\n"
        f"【本世界线】{result.theme} / 种子={result.branch_seed}\n\n"
        f"【推演事件】\n{events_text}\n\n"
        f"【场景状态摘要（仅供理解，勿抄写变量名）】\n{snap_summary}\n\n"
        f"{constraints}\n\n"
        f"请写出「{world.display_name or world.title}」**第{chapter_number}章**正文。"
        f"须自然承接上一章（第{chapter_number - 1}章）结尾，勿重复前情全文，标题自拟。"
    )
    if llm.mock:
        intervention_chapter = canon_chapter if canon_chapter else context
        return _mock_chapter_body(
            world,
            result,
            prologue,
            canon_opening,
            intervention_chapter,
            chapter_number=chapter_number,
        )

    chapter = llm.chat(system, user, temperature=0.65, max_tokens=4096)
    first_draft = chapter

    short_system = (
        f"你是网文状态渲染器。只输出第{chapter_number}章正文，遵守用户给出的硬约束，"
        "1500字左右，不要输出解释、元说明或章节外的标记。"
    )
    simple_user = (
        f"【世界线】{result.theme} / {result.branch_seed}\n"
        f"【推演事件】\n{events_text}\n\n"
        f"{constraints}\n\n"
        f"请写第{chapter_number}章正文，标题自拟。"
    )

    if snap and first_draft.strip():
        violations = validate_chapter_against_snapshot(first_draft, snap)
        if violations:
            repair_user = (
                f"【世界线】{result.theme}\n"
                f"【推演事件】\n{events_text}\n\n"
                f"{constraints}\n\n"
                f"【上次草稿违规】\n"
                + "\n".join(f"- {v}" for v in violations)
                + f"\n\n请只输出重写后的第{chapter_number}章正文（1500字左右），"
                "严格消除违规；勿输出任何变量名或 key = True/False。"
            )
            repaired = llm.chat(system, repair_user, temperature=0.5, max_tokens=4096)
            if repaired.strip() and not is_structured_chapter_fallback(repaired):
                chapter = repaired
            else:
                chapter = _recover_chapter_after_failed_repair(
                    llm,
                    short_system=short_system,
                    simple_user=simple_user,
                    first_draft=first_draft,
                    result=result,
                    snap=snap,
                    chapter_number=chapter_number,
                )
    elif not first_draft.strip():
        chapter = llm.chat(short_system, simple_user, temperature=0.65, max_tokens=4096)

    if not (chapter or "").strip():
        chapter = chapter_from_snapshot_and_events(
            result, snap, chapter_number=chapter_number, include_dev_notice=False
        )
    jade_used = bool((snap.get("scene_flags") or {}).get("jade_slip_used"))
    chapter = polish_chapter_text(chapter.strip(), world, jade_slip_used=jade_used)
    if validate_debug_variable_leak(chapter) or is_structured_chapter_fallback(chapter):
        fallback = chapter_from_snapshot_and_events(
            result, snap, chapter_number=chapter_number, include_dev_notice=False
        )
        if fallback.strip():
            chapter = polish_chapter_text(
                fallback.strip(), world, jade_slip_used=jade_used
            )
        else:
            chapter = strip_debug_variable_leak(chapter)
    return chapter

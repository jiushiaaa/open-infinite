from __future__ import annotations

import os
from pathlib import Path

from living_novel_engine.llm.client import LLMClient
from living_novel_engine.models import StoryWorld
from living_novel_engine.models.events import SimulationResult

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
        return (
            f"【{result.theme}】林晚舟在雨夜做出选择，"
            f"立场倾向「{result.branch_seed}」。"
            f"林凡与墨青烟的暗线在此世界线产生不同张力。"
            f"（终止：{result.termination_reason}）"
        )
    return llm.chat(system, user, temperature=0.5, max_tokens=800)


def render_chapter(
    world: StoryWorld,
    result: SimulationResult,
    canon_excerpt: str,
    llm: LLMClient,
) -> str:
    events_text = "\n".join(
        f"第{e.round_num}轮 {e.subject}: {e.narrative}" for e in result.accepted_events
    )
    style = genre_style_hint()
    length_hint = "1500-2500 字" if not llm.mock else "300-600 字（mock 演示）"
    system = f"""你是网文叙事渲染器，将结构化推演结果写成小说章节正文。
要求：
- {length_hint}
- 保持人设一致，遵守世界规则
- 承接原作语气，但不要照抄原作
- 写出角色对干预的合理反应（相信/怀疑/拒绝）
- 不要打破第四面墙

题材风格参考：
{style}
"""
    user = (
        f"【原作结尾节选】\n{canon_excerpt[-1200:]}\n\n"
        f"【世界规则】\n{world.rules_text()}\n\n"
        f"【本世界线】{result.theme} / 种子={result.branch_seed}\n\n"
        f"【推演事件】\n{events_text}\n\n"
        f"请写出「{world.display_name or world.title}」干预后的下一章正文，标题自拟。"
    )
    if llm.mock:
        return (
            "# 第十三章 雨线分叉\n\n"
            "【模拟章节】雨夜天荒，林晚舟在听雨轩前驻足。"
            "一道无形低语落入她心湖，她指尖微颤，却未立刻折返。"
            "林凡在暗处咬破舌尖，传讯玉简终究没有捏碎。"
            "子时更漏已尽，竹林方向传来一声极轻的铃响。\n\n"
            f"（本世界线：{result.theme}）"
        )
    return llm.chat(system, user, temperature=0.75, max_tokens=4096)

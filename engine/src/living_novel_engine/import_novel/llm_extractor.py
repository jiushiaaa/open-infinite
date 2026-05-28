"""LLM Extractor — 真实 LLM 抽取世界锚定（world pass + character pass）。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from living_novel_engine.import_novel.mock_extractor import ExtractionResult
from living_novel_engine.import_novel.splitter import SplitChapter
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.resources.genre_loader import (
    get_genre_display_name,
    load_genre_template,
)


WORLD_SYSTEM_PROMPT = """你是一个小说世界分析引擎。用户会给你 3-10 章小说文本的摘要。
你需要从中抽取可结构化运行的世界设定。

输出严格 JSON，不要 markdown，不要解释文字。

JSON 结构:
{
  "title": "小说标题（从正文推断）",
  "display_name": "中文展示名",
  "canonical_place_name": "主要场景地名",
  "divergence_point": "干预锚定点描述（最后一章结尾悬念）",
  "scene_description": "干预节点场景描写（200字以内）",
  "rules": ["世界规则1", "世界规则2", ...],
  "locations": [
    {"id": "snake_case_id", "name": "地点名", "description": "简述"}
  ],
  "factions": ["势力1", "势力2"],
  "timeline": ["事件1", "事件2", ...]
}

规则要求:
- rules 至少 3 条，包含：1) 战力/能力体系限制 2) 禁止 OOC 3) 禁止未声明设定（重生/系统/穿越等）
- locations 至少 2 个，id 为英文 snake_case
- timeline 按时间顺序，覆盖已知关键事件
- divergence_point 描述最后一章结尾的悬念/冲突节点
- scene_description 写清干预节点时各角色的位置和即时局面"""

CHARACTER_SYSTEM_PROMPT = """你是一个小说角色分析引擎。用户会给你小说文本摘要和已抽取的世界设定。
你需要从中抽取所有重要角色的结构化数据。

输出严格 JSON，不要 markdown，不要解释文字。

JSON 结构:
{
  "characters": [
    {
      "id": "snake_case_id",
      "name": "角色全名",
      "narrative_role": "protagonist_candidate | antagonist | supporting",
      "gender": "男 | 女 | 未知",
      "persona": {
        "traits": ["性格特征1", "性格特征2", "性格特征3"],
        "desires": ["目标/欲望1", "目标/欲望2"],
        "fears": ["恐惧/弱点1", "恐惧/弱点2"],
        "boundaries": ["行为底线1（不会做的事）", "行为底线2"]
      },
      "memory": ["已知关键记忆/经历1", "关键记忆2"],
      "relationships": {"other_char_id": "关系描述"},
      "current_state": {
        "location": "当前位置（干预节点时）",
        "emotion": "当前情绪",
        "resources": ["持有物品/能力"]
      },
      "present_in_scene": true/false
    }
  ],
  "open_threads": [
    {"id": "snake_case_id", "title": "伏笔标题", "description": "伏笔说明", "status": "open"}
  ]
}

要求:
- 抽取 3-8 个重要角色（有名字、有行动的才算）
- 至少 1 个 present_in_scene=true（干预节点在场）
- id 一律英文 snake_case，不要中文
- relationships 的 key 用其他角色的 id
- open_threads 至少 2 条：未解决的悬念/冲突
- boundaries 非常重要：写清角色绝对不会做的事，这是后续干预拒绝的依据"""


def llm_extract(
    chapters: list[SplitChapter],
    llm: LLMClient,
    *,
    story_name: str = "unnamed",
    genre: str = "xianxia",
    anchor_chapter_index: int | None = None,
) -> ExtractionResult:
    """调用 LLM 两次抽取世界锚定数据。"""
    if anchor_chapter_index is None:
        anchor_chapter_index = len(chapters) - 1

    chapter_summaries = _build_chapter_summaries(chapters)
    anchor = chapters[anchor_chapter_index]

    # --- World pass ---
    world_user = _build_world_user_prompt(chapter_summaries, anchor, genre)
    world_raw = llm.chat(
        WORLD_SYSTEM_PROMPT, world_user, temperature=0.3, max_tokens=4096
    )
    world_yaml = _parse_json_response(world_raw, "world")
    _patch_world_defaults(world_yaml, story_name, anchor)

    # --- Character pass ---
    char_user = _build_character_user_prompt(chapter_summaries, anchor, world_yaml)
    char_raw = llm.chat(
        CHARACTER_SYSTEM_PROMPT, char_user, temperature=0.3, max_tokens=6000
    )
    char_data = _parse_json_response(char_raw, "characters")
    characters_yaml = {"characters": char_data.get("characters", [])}
    open_threads = char_data.get("open_threads", [])

    # --- Validation & repair ---
    warnings = _validate_and_repair(world_yaml, characters_yaml, open_threads)

    anchor_proposal = _build_anchor_proposal(world_yaml, characters_yaml, chapters)

    return ExtractionResult(
        world_yaml=world_yaml,
        characters_yaml=characters_yaml,
        open_threads=open_threads,
        anchor_proposal=anchor_proposal,
        warnings=warnings,
    )


def _build_chapter_summaries(chapters: list[SplitChapter]) -> str:
    parts: list[str] = []
    for ch in chapters:
        head = ch.content[:800]
        tail = ch.content[-400:] if len(ch.content) > 1200 else ""
        summary = f"=== {ch.title} ===\n{head}"
        if tail:
            summary += f"\n...\n{tail}"
        parts.append(summary)
    return "\n\n".join(parts)


def _build_world_user_prompt(summaries: str, anchor: SplitChapter, genre: str) -> str:
    genre_name = get_genre_display_name(genre)
    genre_template = load_genre_template(genre)
    if len(genre_template) > 3000:
        genre_template = genre_template[:3000] + "\n...（题材模板已截断）"
    return (
        f"【题材】{genre} / {genre_name}\n\n"
        f"【题材模板】\n{genre_template}\n\n"
        f"【章节摘要】\n{summaries}\n\n"
        f"【干预锚定章（全文）】\n{anchor.content}\n\n"
        "请抽取世界设定 JSON。"
    )


def _build_character_user_prompt(
    summaries: str, anchor: SplitChapter, world_yaml: dict
) -> str:
    world_brief = json.dumps(
        {k: world_yaml[k] for k in ("title", "rules", "locations", "factions", "timeline") if k in world_yaml},
        ensure_ascii=False,
        indent=None,
    )
    return (
        f"【已抽取的世界设定】\n{world_brief}\n\n"
        f"【章节摘要】\n{summaries}\n\n"
        f"【干预锚定章（全文）】\n{anchor.content}\n\n"
        "请抽取角色和伏笔 JSON。"
    )


def _parse_json_response(raw: str, context: str) -> dict:
    """从 LLM 响应中提取 JSON，容错处理。"""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [ln for ln in lines if not ln.strip().startswith("```")]
        text = "\n".join(lines)
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM {context} 响应不是合法 JSON: {e}\n原始响应前 500 字: {raw[:500]}"
        )


def _patch_world_defaults(world_yaml: dict, story_name: str, anchor: SplitChapter) -> None:
    """补全缺失字段的默认值。"""
    world_yaml.setdefault("id", f"world_{story_name}")
    world_yaml.setdefault("slug", story_name)
    world_yaml["source_type"] = "imported"
    world_yaml.setdefault("worldline_policy", "branch_on_major_intervention")
    if not world_yaml.get("divergence_point"):
        world_yaml["divergence_point"] = f"chapter_{anchor.index}_end"
    if not world_yaml.get("display_name"):
        world_yaml["display_name"] = world_yaml.get("title", story_name)


def _validate_and_repair(
    world_yaml: dict,
    characters_yaml: dict,
    open_threads: list,
) -> list[str]:
    """基础验证与修复，返回 warnings。"""
    warnings: list[str] = []

    rules = world_yaml.get("rules", [])
    if len(rules) < 3:
        warnings.append(f"rules 仅 {len(rules)} 条，建议补充至 3 条以上")

    locations = world_yaml.get("locations", [])
    if len(locations) < 2:
        warnings.append(f"locations 仅 {len(locations)} 个，建议补充")

    chars = characters_yaml.get("characters", [])
    if len(chars) < 2:
        warnings.append(f"仅抽取到 {len(chars)} 个角色，建议检查")

    has_present = any(c.get("present_in_scene") for c in chars)
    if not has_present and chars:
        warnings.append("无 present_in_scene=true 角色，已自动设置第一个角色")
        chars[0]["present_in_scene"] = True

    seen_ids: set[str] = set()
    for i, c in enumerate(chars):
        cid = c.get("id", "")
        if not cid:
            cid = f"char_{i}"
            c["id"] = cid
            warnings.append(f"角色 {c.get('name', '?')} 缺少 id，已自动分配 {cid}")
        if cid in seen_ids:
            new_id = f"{cid}_{i}"
            c["id"] = new_id
            warnings.append(f"角色 id 重复 '{cid}'，已改为 '{new_id}'")
            cid = new_id
        seen_ids.add(cid)

    if len(open_threads) < 2:
        warnings.append(f"open_threads 仅 {len(open_threads)} 条，建议补充")

    return warnings


def _build_anchor_proposal(
    world_yaml: dict,
    characters_yaml: dict,
    chapters: list[SplitChapter],
) -> dict:
    chars = characters_yaml.get("characters", [])
    protagonists = [c["id"] for c in chars if c.get("narrative_role") == "protagonist_candidate"]
    present = [c["id"] for c in chars if c.get("present_in_scene")]

    return {
        "extraction_version": "0.2",
        "confidence": "llm",
        "warnings": [],
        "protagonist_candidates": protagonists or [c["id"] for c in chars[:2]],
        "intervention_hints": [
            f"建议在 {world_yaml.get('divergence_point', '最后一章结尾')} 前干预",
        ],
        "suggested_targets": [
            {"id": cid, "reason": "干预节点在场"}
            for cid in present[:3]
        ],
        "raw_notes": f"基于 {len(chapters)} 章 LLM 抽取",
    }

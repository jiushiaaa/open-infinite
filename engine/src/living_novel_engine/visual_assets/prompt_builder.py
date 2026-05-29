"""中文视觉 prompt 构造器（确定性、可单测）。

原则：
- 全中文，围绕故事/世界/角色已有设定，不堆砌 AI 味词。
- 克制画面感，偏小说插画/封面气质，避免过度现代 UI 风。
- 不要求模仿在世艺术家、不做版权规避表述。
"""

from __future__ import annotations

from living_novel_engine.models import CharacterAgent, StoryWorld

_ROLE_LABEL = {
    "protagonist": "主角",
    "protagonist_candidate": "主角",
    "antagonist": "对立者",
    "supporting": "配角",
    "mentor": "引路人",
}

_BASE_STYLE = "中国风小说插画，水墨与工笔结合，构图克制，留白考究，情绪含蓄，不出现文字与水印"


def _role_label(role: str) -> str:
    return _ROLE_LABEL.get(role, "角色")


def _clip(text: str, limit: int) -> str:
    text = (text or "").strip().replace("\n", "　")
    return text[:limit]


def build_character_prompt(world: StoryWorld, character: CharacterAgent) -> str:
    """角色头像 prompt：姓名、性别、叙事身份、性格、欲望、恐惧、当前状态、题材。"""
    p = character.persona
    parts = [
        f"人物半身肖像：{character.name}",
        f"身份：{_role_label(character.narrative_role)}",
    ]
    if character.gender:
        parts.append(f"性别：{character.gender}")
    if p.traits:
        parts.append(f"性格：{'、'.join(p.traits[:4])}")
    if p.desires:
        parts.append(f"心之所向：{'、'.join(p.desires[:2])}")
    if p.fears:
        parts.append(f"所惧：{'、'.join(p.fears[:2])}")
    state = character.current_state
    if state.emotion:
        parts.append(f"此刻神情：{state.emotion}")
    if state.location:
        parts.append(f"所处：{state.location}")
    parts.append(f"故事氛围：{_clip(world.title, 20)}")
    parts.append(_BASE_STYLE)
    return "，".join(parts) + "。"


def build_cover_prompt(world: StoryWorld) -> str:
    """故事封面 prompt：标题、世界规则、当前场景、核心冲突、古风封面风格。"""
    parts = [f"小说封面：《{_clip(world.display_name or world.title, 24)}》"]
    if world.canonical_place_name:
        parts.append(f"主场景：{world.canonical_place_name}")
    if world.scene_description:
        parts.append(f"场景气象：{_clip(world.scene_description, 60)}")
    threads = [t.title for t in world.open_threads if t.title][:2]
    if threads:
        parts.append(f"核心张力：{'、'.join(threads)}")
    if world.rules:
        parts.append(f"世界设定：{_clip(world.rules[0], 40)}")
    parts.append("古风小说封面构图，主视觉居中，氛围深沉而有余韵")
    parts.append(_BASE_STYLE)
    return "，".join(parts) + "。"


def build_scene_prompt(world: StoryWorld, chapter_summary: str = "") -> str:
    """场景背景 prompt：scene_description、locations、当前章节摘要。"""
    parts = ["场景背景图，无人物特写，重在环境与气氛"]
    if world.scene_description:
        parts.append(f"环境：{_clip(world.scene_description, 80)}")
    locs = [loc.name for loc in world.locations if loc.name][:2]
    if locs:
        parts.append(f"地点：{'、'.join(locs)}")
    if chapter_summary:
        parts.append(f"当下情节：{_clip(chapter_summary, 60)}")
    parts.append(_BASE_STYLE)
    return "，".join(parts) + "。"


def build_worldline_node_prompt(
    *,
    branch_theme: str = "",
    intervention_summary: str = "",
    causal_summary: str = "",
    chapter_summary: str = "",
) -> str:
    """世界线节点缩略图 prompt（本轮预留，UI 暂以占位呈现）。"""
    parts = ["世界线分支缩略意象，象征性构图，弱化具体人物"]
    if branch_theme:
        parts.append(f"分支主题：{_clip(branch_theme, 30)}")
    if intervention_summary:
        parts.append(f"干预要旨：{_clip(intervention_summary, 40)}")
    if causal_summary:
        parts.append(f"因果变化：{_clip(causal_summary, 40)}")
    if chapter_summary:
        parts.append(f"情节：{_clip(chapter_summary, 40)}")
    parts.append(_BASE_STYLE)
    return "，".join(parts) + "。"

"""console-free 主题创世服务（v0.7 第六刀：主题创世 Web 入口）。

用户不上传小说，只给题材/主题/主角/风格，系统生成一个可运行的初始项目，
项目结构与 import-novel 同构（复用 write_project / validate_project）。

- mock 路径：deterministic，便于测试。
- llm 路径：复用 LLMClient.chat_json_with_usage；无 key 或异常时安全退化 mock。
- 零新依赖；不接 Seedream / LangGraph / Zep。
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from living_novel_engine.import_novel.mock_extractor import ExtractionResult
from living_novel_engine.import_novel.splitter import SplitChapter
from living_novel_engine.import_novel.validator import validate_project
from living_novel_engine.import_novel.writer import _default_projects_dir, write_project
from living_novel_engine.llm.client import LLMClient, LLMSettings

GENESIS_VERSION = "v0.7-genesis"
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class GenesisRequestError(ValueError):
    """入参非法（坏 slug、空 premise）——映射为 HTTP 400。"""


class GenesisProjectExistsError(Exception):
    """同名项目已存在且未允许覆盖——映射为 HTTP 409。"""


@dataclass
class GenesisServiceResult:
    story_slug: str
    display_name: str
    chapter_count: int
    character_count: int
    anchor_chapter_index: int
    generation_mode: str = "mock"
    warnings: list[str] = field(default_factory=list)


# ── LLM 草稿模型（结构化输出） ─────────────────────────────


class _GenChar(BaseModel):
    id: str
    name: str
    narrative_role: str = "supporting"
    gender: str = ""
    traits: list[str] = Field(default_factory=list)
    desires: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    location: str = ""
    emotion: str = ""
    resources: list[str] = Field(default_factory=list)
    present_in_scene: bool = True


class _GenThread(BaseModel):
    id: str
    title: str
    description: str = ""
    status: str = "open"


class _GenesisDraft(BaseModel):
    title: str
    display_name: str = ""
    canonical_place_name: str = ""
    scene_description: str = ""
    rules: list[str] = Field(default_factory=list)
    locations: list[dict] = Field(default_factory=list)
    factions: list[str] = Field(default_factory=list)
    timeline: list[str] = Field(default_factory=list)
    characters: list[_GenChar] = Field(default_factory=list)
    open_threads: list[_GenThread] = Field(default_factory=list)
    first_chapter: str


_GENESIS_SYSTEM = """你是一个小说创世引擎。用户给出题材、主题、主角提示与风格偏好，
你据此生成一个可结构化运行的初始故事世界，并写出第一章正文。

要求：
- rules 至少 3 条，含战力/能力体系限制、禁止 OOC、禁止未声明设定（重生/系统/穿越等）。
- characters 至少 3 个，至少 1 个 present_in_scene=true；id 一律英文 snake_case。
- boundaries 写清角色绝对不会做的事（后续干预拒绝依据）。
- open_threads 至少 2 条未解决悬念。
- first_chapter 为完整中文首章正文（不少于 400 字），首行可作标题。
- 所有内容须围绕用户给出的题材与主题，不要套用无关模板。"""


# ── 内部组装 ────────────────────────────────────────────


def _build_chapter(first_chapter_text: str, title: str) -> SplitChapter:
    return SplitChapter(index=1, title=title, content=first_chapter_text.strip())


def _draft_to_extraction(
    draft: _GenesisDraft, *, name: str, mode: str
) -> ExtractionResult:
    world_yaml = {
        "id": f"world_{name}",
        "slug": name,
        "title": draft.title or name,
        "display_name": draft.display_name or draft.title or name,
        "canonical_place_name": draft.canonical_place_name or "",
        "source_type": "genesis",
        "worldline_policy": "branch_on_major_intervention",
        "divergence_point": "chapter_1_end",
        "scene_description": draft.scene_description or "",
        "rules": list(draft.rules),
        "locations": [dict(loc) for loc in draft.locations],
        "factions": list(draft.factions),
        "timeline": list(draft.timeline),
    }
    characters_yaml = {
        "characters": [
            {
                "id": c.id,
                "name": c.name,
                "narrative_role": c.narrative_role,
                "gender": c.gender,
                "persona": {
                    "traits": c.traits,
                    "desires": c.desires,
                    "fears": c.fears,
                    "boundaries": c.boundaries,
                },
                "memory": [],
                "relationships": {},
                "current_state": {
                    "location": c.location,
                    "emotion": c.emotion,
                    "resources": c.resources,
                },
                "fourth_wall_awareness": 0,
                "present_in_scene": c.present_in_scene,
            }
            for c in draft.characters
        ]
    }
    open_threads = [
        {"id": t.id, "title": t.title, "description": t.description, "status": t.status}
        for t in draft.open_threads
    ]
    anchor_proposal = {
        "extraction_version": GENESIS_VERSION,
        "confidence": mode,
        "warnings": [],
        "protagonist_candidates": [
            c.id for c in draft.characters if c.narrative_role.startswith("protagonist")
        ],
        "intervention_hints": ["可在第一章结尾前后干预在场主角的选择"],
        "suggested_targets": [
            {"id": c.id, "reason": "创世首章在场"}
            for c in draft.characters
            if c.present_in_scene
        ][:3],
        "raw_notes": f"主题创世（{mode}）",
    }
    return ExtractionResult(
        world_yaml=world_yaml,
        characters_yaml=characters_yaml,
        open_threads=open_threads,
        anchor_proposal=anchor_proposal,
        warnings=[f"主题创世（{mode}）：初始世界为生成草稿，可在世界锚定页确认"],
    )


def _mock_draft(
    *, name: str, genre: str, premise: str, protagonist_hint: str, style_hint: str
) -> _GenesisDraft:
    """deterministic mock 创世草稿，吸收用户输入，便于测试。"""
    protagonist_name = (protagonist_hint.strip().splitlines()[0][:12] if protagonist_hint.strip() else "云栖")
    title = premise.strip().splitlines()[0][:16] if premise.strip() else name.replace("-", " ").title()
    style_note = style_hint.strip() or "克制、画面感、留白"

    rules = [
        "角色不能无理由 OOC：性格在短时间内不会剧变",
        "禁止新增未声明设定：重生、穿越、系统、前世记忆、金手指等",
        f"{genre} 体系内力量受限：弱者不能凭空逆转强者，但可借信息、谋略、外物破局",
    ]
    locations = [
        {"id": "origin_hall", "name": "起始之地", "description": f"主角{protagonist_name}所在之处，故事自此展开"},
        {"id": "outer_road", "name": "城外长路", "description": "通往主题冲突核心的去向"},
    ]
    characters = [
        _GenChar(
            id="protagonist",
            name=protagonist_name,
            narrative_role="protagonist_candidate",
            gender="未知",
            traits=["坚韧", "敏锐", "有所守"],
            desires=["追寻主题中的目标", "守护在意之人"],
            fears=["失去方向", "辜负所托"],
            boundaries=["不会为达目的伤害无辜", "不会背弃立下的承诺"],
            location="起始之地",
            emotion="将行未行",
            resources=["随身旧物"],
            present_in_scene=True,
        ),
        _GenChar(
            id="rival",
            name="玄渊",
            narrative_role="antagonist",
            gender="未知",
            traits=["深沉", "执念", "有底线"],
            desires=["达成自身图谋"],
            fears=["计划被识破"],
            boundaries=["不会在毫无必要时自曝身份"],
            location="城外长路",
            emotion="静观",
            resources=["未明手段"],
            present_in_scene=False,
        ),
        _GenChar(
            id="ally",
            name="青禾",
            narrative_role="supporting",
            gender="未知",
            traits=["温和", "机敏"],
            desires=["帮助主角一程"],
            fears=["被卷入更大的漩涡"],
            boundaries=["不会无偿涉险"],
            location="起始之地",
            emotion="关切",
            resources=["一点旧时人脉"],
            present_in_scene=True,
        ),
    ]
    open_threads = [
        _GenThread(id="core_conflict", title="核心冲突", description=premise.strip()[:120] or "主题尚未展开的张力"),
        _GenThread(id="protagonist_drive", title="主角动机", description=f"{protagonist_name}为何踏上此路，仍待揭示"),
    ]
    scene = (
        f"创世主题：{premise.strip()[:200]}\n\n"
        f"风格基调：{style_note}\n\n"
        f"第一章结尾，{protagonist_name}立于起始之地，抉择将至。"
    )
    first_chapter = (
        f"{title}\n\n"
        f"{premise.strip()}\n\n"
        f"{protagonist_name}立于起始之地，夜色未央。"
        f"风从城外长路吹来，带着尚未说破的来意。"
        f"青禾在侧低声提醒，玄渊的影子却已落在远处的檐角。\n\n"
        f"这是故事的第一笔——以{style_note}的笔触落下。"
        f"{protagonist_name}握紧随身旧物，知道一旦迈出这一步，世界便会沿着选择悄然分叉。\n\n"
        f"子时将至，抉择就在眼前。"
    )
    return _GenesisDraft(
        title=title,
        display_name=title,
        canonical_place_name="起始之地",
        scene_description=scene,
        rules=rules,
        locations=locations,
        factions=["主角阵营", "对立面"],
        timeline=["序幕：主题浮现", "第一章：主角登场，抉择将至"],
        characters=characters,
        open_threads=open_threads,
        first_chapter=first_chapter,
    )


def _llm_draft(
    llm: LLMClient,
    *,
    name: str,
    genre: str,
    premise: str,
    protagonist_hint: str,
    style_hint: str,
) -> _GenesisDraft:
    user = (
        f"【项目 slug】{name}\n"
        f"【题材】{genre}\n"
        f"【主题/想看的故事】\n{premise}\n\n"
        f"【主角提示】{protagonist_hint or '（未指定，自行设计）'}\n"
        f"【文风偏好】{style_hint or '（未指定）'}\n\n"
        "请据此创世，输出 JSON。"
    )
    draft, _usage = llm.chat_json_with_usage(
        _GENESIS_SYSTEM, user, _GenesisDraft, temperature=0.8
    )
    return draft


def _resolve_mode(mock: bool) -> tuple[bool, LLMClient | None]:
    """返回 (use_mock, llm)；无 key / mock=true 时 use_mock=True。"""
    settings = LLMSettings.from_env()
    env_mock = os.environ.get("LNE_MOCK", "").lower() in ("1", "true", "yes")
    if mock or env_mock or not settings.llm_api_key:
        return True, None
    llm = LLMClient(settings=settings, mock=False)
    if not llm.available:
        return True, None
    return False, llm


def generate_story(
    *,
    name: str,
    premise: str,
    genre: str = "xianxia",
    protagonist_hint: str = "",
    style_hint: str = "",
    mock: bool = False,
    force: bool = False,
    projects_dir: Path | None = None,
) -> GenesisServiceResult:
    """从主题创世一个初始项目并落盘，结构与 import-novel 同构。

    抛出：
    - GenesisRequestError：坏 slug / 空 premise（HTTP 400）
    - GenesisProjectExistsError：同名项目存在且 force=False（HTTP 409）
    """
    name = (name or "").strip()
    if not _SLUG_RE.match(name):
        raise GenesisRequestError("项目名须为英文小写字母+数字+连字符，如 my-story")
    if not (premise or "").strip():
        raise GenesisRequestError("请填写主题/想看的故事（premise 不能为空）")

    pdir = projects_dir or _default_projects_dir()
    if (pdir / name).exists() and not force:
        raise GenesisProjectExistsError(f"项目 '{name}' 已存在，如需覆盖请开启覆盖选项")

    use_mock, llm = _resolve_mode(mock)
    warnings: list[str] = []
    mode = "mock"
    draft: _GenesisDraft
    if use_mock or llm is None:
        draft = _mock_draft(
            name=name,
            genre=genre,
            premise=premise,
            protagonist_hint=protagonist_hint,
            style_hint=style_hint,
        )
    else:
        try:
            draft = _llm_draft(
                llm,
                name=name,
                genre=genre,
                premise=premise,
                protagonist_hint=protagonist_hint,
                style_hint=style_hint,
            )
            mode = "llm"
        except Exception as exc:  # LLM 失败安全退化 mock
            warnings.append(f"LLM 创世失败，已退化为 mock：{exc}")
            draft = _mock_draft(
                name=name,
                genre=genre,
                premise=premise,
                protagonist_hint=protagonist_hint,
                style_hint=style_hint,
            )

    extraction = _draft_to_extraction(draft, name=name, mode=mode)
    chapter = _build_chapter(draft.first_chapter, draft.title or name)

    project_dir = write_project(
        name,
        [chapter],
        extraction,
        anchor_chapter_index=0,
        projects_dir=pdir,
        allow_overwrite=force,
        genre=genre,
    )

    # 追加 genesis_meta.json（additive，不影响 import_meta.json / indexer）
    genesis_meta = {
        "slug": name,
        "created_at": datetime.now().isoformat(),
        "source_type": "genesis",
        "genesis_version": GENESIS_VERSION,
        "generation_mode": mode,
        "genre": genre,
        "premise": premise,
        "protagonist_hint": protagonist_hint,
        "style_hint": style_hint,
    }
    (project_dir / "genesis_meta.json").write_text(
        json.dumps(genesis_meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    vr = validate_project(project_dir)
    warnings.extend(extraction.warnings)
    warnings.extend(vr.warnings)
    warnings.extend(f"校验未通过：{e}" for e in vr.errors)

    world = extraction.world_yaml
    display_name = world.get("display_name") or world.get("title") or name
    character_count = len(extraction.characters_yaml.get("characters", []) or [])

    return GenesisServiceResult(
        story_slug=name,
        display_name=display_name,
        chapter_count=1,
        character_count=character_count,
        anchor_chapter_index=0,
        generation_mode=mode,
        warnings=warnings,
    )

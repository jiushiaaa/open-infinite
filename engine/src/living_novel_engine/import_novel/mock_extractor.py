"""Mock Extractor — 生成结构合法的占位 world/characters YAML，不调 LLM。"""

from __future__ import annotations

from dataclasses import dataclass, field

from living_novel_engine.import_novel.splitter import SplitChapter


@dataclass
class ExtractionResult:
    """LLM 或 mock 抽取的统一输出结构。"""

    world_yaml: dict
    characters_yaml: dict
    open_threads: list[dict] = field(default_factory=list)
    anchor_proposal: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def mock_extract(
    chapters: list[SplitChapter],
    *,
    story_name: str = "unnamed",
    genre: str = "xianxia",
    anchor_chapter_index: int | None = None,
) -> ExtractionResult:
    """基于章节文本生成 mock 抽取结果（不依赖 LLM）。

    Mock 逻辑：从章节标题/内容中做最简单的关键词提取，
    生成满足 StoryWorld/CharacterAgent 最低字段的结构。
    """
    if anchor_chapter_index is None:
        anchor_chapter_index = len(chapters) - 1

    anchor = chapters[anchor_chapter_index]

    world_yaml = {
        "id": f"world_{story_name}",
        "slug": story_name,
        "title": _infer_title(chapters, story_name),
        "display_name": _infer_title(chapters, story_name),
        "canonical_place_name": "云城",
        "source_type": "imported",
        "worldline_policy": "branch_on_major_intervention",
        "divergence_point": f"chapter_{anchor.index}_end",
        "scene_description": _build_scene_desc(anchor),
        "rules": [
            "角色不能无理由 OOC：性格在短时间内不会剧变",
            "禁止新增原文未声明设定：重生、穿越、系统、前世记忆等",
            "境界压制：低境界者无法以蛮力击败高两境以上修士",
            "凡人无法直接对抗修士，但可借信息差、阵法或外物破局",
        ],
        "locations": [
            {"id": "yun_city", "name": "云城", "description": "苍澜山脉东麓，凡人城镇"},
            {"id": "gui_yun_zhai", "name": "归云斋", "description": "城东旧仓库区的古玩商铺"},
            {"id": "yun_xi_academy", "name": "云溪书院", "description": "城外书院"},
        ],
        "factions": ["苍澜派", "赵家（城主府）", "韩无归势力"],
        "timeline": [
            "三个月前：风鸣铃从苍澜派密库失窃",
            "三日前：沈冰月到达云城",
            "今日：赵轩与沈冰月潜入归云斋",
        ],
    }

    characters_yaml = {
        "characters": [
            {
                "id": "zhao_xuan",
                "name": "赵轩",
                "narrative_role": "protagonist_candidate",
                "gender": "男",
                "persona": {
                    "traits": ["正直", "聪慧", "重恩"],
                    "desires": ["查明真相", "保护云城", "理解父亲旧事"],
                    "fears": ["无力保护家人", "父亲有不可告人之事"],
                    "boundaries": ["不会背弃三代恩情", "不会见死不救"],
                },
                "memory": [
                    "父亲曾告诫苍澜派与赵家有三代恩情",
                    "发现账簿中三个月前有人购入铜铃形器物",
                    "潜入归云斋地下室，发现灵脉引导阵与风鸣铃",
                ],
                "relationships": {
                    "shen_bing_yue": "合作者，互相信任尚浅",
                    "han_wu_gui": "对手，被质问父亲旧事",
                    "zhao_yuan_shan": "已故父亲，对其旧事存疑",
                },
                "current_state": {
                    "location": "归云斋地下室",
                    "emotion": "震惊与困惑",
                    "resources": ["父亲加锁手记"],
                },
                "fourth_wall_awareness": 0,
                "present_in_scene": True,
            },
            {
                "id": "shen_bing_yue",
                "name": "沈冰月",
                "narrative_role": "protagonist_candidate",
                "gender": "女",
                "persona": {
                    "traits": ["冷峻", "果断", "忠于师门"],
                    "desires": ["追回风鸣铃", "完成师门任务"],
                    "fears": ["灵潮逆涌伤及无辜", "任务失败"],
                    "boundaries": ["不会为完成任务伤害无辜", "不会背弃苍澜派"],
                },
                "memory": [
                    "追踪风鸣铃线索至云城",
                    "确认归云斋地下室有灵脉引导阵",
                    "韩无归是被逐出山门的师兄",
                ],
                "relationships": {
                    "zhao_xuan": "合作者，对其凡人身份有些意外",
                    "han_wu_gui": "昔日师兄，如今敌对",
                },
                "current_state": {
                    "location": "归云斋地下室",
                    "emotion": "警戒",
                    "resources": ["长剑", "苍澜派玉牌"],
                },
                "fourth_wall_awareness": 0,
                "present_in_scene": True,
            },
            {
                "id": "han_wu_gui",
                "name": "韩无归",
                "narrative_role": "antagonist",
                "gender": "男",
                "persona": {
                    "traits": ["深沉", "记仇", "有底线"],
                    "desires": ["向赵家问清旧事", "证明自己清白"],
                    "fears": ["真相永远被埋没"],
                    "boundaries": ["声称不想杀无辜", "但会以百姓昏厥为代价"],
                },
                "memory": [
                    "十二年前被赵远山举报暗修禁术而逐出苍澜派",
                    "参与铸造风鸣铃",
                    "布置灵脉引导阵",
                ],
                "relationships": {
                    "shen_bing_yue": "昔日师妹",
                    "zhao_xuan": "赵远山之子，质问对象",
                },
                "current_state": {
                    "location": "归云斋地下室",
                    "emotion": "从容",
                    "resources": ["风鸣铃（控制中）", "灵脉引导阵"],
                },
                "fourth_wall_awareness": 0,
                "present_in_scene": True,
            },
        ]
    }

    open_threads = [
        {"id": "wind_bell_retrieval", "title": "风鸣铃争夺", "description": "沈冰月需夺回风鸣铃，韩无归拒绝归还", "status": "open"},
        {"id": "zhao_father_secret", "title": "赵远山旧事", "description": "韩无归质问赵轩父亲当年举报真相", "status": "open"},
        {"id": "spirit_tide_threat", "title": "灵潮逆涌威胁", "description": "灵脉引导阵一旦激活将危及全城", "status": "open"},
    ]

    anchor_proposal = {
        "extraction_version": "0.1",
        "confidence": "mock",
        "warnings": ["这是 mock 抽取结果，非 LLM 真实分析"],
        "protagonist_candidates": ["zhao_xuan", "shen_bing_yue"],
        "intervention_hints": [
            "可在韩无归激活阵法前干预赵轩或沈冰月的行动",
            "可向赵轩透露父亲手记中的信息",
        ],
        "suggested_targets": [
            {"id": "zhao_xuan", "reason": "场景内凡人主角，可接收 whisper/信息"},
            {"id": "shen_bing_yue", "reason": "场景内修士，可被劝阻或引导"},
        ],
        "raw_notes": f"基于 {len(chapters)} 章 mock 抽取",
    }

    return ExtractionResult(
        world_yaml=world_yaml,
        characters_yaml=characters_yaml,
        open_threads=open_threads,
        anchor_proposal=anchor_proposal,
        warnings=["mock 模式：未使用 LLM，结果为预设模板"],
    )


def _infer_title(chapters: list[SplitChapter], fallback: str) -> str:
    if chapters:
        first_title = chapters[0].title
        for pattern in ["风起", "云城"]:
            if pattern in first_title:
                return "风起云城"
    return fallback.replace("-", " ").replace("_", " ").title()


def _build_scene_desc(anchor: SplitChapter) -> str:
    lines = anchor.content.strip().split("\n")
    tail = "\n".join(lines[-6:]) if len(lines) > 6 else anchor.content
    if len(tail) > 300:
        tail = tail[-300:]
    return f"干预节点：{anchor.title}\n\n{tail}"

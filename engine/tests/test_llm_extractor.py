"""测试 llm_extractor 的结构解析与验证逻辑。"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from living_novel_engine.import_novel.llm_extractor import (
    _build_anchor_proposal,
    _build_chapter_summaries,
    _parse_json_response,
    _patch_world_defaults,
    _validate_and_repair,
    llm_extract,
)
from living_novel_engine.import_novel.splitter import SplitChapter, split_chapters
from living_novel_engine.llm.client import LLMClient


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "mini_novel"

MOCK_WORLD_RESPONSE = json.dumps(
    {
        "title": "风起云城",
        "display_name": "风起云城",
        "canonical_place_name": "云城",
        "divergence_point": "第三章结尾韩无归激活阵法",
        "scene_description": "归云斋地下室，符文亮起，韩无归与沈冰月对峙",
        "rules": [
            "境界压制：低境界者无法蛮力击败高两境修士",
            "角色不能无理由 OOC",
            "禁止新增原文未声明设定：重生、穿越、系统等",
            "灵脉引导阵激活后方圆十里灵力波动",
        ],
        "locations": [
            {"id": "yun_city", "name": "云城", "description": "苍澜山脉东麓凡人城镇"},
            {"id": "gui_yun_zhai", "name": "归云斋", "description": "城东古玩商铺"},
            {"id": "underground", "name": "归云斋地下室", "description": "灵脉引导阵所在"},
        ],
        "factions": ["苍澜派", "赵家", "韩无归"],
        "timeline": [
            "三月前：风鸣铃失窃",
            "三日前：沈冰月到云城",
            "今夜：潜入归云斋",
        ],
    },
    ensure_ascii=False,
)

MOCK_CHAR_RESPONSE = json.dumps(
    {
        "characters": [
            {
                "id": "zhao_xuan",
                "name": "赵轩",
                "narrative_role": "protagonist_candidate",
                "gender": "男",
                "persona": {
                    "traits": ["正直", "聪慧"],
                    "desires": ["保护云城"],
                    "fears": ["无力保护"],
                    "boundaries": ["不背弃恩情"],
                },
                "memory": ["发现账簿异常"],
                "relationships": {"shen_bing_yue": "合作者"},
                "current_state": {
                    "location": "归云斋地下室",
                    "emotion": "震惊",
                    "resources": ["父亲手记"],
                },
                "present_in_scene": True,
            },
            {
                "id": "shen_bing_yue",
                "name": "沈冰月",
                "narrative_role": "protagonist_candidate",
                "gender": "女",
                "persona": {
                    "traits": ["冷峻", "果断"],
                    "desires": ["夺回风鸣铃"],
                    "fears": ["任务失败"],
                    "boundaries": ["不伤无辜"],
                },
                "memory": ["追踪风鸣铃至云城"],
                "relationships": {"zhao_xuan": "合作者", "han_wu_gui": "敌对"},
                "current_state": {
                    "location": "归云斋地下室",
                    "emotion": "警戒",
                    "resources": ["长剑"],
                },
                "present_in_scene": True,
            },
            {
                "id": "han_wu_gui",
                "name": "韩无归",
                "narrative_role": "antagonist",
                "gender": "男",
                "persona": {
                    "traits": ["深沉", "记仇"],
                    "desires": ["问清旧事"],
                    "fears": ["真相被埋"],
                    "boundaries": ["不想杀无辜"],
                },
                "memory": ["被逐出师门十二年"],
                "relationships": {"shen_bing_yue": "师妹"},
                "current_state": {
                    "location": "归云斋地下室",
                    "emotion": "从容",
                    "resources": ["风鸣铃"],
                },
                "present_in_scene": True,
            },
        ],
        "open_threads": [
            {
                "id": "wind_bell",
                "title": "风鸣铃争夺",
                "description": "沈冰月要夺回，韩无归拒绝",
                "status": "open",
            },
            {
                "id": "father_secret",
                "title": "赵远山旧事",
                "description": "赵轩父亲当年举报的真相",
                "status": "open",
            },
        ],
    },
    ensure_ascii=False,
)


class TestParseJsonResponse:
    def test_clean_json(self):
        data = _parse_json_response('{"a": 1}', "test")
        assert data == {"a": 1}

    def test_json_in_markdown_block(self):
        raw = '```json\n{"a": 1}\n```'
        data = _parse_json_response(raw, "test")
        assert data == {"a": 1}

    def test_json_with_preamble(self):
        raw = 'Here is the result:\n\n{"a": 1, "b": [2]}'
        data = _parse_json_response(raw, "test")
        assert data == {"a": 1, "b": [2]}

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="不是合法 JSON"):
            _parse_json_response("not json at all", "test")


class TestValidateAndRepair:
    def test_no_warnings_on_good_data(self):
        world = {"rules": ["r1", "r2", "r3"], "locations": [{"id": "a"}, {"id": "b"}]}
        chars = {"characters": [{"id": "c1", "present_in_scene": True}, {"id": "c2", "present_in_scene": False}]}
        threads = [{"id": "t1"}, {"id": "t2"}]
        warnings = _validate_and_repair(world, chars, threads)
        assert warnings == []

    def test_auto_assigns_present_in_scene(self):
        chars = {"characters": [{"id": "c1", "name": "X", "present_in_scene": False}]}
        _validate_and_repair({"rules": ["r"] * 3, "locations": [{}, {}]}, chars, [{}, {}])
        assert chars["characters"][0]["present_in_scene"] is True

    def test_auto_assigns_missing_id(self):
        chars = {"characters": [{"name": "X", "present_in_scene": True}]}
        warnings = _validate_and_repair({"rules": ["r"] * 3, "locations": [{}, {}]}, chars, [{}, {}])
        assert chars["characters"][0]["id"] == "char_0"
        assert any("自动分配" in w for w in warnings)

    def test_deduplicates_ids(self):
        chars = {
            "characters": [
                {"id": "hero", "present_in_scene": True},
                {"id": "hero", "present_in_scene": False},
            ]
        }
        warnings = _validate_and_repair({"rules": ["r"] * 3, "locations": [{}, {}]}, chars, [{}, {}])
        ids = [c["id"] for c in chars["characters"]]
        assert len(set(ids)) == 2
        assert any("重复" in w for w in warnings)


class TestLlmExtractIntegration:
    def test_full_extraction_with_fake_llm(self):
        """模拟 LLM 返回预设 JSON，验证整条链路。"""
        chapters = split_chapters(FIXTURES_DIR)

        fake_llm = MagicMock(spec=LLMClient)
        fake_llm.mock = False
        call_count = [0]
        seen_users: list[str] = []

        def fake_chat(system, user, *, temperature=0.3, max_tokens=4096):
            call_count[0] += 1
            seen_users.append(user)
            if call_count[0] == 1:
                return MOCK_WORLD_RESPONSE
            return MOCK_CHAR_RESPONSE

        fake_llm.chat = fake_chat

        result = llm_extract(chapters, fake_llm, story_name="test-llm")

        assert call_count[0] == 2
        assert result.world_yaml["source_type"] == "imported"
        assert result.world_yaml["title"] == "风起云城"
        assert len(result.world_yaml["rules"]) >= 3
        assert len(result.world_yaml["locations"]) >= 2

        chars = result.characters_yaml["characters"]
        assert len(chars) == 3
        assert any(c["id"] == "zhao_xuan" for c in chars)

        assert len(result.open_threads) >= 2
        assert result.anchor_proposal["confidence"] == "llm"
        assert "【题材模板】" in seen_users[0]
        assert "修仙" in seen_users[0]

    def test_chapter_summaries_format(self):
        chapters = split_chapters(FIXTURES_DIR)
        summaries = _build_chapter_summaries(chapters)
        assert "===" in summaries
        assert "风起云城" in summaries


class TestPatchWorldDefaults:
    def test_fills_missing_fields(self):
        world = {"title": "Test"}
        anchor = SplitChapter(index=5, title="Ch5", content="text")
        _patch_world_defaults(world, "my-story", anchor)
        assert world["id"] == "world_my-story"
        assert world["source_type"] == "imported"
        assert world["divergence_point"] == "chapter_5_end"
        assert world["display_name"] == "Test"

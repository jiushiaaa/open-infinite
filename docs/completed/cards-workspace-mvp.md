# Cards Workspace MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第六刀，设定资产产品化的只读/轻编辑切片。  
> 范围：世界卡、角色卡、风格卡展示；不生成独立卡片 artifact，不做版本化，不扩成完整作者工作台。

## 1. 目标

Cards Workspace MVP 用于把已有长篇设定从“分散的 memory 文件”整理成作者能扫读的设定资产入口。第一刀只从现有 `master_setting.yaml`、`memory/character_states/*.yaml` 和 `characters.yaml` 降级源派生卡片，帮助用户快速确认世界规则、角色状态和风格边界。

## 2. 已完成

- 新增 service：`living_novel_engine.service.get_cards_workspace(story_slug)`。
- 新增 API：`GET /api/stories/<slug>/cards-workspace`。
- 新增前端入口：长篇项目工作台「设定卡片」面板。
- 支持卡片：
  - 世界卡：作品名、题材、世界规则、力量限制、禁用设定、地点、势力。
  - 角色卡：人物名、叙事定位、当前位置、情绪状态、边界、资源、记忆。
  - 风格卡：题材基调、叙事口径、避免项。
- 轻编辑边界：可编辑字段仍复用现有 MasterSetting 白名单保存链路；Cards Workspace 本身只读。

## 3. API 契约

返回核心字段：

```json
{
  "version": "cards-workspace-mvp",
  "mode": "read_only_cards_workspace",
  "status": "ready | attention",
  "story_slug": "my-story",
  "source_kind": "imported | builtin",
  "summary": {
    "card_count": 0,
    "world_card_count": 1,
    "character_card_count": 0,
    "style_card_count": 1,
    "editable_card_count": 0,
    "writes_artifacts": false,
    "external_services_required": false
  },
  "groups": [],
  "cards": [],
  "warnings": [],
  "boundaries": [],
  "next_steps": []
}
```

错误边界：

- 坏 slug 返回 400。
- 缺项目返回 404。
- `master_setting.yaml` 缺失或损坏不抛 500，降级为 `attention`。
- 角色状态目录缺失时尝试从 `characters.yaml` 降级生成角色卡。

## 4. 安全边界

- 不调用真实 LLM。
- 不调用 embedding、向量库、GraphRAG、Zep 或 reranker。
- 不写 artifact，不生成 `cards.yaml`。
- 不改变 `master_setting.yaml` 保存白名单。
- 不改变 `run_scene`、job 或 runner 默认行为。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_cards_workspace.py -q
python -m pytest engine\tests\test_cards_workspace.py engine\tests\test_v088_long_project_workspace.py engine\tests\test_v092_master_setting_update.py engine\tests\test_project_health.py -q
cd engine\ui
pnpm run build
cd ..
python -m pytest -q
cd ..
git diff --check
```

该刀收口时后端全量基线：`731 passed`；当前全量基线以 `../../memory.md` 为准。

## 6. 后续状态

`OpenAPI / Typed Client MVP` 已在后续第七刀收口，见 `openapi-typed-client-mvp.md`。下一刀建议进入 `Bundled Release / Desktop Packaging` 的轻量发行准备评估。

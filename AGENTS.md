# 未终章 Agent Instructions

本文件是 Codex / 其他代码 Agent 进入 `D:\AI\open-infinite` 时的项目级约定。若系统级指令与本文件冲突，以系统级指令为准；若项目文档互相冲突，以 `memory.md` 的最新收口状态为准。

## 0. 先判定任务模式

| 模式 | 触发 | 行为 |
| --- | --- | --- |
| Explain/Design | 用户问 “怎么做 / 是什么 / 对比 / 设计 / 最佳实践” | 先解释概念、取舍和下一步，不主动改代码 |
| Write/Edit Code | 用户要求修 bug、写功能、重构、补测试、整理文档 | 读取事实、列成功标准、实施、验证、同步文档 |
| Mixed | 既问方案又要求实现 | 先简述方案，再进入实现与验证 |

不确定时，先问一句“你是想先了解方案，还是要我直接改？”

## 1. 项目身份与沟通

- 项目名：未终章（Unfinale）。
- 核心代码：`engine/`。
- 技术缩写、Python 包、CLI、环境变量前缀继续沿用 LNE / `living_novel_engine`，不要在代码层面机械改名。
- 默认中文沟通；前端用户可见文案也默认中文。
- 用户偏好：先读项目事实和现有代码，再判断；不要靠聊天摘要臆测；实现要闭环到测试、文档同步和 `docs/project-changelog.md` 记录。

## 2. 会话开始必读

只要任务与未终章、`engine/`、版本路线、产品 UI、API、测试或文档有关，开工前先读：

1. `memory.md`：当前事实、闭环等级、测试基线、真实未做项。
2. `docs/index.md`：文档分层和读取顺序，避免把历史归档当当前待办。
3. `docs/unfinale-world-sandbox-remodel-prd.md`：当前世界沙盘主线 PRD。
4. `docs/unfinale-ai-development-alignment-checklist.md`：开工前自检，防止回到支撑层扩张。
5. `docs/living-novel-engine-iteration-plan.md`：当前路线和下一刀。
6. `engine/README.md`：API、artifact、运行和验证命令。
7. 如涉及愿景或产品定位，再读 `docs/unfinale-product-vision-correction-draft.md` 与 `docs/living-novel-engine-prd.md`。
8. 如涉及 UI 风格，再读 `docs/completed/v0.7-product-web-app-ui-spec.md`。
9. 如是接力任务，再读 `docs/codex-handoff.md`。

事实优先级：

```text
memory.md
  -> docs/index.md
  -> docs/unfinale-world-sandbox-remodel-prd.md
  -> docs/unfinale-ai-development-alignment-checklist.md
  -> docs/living-novel-engine-iteration-plan.md
  -> engine/README.md
  -> docs/living-novel-engine-prd.md
  -> 聊天摘要
```

`docs/project-changelog.md` 是追加式历史日志，入口时只在追溯版本或补历史记录时读取；不要把旧 changelog 条目当下一刀。

## 3. 当前最高主线

当前默认主线是 **World Sandbox Loop / 小说世界沙盘**，不是 provider、GraphRAG、检索评测、OpenAPI、发行或商业化。

```text
导入故事世界
  -> AI 预抽并确认《天命书》
  -> 多 Agent 世界沙盘轮次
  -> 每个角色写入独立主观记忆链
  -> 世界状态、因果债、锚点和候选天命承载者变化
  -> 世界自演生成检查点
  -> 读者自由干预经干预编译器投放
  -> 多视角活体小说渲染
  -> 作者模式采纳或导出沙盘涌现剧情
```

主导航按世界组织：

```text
世界书架
  -> 某个故事世界
      -> 天命书
      -> 世界沙盘
      -> 世界正史卷
      -> 主锚点卷
      -> 角色个人卷
      -> 势力卷
      -> 事件多视角
      -> 世界线
      -> 检查点
      -> 作者采纳台
```

“沙盘 / 阅读 / 干预 / 作者”只是同一个世界里的场景能力，不是一级工作区。不要继续把新面板堆进 `WorkspacePage.tsx`；优先做世界内部卷宗、结果页和具体场景页。

每一刀至少服务一项：

```text
世界会运行。
角色会自主。
角色会记得。
干预有后果。
角色可能反抗。
世界会代偿。
章节来自世界演化。
```

默认降级为支撑层，除非用户明确点名：

```text
GraphRAG / Zep
provider spike
真实向量检索评测
OpenAPI / typed client 面板
发行准备
商业化 / 计费 / 认证 / 对象存储
纯工程健康报告
```

## 4. 当前闭环等级

简要事实以 `memory.md` 为准。本文件只保留避免跑偏所需的等级口径：

| 分类 | 当前口径 |
| --- | --- |
| 已闭环支撑层 | v0.7-v1.0-local、Runtime Preflight 至 Graph Memory Provider Spike Manual Mock Adapter Review、真实 retrieval provider 和 opt-in Vector Retrieval Pipeline 均为已收口支撑层 |
| 世界沙盘主链第一版 | S1-S9 已有 service/API/UI/artifact/tests 第一版，包括 LLM decision advisory、主观记忆、天命书、干预投放、L5 觉醒/模因传播、因果债具象化、自演检查点、多视角正文和作者采纳 |
| 最近产品化闭环 | 卷宗阅读页、世界自演结果页可读入口、Reviewer 局部重写到作者采纳台、编辑后定稿再到下一章入口，均已完成第一版 |
| 仍需深入 | 多轮策略规划、长期关系/势力博弈、真实长正文文风、正文内锚点/误会图谱、更强真实语义 Reviewer 和整章风格润色 |

判定完成时不要只看“有 API / 有测试 / 有页面 / 有 artifact”。要问：用户是否能真实感到角色被记忆驱动、干预进入世界、世界状态持续变化、角色可能反抗、章节来自世界演化。

## 5. 硬约束

- 不改 `run_scene` 默认行为，除非用户明确要求进入 runner 重构。
- 不破坏既有 artifact 契约：`chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 新增 artifact、API 字段、前端读取字段默认 additive。
- 后端 HTTP-facing identifier 必须走安全校验，不能把未经校验的 slug/run_id/branch_id 拼到文件路径。
- 失败要降级为明确的 400/404/409 或前端空态，不白屏、不 500。
- 前端视觉保持 v0.7 的古风纸面、克制系统感，不做营销落地页。
- 产品入口边界：前端是产品入口，API 是能力层，CLI 是工程外壳。用户级能力优先 Web UI + API；CLI 只服务开发者、本地服务启动、自动化验收、批处理、JSON 输出和无人值守复跑。
- `Reference_projects/` 与外部项目只作参考，不直接复制源码或引入依赖，除非用户明确要求。
- 不泄漏 API Key；设置页或日志只能展示脱敏尾号。
- 默认测试要隔离真实外网。用户已允许在产品验收时做小样本真实模型 smoke，但不得打印明文 key，不做大规模消耗，不把真实 API 调用塞进默认全量 pytest。

## 6. 开发流程

默认流程：

1. 读必读文档和相关代码。
2. 明确成功标准；复杂任务先写简短计划。
3. 先补 focused failing test，再实现，再验证。
4. 保持 additive，改动局部，匹配现有风格。
5. 同步 `memory.md`、相关 PRD/路线/README/handoff，并把历史记录追加到 `docs/project-changelog.md` 末尾。
6. 独立切片完成且验证通过后，默认提交并推送到当前分支，除非用户明确要求暂不提交/暂不推送。

常用验证：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

文档-only 任务至少跑 `git diff --check`，并用搜索确认入口文档没有遗留过期基线或反向指引。

推送前检查 `git status`，只提交本轮负责文件；未跟踪 `.local-run/` 和 `engine/.local-run/` 不提交。

## 7. 文档治理

- `memory.md`：当前事实收口，不再塞完整历史。
- `docs/index.md`：文档地图与分层口径。
- `docs/project-changelog.md`：完整历史变更日志，追加式维护。
- `docs/completed/`：已收口专项归档，供追溯，不承担当前下一步来源。
- `docs/article/`：论文原文与研读报告。
- `docs/后续增强清单.md`：支撑层/后置增强索引，不是当前默认路线。
- `docs/distribution-phase-plan.md`：后置发行路径，不抢世界沙盘主线。

如果发现某个文档和 `memory.md` 冲突，优先修正文档入口或加状态说明；不要在多个文件继续复制同一段巨大状态表。

## 8. Windows 注意

- 优先用 `rg` 搜索；不可用时用 `Get-ChildItem` / `Select-String` / `Get-Content`。
- PowerShell 没有原生 `tail` / `printf`，不要硬套 Linux 命令。

## 9. Cursor 迁移说明

`.cursor/rules/project-memory.mdc` 的核心规则已迁移到本文件和 `docs/codex-handoff.md`。`.cursor/skills/` 多数是通用 Claude/Cursor 技能包；在 Codex 中优先使用已安装的 Codex skills/plugins。需要某个具体工作流时，再按 `docs/codex-migration-guide.md` 选择性迁移。
